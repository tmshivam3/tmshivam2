# utils.py

import os
from PIL import Image

def list_subfolders(directory: str) -> list:
    """
    List all subfolders in a given directory.
    
    Args:
        directory (str): Path to the directory.
    
    Returns:
        list: Names of subfolders.
    """
    try:
        return [f.name for f in os.scandir(directory) if f.is_dir()]
    except FileNotFoundError:
        print(f"Directory {directory} not found.")
        return []

def generate_preview(year: int, theme: str, new_value: str) -> str:
    """
    Generate a preview string based on inputs.
    
    Args:
        year (int): Year value.
        theme (str): Theme name.
        new_value (str): Any new value.
    
    Returns:
        str: Preview string.
    """
    print("DEBUG: generate_preview() was called!")
    print(f"Inputs => year: {year}, theme: {theme}, new_value: {new_value}")

    preview = f"Preview for {year} - Theme: {theme} - Value: {new_value}"
    print("Generated Preview:", preview)
    return preview

def smart_crop(img: Image.Image, target_ratio: float = 3/4) -> Image.Image:
    """
    Crop image to target aspect ratio (default 3:4).
    
    Args:
        img (PIL.Image.Image): Input image.
        target_ratio (float, optional): Desired width/height ratio. Defaults to 3/4.
    
    Returns:
        PIL.Image.Image: Cropped image.
    """
    w, h = img.size
    if w / h > target_ratio:
        # Image is too wide
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        return img.crop((left, 0, left + new_w, h))
    else:
        # Image is too tall
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        return img.crop((0, top, w, top + new_h))
