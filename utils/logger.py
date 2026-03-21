"""日志系统"""
import logging
import sys
from rich.console import Console
from rich.logging import RichHandler


def setup_logger(level: str = 'INFO') -> logging.Logger:
    """配置日志系统（使用 rich 美化输出）"""
    console = Console(stderr=True)

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                console=console,
                rich_tracebacks=True,
                show_time=True,
                show_path=False
            )
        ]
    )
    return logging.getLogger('ai-photo-dedup')
