import json
from logging import getLogger
import time
import keyboard
import pyperclip
from threading import Thread
from config_manager import ConfigurationManager
import websocket
import requests
from module.utils import show_message


logger = getLogger(__name__)


class KeyListener(Thread):
    def __init__(self, config_manager: ConfigurationManager):
        super().__init__(daemon=True)
        self.__config = config_manager
        self.__key_combination = self.__config.user.translate_keyboard  # например "alt+shift+t"
        self.__running = True
        self.__ws_connected = False
        self.__reconnect_delay = 5  # Задержка перед переподключением в секундах
        logger.info(f"Инициализация KeyListener с комбинацией {self.__key_combination}")
        self.ws = None
           
    def __connect_websocket(self):
        """Устанавливает соединение с WebSocket."""
        if self.ws and self.ws.connected:
            return True
        try:
            self.ws = websocket.WebSocket()
            self.ws.connect(self.__config.server.websocket_url)
            self.__ws_connected = True
            logger.info("Успешное подключение к WebSocket.")
            return True
        except Exception as e:
            logger.error(f"Ошибка подключения к WebSocket: {e}")
            self.__ws_connected = False
            if self.ws:
                self.ws.close()
            return False

    def run(self):
        """Метод, который запускается при старте потока"""
        logger.info("Started KeyListener...")
        session_id = None

        def on_hotkey_press():
            """Обработчик нажатия комбинации клавиш"""
            nonlocal session_id # Для доступа к session_id из внешней области видимости
            logger.info(f"Обнаружено нажатие комбинации {self.__key_combination}")
            if not self.__ws_connected or not self.ws or not self.ws.connected:
                logger.warning("WebSocket не подключен. Попытка переподключения...")
                if not self.__connect_websocket():
                    logger.error("Не удалось переподключиться к WebSocket. Операция отменена.")
                    return
                try:
                    # Повторное получение session_id после переподключения
                    session_id_data = json.loads(self.ws.recv())
                    session_id = session_id_data.get("room_id").replace("room_", "")
                    if not session_id:
                        logger.error("Не удалось получить session_id после переподключения.")
                        self.ws.close()
                        self.__ws_connected = False
                        return
                    logger.info(f"Получен новый session_id: {session_id}")
                except Exception as e:
                    logger.error(f"Ошибка при получении session_id после переподключения: {e}")
                    if self.ws:
                        self.ws.close()
                    self.__ws_connected = False
                    return
            
            try:
                clipboard_text = pyperclip.paste()
                trimmed_text = clipboard_text[:900] if clipboard_text else ""

                session = requests.Session()
                response = session.post(
                    url=self.__config.server.api_url + "translate",
                    json={
                        "method": "translate",
                        "ws_session_id": session_id,
                        "payload": {
                            "text": trimmed_text,
                            "translator_code": self.__config.user.selected_translator,
                            "target_lang": self.__config.user.selected_language,
                        }
                    }
                )

                if response.status_code != 200:
                    logger.error(f"Ошибка при отправке запроса: {response.status_code} - {response.text}")
                    return

                if not self.ws or not self.ws.connected:
                    logger.error("WebSocket был отключен перед получением результата перевода.")
                    self.__ws_connected = False
                    return

                translated_text_data = json.loads(self.ws.recv())

                if translated_text_data.get("error") is not "":
                    title, msg = "Ошибка", f'язык не дсотупен'  # TODO: Написать сообщение
                    logger.error(msg)
                    show_message(title, msg)
                else:
                    translated_text = translated_text_data.get("result", {}).get("result", {}).get("text")
                    if translated_text is not None:
                        logger.info(f"Перведённый текст: {translated_text}")
                        pyperclip.copy(translated_text)
                    else:
                        logger.error(f"Не удалось извлечь переведенный текст из ответа: {translated_text_data}")

            except websocket.WebSocketConnectionClosedException as e:
                logger.error(f"Соединение WebSocket было закрыто во время обработки горячей клавиши: {e}")
                self.__ws_connected = False
                if self.ws:
                    self.ws.close()
            except Exception as e:
                logger.error(f"Ошибка при обработке комбинации клавиш: {e}")
                if self.ws and self.ws.connected: # Закрываем только если еще подключен
                    self.ws.close()
                self.__ws_connected = False


        keyboard.add_hotkey(self.__key_combination, on_hotkey_press)

        while self.__running:
            if not self.__ws_connected:
                logger.info(f"Попытка подключения к WebSocket (задержка {self.__reconnect_delay} сек)...")
                if self.__connect_websocket():
                    try:
                        session_id_data = json.loads(self.ws.recv()) # Получаем session_id при первом подключении
                        session_id = session_id_data.get("room_id").replace("room_", "")
                        if not session_id:
                            logger.error("Не удалось получить session_id.")
                            self.ws.close()
                            self.__ws_connected = False
                        else:
                             logger.info(f"Получен session_id: {session_id}")
                    except Exception as e:
                        logger.error(f"Ошибка при получении session_id: {e}")
                        if self.ws:
                            self.ws.close()
                        self.__ws_connected = False
                
                if not self.__ws_connected and self.__running: # Если не удалось подключиться и поток все еще работает
                    time.sleep(self.__reconnect_delay)
            else:
                # Проверяем состояние соединения
                try:
                    if self.ws and self.ws.connected:
                        # Можно отправить пинг или просто проверить статус
                        # self.ws.ping() # Если сервер поддерживает пинги
                        pass
                    else:
                        # Соединение было потеряно
                        logger.warning("Соединение WebSocket потеряно.")
                        self.__ws_connected = False
                        if self.ws:
                            self.ws.close()
                except Exception as e:
                    logger.error(f"Ошибка при проверке соединения WebSocket: {e}")
                    self.__ws_connected = False
                    if self.ws:
                        self.ws.close()

                time.sleep(0.1)  # Небольшая пауза, чтобы не загружать CPU

        logger.info("KeyListener остановлен.")
        if self.ws:
            self.ws.close()

    def stop(self):
        """Метод для остановки потока"""
        logger.info("Остановка отслеживания комбинации клавиш")
        self.__running = False
        keyboard.unhook_all()
        if self.ws:
            logger.info("Закрытие WebSocket соединения...")
            self.ws.close()
            logger.info("WebSocket соединение закрыто.")
