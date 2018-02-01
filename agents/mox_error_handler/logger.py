import logging


def start_logging(
    name,
    logfile="debug.log",
    loglevel=10
):

    if not name:
        return False

    # Set logger name
    logger = logging.getLogger(name)

    # Set logger handler
    handler = logging.FileHandler(logfile)
    logger.addHandler(handler)

    # Set logger formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)

    # Set loglevel
    logger.setLevel(loglevel)
    handler.setLevel(loglevel)

    # Return logger
    return logger

# TESTING PURPOSES
if __name__ == "__main__":
    # Create logger
    log = start_logging("TestLogger")

    # Log something
    log.debug("Deeply hidden logs")
    log.info("For your information only")
    log.warning("Consider yourself warned")
    log.error("Something broke")
