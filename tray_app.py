import sys
from pystray import Icon, Menu, MenuItem as Item
from module.utils import create_app_icon
from logging import getLogger
from config_manager import ConfigurationManager
from webbrowser import open as open_link
from websocket_client import WebSocketClient
from module.utils import show_message
from key_listener import KeyListener


logger = getLogger(__name__)


class TrayApp:
    def __init__(self, config_manager: ConfigurationManager) -> None:
        logger.info("Starting TrayApp initialization")
        self.__config = config_manager

        self.ws_client = WebSocketClient(self.__config.server.websocket_url)
        self.session_id = None

        if self.ws_client.connect():
            self.session_id = self.ws_client.session_id
        else:
            title, msg, msg_type = "Ошибка при websocket подключении", "Не удалось выполнить WebSocket соединение", "error"
            logger.error(msg)
            show_message(title, msg, msg_type)
            sys.exit(1)

        self.__key_listener = KeyListener(self.__config, self.ws_client)
        self.__key_listener.start()

        self.__icon = Icon(
            self.__config.app.name,
            create_app_icon(),
            self.__config.app.description,
            self.__create_menu()
        )

        logger.info("TrayApp initialized successfully")

        self.__run()

    def __create_menu(self) -> Menu:
        translators = self.__config.translators
        translator_menu = []

        for translator in translators:
            t_item = Item(
                translator.name,
                self.__on_translator_select(translator),
                checked=lambda item, t=translator.code: self.__config.user.selected_translator == t
            )
            translator_menu.append(t_item)

        languages = self.__config.languages
        language_menu = []

        for language in languages:
            lang_item = Item(
                language.name,
                self.__on_language_select(language),
                checked=lambda item, lang=language.code: self.__config.user.selected_language == lang
            )
            language_menu.append(lang_item)

        menu = Menu(
            Item(
                "Переводчик",
                Menu(*translator_menu)
            ),
            Item(
                "Переводить на",
                Menu(*language_menu)
            ),
            Menu.SEPARATOR,
            Item("⚡ Обратная связь", self.__on_info),
            Item("Выход", self.__on_exit),
        )

        logger.info("TrayApp menu initialized successfully")
        return menu

    def __on_language_select(self, language):
        def handler():
            logger.info(f'Translation language changed to "{language.name}"')
            self.__config.user.set_language(language)
            self.__icon.update_menu()

        return handler

    def __on_translator_select(self, translator):
        def handler():
            logger.info(f'Translator changed to "{translator.name}"')
            self.__config.user.set_translator(translator)
            self.__icon.update_menu()

        return handler

    def __on_exit(self):
        logger.info('Button "Exit" clicked')

        if self.__key_listener:
            logger.info("Stopping KeyListener...")
            self.__key_listener.stop()

        if self.ws_client:
            logger.info("Closing WebSocket connection...")
            self.ws_client.disconnect()

        logger.info("TrayApp is shutting down...")
        self.__icon.stop()

    def __on_info(self):
        logger.info('Button "Information" clicked')
        open_link(self.__config.app.site)
        logger.info("Information website opened successfully")

    def __run(self):
        logger.info("Successfully started TrayApp")
        self.__icon.run()
