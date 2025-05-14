from logging import getLogger
from typing import List
from module.translators import Translator, Language
from module.configs import AppConfig, ServerConfig, UserConfig
import requests
import sys


logger = getLogger(__name__)


class ConfigurationManager:
    def __init__(self):
        self.__translators_data = []
        self.__languages_data = []

        self.app = AppConfig()
        self.server = ServerConfig()
        self.user = UserConfig()

        self.__load_config()

        session = requests.Session()
        response = session.get(self.server.api_url + "get_config")

        if response.status_code == 200:  # TODO: ВЫНЕСТИ В ОТДЕЛЬНЫЙ МОДУЛЬ
            data = response.json()
            self.__translators_data = list(data.get('translators', {}).items())
            self.__languages_data = list(data.get('languages', {}).items())
        else:
            logger.error("Ошибка при загрузке конфигурации с сервера")  # TODO: Если self.__translators и self.__languages пустые, то завершаем работу программы.
            sys.exit()

        self.__translators = self.__init_translators()
        self.__languages = self.__init_languages()

    def __init_translators(self) -> List[Translator]:
        return [Translator(code, name) for code, name in self.__translators_data]

    def __init_languages(self) -> List[Language]:
        return [Language(code, name) for code, name in self.__languages_data]

    def __load_config(self) -> None:
        self.app.load()
        self.server.load()
        self.user.load()

    @property
    def languages(self) -> List[Language]:
        return self.__languages

    @property
    def translators(self) -> List[Translator]:
        return self.__translators
