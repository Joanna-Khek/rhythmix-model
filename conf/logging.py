from loguru import logger
import sys
import logging
from conf import settings

# Clean up existing Loguru handlers to avoid duplicates
logger.remove()

# Format string for logs
log_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)

# Configure file logger for all logs
log_file_path = settings.ROOT / "logs" / "runtime.log"
log_file_path.parent.mkdir(
    parents=True, exist_ok=True
)  # Create logs/ directory if needed

logger.add(
    log_file_path,
    rotation="1 MB",
    retention="7 days",
    level="INFO",
    format=log_format,
    enqueue=True,  # Safe for async environments
)

# Add console logger for all logs
logger.add(sys.stderr, level="INFO", format=log_format)


# Redirect Loguru's internal errors to the same file logger
def loguru_error_handler(record):
    logger.error(f"Loguru internal error: {record}")


# Add error handler to catch Loguru's internal errors
logger.add(log_file_path, level="ERROR", format=log_format)


# Intercept Python's standard logging (used by Uvicorn/FastAPI) and redirect to Loguru
class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find the caller from where the log originated
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        # Log using Loguru
        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


# Configure Uvicorn and FastAPI loggers to use Loguru
def setup_logging():
    # Redirect all standard logging to Loguru
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Update loggers for Uvicorn, FastAPI, and root logger
    for logger_name in ("", "uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"):
        py_logger = logging.getLogger(logger_name)
        py_logger.handlers = [InterceptHandler()]
        py_logger.propagate = False


# Call setup_logging when the module is imported
setup_logging()
