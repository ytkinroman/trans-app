import websocket
from threading import Thread
from logging import getLogger
from json import loads
from config_manager import ConfigurationManager

logger = getLogger(__name__)


class WebSocketClient:
    def __init__(self, config_manager: ConfigurationManager) -> None:
        self.__config_manager = config_manager
        self.__server_url = self.__config_manager.get_ws_url()

        self.__ws = None
        self.__ws_thread = None
        self.__ws_session_id = None
        self.__connected = False

    def connect(self):
        self.__ws = websocket.WebSocketApp(
            self.__server_url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )

        self.__ws_thread = Thread(target=self.__ws.run_forever, deamon=True)
        self.__ws_thread.start()

    def on_open(self, ws):
        self.__connected = True
        logger.info(f"WebSocket connection opened to {self.__server_url}")

    def on_message(self, ws, message):
        logger.info(f"Message received: {message}")
        try:
            data = loads(message)
            session_id = data.get("session_id")
            if session_id:
                self.__ws_session_id = session_id
                logger.info(f"Session ID updated: {session_id}")
        except Exception as e:
            logger.error(f"Failed to parse message: {e}")

    def on_error(self, ws, error):
        self.__connected = False
        logger.error(f"WebSocket error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        self.__connected = False
        logger.info(f"WebSocket connection closed: {close_status_code} - {close_msg}")

    def send_message(self, text: str):
        if self.__ws and self.__connected:
            self.__ws.send(text)
            logger.info(f"Sent message: {text}")
        else:
            logger.warning("Can't send message: WebSocket is not connected.")

    def close_connection(self):
        if self.__ws:
            self.__ws.close()
        if self.__ws_thread and self.__ws_thread.is_alive():
            self.__ws_thread.join(timeout=1)
        self.__connected = False
        logger.info("WebSocket connection closed manually.")

    def get_session_id(self) -> str | None:
        return self.__ws_session_id


if __name__ == "__main__":
    config = ConfigurationManager()  # Предполагается, что класс реализован
    client = WebSocketClient(config)
    client.connect()

    # Пример использования (только для теста)
    import time
    time.sleep(2)
    client.send_message('{"action": "hello"}')
    time.sleep(10)
    client.close_connection()
