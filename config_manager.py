import sys
import requests
from logging import getLogger
from typing import List
from module.translators import Translator, Language
from module.configs import AppConfig, ServerConfig, UserConfig
from module.utils import show_error_message


SERVER_REQUEST_TIMEOUT = 2

logger = getLogger(__name__)


class ConfigurationManager:
    def __init__(self):
        self.__translators_data = []
        self.__languages_data = []

        self.app = AppConfig()
        self.server = ServerConfig()
        self.user = UserConfig()

        self.__load_config()

        try:
            session = requests.Session()
            response = session.get(self.server.config_url, timeout=SERVER_REQUEST_TIMEOUT)

            if response.status_code == 200:
                data = response.json()
                self.__translators_data = list(data.get('translators', {}).items())
                self.__languages_data = list(data.get('languages', {}).items())

                if not self.__translators_data or not self.__languages_data:
                    title, msg = "Ошибка при загрузке данных с сервера", "Полученные данные с сервера пустые"

                    logger.error(msg)
                    show_error_message(title, msg)

                    sys.exit(1)
            else:
                title, msg = "Ошибка при загрузке данных с сервера", f'Ошибка при загрузке конфигурации с сервера. Статус: "{response.status_code}"'

                logger.error(msg)
                show_error_message(title, msg)

                sys.exit(1)

        except Exception as e:
            title, msg = "Ошибка при загрузке конфигурации с сервера", f'Ошибка при загрузке конфигурации с сервера: "{e}"'

            logger.error(msg)
            show_error_message(title, msg)

            sys.exit(1)

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
