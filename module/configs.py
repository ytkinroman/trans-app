import os
from json import load, dump
from logging import getLogger
from typing import Dict, Any
from module.translators import Translator, Language
from module.utils import get_config_dir


CONFIG_DIR = get_config_dir()
APP_CONFIG_FILE = "app_config.json"
USER_CONFIG_FILE = "user_config.json"
SERVER_CONFIG_FILE = "server_config.json"

DEFAULT_APP_CONFIG = {
    "app_name": "AI Translate HUB",
    "app_description": "AI Translate HUB – онлайн переводчик",
    "app_version": "1.2",  # TODO: ЗАМЕНИТЬ НА РЕЛИЗЕ !
    "app_site": "https://ai-translate-hub.ru/"  # TODO: ЗАМЕНИТЬ НА ДОКУМЕНТАЦИЮ !
}

DEFAULT_USER_CONFIG = {
    "selected_language": "ru",
    "selected_translator": "yandex",
    "translate_keyboard": "alt+shift+t"  # TODO: ЗАМЕНА ГОРЯЧИХ КЛАВИШ ТОЛЬКО В CFG !
}

DEFAULT_SERVER_CONFIG = {
    "server_host": "0.0.0.0",  # TODO: СЮДА НАДО АДРЕС СЕРВЕРА !
    "server_port": "8080"
}


logger = getLogger(__name__)


class BaseConfig:
    def __init__(self, config_path: str, default_config: Dict[str, Any]):
        self.__config_path = config_path
        self.__default_config = default_config
        self.__config = None

    def load(self) -> None:
        # os.makedirs(os.path.dirname(self.__config_path), exist_ok=True)  # Проверя

        if os.path.isfile(self.__config_path):
            with open(self.__config_path, "r", encoding="utf-8") as f:
                self.__config = load(f)
            logger.info(f"Config loaded from {self.__config_path}")
        else:
            self.__config = self.__default_config
            with open(self.__config_path, "w", encoding="utf-8") as f:
                dump(self.__default_config, f, indent=4, ensure_ascii=False)
            logger.info(f"Created default config at {self.__config_path}")

    def save(self) -> None:
        with open(self.__config_path, "w", encoding="utf-8") as f:
            dump(self.__config, f, indent=4, ensure_ascii=False)
        logger.info(f"Config saved to {self.__config_path}")

    @property
    def config(self) -> Dict[str, Any]:
        return self.__config


class AppConfig(BaseConfig):
    def __init__(self):
        super().__init__(os.path.join(get_config_dir(), "app_config.json"), DEFAULT_APP_CONFIG)

    @property
    def name(self) -> str:
        return self.config["app_name"]

    @property
    def version(self) -> str:
        return self.config["app_version"]

    @property
    def description(self) -> str:
        return self.config["app_description"]

    @property
    def site(self) -> str:
        return self.config["app_site"]


class ServerConfig(BaseConfig):
    def __init__(self):
        super().__init__(os.path.join(get_config_dir(), "server_config.json"), DEFAULT_SERVER_CONFIG)

    @property
    def server_address(self) -> str:
        return f"{self.config['server_host']}:{self.config['server_port']}"

    @property
    def websocket_url(self) -> str:
        return f"ws://{self.server_address}/ws"

    @property
    def api_url(self) -> str:
        # return f"http://{self.server_address}/translate"  # TODO: ВЫКАТИТЬ ОБНОВУ return f"https://{self.server_address}/api/v1/translate"
        return f"http://{self.server_address}/api/v1/"  # TODO: ВЫКАТИТЬ ОБНОВУ return f"https://{self.server_address}/api/v1/translate"


class UserConfig(BaseConfig):
    def __init__(self):
        super().__init__(os.path.join(get_config_dir(), "user_config.json"), DEFAULT_USER_CONFIG)

    @property
    def translate_keyboard(self) -> str:
        return self.config["translate_keyboard"]

    @property
    def selected_translator(self) -> str:
        return self.config["selected_translator"]

    @property
    def selected_language(self) -> str:
        return self.config["selected_language"]

    def set_language(self, language: Language) -> None:
        self.config["selected_language"] = language.code
        self.save()

    def set_translator(self, translator: Translator) -> None:
        self.config["selected_translator"] = translator.code
        self.save()
