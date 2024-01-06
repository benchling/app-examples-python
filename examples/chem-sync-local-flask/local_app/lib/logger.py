import logging
import os

# Enable basic logging for development debugging
logging.basicConfig(format="%(name)s - %(asctime)s - {%(pathname)s:%(lineno)d} - %(message)s",
                    level=logging.WARNING)


# Get a logger for our App, with a level enabled specifically for our logging but not other libraries
def get_logger(name: str = "benchling-app") -> logging.Logger:
    level = os.environ.get("BENCHLING_APP_LOG_LEVEL", "INFO").upper()
    logger = logging.getLogger(name)
    logger.setLevel(level)
    return logger
