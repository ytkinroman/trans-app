from json import load
import logging.config
from logging import getLogger
from config_manager import ConfigurationManager
from tray_app import TrayApp


def main() -> None:
    LOGGING_CONFIG_FILE = "config/logging_config.json"

    with open(LOGGING_CONFIG_FILE, "r", encoding="utf-8") as file:
        logging_config = load(file)

    logging.config.dictConfig(logging_config)
    logger = getLogger()
    logger.info("Logger успешно загружен и настроен")

    config_manager = ConfigurationManager()

    # ws
    # key

    tray_app = TrayApp(config_manager)


if __name__ == "__main__":
    main()
