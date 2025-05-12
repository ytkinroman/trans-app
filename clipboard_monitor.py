from logging import getLogger
import keyboard
import pyperclip
from threading import Thread, Lock
import time
from config_manager import ConfigurationManager


logger = getLogger(__name__)


class KeyListener(Thread):
    def __init__(self, config_manager: ConfigurationManager):
        super().__init__(daemon=True)
        self.__config_manager = config_manager
        self.__key_combination = self.__config_manager.get_hotkey()  # например "alt+shift+t"
        self.__running = True
        logger.info(f"Инициализация KeyListener с комбинацией {self.__key_combination}")

    def run(self):
        """Метод, который запускается при старте потока"""
        logger.info("Запуск отслеживания комбинации клавиш")

        def on_hotkey_press():
            """Обработчик нажатия комбинации клавиш"""
            logger.info(f"Обнаружено нажатие комбинации {self.__key_combination}")
            try:
                # Здесь можно добавить логику обработки
                print("Hotkey pressed!")
                clipboard_text = pyperclip.paste()
                trimmed_text = clipboard_text[:200] if clipboard_text else ""

                print(trimmed_text)
                # pyperclip.copy("Текст из горячей клавиши")
            except Exception as e:
                logger.error(f"Ошибка при обработке комбинации клавиш: {e}")

        # Регистрируем горячую клавишу
        keyboard.add_hotkey(self.__key_combination, on_hotkey_press)

        # Бесконечный цикл, пока поток работает
        while self.__running:
            keyboard.wait()  # Блокируем поток, пока не придет команда на остановку

    def stop(self):
        """Метод для остановки потока"""
        logger.info("Остановка отслеживания комбинации клавиш")
        self.__running = False
        keyboard.unhook_all()
