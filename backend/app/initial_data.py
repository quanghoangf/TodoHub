import logging

from app.database.init_db import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Creating initial data")
    init_db()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
