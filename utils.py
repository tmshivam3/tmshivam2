import os

def list_subfolders(directory):
    try:
        return [f.name for f in os.scandir(directory) if f.is_dir()]
    except FileNotFoundError:
        print(f"Directory {directory} not found.")
        return []

def generate_preview(year, theme, new_value):
    print("DEBUG: generate_preview() was called!")
    print(f"Inputs => year: {year}, theme: {theme}, new_value: {new_value}")

    preview = f"Preview for {year} - Theme: {theme} - Value: {new_value}"
    print("Generated Preview:", preview)
    return preview
# utils.py
from PIL import Image

def smart_crop(img: Image.Image, target_ratio: float = 3/4) -> Image.Image:
    """Crop image to target aspect ratio (default 3:4)."""
    w, h = img.size
    if w / h > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        return img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        return img.crop((0, top, w, top + new_h))
