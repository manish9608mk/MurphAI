import logging
import sys


# MurphAI Application Logging

LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | "
    "%(name)s | %(message)s"
)

LOG_LEVEL = logging.INFO


def configure_logging() -> None:
    """
    Configure application logging for MurphAI.

    Logs are written to stdout so Docker and
    cloud logging systems can collect them.
    """

    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        stream=sys.stdout,
        force=True,
    )