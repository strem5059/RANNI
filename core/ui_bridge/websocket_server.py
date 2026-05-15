import asyncio
import json
import websockets
from core.utils.logger import ranni_logger

class UIBridge:
    def __init__(self, host="127.0.0.1", port=9876):
        self.logger = ranni_logger.bind(module="ui_bridge")
        self.host = host
        self.port = port
        self.clients = set()
        self.server = None
        self._on_message = None

    def set_message_handler(self, handler):
        self._on_message = handler

    async def _handler(self, websocket):
        self.clients.add(websocket)
        self.logger.info(f"Cliente UI conectado: {websocket.remote_address}")
        try:
            async for message in websocket:
                data = json.loads(message)
                if self._on_message:
                    response = await self._on_message(data)
                    await websocket.send(json.dumps(response))
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.discard(websocket)
            self.logger.info("Cliente UI desconectado")

    async def start(self):
        self.server = await websockets.serve(self._handler, self.host, self.port)
        self.logger.info(f"WebSocket server en ws://{self.host}:{self.port}")

    async def broadcast(self, event_type, data):
        message = json.dumps({"type": event_type, "data": data})
        if self.clients:
            await asyncio.gather(
                *(client.send(message) for client in self.clients.copy()),
                return_exceptions=True
            )

    async def send_state(self, state):
        await self.broadcast("state", state)

    async def send_audio_level(self, level):
        await self.broadcast("audio_level", {"level": level})

    async def send_status(self, status, text=""):
        await self.broadcast("status", {"status": status, "text": text})

    async def stop(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()
