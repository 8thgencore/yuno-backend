import logging
import sys
from pprint import pformat

from loguru import logger
from loguru._defaults import LOGURU_FORMAT

from app.core.config import settings


class InterceptHandler(logging.Handler):
    """
    Default handler from examples in loguru documentation.

    This handler intercepts all log requests and
    passes them to loguru.

    For more info see:
    https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover
        """
        Propagates logs to loguru.

        :param record: record to log.
        """
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back  # type: ignore
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )


def record_formatter(record: dict) -> str:
    """
    Custom format for loguru loggers.
    Uses pformat for log any data like request/response body during debug.
    Works with logging if loguru handler it.
    Example:
    >>> payload = [{"users":[{"name": "Nick", "age": 87, "is_active": True}, {"name": "Alex", "age": 27, "is_active": True}], "count": 2}]
    >>> logger.bind(payload=).debug("users payload")
    >>> [   {   'count': 2,
    >>>         'users': [   {'age': 87, 'is_active': True, 'name': 'Nick'},
    >>>                      {'age': 27, 'is_active': True, 'name': 'Alex'}]}]
    """

    format_string = LOGURU_FORMAT
    if record["extra"].get("payload") is not None:
        record["extra"]["payload"] = pformat(
            record["extra"]["payload"],
            indent=4,
            compact=True,
            width=88,
        )
        format_string += "\n<level>{extra[payload]}</level>"

    format_string += "{exception}\n"

    return format_string


def configure_logging() -> None:  # pragma: no cover
    """Configures logging."""
    intercept_handler = InterceptHandler()

    logging.basicConfig(handlers=[intercept_handler], level=logging.NOTSET)

    for logger_name in logging.root.manager.loggerDict:
        if logger_name.startswith("uvicorn."):
            logging.getLogger(logger_name).handlers = []

    # change handler for default uvicorn logger
    logging.getLogger("uvicorn").handlers = [intercept_handler]
    logging.getLogger("uvicorn.access").handlers = [intercept_handler]

    # set logs output, level and format
    logger.remove()
    logger.add(
        sys.stdout,
        level=settings.logging.level,
        format=record_formatter,
    )
