from pystray import Icon, Menu, MenuItem as Item
from PIL import Image, ImageDraw
from logging import getLogger
from config_manager import ConfigurationManager
from webbrowser import open as open_url
# from web_socket_client import WebSocketClient


logger = getLogger(__name__)


class TrayApp:
    def __init__(self, config_manager: ConfigurationManager, websocket_client=None) -> None:
        logger.info("Инициализация TrayApp началась...")

        self.__config_manager = config_manager
        self.__websocket_client = websocket_client

        self.__icon = Icon(
            self.__config_manager.get_app_name(),
            self.__create_tray_icon(),
            self.__config_manager.get_app_description(),
            self.__create_menu()
        )
        logger.info("Инициализация TrayApp завершена")

        self.__run()

    @staticmethod
    def __create_tray_icon() -> Image:
        width, height = 64, 64
        image = Image.new("RGB", (width, height), color="blue")
        dc = ImageDraw.Draw(image)
        dc.ellipse((10, 10, width - 10, height - 10), fill="yellow")
        logger.info("Инициализация иконки для TrayApp завершена")
        return image

    def __create_menu(self) -> Menu:
        logger.info("Инициализация меню для TrayApp завершена")

        translator_groups = (
            self.__config_manager.get_all_translators()[:1],
            self.__config_manager.get_all_translators()[1:5],
            self.__config_manager.get_all_translators()[5:]
        )

        language_groups = (
            self.__config_manager.get_all_languages()[:2],
            self.__config_manager.get_all_languages()[2:],
        )

        translator_menu = []
        for i, group in enumerate(translator_groups):
            if i > 0:
                translator_menu.append(Menu.SEPARATOR)

            for translator in group:
                translator_menu.append(
                    Item(
                        translator.display_name,
                        self.__on_translator_select(translator),
                        checked=lambda item, t=translator: self.__config_manager.get_translator() == t
                    )
                )

        language_menu = []
        for i, group in enumerate(language_groups):
            if i > 0:
                language_menu.append(Menu.SEPARATOR)

            for language in group:
                language_menu.append(
                    Item(
                        language.display_name,
                        self.__on_language_select(language),
                        checked=lambda item, lang=language: self.__config_manager.get_language() == lang
                    )
                )

        return Menu(
            Item(
                "Переводчик",
                Menu(*translator_menu)
            ),
            Item(
                "Язык перевода",
                Menu(*language_menu)
            ),
            Menu.SEPARATOR,
            Item("Информация", self.__on_info),
            Item("Выход", self.__on_exit),
        )

    def __on_language_select(self, language):
        def handler():
            self.__config_manager.set_language(language)
            self.__icon.update_menu()
            logger.info(f"Язык перевода изменён на {language.display_name}")

        return handler

    def __on_translator_select(self, translator):
        def handler():
            self.__config_manager.set_translator(translator)
            self.__icon.update_menu()
            logger.info(f"Переводчик изменён на {translator.display_name}")

        return handler

    def __on_exit(self):
        logger.info('Нажата кнопка "Выход"')
        logger.info("Завершение работы TrayApp...")
        # self.__websocket_client.close_connection()
        self.__icon.stop()

    def __on_info(self):
        logger.info('Нажата кнопка "Информация"')
        open_url(self.__config_manager.get_app_site())

    def __run(self):
        logger.info("Запуск TrayApp...")
        self.__icon.run()
