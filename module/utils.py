from PIL import Image, ImageDraw
from logging import getLogger
import os
import sys


logger = getLogger(__name__)


def create_app_icon() -> Image:
    width, height, padding = 64, 64, 10
    image = Image.new("RGB", (width, height), color="blue")
    dc = ImageDraw.Draw(image)
    dc.ellipse((padding, padding, width - padding, height - padding), fill="yellow")
    logger.info("Application icon initialized successfully")
    return image

def get_config_dir() -> str:
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    config_dir = os.path.join(base_dir, "config")
    os.makedirs(config_dir, exist_ok=True)

    return config_dir
