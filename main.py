from main_app import App
import subprocess


if __name__ == "__main__":
    userId = subprocess.check_output(["python", "login_app.py"])
    app = App(userId)
