from logging import getLogger
import os
from json import load, dump
from enum import Enum


USER_CONFIG_FILE = "config/user_config.json"
APP_CONFIG_FILE = "config/app_config.json"

logger = getLogger(__name__)


class Translator(Enum):
    ARDRAY = ("ardray", "АРДРЕЙ-ГПТ 2000.1")
    YANDEX = ("yandex", "Яндекс Переводчик")
    GOOGLE = ("google", "Google Translate")
    DEEPL = ("deepl", "DeepL Translate")
    BING = ("bing", "Bing (Microsoft) Translator")
    HUGGING_FACE_1 = ("hugging-face-1", "Hugging Face 1")
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
        return cls.YANDEX


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
    def get_by_code(cls, code):
        for language in cls:
            if language.code == code:
                return language
        return cls.RU


class ConfigurationManager:
    def __init__(self):
        self.__app_name = None
        self.__app_desc = None

        self.__selected_language = Language.RU
        self.__selected_translator = Translator.YANDEX

        self.__load_config()

    def __load_application_config(self):
        if os.path.exists(APP_CONFIG_FILE):
            with open(APP_CONFIG_FILE, "r", encoding="utf-8") as file:
                config = load(file)
                self.__app_name = config.get("app_name", "AI Translate HUB")
                self.__app_desc = config.get("app_desc", "AI Translate HUB – онлайн переводчик")
                self.__app_ver = config.get("app_ver", "1.0.0")
                self.__app_site = config.get("app_site", "https://ai-translate-hub.ru")
            logger.info('Application settings loaded')

    def __load_user_config(self):
        if os.path.exists(USER_CONFIG_FILE):
            with open(USER_CONFIG_FILE, "r", encoding="utf-8") as file:
                config = load(file)
                lang_code = config.get("selected_language", "ru")
                translator_code = config.get("selected_translator", "yandex")

                self.__selected_language = Language.get_by_code(lang_code)
                self.__selected_translator = Translator.get_code(translator_code)

            logger.info('User settings loaded')
        else:
            logger.info('Default user settings loaded')
            self.__save_config()

    def __load_config(self):
        self.__load_application_config()
        self.__load_user_config()

    def __save_config(self):
        config = {
            "selected_language": self.__selected_language.code,
            "selected_translator": self.__selected_translator.code
        }

        os.makedirs(os.path.dirname(USER_CONFIG_FILE), exist_ok=True)
        with open(USER_CONFIG_FILE, "w", encoding="utf-8") as file:
            dump(config, file, ensure_ascii=False, indent=4)

    def get_app_name(self):
        return self.__app_name

    def get_app_description(self):
        return self.__app_desc

    def get_app_site(self):
        return self.__app_site

    def get_app_version(self):
        return self.__app_ver

    def get_language(self):
        return self.__selected_language

    def get_translator(self) -> Translator:
        return self.__selected_translator

    def set_language(self, language: Language):
        self.__selected_language = language
        self.__save_config()

    def set_translator(self, translator: Translator):
        self.__selected_translator = translator
        self.__save_config()

    @staticmethod
    def get_all_languages():
        return list(Language)

    @staticmethod
    def get_all_translators():
        return list(Translator)
