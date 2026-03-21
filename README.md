# 🤖 AI Photo Dedup — AI 智能清理重复照片

> 基于 **感知哈希 (Perceptual Hash) + 深度学习特征向量** 的重复照片智能检测与清理工具

## ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🔍 **感知哈希** | 使用 aHash/pHash/dHash 多算法检测视觉相似图片 |
| 🧠 **深度学习** | CLIP 特征向量计算，捕捉语义级相似性 |
| 📊 **可视化报告** | 生成 HTML 交互式去重报告 |
| ⚡ **批量处理** | 支持百万级照片库并发处理 |
| 🗑️ **安全删除** | 保留原始质量，智能备份删除文件 |

## 🚀 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 扫描照片目录
python dedup.py scan ./photos --output report.html

# 自动清理（预览模式）
python dedup.py clean ./photos --dry-run

# 执行清理
python dedup.py clean ./photos --confirm
```

## 📁 项目结构

```
ai-photo-dedup/
├── dedup.py              # 主程序入口
├── core/
│   ├── __init__.py
│   ├── phash.py           # 感知哈希算法
│   ├── clip_features.py   # CLIP 深度学习特征
│   └── dedup_engine.py   # 去重引擎
├── utils/
│   ├── __init__.py
│   ├── file_utils.py      # 文件处理工具
│   └── logger.py          # 日志系统
├── reports/
│   └── html_report.py     # HTML 报告生成器
├── tests/
│   └── test_dedup.py      # 单元测试
├── config/
│   └── settings.py         # 配置文件
├── requirements.txt
└── README.md
```

## ⚙️ 配置说明

编辑 `config/settings.py`:

```python
HASH_THRESHOLD = 0.90        # 哈希相似度阈值
CLIP_THRESHOLD = 0.95       # CLIP 相似度阈值
BATCH_SIZE = 32             # 批处理大小
SCAN_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.heic', '.webp']
BACKUP_DIR = './backup'     # 删除前备份目录
```

## 📊 工作原理

```
[照片文件]
    │
    ▼
┌─────────────────┐
│  感知哈希 (aHash)  │  ←── 快速预筛，O(n²) → O(n log n)
└────────┬────────┘
         │ 疑似重复
         ▼
┌─────────────────┐
│  CLIP 特征向量   │  ←── 深度语义相似度计算
└────────┬────────┘
         │ 确认为重复
         ▼
┌─────────────────┐
│  生成 HTML 报告  │  ←── 人工确认 / 自动清理
└─────────────────┘
```

## 📝 License

MIT License © 2026
