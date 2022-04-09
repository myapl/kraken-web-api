import logging


def log_message(message: str):
    logging.debug(message)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    log_message("this is a debug message")
