import tkinter
import tkinter.messagebox
import customtkinter
import asyncio
import socket
import websockets
import json
from customtkinter import CTkImage
from datetime import datetime
from PIL import Image, ImageTk
from database import DataBaseManager
from values import URL, KEY
from user import User
from game import Game
from connectionManager import ConnectionManager
from result import GameResult


WINDOW_WIDTH = 650
WINDOW_HEIGHT = 600
PADDING = 40

customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("blue")


class App(customtkinter.CTk):
    def __init__(self, userId):
        super().__init__()
        self.protocol("WM_DELETE_WINDOW", self.onClose)
        self.userId = userId
        self.game = Game(self)
        self.connManager = ConnectionManager(self)
        self.isAppRunning = True
        self.cm_createLobby = False
        self.cm_joinLobby = False
        self.host_ip = ""
        self.gm_isRunning = False
        self.gm_myScore = 0
        self.gm_startGame = False
        self.gm_duration = 0
        self.gm_ended = False
        self.gm_result = []

        self.db_manager = DataBaseManager(URL, KEY)
        self.title("Falling raspberry [Menu]")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(False, False)

        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(1, weight=0)

        self.tabview = customtkinter.CTkTabview(
            self, width=WINDOW_WIDTH - PADDING, height=WINDOW_HEIGHT - PADDING
        )
        self.tabview._segmented_button.configure(
            font=customtkinter.CTkFont(family="Verdana", size=25, weight="bold"),
            height=100,
            width=100,
            fg_color="#272727",
        )
        self.tabview._segmented_button.grid(sticky="W")

        self.tabview.grid(row=0, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.tabview.add("  PROFILE  ")
        self.tabview.add("  LEADERBOARD  ")
        self.tabview.add("  LOBBIES  ")
        self.tabview.tab("  PROFILE  ").grid_columnconfigure(2, weight=1)
        self.tabview.tab("  LEADERBOARD  ").grid_columnconfigure(0, weight=1)

        self.label_username = customtkinter.CTkLabel(
            self.tabview.tab("  PROFILE  "),
            font=customtkinter.CTkFont(family="Verdana", size=35, weight="bold"),
            justify="left",
        )
        self.label_username.grid(row=0, column=0, padx=30, pady=(20, 0), sticky="w")

        self.label_wins = customtkinter.CTkLabel(
            self.tabview.tab("  PROFILE  "),
            font=customtkinter.CTkFont(family="Verdana", size=25),
            justify="left",
        )
        self.label_wins.grid(row=3, column=0, padx=30, pady=(20, 0), sticky="w")

        self.label_registration_date = customtkinter.CTkLabel(
            self.tabview.tab("  PROFILE  "),
            font=customtkinter.CTkFont(family="Verdana", size=25),
            justify="left",
        )
        self.label_registration_date.grid(
            row=4, column=0, padx=30, pady=(5, 0), sticky="w"
        )

        self.label_header_tabel = customtkinter.CTkLabel(
            self.tabview.tab("  PROFILE  "),
            font=customtkinter.CTkFont(family="Verdana", size=20),
            text="{:<34} {:<22} {:<6}".format("Date", "Enemy", "Result"),
            justify="left",
        )
        self.label_header_tabel.grid(
            row=5, column=0, padx=30, pady=(20, 10), sticky="w"
        )

        self.scrollable_frame = customtkinter.CTkScrollableFrame(
            master=self.tabview.tab("  PROFILE  "),
            width=WINDOW_WIDTH - 130,
            height=WINDOW_HEIGHT - 340,
            border_color="white",
            border_width=3,
        )
        self.scrollable_frame.grid(row=6, column=0, padx=30, pady=0, sticky="w")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame.grid_columnconfigure(1, weight=0)

        self.label_leaders = customtkinter.CTkLabel(
            self.tabview.tab("  LEADERBOARD  "),
            font=customtkinter.CTkFont(family="Verdana", size=25),
            text="{:<44} {:<4}".format("Username", "Wins"),
            justify="left",
        )
        self.label_leaders.grid(row=0, column=0, padx=30, pady=(30, 10), sticky="w")

        self.scrollable_frame_leaders = customtkinter.CTkScrollableFrame(
            master=self.tabview.tab("  LEADERBOARD  "),
            width=WINDOW_WIDTH - 130,
            height=WINDOW_HEIGHT - 203,
            border_color="white",
            border_width=3,
        )
        self.scrollable_frame_leaders.grid(row=1, column=0, padx=30, pady=0)
        self.scrollable_frame_leaders.grid_columnconfigure(0, weight=1)
        self.scrollable_frame_leaders.grid_columnconfigure(1, weight=0)

        self.frame = customtkinter.CTkFrame(
            self.tabview.tab("  LOBBIES  "),
            width=WINDOW_WIDTH - 50,
            height=50,
        )
        self.frame.grid(row=0, column=0, padx=0, pady=0)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=0)

        self.button_create_lobby = customtkinter.CTkButton(
            self.frame,
            width=250,
            height=50,
            text="Create lobby",
            font=customtkinter.CTkFont(family="Verdana", size=25, weight="bold"),
            command=self.createLobby,
        )

        self.button_create_lobby.grid(
            row=0, column=1, padx=(30, 0), pady=(10, 20), sticky="w"
        )

        pil_image = Image.open("img/refresh_icon.png")

        self.image = customtkinter.CTkImage(pil_image)

        self.button_refresh_lobby = customtkinter.CTkButton(
            self.frame,
            width=50,
            height=50,
            text="",
            image=self.image,
            command=self.showLobbies,
        )

        self.button_refresh_lobby.grid(
            row=0, column=0, padx=0, pady=(10, 20), sticky="w"
        )

        self.roundDurationVar = customtkinter.StringVar(value="30s")

        self.roundDurationMenu = customtkinter.CTkOptionMenu(
            self.frame,
            values=["10s", "30s", "60s", "90s", "120s"],
            variable=self.roundDurationVar,
            font=customtkinter.CTkFont(family="Verdana", size=25, weight="bold"),
            dropdown_font=customtkinter.CTkFont(family="Verdana", size=20),
        )
        self.roundDurationMenu.grid(row=0, column=2, padx=30, pady=(0, 10), sticky="e")

        self.scrollable_frame_lobbies = customtkinter.CTkScrollableFrame(
            master=self.tabview.tab("  LOBBIES  "),
            width=WINDOW_WIDTH - 130,
            height=WINDOW_HEIGHT - 212,
            border_color="white",
            border_width=3,
        )
        self.scrollable_frame_lobbies.grid(row=2, column=0, padx=30, pady=(0, 0))
        self.scrollable_frame_lobbies.grid_columnconfigure(0, weight=1)
        self.scrollable_frame_lobbies.grid_columnconfigure(1, weight=0)

        self.refreshUI()
        asyncio.run(self.runAsync())

    def showUserProfile(self, userId):
        self.user = User(userId)
        self.label_username.configure(text=self.user.getUsername())
        self.label_wins.configure(text=f"Wins: {self.user.getWinsCount()}")
        self.label_registration_date.configure(
            text=f"Registration date: {self.user.getRegistrationDate().replace('T', ' ')}"
        )

        rowN = 0
        for game in self.user.getGamesHistory():
            enemy_username = game["enemyusername"]
            game_date = game["date"].replace("T", " ")
            win = game["userwin"]

            customtkinter.CTkLabel(
                self.scrollable_frame,
                text=game_date,
                font=customtkinter.CTkFont(family="Verdana", size=16),
                justify="left",
            ).grid(row=rowN, column=0, pady=0, padx=(5, 0), sticky="w")

            customtkinter.CTkLabel(
                self.scrollable_frame,
                text=enemy_username,
                font=customtkinter.CTkFont(family="Verdana", size=16),
                justify="left",
            ).grid(row=rowN, column=1, pady=0, padx=0, sticky="w")

            if win:
                customtkinter.CTkLabel(
                    self.scrollable_frame,
                    text="Win",
                    text_color="#91AD54",
                    font=customtkinter.CTkFont(family="Verdana", size=16),
                    justify="left",
                    width=100,
                ).grid(row=rowN, column=2, pady=0, padx=0, sticky="w")
            else:
                customtkinter.CTkLabel(
                    self.scrollable_frame,
                    text="Lose",
                    text_color="#D44213",
                    font=customtkinter.CTkFont(family="Verdana", size=16),
                    justify="left",
                    width=100,
                ).grid(row=rowN, column=2, pady=0, padx=0, sticky="w")
            rowN += 1

    def showLeaders(self):
        self.leaders = self.db_manager.getLeaderboard()

        rowN = 0
        for leader in self.leaders:
            customtkinter.CTkLabel(
                self.scrollable_frame_leaders,
                text=leader["username"],
                font=customtkinter.CTkFont(family="Verdana", size=16),
                justify="left",
            ).grid(row=rowN, column=0, pady=0, padx=(5, 0), sticky="w")

            customtkinter.CTkLabel(
                self.scrollable_frame_leaders,
                text=leader["wins"],
                text_color="#91AD54",
                font=customtkinter.CTkFont(family="Verdana", size=16),
                justify="left",
            ).grid(row=rowN, column=1, pady=0, padx=(0, 50), sticky="e")
            rowN += 1

    def showLobbies(self):
        for widget in self.scrollable_frame_lobbies.winfo_children():
            widget.destroy()

        self.lobbies = self.db_manager.getLobbies()
        isMyIdInLobbies = (
            len(list(filter(lambda lb: lb["hostid"] == self.userId, self.lobbies))) > 0
        )

        rowN = 0
        if isMyIdInLobbies:
            self.button_refresh_lobby.configure(state="disabled")
            self.button_create_lobby.configure(state="disabled")
            self.roundDurationMenu.configure(state="disabled")
        else:
            self.button_refresh_lobby.configure(state="normal")
            self.button_create_lobby.configure(state="normal")
            self.roundDurationMenu.configure(state="normal")

        for lobby in self.lobbies:
            myState = "normal" if lobby["status"] == 1 else "disabled"
            if isMyIdInLobbies:
                if lobby["status"] == 1:
                    button_text = "Leave" if lobby["hostid"] == self.userId else "Join"
                else:
                    button_text = "In Game"
                if lobby["hostid"] != self.userId:
                    myState = "disabled"
            else:
                button_text = "Join" if lobby["status"] == 1 else "In Game"

            customtkinter.CTkLabel(
                self.scrollable_frame_lobbies,
                font=customtkinter.CTkFont(family="Verdana", size=25),
                text=f"{lobby['roundduration']}s | {lobby['username']}",
                justify="left",
            ).grid(row=rowN, column=0, padx=(10, 0), sticky="w")
            customtkinter.CTkButton(
                self.scrollable_frame_lobbies,
                font=customtkinter.CTkFont(family="Verdana", size=25),
                command=(
                    self.leaveLobby
                    if button_text == "Leave"
                    else lambda ip=lobby["hostip"]: self.joinLobby(ip)
                ),
                text=button_text,
                state=myState,
            ).grid(row=rowN, column=1, sticky="e", padx=(0, 10), pady=(10, 0))
            rowN += 1

    async def endlessUpdate(self):
        while self.isAppRunning:
            if self.cm_joinLobby:
                self.cm_joinLobby = False
                self.withdraw()
                await self.runGameAsClient(self.host_ip)
                self.deiconify()
            else:
                self.update()
            await asyncio.sleep(0.05)

    def onClose(self):
        self.isAppRunning = False

    def get_local_ip(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("1.1.1.1", 1))
            IP = s.getsockname()[0]
        return IP

    def createLobby(self):
        self.db_manager.createLobby(
            self.userId,
            f"{self.get_local_ip()}:{self.connManager._port}",
            self.getRoundDurationVar(),
        )
        self.showLobbies()
        self.cm_createLobby = True
        self.gm_duration = self.getRoundDurationVar()
        self.onCreateLobby()

    def leaveLobby(self):
        self.db_manager.removeLobby(self.userId)
        self.connManager._server_stop_event.set()
        self.showLobbies()

    def joinLobby(self, ip):
        self.host_ip = ip
        self.cm_joinLobby = True

    def getRoundDurationVar(self):
        return int(self.roundDurationVar.get()[:-1])

    def onCreateLobby(self):
        if self.gm_ended:
            self.gm_ended = False
            GameResult(self.gm_result)
            return
        if self.gm_startGame:
            self.gm_startGame = False
            self.game.game(self.gm_duration)
        self.after(100, self.onCreateLobby)

    async def runAsync(self):
        await asyncio.gather(self.connManager.run(), self.endlessUpdate())

    async def runGameAsClient(self, hostIp):
        uri = f"ws://{hostIp}"
        async with websockets.connect(uri) as websocket:
            await websocket.send(
                json.dumps(
                    {"userId": self.userId, "message": "start game", "duration": 10}
                )
            )
            response = json.loads(await websocket.recv())
            if response["message"] == "go":
                score, _ = self.game.game(response["duration"])
                await websocket.send(
                    json.dumps(
                        {
                            "userId": self.userId,
                            "message": "end game",
                            "duration": 10,
                            "score": score,
                        }
                    )
                )
                response = json.loads(await websocket.recv())
                if response["message"] == "draw":
                    score, duration = self.game.game()
                    await websocket.send(
                        json.dumps(
                            {
                                "userId": self.userId,
                                "message": "fatality",
                                "duration": duration,
                                "score": score,
                            }
                        )
                    )
                    response = json.loads(await websocket.recv())
                    if duration > response["duration"]:
                        self.gm_result = (True, "You win")
                        self.db_manager.addGame(self.userId, response["userId"])
                    else:
                        self.gm_result = (False, "You lose")
                        self.db_manager.addGame(response["userId"], self.userId)

                else:
                    if score > response["score"]:
                        self.gm_result = (True, "You win")
                        self.db_manager.addGame(self.userId, response["userId"])
                    else:
                        self.gm_result = (False, "You lose")
                        self.db_manager.addGame(response["userId"], self.userId)
                GameResult(self.gm_result)
                self.db_manager.removeLobby(response["userId"])
                self.after(150, self.refreshUI)
                await asyncio.sleep(3)
                self.connManager._server_stop_event.set()

    def refreshUI(self):
        self.showUserProfile(self.userId)
        self.showLeaders()
        self.showLobbies()
