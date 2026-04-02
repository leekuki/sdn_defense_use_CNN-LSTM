

# Lightweight SDN DDoS Mitigation Framework 

This repository contains the source code for a lightweight, proactive DDoS mitigation framework in Software-Defined Networking (SDN) environments, as described in our research paper. The system leverages a domain-aligned **CNN-LSTM** model to achieve high-precision detection and rapid hardware-offloading mitigation.

## 🌟 Key Features
* **Real-time Detection**: Entropy-based feature extraction for rapid attack identification.
* **Hybrid Model**: Combines CNN (spatial features) and LSTM (temporal features) for superior accuracy.
* **Low Overhead**: Lightweight design ensuring controller CPU utilization stays below 1.0% during mitigation.
* **V-Shaped Recovery**: Proven ability to restore bandwidth within 5 seconds of an attack.

---

## 📂 Project Structure

* `ryu_ai_defender.py`: The core SDN controller application (based on Ryu).
* `final_ryu_model.pth`: Pre-trained CNN-LSTM model weights.
* `monitor_ryu_overhead.py`: Script to monitor controller CPU and memory usage.
* `all_traffic_features.csv`: Sample spatiotemporal traffic features.
* `plot_v_curve.py` / `zhexiantyu.py`: Visualization scripts for bandwidth and recovery analysis.
* `iperf_log_deep_v.txt`: Raw log data from red-blue confrontation experiments.

---

## 🚀 Getting Started

### 1. Prerequisites
* **Operating System**: Ubuntu 20.04+
* **SDN Controller**: Ryu Manager
* **Network Emulator**: Mininet
* **Environment**: Python 3.8+ with the following libraries:
  ```bash
  pip install torch scapy numpy pandas matplotlib ryu
  ```

### 2. Deployment

#### Step A: Start the Mininet Topology
Run your custom topology (ensure your switches point to the Remote Controller):
```bash
sudo mn --controller=remote,ip=127.0.0.1 --topo=single,3
```

#### Step B: Launch the AI Defender
Start the Ryu controller with our proactive defense script:
```bash
ryu-manager ryu_ai_defender.py
```
*The controller will automatically load `final_ryu_model.pth` and begin monitoring flow-table entropy.*

#### Step C: Simulate DDoS Attack
From the Mininet CLI, use `h1` to attack `h2`:
```bash
h1 hping3 --flood --udp -p 80 h2
```

---

## 📊 Performance & Visualization

To reproduce the **V-shaped bandwidth recovery curve** shown in the paper, run the plotting script after an attack simulation:

```bash
python3 plot_v_curve.py
```

This will process the `iperf_log_deep_v.txt` data and generate the mitigation performance graph (`mitigation_v_curve.png`), demonstrating the 5-second "Hard Drop" rule deployment.


这份 README 配合你的代码，绝对能给审稿人留下“工作扎实、可复现性高”的极佳印象！准备好提交了吗？
