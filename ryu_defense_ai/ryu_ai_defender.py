from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv4, tcp, udp
from ryu.lib import hub

import torch
import torch.nn as nn
import numpy as np
import math
import collections
import joblib
import warnings

warnings.filterwarnings('ignore')

# ==========================================
# AI 模型架构 
# ==========================================
NUM_CLASSES = 6
NORMAL_CLASS_INDEX = 2

class MultiClassCNNLSTM(nn.Module):
    def __init__(self, num_features=3, hidden_dim=128, num_classes=NUM_CLASSES):
        super(MultiClassCNNLSTM, self).__init__()
        self.cnn = nn.Sequential(
            nn.Conv1d(in_channels=num_features, out_channels=64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=2)
        )
        self.lstm = nn.LSTM(input_size=64, hidden_size=hidden_dim, num_layers=1, batch_first=True)
        self.fc = nn.Linear(hidden_dim, num_classes)
    def forward(self, x):
        c_out = self.cnn(x).transpose(1, 2)
        l_out, _ = self.lstm(c_out)
        return self.fc(l_out[:, -1, :])

def calc_entropy(data_list):
    if not data_list: return 0.0
    counts = collections.Counter(data_list)
    total = len(data_list)
    return sum(- (c / total) * math.log2(c / total) for c in counts.values())

# ==========================================
# 2. Ryu SDN 防御核心逻辑 
# ==========================================
class AIDefender(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(AIDefender, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.datapaths = {}
        self.monitor_interval = 1.0 
        
        self.current_src_ips = []
        self.current_dst_ports = []
        self.current_packet_count = 0
        self.sequence_buffer = collections.deque(maxlen=10)
        
        self.logger.info(" 正在加载 AI 模型与缩放器...")
        self.model = MultiClassCNNLSTM()
        self.model.load_state_dict(torch.load('final_ryu_model.pth', map_location='cpu'))
        self.model.eval()
        self.scaler = joblib.load('ryu_scaler.pkl')
        self.logger.info("武器装填完毕！AI 守卫开始巡视网络。")

        self.monitor_thread = hub.spawn(self._monitor)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        self.datapaths[datapath.id] = datapath
        parser = datapath.ofproto_parser
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(datapath.ofproto.OFPP_CONTROLLER, datapath.ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, idle_timeout=0, hard_timeout=0):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                idle_timeout=idle_timeout, hard_timeout=hard_timeout,
                                match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        if eth.ethertype == 0x88cc: return 
        
        ip_pkt = pkt.get_protocol(ipv4.ipv4)
        tcp_pkt = pkt.get_protocol(tcp.tcp)
        udp_pkt = pkt.get_protocol(udp.udp)
        
        is_attack_port = False 
        
        if ip_pkt:
            self.current_src_ips.append(ip_pkt.src)
            self.current_packet_count += 1
            if tcp_pkt: 
                self.current_dst_ports.append(tcp_pkt.dst_port)
                if tcp_pkt.dst_port == 80: is_attack_port = True 
            elif udp_pkt: 
                self.current_dst_ports.append(udp_pkt.dst_port)
                if udp_pkt.dst_port == 80: is_attack_port = True # 已增加对 UDP 80 端口的攻击判定

        in_port = msg.match['in_port']
        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][eth.src] = in_port
        out_port = self.mac_to_port[dpid].get(eth.dst, datapath.ofproto.OFPP_FLOOD)
        actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]
        
        if out_port != datapath.ofproto.OFPP_FLOOD:
            # 坚决不给 80 端口下发直通流表，强制交由 AI 审查
            if not is_attack_port:
                match = datapath.ofproto_parser.OFPMatch(in_port=in_port, eth_dst=eth.dst, eth_src=eth.src)
                self.add_flow(datapath, 1, match, actions, idle_timeout=10)
        
        out = datapath.ofproto_parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                                   in_port=in_port, actions=actions, data=msg.data if msg.buffer_id == datapath.ofproto.OFP_NO_BUFFER else None)
        datapath.send_msg(out)

    def _monitor(self):
        while True:
            hub.sleep(self.monitor_interval)
            
            # 1. 尺度对齐：只取前 10 个包算熵
            sample_size = 10
            src_sample = self.current_src_ips[:sample_size] if len(self.current_src_ips) > sample_size else self.current_src_ips
            dst_sample = self.current_dst_ports[:sample_size] if len(self.current_dst_ports) > sample_size else self.current_dst_ports
            
            src_entropy = calc_entropy(src_sample)
            dst_entropy = calc_entropy(dst_sample)
            pkt_rate = self.current_packet_count / self.monitor_interval
            
            if pkt_rate > 0:
                self.logger.info(f"📊 对齐特征 -> 速率: {pkt_rate:.0f} pps | 源IP熵: {src_entropy:.2f} | 端口熵: {dst_entropy:.2f}")

            self.current_src_ips = []
            self.current_dst_ports = []
            self.current_packet_count = 0
            
            if pkt_rate == 0:
                self.sequence_buffer.append([0.0, 0.0, 0.0])
                continue
                
            # 2. 量纲对齐：放大物理速率
            aligned_rate = pkt_rate * 10000 
            scaled_feature = self.scaler.transform([[src_entropy, dst_entropy, aligned_rate]])[0]
            self.sequence_buffer.append(scaled_feature)
            
            # 3. 凑齐 10 秒特征进行推断
            if len(self.sequence_buffer) == 10:
                seq_array = np.array([list(self.sequence_buffer)]) 
                tensor_input = torch.FloatTensor(seq_array).transpose(1, 2) 
                
                with torch.no_grad():
                    output = self.model(tensor_input)
                    pred_class = torch.max(output, 1)[1].item()
                
                self.logger.info(f" [AI 思考中] 模型当前预测 ID: {pred_class} (正常设定是 {NORMAL_CLASS_INDEX})")
                
                # 触发防御机制
                if pred_class != NORMAL_CLASS_INDEX and pkt_rate > 50: 
                    self.logger.warning(f"！CNN-LSTM 侦测到攻击！预测分类 ID: {pred_class} | 当前速率: {pkt_rate:.1f} pps")
                    self.mitigate_attack()
                    self.sequence_buffer.clear()

    def mitigate_attack(self):
        self.logger.info("[主动防御] 正在下发 OpenFlow 阻断规则，全面隔离恶意流量...")
        for dp in self.datapaths.values():
            parser = dp.ofproto_parser
            
            # 阻断 TCP 80
            match_tcp = parser.OFPMatch(eth_type=0x0800, ip_proto=6, tcp_dst=80)
            self.add_flow(dp, priority=100, match=match_tcp, actions=[], hard_timeout=20) 
            
            # 阻断 UDP 80
            match_udp = parser.OFPMatch(eth_type=0x0800, ip_proto=17, udp_dst=80)
            self.add_flow(dp, priority=100, match=match_udp, actions=[], hard_timeout=20) 
            
            self.logger.info(f"已在交换机 {dp.id} 成功下发双重流表！(TCP/UDP 洪水均已屏蔽 20 秒)")
