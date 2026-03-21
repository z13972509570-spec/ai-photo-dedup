# API 文档

## DedupEngine

主去重引擎类。

### 构造函数

```python
DedupEngine(
    hash_threshold: float = 0.90,   # 哈希相似度阈值
    clip_threshold: float = 0.95,    # CLIP 相似度阈值
    batch_size: int = 32             # 批处理大小
)
```

### 方法

#### `scan_directory()`

扫描目录获取图片文件。

```python
def scan_directory(
    self,
    directory: Path,
    extensions: Optional[Set[str]] = None
) -> List[Path]
```

#### `analyze()`

分析图片并返回重复组。

```python
def analyze(
    self,
    image_paths: List[Path],
    use_clip: bool = True
) -> List[DuplicateGroup]
```

#### `generate_report_data()`

生成报告数据。

```python
def generate_report_data(
    self,
    groups: List[DuplicateGroup],
    total_files: int
) -> Dict
```

## PerceptualHasher

感知哈希器。

### 构造函数

```python
PerceptualHasher(
    algorithms: Optional[List[str]] = None,  # 算法列表
    hash_size: int = 8,                     # 哈希大小
    threshold: float = 0.90                 # 相似度阈值
)
```

### 方法

#### `compute_hash()`

计算单张图片哈希。

```python
def compute_hash(self, image_path: Path) -> Optional[Dict[str, np.ndarray]]
```

#### `batch_compute()`

批量计算哈希。

```python
def batch_compute(
    self,
    image_paths: List[Path],
    n_workers: int = 8
) -> Dict[Path, Dict[str, str]]
```

#### `find_duplicates()`

找出疑似重复图片。

```python
def find_duplicates(
    self,
    hash_results: Dict
) -> List[Tuple[Path, Path, float]]
```

## CLIPFeatureExtractor

CLIP 特征提取器。

### 构造函数

```python
CLIPFeatureExtractor(
    model_name: str = 'ViT-B-32',
    device: Optional[str] = None,
    batch_size: int = 32
)
```

### 方法

#### `extract_features()`

提取单张图片特征。

```python
def extract_features(self, image_path: Path) -> Optional[np.ndarray]
```

#### `batch_extract()`

批量提取特征。

```python
def batch_extract(
    self,
    image_paths: List[Path],
    n_workers: int = 4
) -> Dict[Path, np.ndarray]
```

#### `cosine_similarity()`

计算余弦相似度。

```python
def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float
```

## CLI 命令

### scan

扫描目录并生成报告。

```bash
python dedup.py scan ./photos --output report.html
```

### clean

清理重复文件。

```bash
python dedup.py clean ./photos --dry-run
python dedup.py clean ./photos --confirm --backup-dir ./backup
```
