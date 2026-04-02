import matplotlib.pyplot as plt

# ---------------------------------------------------------
# 1. 风格字体设置
# ---------------------------------------------------------
plt.rcParams['font.family'] = 'serif'

plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif'] 
plt.rcParams['font.size'] = 12
plt.rcParams['axes.unicode_minus'] = False


# ---------------------------------------------------------
time = [16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]
cpu_proposed = [0.0, 0.0, 0.0, 0.0, 0.0, 29.0, 44.9, 47.0, 42.9, 42.9, 40.0, 21.0, 1.0, 0.0, 0.0]
cpu_baseline = [0.0, 0.0, 0.0, 0.0, 0.0, 82.9, 99.8, 100.9, 98.8, 99.8, 99.9, 100.9, 99.9, 99.0, 100.8]

# ---------------------------------------------------------
# 3. 核心绘图逻辑
# ---------------------------------------------------------
# 设置画布大小，DPI=300 符合学术期刊的高清印刷要求
plt.figure(figsize=(8, 5), dpi=300)

# 传统重型基线: 红色, 虚线, X型标记
plt.plot(time, cpu_baseline, color='red', linestyle='--', linewidth=2, 
         marker='x', markersize=6, label='Heavy-IDS Baseline')

# 本文轻量级框架: 蓝色, 实线, 圆形标记
plt.plot(time, cpu_proposed, color='blue', linestyle='-', linewidth=2, 
         marker='o', markersize=6, label='Proposed CNN-LSTM Framework')

# 添加关键事件标注线
plt.axvline(x=21, color='gray', linestyle=':', alpha=0.7)
plt.text(21.2, 70, 'Attack Erupted', fontsize=11, color='gray', fontweight='bold')

plt.axvline(x=27, color='green', linestyle=':', alpha=0.7)
plt.text(27.2, 10, 'Mitigation Triggered', fontsize=11, color='green', fontweight='bold')

# 坐标轴与标签设计
plt.xlabel('Time (s)', fontsize=14, labelpad=10)
plt.ylabel('Controller CPU Utilization (%)', fontsize=14, labelpad=10)

# 图例与网格样式
plt.legend(loc='center right', fontsize=11, frameon=True)
plt.grid(True, linestyle='--', alpha=0.5)
plt.ylim(-5, 120)       # 顶部留白，防止图例和折线粘连
plt.tight_layout()      # 自动收紧边缘留白

# ---------------------------------------------------------

# ---------------------------------------------------------

plt.savefig('controller_cpu_comparison.png', bbox_inches='tight', dpi=600)
# 导出为 PDF 矢量
plt.savefig('controller_cpu_comparison.pdf', bbox_inches='tight')

print("格式图片已生成！")
