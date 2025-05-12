import json
from logging import getLogger
import keyboard
import pyperclip
from threading import Thread, Lock
import time
from config_manager import ConfigurationManager
import websocket
import requests


logger = getLogger(__name__)


class KeyListener(Thread):
    def __init__(self, config_manager: ConfigurationManager):
        super().__init__(daemon=True)
        self.__config_manager = config_manager
        self.__key_combination = self.__config_manager.get_hotkey()  # например "alt+shift+t"
        self.__running = True
        logger.info(f"Инициализация KeyListener с комбинацией {self.__key_combination}")
        self.ws = websocket.WebSocket()

    def run(self):
        """Метод, который запускается при старте потока"""
        logger.info("Запуск отслеживания комбинации клавиш")
        
        
        self.ws.connect("ws://212.220.211.93:8081/ws")
        session_id = json.loads(self.ws.recv()).get("session_id")
        logger.info(f"Получен session_id: {session_id}")
        
        def on_hotkey_press():
            """Обработчик нажатия комбинации клавиш"""
            logger.info(f"Обнаружено нажатие комбинации {self.__key_combination}")
            try:
                # Здесь можно добавить логику обработки
                print("Hotkey pressed!")
                clipboard_text = pyperclip.paste()
                trimmed_text = clipboard_text[:900] if clipboard_text else ""

                #print(trimmed_text)
                session = requests.Session()
                response = session.post(
                    url="http://212.220.211.93:8081/translate", 
                    json={
                        "method": "translate", 
                        "ws_session_id": session_id, 
                        "payload": {
                            "text": trimmed_text, 
                            "translator_code": "yandex",#self.__config_manager.get_translator().get_code(),
                            "target_lang": "ru",#self.__config_manager.get_language().get_code(),
                        }
                    }
                )
                
                print(response.json())
                
                if response.status_code != 200:
                    logger.error(f"Ошибка при отправке запроса: {response.status_code} - {response.text}")
                    return

                if response.json().get("status") == "success":
                    translated_text = json.loads(self.ws.recv()).get("result").get("result").get("text")
                    print(f"Перведённый текст: {translated_text}")
                    pyperclip.copy(translated_text)
            except Exception as e:
                logger.error(f"Ошибка при обработке комбинации клавиш: {e}")
                self.ws.close()

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
        self.ws.close()
