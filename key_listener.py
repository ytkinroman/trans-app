import json
from logging import getLogger
import time
import keyboard
import pyperclip
from threading import Thread
from config_manager import ConfigurationManager
import requests
from module.utils import show_message
from websocket_client import WebSocketClient
import sys


logger = getLogger(__name__)


class KeyListener(Thread):
    def __init__(self, config_manager: ConfigurationManager, ws_client: WebSocketClient):
        super().__init__(daemon=True)
        self.__config = config_manager
        self.__key_combination = self.__config.user.translate_keyboard
        self.__running = True
        self.__reconnect_delay = 5
        self.ws_client = ws_client
        self.__session_id = self.ws_client.session_id
        logger.info(f"Инициализация KeyListener с комбинацией {self.__key_combination}")

    def run(self):
        logger.info("Started KeyListener...")
        self.__session_id = self.ws_client.session_id

        def on_hotkey_press():
            logger.info(f"Обнаружено нажатие комбинации {self.__key_combination}")
            if not self.ws_client.is_alive():
                logger.warning("WebSocket не подключен. Попытка переподключения...")
                if not self.ws_client.connect():
                    logger.error("Не удалось переподключиться к WebSocket. Операция отменена.")
                    return
                self.__session_id = self.ws_client.session_id

            try:
                clipboard_text = pyperclip.paste()
                trimmed_text = clipboard_text[:900] if clipboard_text else ""

                session = requests.Session()
                response = session.post(
                    url=self.__config.server.api_url + "translate",
                    json={
                        "method": "translate",
                        "ws_session_id": self.__session_id,
                        "payload": {
                            "text": trimmed_text,
                            "translator_code": self.__config.user.selected_translator,
                            "target_lang": self.__config.user.selected_language,
                        }
                    }
                )

                if response.status_code != 200:
                    title, msg, msg_type = "Ошибка при websocket подключении", f"Ошибка при отправке запроса: {response.status_code} - {response.text}", "error"
                    logger.error(msg)
                    show_message(title, msg, msg_type)
                    sys.exit(1)

                translated_text_data = self.ws_client.recv()
                if not translated_text_data:
                    return

                if translated_text_data.get("error"):
                    title, msg = "Ошибка", "Язык недоступен"
                    logger.error(msg)
                    show_message(title, msg)
                else:
                    translated_text = translated_text_data.get("result", {}).get("result", {}).get("text")

                    print(translated_text_data)

                    if translated_text:
                        logger.info(f"Переведённый текст: {translated_text}")
                        pyperclip.copy(translated_text)
                    else:
                        logger.error(f"Не удалось извлечь переведенный текст: {translated_text_data}")

            except Exception as e:
                logger.error(f"Ошибка при обработке горячей клавиши: {e}")

        keyboard.add_hotkey(self.__key_combination, on_hotkey_press)

        while self.__running:
            if not self.ws_client.is_alive():
                logger.info(f"WebSocket разорван, попытка переподключения через {self.__reconnect_delay} сек...")
                self.ws_client.reconnect(self.__reconnect_delay)
            time.sleep(0.5)

    def stop(self):
        logger.info("Остановка отслеживания комбинации клавиш")
        self.__running = False
        keyboard.unhook_all()
