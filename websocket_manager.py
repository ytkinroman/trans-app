import json
import websocket
import time
import threading
from logging import getLogger

logger = getLogger(__name__)


class WebSocketManager:
    def __init__(self, config):
        self.config = config
        self.ws = None
        self.connected = False
        self.session_id = None
        self.running = False
        self.reconnect_thread = None
        self.ping_interval = 10  # Проверка каждые 10 секунд

    def connect(self):
        """Подключение к WebSocket и получение session_id"""
        if self.connected and self.ws and self.ws.connected:
            return True

        try:
            self.ws = websocket.WebSocket()
            self.ws.connect(self.config.server.websocket_url)
            self.connected = True

            response = self.ws.recv()
            data = json.loads(response)
            self.session_id = data.get("room_id", "").replace("room_", "")

            if not self.session_id:
                logger.error("Не удалось получить session_id.")
                self.disconnect()
                return False

            logger.info(f"WebSocket: успешно подключено, session_id={self.session_id}")
            return True

        except Exception as e:
            logger.error(f"Ошибка при подключении к WebSocket: {e}")
            self.disconnect()
            return False

    def disconnect(self):
        """Закрытие соединения"""
        self.connected = False
        if self.ws:
            try:
                self.ws.close()
            except Exception as e:
                logger.warning(f"Ошибка при закрытии WebSocket: {e}")
            self.ws = None
        self.session_id = None

    def is_connected(self):
        """Проверка активности соединения"""
        if not self.connected or not self.ws or not self.ws.connected:
            self.connected = False
            return False
        return True

    def recv(self):
        """Получение данных из WebSocket"""
        if not self.is_connected():
            raise websocket.WebSocketConnectionClosedException("WebSocket не подключен")
        try:
            return self.ws.recv()
        except websocket.WebSocketConnectionClosedException as e:
            logger.warning("Соединение было внезапно потеряно при попытке получения данных.")
            self.connected = False
            raise e

    def start_background_monitor(self):
        """Запуск фонового монитора для проверки соединения и авто-переподключения"""
        if self.running:
            return

        self.running = True
        self.reconnect_thread = threading.Thread(target=self.__monitor_connection, daemon=True)
        self.reconnect_thread.start()
        logger.info("Фоновый монитор WebSocket запущен.")

    def stop_background_monitor(self):
        """Остановка фонового монитора"""
        self.running = False
        if self.reconnect_thread:
            self.reconnect_thread.join()
        logger.info("Фоновый монитор WebSocket остановлен.")

    def __monitor_connection(self):
        """Фоновая задача проверки соединения и переподключения"""
        while self.running:
            if not self.is_connected():
                logger.warning("Соединение с WebSocket потеряно. Попытка переподключения...")
                if self.connect():
                    logger.info("Соединение восстановлено.")
                else:
                    logger.warning(f"Переподключение не удалось. Повтор через {self.ping_interval} сек.")
            time.sleep(self.ping_interval)

    def reconnect(self, delay=5):
        """Метод принудительного переподключения"""
        logger.info(f"Принудительное переподключение к WebSocket через {delay} сек...")
        time.sleep(delay)
        self.disconnect()
        return self.connect()


