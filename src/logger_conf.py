from loguru import logger


logger.add(
    "logs/service.log",
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    rotation="30 MB",
    diagnose=True,
    backtrace=False,
)
