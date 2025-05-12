from logging import getLogger
from json import load, dump
from enum import Enum
import os


logger = getLogger(__name__)

USER_CONFIG_FILE = "config/user_config.json"
APP_CONFIG_FILE = "config/app_config.json"
WS_CONFIG_FILE = "config/websocket_config.json"
# LOGGING_CONFIG_FILE = "config/logging_config.json"


class Translator(Enum):
    ARDRAY1 = ("ardray1", "АРДРЕЙ-ГПТ 2000.1")
    ARDRAY2 = ("ardray2", "ARDRAY 5000")
    YANDEX = ("yandex", "Яндекс Переводчик")
    GOOGLE = ("google", "Google Translate (Бета)")
    DEEPL = ("deepl", "DeepL Translate (Бета)")
    BING = ("bing", "Bing (Microsoft) Translator (Бета)")
    HUGGING_FACE_1 = ("hugging-face-1", "ChatGPT (Бета)")
    HUGGING_FACE_2 = ("hugging-face-2", "Hugging Face 2")
    HUGGING_FACE_3 = ("hugging-face-3", "Hugging Face 3")
    HUGGING_FACE_4 = ("hugging-face-4", "Hugging Face 4")

    def __init__(self, code, display_name):
        self.code = code
        self.display_name = display_name

    @classmethod
    def get_code(cls, code):
        for translator in cls:
            if translator.code == code:
                return translator


class Language(Enum):
    RU = ("ru", "Русский")
    EN = ("en", "Английский")
    DE = ("de", "Немецкий (Бета)")
    FR = ("fr", "Французский (Бета)")
    ES = ("es", "Испанский (Бета)")
    AZ = ("az", "Азербайджанский (Бета)")

    def __init__(self, code, display_name):
        self.code = code
        self.display_name = display_name

    @classmethod
    def get_code(cls, code):
        for language in cls:
            if language.code == code:
                return language


class ConfigurationManager:
    def __init__(self):
        self.__app_name = None
        self.__app_desc = None
        self.__app_site = None
        self.__app_ver = None
        self.__app_copy_to_clipboard = False
        self.__app_translate_keyboard = None

        self.__selected_language = Language.RU
        self.__selected_translator = Translator.ARDRAY1

        self.__websocket_url = None
        self.__websocket_token = ""

        self.__load_config()

    def __load_config(self):
        # self.__load_logger_config()
        self.__load_app_config()
        self.__load_user_config()
        self.__load_ws_config()

    def __load_app_config(self):
        if os.path.exists(APP_CONFIG_FILE):
            with open(APP_CONFIG_FILE, "r", encoding="utf-8") as file:
                app_config = load(file)

                self.__app_name = app_config.get("app_name")
                self.__app_desc = app_config.get("app_description")
                self.__app_site = app_config.get("app_version")
                self.__app_ver = app_config.get("app_site")
                self.__app_copy_to_clipboard = app_config.get("app_copy_to_clipboard")
                self.__app_translate_keyboard = app_config.get("app_translate_keyboard")

            logger.info("Application config loaded")

    def save_app_config(self):
        config = {
            "app_name": self.__app_name,
            "app_description": self.__app_desc,
            "app_version": self.__app_ver,
            "app_site": self.__app_site,
            "app_copy_to_clipboard": self.__app_copy_to_clipboard,
            "app_translate_keyboard": self.__app_translate_keyboard
        }

        with open(APP_CONFIG_FILE, "w", encoding="utf-8") as file:
            dump(config, file, ensure_ascii=False, indent=4)

        logger.info("Application configuration saved successfully")

    def __load_user_config(self):
        if os.path.exists(USER_CONFIG_FILE):
            with open(USER_CONFIG_FILE, "r", encoding="utf-8") as file:
                user_config = load(file)

                lang_code = user_config.get("selected_language")
                self.__selected_language = Language.get_code(lang_code)

                translator_code = user_config.get("selected_translator")
                self.__selected_translator = Translator.get_code(translator_code)

            logger.info("User config loaded")

    def save_user_config(self):
        config = {
            "selected_language": self.__selected_language.code,
            "selected_translator": self.__selected_translator.code
        }

        os.makedirs(os.path.dirname(USER_CONFIG_FILE), exist_ok=True)

        with open(USER_CONFIG_FILE, "w", encoding="utf-8") as file:
            dump(config, file, ensure_ascii=False, indent=4)

        logger.info("User configuration saved successfully")

    def __load_ws_config(self):
        if os.path.exists(WS_CONFIG_FILE):
            with open(WS_CONFIG_FILE, "r", encoding="utf-8") as file:
                ws_config = load(file)

                self.__websocket_url = ws_config.get("websocket_url")

            logger.info("Websocket config loaded")

    def get_app_name(self):
        return self.__app_name

    def get_app_description(self):
        return self.__app_desc

    def get_app_site(self):
        return self.__app_site

    def is_copy_to_clipboard(self) -> bool:
        return self.__app_copy_to_clipboard

    def set_copy_to_clipboard(self, value: bool):
        self.__app_copy_to_clipboard = value
        self.save_app_config()

    @staticmethod
    def get_all_languages():
        return list(Language)

    def get_language(self):
        return self.__selected_language

    def set_language(self, language: Language):
        self.__selected_language = language
        self.save_user_config()

    @staticmethod
    def get_all_translators():
        return list(Translator)

    def get_translator(self) -> Translator:
        return self.__selected_translator

    def set_translator(self, translator: Translator):
        self.__selected_translator = translator
        self.save_user_config()

    def get_ws_url(self) -> str:
        return self.__websocket_url

    def get_hotkey(self) -> dict:
        return self.__app_translate_keyboard
