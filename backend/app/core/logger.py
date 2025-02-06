import logging
import sys
from typing import Optional

import loguru
from loguru import logger
from pydantic import BaseModel

LOGURU_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)


class LogConfig(BaseModel):
    """Logging configuration to be set for the server"""

    LEVEL: str = "INFO"
    FORMAT: str = "%(levelprefix)s | %(asctime)s | %(message)s"


class InterceptHandler(logging.Handler):
    """
    Default handler that intercepts logging messages and redirects them to loguru.
    """

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging(config: Optional[LogConfig] = None) -> None:
    """
    Configure logging with custom colors and formatting.
    """
    logger.remove()

    config = config or LogConfig()

    logger.add(
        sys.stdout,
        level=config.LEVEL,
        format=LOGURU_FORMAT,
        colorize=True,
        backtrace=True,
        catch=True,
    )

    logger.add(
        "logs/app.log",
        rotation="10 MB",
        retention="10 days",
        level=config.LEVEL,
        format=LOGURU_FORMAT,
        backtrace=True,
        catch=True,
    )

    # Intercept standard logging
    logging.basicConfig(
        handlers=[InterceptHandler()], level=logging.getLevelName(config.LEVEL)
    )

    # Replace standard logging loggers for popular libraries
    for name in logging.root.manager.loggerDict:
        if name not in ["root", "uvicorn"]:
            logging.getLogger(name).handlers = [InterceptHandler()]
            logging.getLogger(name).propagate = False

    # Set specific logger handlers for specific libraries
    # Uvicorn loggers
    logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]
    logging.getLogger("uvicorn.error").handlers = [InterceptHandler()]


logger = loguru.logger
