import logging


def set_up_logging(log_location):
    """Set up logging to file."""
    logger = logging.getLogger("get_posts")
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(log_location, mode="w")
    fh.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(message)s"
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger
