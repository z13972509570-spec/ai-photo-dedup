"""CLIP 深度学习特征提取模块"""
import torch
import numpy as np
from PIL import Image
from pathlib import Path
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor
import logging
import os

logger = logging.getLogger(__name__)


class CLIPFeatureExtractor:
    """基于 OpenAI CLIP 的深度学习特征提取器"""

    def __init__(
        self,
        model_name: str = 'ViT-B-32',
        device: Optional[str] = None,
        batch_size: int = 32
    ):
        self.model_name = model_name
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.batch_size = batch_size
        self.model = None
        self.processor = None

    def _lazy_load(self):
        """懒加载 CLIP 模型（首次使用时加载）"""
        if self.model is None:
            try:
                from transformers import CLIPProcessor, CLIPModel
                logger.info(f"正在加载 CLIP 模型: {self.model_name}...")
                self.model = CLIPModel.from_pretrained(
                    f"openai/clip-{self.model_name.lower()}"
                ).to(self.device)
                self.processor = CLIPProcessor.from_pretrained(
                    f"openai/clip-{self.model_name.lower()}"
                )
                self.model.eval()
                logger.info(f"CLIP 模型加载成功，运行设备: {self.device}")
            except ImportError:
                logger.error("请安装 transformers: pip install transformers")
                raise
            except Exception as e:
                logger.warning(f"CLIP 模型加载失败: {e}，将跳过深度特征")
                self.model = None

    def extract_features(self, image_path: Path) -> Optional[np.ndarray]:
        """提取单张图片的 CLIP 特征向量"""
        self._lazy_load()
        if self.model is None:
            return None
        try:
            image = Image.open(image_path).convert('RGB')
            inputs = self.processor(images=image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            with torch.no_grad():
                image_features = self.model.get_image_features(**inputs)
            # L2 归一化
            features = image_features.cpu().numpy().flatten()
            features = features / np.linalg.norm(features)
            return features
        except Exception as e:
            logger.warning(f"CLIP 特征提取失败 {image_path}: {e}")
            return None

    def batch_extract(
        self,
        image_paths: List[Path],
        n_workers: int = 4
    ) -> Dict[Path, np.ndarray]:
        """批量提取图片特征向量"""
        self._lazy_load()
        results = {}
        if self.model is None:
            return results

        # 逐批次处理
        for i in range(0, len(image_paths), self.batch_size):
            batch = image_paths[i:i + self.batch_size]
            images = []
            valid_paths = []
            for p in batch:
                try:
                    img = Image.open(p).convert('RGB')
                    images.append(img)
                    valid_paths.append(p)
                except Exception:
                    pass

            if not images:
                continue

            try:
                inputs = self.processor(
                    images=images,
                    return_tensors="pt",
                    padding=True
                )
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                with torch.no_grad():
                    features = self.model.get_image_features(**inputs)
                features = features.cpu().numpy()
                # L2 归一化
                norms = np.linalg.norm(features, axis=1, keepdims=True)
                features = features / (norms + 1e-8)

                for p, f in zip(valid_paths, features):
                    results[p] = f.flatten()
            except Exception as e:
                logger.warning(f"批次特征提取失败: {e}")

        return results

    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """计算两个向量的余弦相似度"""
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(np.dot(vec1, vec2) / (norm1 * norm2))

    def find_similar(
        self,
        features: Dict[Path, np.ndarray],
        threshold: float = 0.95
    ) -> List[tuple]:
        """找出所有超过阈值的相似图片对"""
        paths = list(features.keys())
        similar_pairs = []
        for i in range(len(paths)):
            for j in range(i + 1, len(paths)):
                sim = self.cosine_similarity(features[paths[i]], features[paths[j]])
                if sim >= threshold:
                    similar_pairs.append((paths[i], paths[j], sim))
        return sorted(similar_pairs, key=lambda x: -x[2])
