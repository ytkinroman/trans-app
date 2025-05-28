from PIL import Image, ImageDraw
from logging import getLogger
import os
import sys
import tkinter as tk
from tkinter import messagebox


logger = getLogger(__name__)


def create_app_icon() -> Image:
    width, height, padding = 64, 64, 10
    image = Image.new("RGB", (width, height), color="blue")
    dc = ImageDraw.Draw(image)
    dc.ellipse((padding, padding, width - padding, height - padding), fill="yellow")
    logger.info("Application icon initialized successfully")
    return image


def get_config_dir() -> str:
    if getattr(sys, "frozen", False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    config_dir = os.path.join(base_dir, "config")
    os.makedirs(config_dir, exist_ok=True)

    return config_dir


def show_message(title: str, message: str, message_type: str = "info") -> None:
    root = tk.Tk()
    root.withdraw()

    if message_type == "error":
        messagebox.showerror(title, message)
    elif message_type == "warning":
        messagebox.showwarning(title, message)
    else:
        messagebox.showinfo(title, message)

    logger.info(f'The {message_type} message is shown to the user: "{message}"')
    root.destroy()
