"""感知哈希算法模块 — aHash / pHash / dHash 多算法实现"""
import numpy as np
import imagehash
from PIL import Image
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor
import logging

logger = logging.getLogger(__name__)


class PerceptualHasher:
    """感知哈希器，支持 aHash / pHash / dHash 算法"""

    ALGORITHMS = ['ahash', 'phash', 'dhash', 'whash']

    def __init__(
        self,
        algorithms: Optional[List[str]] = None,
        hash_size: int = 8,
        threshold: float = 0.90
    ):
        self.algorithms = algorithms or ['ahash', 'phash']
        self.hash_size = hash_size
        self.threshold = threshold

    def compute_hash(self, image_path: Path) -> Optional[Dict[str, np.ndarray]]:
        """计算单张图片的多种哈希值"""
        try:
            img = Image.open(image_path).convert('RGB')
            hashes = {}
            for algo in self.algorithms:
                if algo == 'ahash':
                    hashes['ahash'] = imagehash.average_hash(img, self.hash_size)
                elif algo == 'phash':
                    hashes['phash'] = imagehash.phash(img, self.hash_size)
                elif algo == 'dhash':
                    hashes['dhash'] = imagehash.dhash(img, self.hash_size)
                elif algo == 'whash':
                    hashes['whash'] = imagehash.whash(img, self.hash_size)
            return hashes
        except Exception as e:
            logger.warning(f"无法计算哈希 {image_path}: {e}")
            return None

    def similarity(self, hash1: str, hash2: str) -> float:
        """计算两个哈希的相似度 (0-1)"""
        try:
            h1 = imagehash.hex_to_hash(hash1)
            h2 = imagehash.hex_to_hash(hash2)
            return 1.0 - (h1 - h2) / (len(h1.hash.flatten()) * 2)
        except Exception:
            return 0.0

    def batch_compute(
        self,
        image_paths: List[Path],
        n_workers: int = 8
    ) -> Dict[Path, Dict[str, str]]:
        """批量计算图片哈希"""
        results = {}
        with ThreadPoolExecutor(max_workers=n_workers) as executor:
            future_to_path = {
                executor.submit(self.compute_hash, p): p
                for p in image_paths
            }
            for future in future_to_path:
                path = future_to_path[future]
                try:
                    result = future.result()
                    if result:
                        str_hashes = {k: str(v) for k, v in result.items()}
                        results[path] = str_hashes
                except Exception as e:
                    logger.error(f"批量计算哈希失败 {path}: {e}")
        return results

    def find_duplicates(
        self,
        hash_results: Dict[Path, Dict[str, str]]
    ) -> List[Tuple[Path, Path, float]]:
        """找出所有疑似重复的图片对"""
        paths = list(hash_results.keys())
        duplicates = []

        for i in range(len(paths)):
            for j in range(i + 1, len(paths)):
                p1, p2 = paths[i], paths[j]
                h1, h2 = hash_results[p1], hash_results[p2]

                # 综合多种算法的相似度
                scores = []
                for algo in self.algorithms:
                    if algo in h1 and algo in h2:
                        score = self.similarity(h1[algo], h2[algo])
                        scores.append(score)

                if scores:
                    avg_score = sum(scores) / len(scores)
                    if avg_score >= self.threshold:
                        duplicates.append((p1, p2, avg_score))

        return sorted(duplicates, key=lambda x: -x[2])
