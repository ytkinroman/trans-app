import websocket
import threading
from logging import getLogger
import os
from json import load, JSONDecodeError, loads

logger = getLogger(__name__)

WEBSOCKET_CONFIG_FILE = "config/websocket_config.json"


class WebSocketClient:
    def __init__(self):
        self.server_url = None
        self.ws = None
        self.ws_session_id = None
        self._first_message_received = False

    def connect(self):
        try:
            self.ws = websocket.WebSocketApp(
                self.server_url,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close
            )
            self.ws.on_open = self.on_open
            threading.Thread(target=self.ws.run_forever, daemon=True).start()
        except Exception as e:
            logger.error(f"Error connecting to WebSocket: {e}")

    @staticmethod
    def on_open(ws):
        logger.info("WebSocket connection opened.")

    def on_message(self, ws, message):
        if not self._first_message_received:
            try:
                data = loads(message)
                if "ws_session_id" in data:
                    self.ws_session_id = data["ws_session_id"]
                    logger.info(f"Session ID received: {self.ws_session_id}")
                    self._first_message_received = True
                    return  # Прекращаем обработку первого сообщения
            except JSONDecodeError:
                logger.error("Failed to parse first WebSocket message as JSON")

        logger.info(f'Response: "{message}"')

    @staticmethod
    def on_error(ws, error):
        logger.error(f"Error: {error}")

    @staticmethod
    def on_close(ws, close_status_code, close_msg):
        logger.info("WebSocket connection closed.")

    def send_message(self, text: str):
        logger.info(f'Request: "{text}"')
        if self.ws:
            self.ws.send(text)

    def close_connection(self):
        if self.ws:
            self.ws.close()

    def get_session_id(self) -> str | None:
        return self.ws_session_id

    def __load_config(self):
        if os.path.exists(WEBSOCKET_CONFIG_FILE):
            with open(WEBSOCKET_CONFIG_FILE, "r", encoding="utf-8") as file:
                config = load(file)
                self.server_url = config.get("websocket_url", "")
            logger.info('Настройки конфигурации подключения к WebSocket успешно загружены.')
        self.__load_config()
