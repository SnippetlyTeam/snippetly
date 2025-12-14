import logging


def setup_logger() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s\t| %(message)s\t| %(asctime)s",
        handlers=[
            logging.StreamHandler(),
        ],
    )


logger = logging.getLogger("snippetly")
