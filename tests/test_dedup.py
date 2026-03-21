"""AI Photo Dedup 单元测试"""
import pytest
from pathlib import Path
from core.phash import PerceptualHasher
from core.clip_features import CLIPFeatureExtractor
from core.dedup_engine import DedupEngine


class TestPerceptualHasher:
    """感知哈希测试"""

    def test_hash_similarity(self):
        """测试哈希相似度计算"""
        phasher = PerceptualHasher()
        # 相同图片相似度应为 1.0
        sim = phasher.similarity('ffffffffffffffff', 'ffffffffffffffff')
        assert sim == 1.0

    def test_hash_difference(self):
        """测试哈希差异计算"""
        phasher = PerceptualHasher()
        sim = phasher.similarity('ffffffffffffffff', '0000000000000000')
        assert 0.0 <= sim < 0.5


class TestCLIPFeatureExtractor:
    """CLIP 特征提取测试"""

    def test_initialization(self):
        """测试初始化"""
        extractor = CLIPFeatureExtractor()
        assert extractor.device in ['cuda', 'cpu']
        assert extractor.batch_size == 32


class TestDedupEngine:
    """去重引擎测试"""

    def test_engine_initialization(self):
        """测试引擎初始化"""
        engine = DedupEngine()
        assert engine.hash_threshold > 0
        assert engine.clip_threshold > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
