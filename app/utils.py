import logging
from config.config import Config

def setup_logging():
    logging.basicConfig(
        level=Config.LOGGING_LEVEL,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger("bank_app")
    logger.setLevel(Config.LOGGING_LEVEL)
    return logger

logger = setup_logging()