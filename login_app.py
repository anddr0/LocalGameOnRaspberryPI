import customtkinter
import tkinter
from PIL import Image, ImageTk
from database import DataBaseManager
from values import URL, KEY

import time
import RPi.GPIO as GPIO
from mfrc522 import MFRC522

WINDOW_WIDTH = 650
WINDOW_HEIGHT = 600
PADDING = 40


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.MIFAREReader = MFRC522()
        self.uid = -1
        self.title("Game")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(False, False)
        self.db_manager = DataBaseManager(URL, KEY)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(1, weight=0)

        customtkinter.CTkLabel(
            self,
            font=customtkinter.CTkFont(family="Verdana", size=35, weight="bold"),
            text="Waiting for your card...",
        ).grid(row=0, column=0, pady=(100, 0))

        pil_image = Image.open("./img/waiting_rfid.png")
        self.image = ImageTk.PhotoImage(pil_image)
        self.image_label = customtkinter.CTkLabel(self, image=self.image, text="")
        self.image_label.grid(row=1, column=0, pady=(50, 0))
        self.after(50, self.rfidRead)

        self.rfidRead()

    def checkUserExists(self, userId):
        try:
            self.db_manager.getUserbyId(userId)
            return True
        except:
            pass
        return False

    def showRegistartionWindow(self):
        dialog_text = "It's your first time here. \n Enter your nickname:"
        dialog = customtkinter.CTkInputDialog(
            text=dialog_text,
            title="Registration",
            font=customtkinter.CTkFont(family="Verdana", size=20),
        )
        self.db_manager.addUser(str(self.uid), dialog.get_input())

    def rfidRead(self):
        if self.uid != -1:
            if not self.checkUserExists(str(self.uid)):
                self.showRegistartionWindow()
            print(str(uid))
            self.destroy()
            return
        (status, TagType) = self.MIFAREReader.MFRC522_Request(
            self.MIFAREReader.PICC_REQIDL
        )
        if status == self.MIFAREReader.MI_OK:
            (status, uid) = self.MIFAREReader.MFRC522_Anticoll()
            if status == self.MIFAREReader.MI_OK:
                num = 0
                for i in range(0, len(uid)):
                    num += uid[i] << (i * 8)
                return num
        self.after(50, self.rfidRead)


if __name__ == "__main__":
    app = App()
    app.mainloop()
