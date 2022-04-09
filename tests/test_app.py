import logging
from project.app import log_message


LOGGER = logging.getLogger(__name__)


def test_log_message(caplog):
    with caplog.at_level(logging.DEBUG):
        log_message("message")
    assert "message" in caplog.text
