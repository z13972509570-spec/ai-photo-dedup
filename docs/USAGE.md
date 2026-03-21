# 使用指南

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 扫描照片库

```bash
python dedup.py scan ./photos --output dedup_report.html
```

### 预览清理

```bash
python dedup.py clean ./photos --dry-run
```

### 执行清理

```bash
python dedup.py clean ./photos --confirm --backup-dir ./backup
```

## 配置说明

编辑 `config/settings.py`:

```python
# 哈希相似度阈值 (0-1，越高越严格)
HASH_THRESHOLD = 0.90

# CLIP 特征相似度阈值
CLIP_THRESHOLD = 0.95

# 批处理大小
BATCH_SIZE = 32

# 支持的图片格式
SCAN_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.heic', '.webp']

# 删除前备份目录
BACKUP_DIR = Path('./backup')
```

## 算法原理

### 阶段1: 感知哈希 (Perceptual Hash)

将图片降维为固定长度哈希值，相似图片的哈希值也相似。

- **aHash**: 均值哈希，简单快速
- **pHash**: DCT 变换，更准确
- **dHash**: 梯度哈希，适合移动端
- **whash**: 小波变换，抗噪声

### 阶段2: CLIP 深度特征

使用 OpenAI CLIP 模型提取图片语义特征，计算深度语义相似度。

### 相似度计算

```python
# 哈希相似度
hash_sim = 1 - (hash1 - hash2) / max_hash_distance

# CLIP 余弦相似度
clip_sim = dot(feature1, feature2) / (norm(feature1) * norm(feature2))
```

## 最佳实践

### 1. 调整阈值

```python
# 严格模式
engine = DedupEngine(hash_threshold=0.95, clip_threshold=0.98)

# 宽松模式
engine = DedupEngine(hash_threshold=0.80, clip_threshold=0.90)
```

### 2. 跳过 CLIP（加速）

```python
groups = engine.analyze(files, use_clip=False)
```

### 3. 自定义图片格式

```python
engine.scan_directory('./photos', extensions={'.jpg', '.png', '.heic'})
```
