import sys
import os
from PIL import Image
from io import BytesIO
import requests


project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from core.scraper import gather_imgs
from config.config import date_url

def get_epaper_details(epaper_name:str ,url: str, date: str = date_url) -> dict:
    individual_images = []
    imgs_urls = gather_imgs(url)
    for url in imgs_urls:
        jpg_response = requests.get(f"{url}.jpg", timeout=5)
        png_response = requests.get(f"{url}.png", timeout=5)

        jpg_img = Image.open(BytesIO(jpg_response.content))
        png_img = Image.open(BytesIO(png_response.content))

        if png_img.mode != "RGBA":
            png_img = png_img.convert("RGBA")

        combined = Image.new("RGBA", jpg_img.size)
        combined.paste(jpg_img.convert('RGB'), (0, 0))
        combined.paste(png_img, (0, 0), png_img)

        if combined.mode == 'RGBA':
            background = Image.new('RGB', combined.size, (255, 255, 255))
            background.paste(combined, mask=combined.split()[3])
            combined = background

        compressed_img = compress_image_for_pdf(combined, quality=60)
        individual_images.append(compressed_img)

    if individual_images:
        pdf_filename = f"{project_root}/newspapers/{epaper_name}/{epaper_name}_{date}.pdf"

        if len(individual_images)>1:
            other_images = individual_images[1:]
            individual_images[0].save(pdf_filename,"PDF",resolution=100.0, save_all=True, append_images=other_images)
        else:
            individual_images[0].save(pdf_filename, "PDF")

        pdf_details = {
            "epaper_name": epaper_name,
            "date": date,
            "file_path": pdf_filename
        }

        return pdf_details
    return {}

def compress_image_for_pdf(image, quality=85, max_size=1650):
    if image.mode != 'RGB':
        image = image.convert('RGB')

    width, height = image.size
    if max(width, height) > max_size:
        ratio = max_size / max(width, height)
        new_size = (int(width * ratio), int(height * ratio))
        image = image.resize(new_size, Image.Resampling.LANCZOS)

    compressed = BytesIO()
    image.save(compressed, "JPEG", quality=quality, optimize=True)
    compressed.seek(0)
    return Image.open(compressed)


if __name__ == "__main__":
    get_epaper_details("eenadu","https://epaper.eenadu.net/Home/Index")


