"""AI Photo Dedup 配置模块"""
import os
from pathlib import Path

# 哈希相似度阈值 (0-1，越高越严格)
HASH_THRESHOLD: float = 0.90

# CLIP 特征相似度阈值
CLIP_THRESHOLD: float = 0.95

# 批处理大小（根据 GPU 内存调整）
BATCH_SIZE: int = 32

# 支持的图片格式
SCAN_EXTENSIONS: list = [
    '.jpg', '.jpeg', '.png', '.heic', 
    '.webp', '.bmp', '.tiff'
]

# 删除前备份目录
BACKUP_DIR: Path = Path('./backup')

# CLIP 模型选择
CLIP_MODEL: str = 'ViT-B-32'

# 日志级别
LOG_LEVEL: str = 'INFO'

# 报告输出目录
REPORT_DIR: Path = Path('./reports/output')

# 最大文件大小 (MB)
MAX_FILE_SIZE_MB: int = 50
