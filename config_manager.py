import os
from json import load, dump
from logging import getLogger
from typing import Dict, Any, List


CONFIG_DIR = "config"

APP_CONFIG_FILE = "app_config.json"
USER_CONFIG_FILE = "user_config.json"
SERVER_CONFIG_FILE = "server_config.json"

DEFAULT_APP_CONFIG = {
    "app_name": "AI Translate HUB",
    "app_description": "AI Translate HUB – онлайн переводчик",
    "app_version": "1.2",
    "app_site": "https://ai-translate-hub.ru/"
}

DEFAULT_USER_CONFIG = {
    "selected_language": "ru",
    "selected_translator": "yandex",
    "translate_keyboard": "alt+shift+t"
}

DEFAULT_SERVER_CONFIG = {
    "server_host": "0.0.0.0",
    "server_port": "8080"
}


translators_data = [
    ("ardray1", "АРДРЕЙ-ГПТ 2000.1"),
    ("ardray2", "ARDRAY 5000"),
    ("yandex", "Яндекс Переводчик"),
    ("google", "Google Translate"),
]

languages_data = [
    ("ru", "Русский"),
    ("en", "Английский"),
    ("de", "Немецкий"),
    ("fr", "Французский"),
]


logger = getLogger(__name__)


class Translator:
    def __init__(self, code: str, name: str):
        self._code = code
        self._name = name

    @property
    def code(self) -> str:
        return self._code

    @property
    def name(self) -> str:
        return self._name


class Language:
    def __init__(self, code: str, name: str):
        self._code = code
        self._name = name

    @property
    def code(self) -> str:
        return self._code

    @property
    def name(self) -> str:
        return self._name


class BaseConfig:
    def __init__(self, config_path: str, default_config: Dict[str, Any]):
        self._config_path = config_path
        self._default_config = default_config
        self._config = None

    def load(self) -> None:
        if os.path.isfile(self._config_path):
            with open(self._config_path, "r", encoding="utf-8") as f:
                self._config = load(f)
            logger.info(f"Config loaded from {self._config_path}")
        else:
            self._config = self._default_config
            with open(self._config_path, "w", encoding="utf-8") as f:
                dump(self._default_config, f, indent=4, ensure_ascii=False)
            logger.info(f"Created default config at {self._config_path}")

    def save(self) -> None:
        with open(self._config_path, "w", encoding="utf-8") as f:
            dump(self._config, f, indent=4, ensure_ascii=False)
        logger.info(f"Config saved to {self._config_path}")

    @property
    def config(self) -> Dict[str, Any]:
        return self._config


class AppConfig(BaseConfig):
    def __init__(self):
        config_path = os.path.join(CONFIG_DIR, APP_CONFIG_FILE)
        super().__init__(config_path, DEFAULT_APP_CONFIG)

    @property
    def name(self) -> str:
        return self._config["app_name"]

    @property
    def version(self) -> str:
        return self._config["app_version"]

    @property
    def description(self) -> str:
        return self._config["app_description"]

    @property
    def site(self) -> str:
        return self._config["app_site"]


class ServerConfig(BaseConfig):
    def __init__(self):
        config_path = os.path.join(CONFIG_DIR, SERVER_CONFIG_FILE)
        super().__init__(config_path, DEFAULT_SERVER_CONFIG)

    @property
    def server_address(self) -> str:
        return f"{self._config['server_host']}:{self._config['server_port']}"

    @property
    def websocket_url(self) -> str:
        return f"ws://{self.server_address}/ws"

    @property
    def translate_api_url(self) -> str:
        return f"https://{self.server_address}/translate"


class UserConfig(BaseConfig):
    def __init__(self):
        config_path = os.path.join(CONFIG_DIR, USER_CONFIG_FILE)
        super().__init__(config_path, DEFAULT_USER_CONFIG)

    @property
    def translate_keyboard(self) -> str:
        return self._config["translate_keyboard"]

    @property
    def selected_translator(self) -> str:
        return self._config["selected_translator"]

    @property
    def selected_language(self) -> str:
        return self._config["selected_language"]

    def set_language(self, language: Language) -> None:
        self._config["selected_language"] = language.code
        self.save()

    def set_translator(self, translator: Translator) -> None:
        self._config["selected_translator"] = translator.code
        self.save()


class ConfigurationManager:
    def __init__(self):
        self.__translators = self.__init_translators()
        self.__languages = self.__init_languages()

        self.app = AppConfig()
        self.server = ServerConfig()
        self.user= UserConfig()

        self.__load_config()

    @staticmethod
    def __init_translators() -> List[Translator]:
        return [Translator(code, name) for code, name in translators_data]

    @staticmethod
    def __init_languages() -> List[Language]:
        return [Language(code, name) for code, name in languages_data]

    def __load_config(self) -> None:
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)

        self.app.load()
        self.server.load()
        self.user.load()

    def get_languages(self) -> List[Language]:
        return self.__languages

    def get_translators(self) -> List[Translator]:
        return self.__translators
