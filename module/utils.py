from PIL import Image, ImageDraw
from logging import getLogger


logger = getLogger(__name__)


def create_app_icon() -> Image:
    width, height, padding = 64, 64, 10
    image = Image.new("RGB", (width, height), color="blue")
    dc = ImageDraw.Draw(image)
    dc.ellipse((padding, padding, width - padding, height - padding), fill="yellow")
    logger.info("Application icon initialized successfully")
    return image
