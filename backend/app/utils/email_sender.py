import logging
from typing import List

logger = logging.getLogger(__name__)


def send_email(to: List[str], subject: str, body: str) -> None:
    logger.info("Sending email to %s with subject '%s'", to, subject)
    logger.debug("Email body: %s", body)
