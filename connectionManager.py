import asyncio
import websockets
import json
from result import GameResult


class ConnectionManager:
    def __init__(self, app, port=3000):
        self._port = port
        self._app = app
        self._server_stop_event = asyncio.Event()

    async def run(self):
        while self._app.isAppRunning:
            if self._app.cm_createLobby:
                self._app.cm_createLobby = False
                self._server_stop_event.clear()
                await self.createLobby()
            await asyncio.sleep(0.05)

    async def createLobby(self):
        async with websockets.serve(self.handle_client, "0.0.0.0", self._port):
            await self._server_stop_event.wait()

    async def handle_client(self, websocket):
        async for message in websocket:
            data = json.loads(message)
            if data["message"] == "start game":
                self._app.gm_startGame = True
                self._app.withdraw()
                await websocket.send(
                    json.dumps(
                        {
                            "userId": self._app.userId,
                            "message": "go",
                            "duration": self._app.gm_duration,
                        }
                    )
                )
            elif data["message"] == "end game":
                while self._app.gm_isRunning:
                    await asyncio.sleep(0.1)
                if self._app.gm_myScore == data["score"]:
                    self._app.gm_duration = 0
                    self._app.gm_startGame = True
                    await websocket.send(
                        json.dumps(
                            {
                                "userId": self._app.userId,
                                "message": "draw",
                                "score": self._app.gm_myScore,
                            }
                        )
                    )
                else:
                    if self._app.gm_myScore > data["score"]:
                        self._app.gm_result = (True, "You win")
                    else:
                        self._app.gm_result = (False, "You lose")
                    self._app.gm_ended = True
                    await websocket.send(
                        json.dumps(
                            {
                                "userId": self._app.userId,
                                "message": "not draw",
                                "score": self._app.gm_myScore,
                            }
                        )
                    )
                    self._server_stop_event.set()
                    self._app.refreshUI()
                    await asyncio.sleep(3)
                    self._app.deiconify()

            elif data["message"] == "fatality":
                while self._app.gm_isRunning:
                    await asyncio.sleep(0.1)
                if self._app.gm_duration >= data["duration"]:
                    self._app.gm_result = (True, "You win")
                else:
                    self._app.gm_result = (False, "You lose")
                self._app.gm_ended = True
                await websocket.send(
                    json.dumps(
                        {"userId": self._app.userId, "duration": self._app.gm_duration}
                    )
                )
                self._server_stop_event.set()

                await asyncio.sleep(3)
                self._app.refreshUI()
                self._app.deiconify()
