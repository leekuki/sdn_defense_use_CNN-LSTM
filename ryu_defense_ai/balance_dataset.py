import pandas as pd
import numpy as np

print("📂 [1/4] 正在加载提取好的时序特征 CSV...")
# 这里必须使用包含你三维特征的专属 CSV
df = pd.read_csv('all_traffic_features.csv')

# 统一二进制标签
df['Binary_Label'] = df['Label'].apply(lambda x: 0 if 'BENIGN' in str(x).upper() or 'NORMAL' in str(x).upper() else 1)
features = df[['Src_IP_Entropy', 'Dst_Port_Entropy', 'Packet_Rate']].values
labels = df['Binary_Label'].values

print(f"   -> 原始离散报文总数: {len(df)} 条")

# ==========================================

# ==========================================
def create_pure_sequences(data, labels, window_size=10):
    X, y = [], []
    # 使用步长等于窗口大小（不重叠），确保样本独立性
    for i in range(0, len(data) - window_size, window_size): 
        window_labels = labels[i:i+window_size]
        # 仅保留纯净窗口（窗口内全为正常，或全为攻击，摒弃混合噪声）
        if len(set(window_labels)) == 1: 
            X.append(data[i:i+window_size])
            y.append(labels[i+window_size-1]) 
    return np.array(X), np.array(y)

print(" [2/4] 正在进行时序滑动窗口切分 (SEQ_LENGTH = 10)...")
X_seq, y_seq = create_pure_sequences(features, labels)

# ==========================================
# 在张量级别进行 1:1 欠采样
# ==========================================
idx_normal = np.where(y_seq == 0)[0]
idx_attack = np.where(y_seq == 1)[0]

print(f"📊 [3/4] 切分后序列分布 - 正常窗口: {len(idx_normal)} 个, 攻击窗口: {len(idx_attack)} 个")

# 找到少数类的数量 (应对 1000 vs 60000 的极度不平衡)
minority_count = min(len(idx_normal), len(idx_attack))

# 设置随机种子以保证 SCI 实验的绝对可复现性 (Reproducibility)
np.random.seed(42)

# 随机抽取与少数类同等数量的样本
idx_normal_downsampled = np.random.choice(idx_normal, minority_count, replace=False)
idx_attack_downsampled = np.random.choice(idx_attack, minority_count, replace=False)

# 合并索引并全局打乱
balanced_indices = np.concatenate([idx_normal_downsampled, idx_attack_downsampled])
np.random.shuffle(balanced_indices)

X_balanced = X_seq[balanced_indices]
y_balanced = y_seq[balanced_indices]

print(f"✅ [4/4] 1:1 分层欠采样完成！")
print(f"   -> 最终平衡数据集大小: {len(y_balanced)} 个窗口 (正常 {minority_count} vs 攻击 {minority_count})")

# ==========================================
# 导出平衡后的张量数据
# ==========================================
np.savez('balanced_sequences.npz', X=X_balanced, y=y_balanced)
print("💾 已将完美平衡的时序张量保存为 'balanced_sequences.npz'！")
