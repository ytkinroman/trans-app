import json
import time
import websocket
from logging import getLogger
import sys
from module.utils import show_message

logger = getLogger(__name__)


class WebSocketClient:
    def __init__(self, ws_url):
        self.ws_url = ws_url
        self.ws = None
        self.session_id = None
        self.connected = False

    def connect(self):
        if self.ws and self.ws.connected:
            return True
        try:
            self.ws = websocket.WebSocket()
            self.ws.connect(self.ws_url)
            logger.info("WebSocket успешно подключен")

            response = json.loads(self.ws.recv())
            self.session_id = response.get("room_id", "").replace("room_", "")
            if not self.session_id:
                logger.error("Не удалось получить session_id")
                self.disconnect()
                return False

            logger.info(f"Получен session_id: {self.session_id}")
            self.connected = True
            return True
        except Exception as e:
            logger.error(f"Ошибка подключения к WebSocket: {e}")
            self.disconnect()
            return False

    def reconnect(self, retry_delay=5, max_retries=3):
        for attempt in range(1, max_retries + 1):
            logger.info(f"Попытка переподключения {attempt}/{max_retries} через {retry_delay} сек...")
            self.disconnect()
            time.sleep(retry_delay)
            if self.connect():
                return True
        logger.error("Все попытки переподключения исчерпаны")
        return False

    def is_alive(self):
        if not self.ws or not self.ws.connected:
            return False
        try:
            return True
        except:
            self.connected = False
            return False

    def recv(self):
        if not self.is_alive():
            logger.warning("WebSocket не подключен, невозможно получить данные.")
            return None
        try:
            return json.loads(self.ws.recv())
        except Exception as e:
            self.connected = False
            logger.error(f"Ошибка при получении данных: {e}")

            # Пытаемся переподключиться
            if not self.reconnect():
                title, msg, msg_type = "Ошибка подключения", "Не удалось переподключиться к серверу", "error"
                show_message(title, msg, msg_type)
                sys.exit(1)
            return None

    def send(self, data):
        if not self.is_alive():
            logger.warning("WebSocket не подключен, невозможно отправить данные.")
            return False
        try:
            self.ws.send(json.dumps(data))
            return True
        except Exception as e:
            self.connected = False
            logger.error(f"Ошибка при отправке данных: {e}")

            # Пытаемся переподключиться
            if not self.reconnect():
                title, msg, msg_type = "Ошибка подключения", "Не удалось переподключиться к серверу", "error"
                show_message(title, msg, msg_type)
                sys.exit(1)
            return False

    def disconnect(self):
        if self.ws:
            try:
                self.ws.close()
            except:
                pass
        self.connected = False
        logger.info("WebSocket соединение закрыто")