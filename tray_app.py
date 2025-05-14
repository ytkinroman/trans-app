from pystray import Icon, Menu, MenuItem as Item
from module.utils import create_app_icon
from logging import getLogger
from config_manager import ConfigurationManager
from webbrowser import open as open_link
from key_listener import KeyListener


logger = getLogger(__name__)


class TrayApp:
    def __init__(self, config_manager: ConfigurationManager) -> None:
        logger.info("Starting TrayApp initialization")

        self.__config = config_manager

        self.__key_listener = KeyListener(self.__config)  # TODO: Init KeyListener
        # self.__key_listener.start()

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
            Item("Информация", self.__on_info),
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

        logger.info("KeyListener is shutting down...")
        self.__key_listener.stop()  # TODO: Остановка потока с KeyListener

        logger.info("TrayApp is shutting down...")
        self.__icon.stop()

    def __on_info(self):
        logger.info('Button "Information" clicked')
        open_link(self.__config.app.site)
        logger.info("Information website opened successfully")

    def __run(self):
        logger.info("Started KeyListener...")
        self.__key_listener.run()  # TODO: Запуск потока с KeyListener

        logger.info("Successfully started TrayApp")
        self.__icon.run()
