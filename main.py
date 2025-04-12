from json import load
import logging.config
from logging import getLogger
from tray_app import TrayApp
from web_socket_client import WebSocketClient


def main() -> None:
    with open("config/logging_config.conf", "r", encoding="utf-8") as file:
        logging_config = load(file)

    logging.config.dictConfig(logging_config)
    logger = getLogger()
    logger.info("Logger успешно загружен и настроен.")

    # client = WebSocketClient()

    # tray_icon = TrayApp(client)
    tray_icon = TrayApp()
    tray_icon.run()


if __name__ == "__main__":
    main()
