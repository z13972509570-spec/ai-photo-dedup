"""文件处理工具"""
import shutil
import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


def ensure_backup_dir(backup_dir: Path) -> Path:
    """确保备份目录存在"""
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir


def move_to_backup(file_path: Path, backup_dir: Path) -> Optional[Path]:
    """将文件移动到备份目录"""
    try:
        ensure_backup_dir(backup_dir)
        dest = backup_dir / file_path.name
        # 避免文件名冲突
        if dest.exists():
            dest = backup_dir / f"{file_path.stem}_{file_path.stat().st_mtime:.0f}{file_path.suffix}"
        shutil.move(str(file_path), str(dest))
        logger.info(f"已备份: {file_path} -> {dest}")
        return dest
    except Exception as e:
        logger.error(f"备份失败 {file_path}: {e}")
        return None


def safe_delete(file_path: Path, backup_dir: Optional[Path] = None) -> bool:
    """安全删除文件（先备份）"""
    if backup_dir:
        result = move_to_backup(file_path, backup_dir)
        return result is not None
    else:
        try:
            file_path.unlink()
            logger.info(f"已删除: {file_path}")
            return True
        except Exception as e:
            logger.error(f"删除失败 {file_path}: {e}")
            return False


def get_file_size_mb(file_path: Path) -> float:
    """获取文件大小（MB）"""
    return file_path.stat().st_size / (1024 * 1024)


def is_valid_image(file_path: Path, max_size_mb: float = 50) -> bool:
    """检查是否是有效的图片文件"""
    try:
        if not file_path.is_file():
            return False
        size_mb = get_file_size_mb(file_path)
        if size_mb > max_size_mb:
            logger.debug(f"文件过大，跳过: {file_path} ({size_mb:.1f}MB)")
            return False
        from PIL import Image
        with Image.open(file_path) as img:
            img.verify()
        return True
    except Exception:
        return False


def format_size(size_bytes: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"
