import obsws_python as obs
from obsws_python import ReqClient

class OBSWebSocket:
    def __init__(self, host: str, port: int, password: str):
        self.host = host
        self.port = port
        self.password = password
        self.client :ReqClient = None

    def connect(self):
        try:
            self.client = obs.ReqClient(host=self.host, port=self.port, password=self.password)
            print("Successfully connected to OBS WebSocket")
            return True
        except Exception as e:
            print(f"Failed to connect to OBS WebSocket: {e}")

            return False

    def disconnect(self):
        """Close the OBS WebSocket connection"""
        if self.client:
            self.client = None
            print("Disconnected from OBS WebSocket")
