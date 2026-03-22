import logging
logger = logging.getLogger(__name__)


class Scanner:
    """Scanner"""
    
    def __init__(self, path="."):
        self.path = path
    
    def scan(self) -> list:
        logger.info("Anmalizing path: {self.path}")"
        return []
