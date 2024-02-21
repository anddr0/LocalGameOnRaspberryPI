import customtkinter

WINDOW_WIDTH = 650
WINDOW_HEIGHT = 350
PADDING = 40


class GameResult(customtkinter.CTk):
    def __init__(self, result):
        super().__init__()

        self.title("Result")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(False, False)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        customtkinter.CTkLabel(
            self,
            font=customtkinter.CTkFont(family="Verdana", size=60, weight="bold"),
            text=result[1],
            text_color="#91AD54" if result[0] else "#D44213",
        ).grid(row=0, column=0)
        self.after(3000, self.destroy)
        self.update()


if __name__ == "__main__":
    app = GameResult(((True, "You win")))
