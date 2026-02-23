import sys

from loguru import logger

from config import BASE_DIR

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

FORMAT = (
    "[{level}]:    '{message}' at {name}:{function}    ({time:YYYY-MM-DD HH:mm:ss})"
)


def setup_logger():
    logger.remove()

    logger.add(sys.stdout, level="DEBUG", format=FORMAT)

    logger.add(
        LOG_DIR / "app.log",
        level="INFO",
        format=FORMAT,
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        enqueue=True,
        backtrace=True,
        diagnose=False,
    )
