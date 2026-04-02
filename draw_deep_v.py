import matplotlib.pyplot as plt
import re

print("🎨 正在解析..")

times = []
bandwidths = []

# 1. 智能解析单位不同的日志，并过滤汇总行
with open('iperf_log_deep_v.txt', 'r') as f:
    for line in f:
        # 抓取时间区间和速度 
        match = re.search(r'(\d+\.\d+)-\s*(\d+\.\d+)\s+sec.*?\s+(\d+\.\d+)\s+([KMG]?bits/sec)', line)
        if match:
            start_t = float(match.group(1))
            end_t = float(match.group(2))
            val = float(match.group(3))
            unit = match.group(4)
            
     
            if end_t - start_t > 2.0:
                continue
            
            # 统一转换成 Mbps
            if unit == 'Kbits/sec':
                val = val / 1024.0
            elif unit == 'bits/sec':
                val = val / 1024.0 / 1024.0
                
            times.append(start_t)
            bandwidths.append(val)

# 2. 绘制
plt.figure(figsize=(11, 5.5))
plt.plot(times, bandwidths, marker='o', color='#2ca02c', linewidth=2, markersize=5, label='TCP Business Throughput')

# 标注区域 1：第一次深V
plt.axvspan(19, 25, color='#d62728', alpha=0.2, label='AI Detection Window')
plt.axvline(x=19, color='#d62728', linestyle='--', linewidth=1.5)
plt.axvline(x=25, color='#2ca02c', linestyle='--', linewidth=1.5)

# 🛠️ 修复文字重叠：把文字在 Y 轴上错开分布
plt.text(19.5, 7.5, 'Attack Launched\n(Drops to 0 Mbps)', color='#d62728', fontweight='bold')
plt.text(25.5, 3.5, 'AI Mitigates\n(Recovers to 10M)', color='#2ca02c', fontweight='bold')

# 标注区域 2：流表老化，二次攻击倒灌
plt.axvspan(44, 60, color='#ff7f0e', alpha=0.2, label='OpenFlow Rule Timeout (Re-attack)')
plt.axvline(x=44, color='#ff7f0e', linestyle='-.', linewidth=1.5)
plt.text(44.5, 7.5, 'Rule Expires (20s)\nAttack Resumes', color='#d95f02', fontweight='bold')

plt.xlabel('Time (Seconds)', fontsize=13, fontweight='bold')
plt.ylabel('Throughput (Mbps)', fontsize=13, fontweight='bold')
plt.title('End-to-End Real-time Bandwidth Recovery and Rule Timeout Mechanics', fontsize=15, fontweight='bold')

plt.ylim(-0.5, 12)
plt.grid(True, linestyle=':', alpha=0.7)
plt.legend(loc='lower left', fontsize=11)
plt.tight_layout()

plt.savefig('deep_v_timeout_curve.pdf', format='pdf', dpi=300)
print("图表保存为 deep_v_timeout_curve.pdf！")
