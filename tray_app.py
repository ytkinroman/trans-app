from pystray import Icon, Menu, MenuItem as Item
from PIL import Image, ImageDraw
from logging import getLogger
from config.config import APP_NAME, APP_DESC
from web_socket_client import WebSocketClient


logger = getLogger(__name__)


class TrayApp:
    # def __init__(self, websocket_client: WebSocketClient) -> None:
    def __init__(self) -> None:
        logger.info("Инициализация TrayApp началась...")
        # self.__websocket_client = websocket_client
        self.__icon = Icon(APP_NAME, self.__create_tray_icon(), APP_DESC, self.__create_menu())
        logger.info("Инициализация TrayApp завершена.")

    @staticmethod
    def __create_tray_icon() -> Image:
        width, height = 64, 64
        image = Image.new("RGB", (width, height), color="blue")
        dc = ImageDraw.Draw(image)
        dc.ellipse((10, 10, width - 10, height - 10), fill="yellow")
        logger.info("Инициализация иконки для TrayApp завершена.")
        return image

    def __create_menu(self) -> Menu:
        logger.info("Инициализация меню для TrayApp завершена.")
        return Menu(
            Item("Информация", self.__on_info),
            Item("Выход", self.__on_exit),
        )

    def __on_exit(self):
        logger.info("Завершение работы TrayApp...")
        # self.__websocket_client.close_connection()
        self.__icon.stop()

    @staticmethod
    def __on_info():
        logger.info('Нажата кнопка "Информация".')

    def run(self):
        logger.info("Запуск TrayApp...")
        self.__icon.run()
