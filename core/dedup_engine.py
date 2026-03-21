"""去重引擎 — 整合感知哈希和 CLIP 特征的去重核心"""
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import json

from .phash import PerceptualHasher
from .clip_features import CLIPFeatureExtractor
from config import settings

logger = logging.getLogger(__name__)


@dataclass
class DuplicateGroup:
    """重复图片组"""
    files: List[Path]
    similarity_scores: List[float]
    hash_score: float = 0.0
    clip_score: float = 0.0

    def get_best_quality_file(self) -> Path:
        """返回质量最高的文件（文件大小最大）"""
        return max(self.files, key=lambda p: p.stat().st_size)


class DedupEngine:
    """AI 智能去重引擎"""

    def __init__(
        self,
        hash_threshold: float = settings.HASH_THRESHOLD,
        clip_threshold: float = settings.CLIP_THRESHOLD,
        batch_size: int = settings.BATCH_SIZE
    ):
        self.hash_threshold = hash_threshold
        self.clip_threshold = clip_threshold
        self.batch_size = batch_size
        self.phasher = PerceptualHasher(threshold=hash_threshold)
        self.clip_extractor = CLIPFeatureExtractor(batch_size=batch_size)

    def scan_directory(
        self,
        directory: Path,
        extensions: Optional[Set[str]] = None
    ) -> List[Path]:
        """扫描目录获取所有图片文件"""
        extensions = extensions or set(settings.SCAN_EXTENSIONS)
        files = []
        for ext in extensions:
            files.extend(directory.rglob(f'*{ext}'))
            files.extend(directory.rglob(f'*{ext.upper()}'))
        return sorted(set(files))

    def analyze(
        self,
        image_paths: List[Path],
        use_clip: bool = True
    ) -> List[DuplicateGroup]:
        """分析图片并返回重复组"""
        logger.info(f"开始分析 {len(image_paths)} 张图片...")

        # 第1阶段：感知哈希快速筛选
        logger.info("阶段1: 计算感知哈希...")
        hash_results = self.phasher.batch_compute(image_paths)
        hash_duplicates = self.phasher.find_duplicates(hash_results)
        logger.info(f"哈希筛选发现 {len(hash_duplicates)} 对疑似重复")

        # 第2阶段：CLIP 深度验证（可选）
        if use_clip and hash_duplicates:
            logger.info("阶段2: CLIP 深度验证...")
            # 提取所有疑似重复的图片
            clip_candidates = set()
            for p1, p2, _ in hash_duplicates:
                clip_candidates.add(p1)
                clip_candidates.add(p2)

            clip_features = self.clip_extractor.batch_extract(
                list(clip_candidates)
            )

            # 重新计算相似度
            verified_duplicates = []
            for p1, p2, hash_score in hash_duplicates:
                if p1 in clip_features and p2 in clip_features:
                    clip_score = self.clip_extractor.cosine_similarity(
                        clip_features[p1], clip_features[p2]
                    )
                    combined = (hash_score + clip_score) / 2
                    if clip_score >= self.clip_threshold or combined >= 0.92:
                        verified_duplicates.append((p1, p2, combined, clip_score))
                else:
                    verified_duplicates.append((p1, p2, hash_score, 0.0))
        else:
            verified_duplicates = [
                (p1, p2, score, 0.0) for p1, p2, score in hash_duplicates
            ]

        # 第3阶段：聚类分组
        logger.info("阶段3: 聚类分组...")
        groups = self._cluster_duplicates(verified_duplicates)
        logger.info(f"发现 {len(groups)} 个重复组")

        return groups

    def _cluster_duplicates(
        self,
        duplicates: List[Tuple[Path, Path, float, float]]
    ) -> List[DuplicateGroup]:
        """将重复对聚类为组"""
        # 构建图
        graph = defaultdict(set)
        scores = {}
        for p1, p2, combined, clip in duplicates:
            graph[p1].add(p2)
            graph[p2].add(p1)
            scores[(p1, p2)] = (combined, clip)

        # 深度优先搜索找连通分量
        visited = set()
        groups = []

        def dfs(node, component):
            visited.add(node)
            component.append(node)
            for neighbor in graph[node]:
                if neighbor not in visited:
                    dfs(neighbor, component)

        for node in graph:
            if node not in visited:
                component = []
                dfs(node, component)

                # 计算组内相似度
                group_scores = []
                for i, p1 in enumerate(component):
                    for p2 in component[i+1:]:
                        if (p1, p2) in scores:
                            group_scores.append(scores[(p1, p2)])
                        elif (p2, p1) in scores:
                            group_scores.append(scores[(p2, p1)])

                if group_scores:
                    avg_combined = sum(s[0] for s in group_scores) / len(group_scores)
                    avg_clip = sum(s[1] for s in group_scores) / len(group_scores)
                else:
                    avg_combined = avg_clip = 0.0

                groups.append(DuplicateGroup(
                    files=component,
                    similarity_scores=group_scores,
                    hash_score=avg_combined,
                    clip_score=avg_clip
                ))

        return groups

    def generate_report_data(
        self,
        groups: List[DuplicateGroup],
        total_files: int
    ) -> Dict:
        """生成报告数据"""
        total_duplicates = sum(len(g.files) - 1 for g in groups)
        space_to_save = sum(
            sum(p.stat().st_size for p in g.files) - g.get_best_quality_file().stat().st_size
            for g in groups
        )

        return {
            'total_files': total_files,
            'duplicate_groups': len(groups),
            'total_duplicates': total_duplicates,
            'space_to_save_mb': space_to_save / (1024 * 1024),
            'groups': [
                {
                    'files': [str(f) for f in g.files],
                    'best_file': str(g.get_best_quality_file()),
                    'sizes': [f.stat().st_size for f in g.files],
                    'hash_score': g.hash_score,
                    'clip_score': g.clip_score
                }
                for g in groups
            ]
        }
