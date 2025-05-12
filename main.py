from json import load
import logging.config
from logging import getLogger
from config_manager import ConfigurationManager
from tray_app import TrayApp
import os


def main() -> None:
    log_dir, log_data = "logs", "data.log"
    log_file = os.path.join(log_dir, log_data)

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    if not os.path.exists(log_file):
        with open(log_file, "w", encoding="utf-8") as file:
            file.write("")

    LOGGING_CONFIG_FILE = "config/logging_config.json"

    with open(LOGGING_CONFIG_FILE, "r", encoding="utf-8") as file:
        logging_config = load(file)

    logging.config.dictConfig(logging_config)
    logger = getLogger()
    logger.info("Logger config loaded")

    config_manager = ConfigurationManager()
    app = TrayApp(config_manager)


if __name__ == "__main__":
    main()
