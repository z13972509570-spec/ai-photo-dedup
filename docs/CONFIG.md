# 配置说明

## 配置文件

位置: `config/settings.py`

## 配置项

### 哈希阈值

```python
HASH_THRESHOLD: float = 0.90
```

| 值 | 效果 |
|-----|------|
| 0.85 | 宽松，可能误判 |
| 0.90 | 平衡（推荐）|
| 0.95 | 严格，可能漏判 |

### CLIP 阈值

```python
CLIP_THRESHOLD: float = 0.95
```

### 批处理大小

```python
BATCH_SIZE: int = 32
```

根据 GPU 内存调整。

### 图片格式

```python
SCAN_EXTENSIONS: list = [
    '.jpg', '.jpeg', '.png', '.heic', 
    '.webp', '.bmp', '.tiff'
]
```

### 备份目录

```python
BACKUP_DIR: Path = Path('./backup')
```

### CLIP 模型

```python
CLIP_MODEL: str = 'ViT-B-32'
```

可选: ViT-B-32, ViT-L-14

### 日志级别

```python
LOG_LEVEL: str = 'INFO'
```

可选: DEBUG, INFO, WARNING, ERROR
