import matplotlib.pyplot as plt
import re


file_path = 'result.txt'
times = []
bandwidths = []

# 正则表达式匹配 iperf 输出格式

pattern = re.compile(r"\[\s*\d+\]\s+\d+\.\d+-\s*(\d+\.\d+)\s+sec\s+[\d\.]+\s+[KMG]?Bytes\s+([\d\.]+)\s+([KMG]?bits/sec)")

with open(file_path, 'r') as f:
    for line in f:
        match = pattern.search(line)
        if match:
            # 提取时间 (取区间的结束时间)
            time_end = float(match.group(1))
            
            # 剔除最后一行总计 (通常时间跨度会很大，比如 0.0-40.1)
            if time_end > 40.0 and "0.0-" in line:
                continue
                
            bw_value = float(match.group(2))
            bw_unit = match.group(3)
            
            # 单位统一转换为 Mbps
            if bw_unit == 'Kbits/sec':
                bw_value = bw_value / 1000.0
            elif bw_unit == 'bits/sec':
                bw_value = bw_value / 1000000.0
                
            times.append(time_end)
            bandwidths.append(bw_value)

# ==========================================

# ==========================================

plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 12
plt.rcParams['axes.linewidth'] = 1.2 # 加粗边框

fig, ax = plt.subplots(figsize=(10, 5), dpi=300) # 300 DPI 保

# 绘制核心折线
ax.plot(times, bandwidths, marker='o', linestyle='-', color='#1f77b4', 
        linewidth=2.5, markersize=6, label='Normal Traffic Throughput')

# ==========================================

# ==========================================

ATTACK_START = 15
MITIGATION_TIME = 20

# 标注攻击区间 
ax.axvspan(ATTACK_START, MITIGATION_TIME, color='red', alpha=0.1, label='Attack Window')

# 标注攻击开始线
ax.axvline(x=ATTACK_START, color='red', linestyle='--', linewidth=2)
ax.text(ATTACK_START + 0.5, 6, 'Attack Launched\n(SYN Flood)', color='#b30000', fontsize=11, fontweight='bold')

# 标注防御生效线
ax.axvline(x=MITIGATION_TIME, color='green', linestyle='--', linewidth=2)
ax.text(MITIGATION_TIME + 0.5, 6, 'Mitigation Triggered\n(CNN-LSTM)', color='#006600', fontsize=11, fontweight='bold')

# ==========================================

# ==========================================
ax.set_xlabel('Time (Seconds)', fontweight='bold')
ax.set_ylabel('Throughput (Mbps)', fontweight='bold')
ax.set_title('Dynamic Mitigation of SYN Flood Attack in SDN', fontweight='bold', pad=15)


ax.set_ylim(0, max(bandwidths) + 3)
ax.set_xlim(0, max(times) + 1)

ax.grid(True, linestyle=':', alpha=0.7)
ax.legend(loc='lower right', framealpha=0.9, edgecolor='black')


plt.tight_layout()
plt.savefig('mitigation_v_curve.pdf', format='pdf', bbox_inches='tight')
plt.savefig('mitigation_v_curve.png', format='png', bbox_inches='tight')

print("图表已生成: mitigation_v_curve.png & mitigation_v_curve.pdf")
# plt.show() # 
