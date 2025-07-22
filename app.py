import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps, ImageChops
import os
import io
import random
import datetime
import zipfile
import numpy as np
import textwrap
from typing import Tuple, List, Optional
import math
import requests
from io import BytesIO
import base64
import re

# =================== CONFIG ===================
st.set_page_config(page_title="⚡ ULTRA PRO MAX IMAGE EDITOR", layout="wide")

# Custom CSS for black/yellow theme with enhancements
st.markdown("""
    <style>
    .main {
        background-color: #ffffff;
    }
    .header-container {
        background-color: #000000;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
        border: 2px solid #ffff00;
        box-shadow: 0 0 15px #ffff00;
    }
    .image-preview-container {
        background-color: #000000;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
        border: 2px solid #ffff00;
    }
    .stButton>button {
        background-color: #000000;
        color: #ffff00;
        border: 2px solid #ffff00;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #ffff00;
        color: #000000;
        box-shadow: 0 0 15px #ffff00;
    }
    .sidebar .sidebar-content {
        background-color: #0a0a0a;
        color: #ffff00;
        border-right: 2px solid #ffff00;
    }
    .stSlider>div>div>div>div {
        background-color: #ffff00;
    }
    .stCheckbox>div>label {
        color: #ffff00 !important;
    }
    .stSelectbox>div>div>select {
        background-color: #000000;
        color: #ffff00 !important;
    }
    .stImage>img {
        border: 2px solid #ffff00;
        border-radius: 8px;
        box-shadow: 0 0 10px rgba(255, 255, 0, 0.5);
    }
    .variant-container {
        display: flex;
        overflow-x: auto;
        gap: 10px;
        padding: 10px 0;
    }
    .variant-item {
        flex: 0 0 auto;
    }
    .download-btn {
        display: block;
        margin-top: 5px;
        text-align: center;
    }
    .glowing-text {
        text-shadow: 0 0 5px #ffff00, 0 0 10px #ffff00, 0 0 15px #ffff00;
    }
    .texture-option {
        margin-top: 10px;
        padding: 10px;
        background-color: #1a1a1a;
        border-radius: 5px;
        border: 1px solid #ffff00;
    }
    .quote-slider {
        margin-top: 10px;
    }
    .feature-card {
        border: 1px solid #ffff00;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        background-color: #000000;
        color: #ffff00;
        box-shadow: 0 0 10px rgba(255, 255, 0, 0.3);
    }
    .pro-badge {
        background-color: #ffff00;
        color: #000;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.8em;
        font-weight: bold;
        margin-left: 5px;
    }
    .section-title {
        color: #ffff00;
        border-bottom: 2px solid #ffff00;
        padding-bottom: 5px;
        margin-top: 20px;
    }
    .effect-card {
        background-color: #1a1a1a;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .stProgress > div > div > div {
        background-color: #ffff00;
    }
    </style>
""", unsafe_allow_html=True)

# Main header with enhanced design
st.markdown("""
    <div class='header-container'>
        <h1 style='text-align: center; color: #ffff00; margin: 0;' class='glowing-text'>
            ⚡ ULTRA PRO MAX IMAGE EDITOR 900% <span style='font-size:0.6em;'>(40+ Features)</span>
        </h1>
        <p style='text-align: center; color: #ffff00;'>The World's Most Powerful Free Image Editor</p>
    </div>
""", unsafe_allow_html=True)

# =================== UTILS ===================
def list_files(folder: str, exts: List[str]) -> List[str]:
    """List files in folder with given extensions"""
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
        return []
    return [f for f in os.listdir(folder) 
           if any(f.lower().endswith(ext.lower()) for ext in exts)]

def smart_crop(img: Image.Image, target_ratio: float = 3/4) -> Image.Image:
    """Smart crop to maintain aspect ratio"""
    w, h = img.size
    if w/h > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        return img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        return img.crop((0, top, w, top + new_h))

def get_text_size(draw: ImageDraw.Draw, text: str, font: ImageFont.FreeTypeFont) -> Tuple[int, int]:
    """Get text dimensions"""
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def get_random_font() -> ImageFont.FreeTypeFont:
    """Get a random font from assets"""
    fonts = list_files("assets/fonts", [".ttf", ".otf"])
    if not fonts:
        try:
            return ImageFont.truetype("arial.ttf", 80)
        except:
            return ImageFont.load_default()
    
    for _ in range(3):  # Try 3 random fonts
        try:
            font_path = os.path.join("assets/fonts", random.choice(fonts))
            return ImageFont.truetype(font_path, 80)
        except:
            continue
    
    try:
        return ImageFont.truetype("arial.ttf", 80)
    except:
        return ImageFont.load_default()

def get_random_wish(greeting_type: str) -> str:
    """Get random wish based on greeting type"""
    wishes = {
        "Good Morning": ["Rise and shine!", "Make today amazing!", "Morning blessings!", "New day, new blessings!"],
        "Good Afternoon": ["Enjoy your day!", "Afternoon delights!", "Sunshine and smiles!", "Perfect day ahead!"],
        "Good Evening": ["Beautiful sunset!", "Evening serenity!", "Twilight magic!", "Peaceful evening!"],
        "Good Night": ["Sweet dreams!", "Sleep tight!", "Night night!", "Rest well!"],
        "Custom Greeting": ["Have a wonderful day!", "Stay blessed!", "Keep smiling!", "Enjoy every moment!"],
        "Happy Birthday": ["Wishing you a fantastic day!", "Many happy returns!", "Celebrate big!", "Best wishes on your special day!"],
        "Merry Christmas": ["Joy to the world!", "Season's greetings!", "Ho ho ho!", "Warmest wishes!"]
    }
    return random.choice(wishes.get(greeting_type, ["Have a nice day!"]))

def get_random_quote() -> str:
    """Get inspirational quote"""
    quotes = [
        "Every morning is a new opportunity\nto rise and shine.",
        "Wake up with determination,\ngo to bed with satisfaction.",
        "Morning is the perfect time\nto start something new.",
        "The early morning\nhas gold in its mouth.",
        "A new day is a new chance\nto be better than yesterday.",
        "Morning is wonderful.\nIts only drawback is that it comes\nat such an inconvenient time of day.",
        "The sun is a daily reminder\nthat we too can rise again\nfrom the darkness.",
        "Today's morning brings\nnew strength, new thoughts,\nand new possibilities.",
        "Morning is the time\nwhen the whole world\nstarts anew.",
        "Every sunrise is an invitation\nfor us to arise\nand brighten someone's day."
    ]
    return random.choice(quotes)

def get_random_color() -> Tuple[int, int, int]:
    """Generate random RGB color"""
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def get_gradient_colors() -> List[Tuple[int, int, int]]:
    """Returns a list of gradient colors (2-4 colors)"""
    num_colors = random.choice([2, 2, 3, 4])  # More chance for 2 colors
    base_colors = [
        (255, 255, 255),  # White
        (255, 255, 0),    # Yellow
        (0, 255, 0),      # Green
        (255, 0, 0),      # Red
        (0, 0, 255),      # Blue
        (255, 0, 255),    # Pink
        (255, 165, 0),    # Orange
        (0, 255, 255),    # Cyan
    ]
    
    # Sometimes use flag colors
    if random.random() < 0.2:
        flag = random.choice([
            [(255, 0, 0), (255, 255, 255), (0, 0, 255)],  # France
            [(255, 215, 0), (255, 255, 255), (0, 128, 0)],  # India
            [(255, 0, 0), (255, 255, 255)],  # Japan
            [(255, 0, 0), (0, 0, 255), (255, 255, 255)],  # Russia
            [(255, 0, 0), (255, 255, 0)],  # China
        ])
        return flag
    
    return random.sample(base_colors, num_colors)

def create_gradient_mask(width: int, height: int, colors: List[Tuple[int, int, int]], direction: str = 'horizontal') -> Image.Image:
    """Create a gradient mask image"""
    gradient = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(gradient)
    
    if direction == 'horizontal':
        for x in range(width):
            ratio = x / width
            r = int(colors[0][0] * (1 - ratio) + colors[-1][0] * ratio)
            g = int(colors[0][1] * (1 - ratio) + colors[-1][1] * ratio)
            b = int(colors[0][2] * (1 - ratio) + colors[-1][2] * ratio)
            draw.line([(x, 0), (x, height)], fill=(r, g, b))
    else:  # vertical
        for y in range(height):
            ratio = y / height
            r = int(colors[0][0] * (1 - ratio) + colors[-1][0] * ratio)
            g = int(colors[0][1] * (1 - ratio) + colors[-1][1] * ratio)
            b = int(colors[0][2] * (1 - ratio) + colors[-1][2] * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    return gradient

def apply_text_effect(draw: ImageDraw.Draw, position: Tuple[int, int], text: str, font: ImageFont.FreeTypeFont, 
                     effect_settings: dict, texture_img: Optional[Image.Image] = None) -> dict:
    """Apply advanced text effects"""
    x, y = position
    effect_type = effect_settings['type']
    text_width, text_height = get_text_size(draw, text, font)
    
    # Create a temporary image for advanced effects
    temp_img = Image.new('RGBA', (text_width, text_height))
    temp_draw = ImageDraw.Draw(temp_img)
    temp_draw.text((0, 0), text, font=font, fill=(255, 255, 255, 255))
    
    if effect_type == 'gradient':
        colors = get_gradient_colors()
        gradient = create_gradient_mask(text_width, text_height, colors)
        gradient_text = Image.new('RGBA', (text_width, text_height))
        gradient_text.paste(gradient, (0, 0), temp_img)
        
        # Apply outline
        outline_size = effect_settings.get('outline_size', 2)
        for ox in range(-outline_size, outline_size+1):
            for oy in range(-outline_size, outline_size+1):
                if ox != 0 or oy != 0:
                    draw.text((x+ox, y+oy), text, font=font, fill=(0, 0, 0))
        
        # Paste gradient text
        draw.bitmap((x, y), gradient_text.convert('L'), fill=None)
        
    elif effect_type == 'neon':
        # Neon glow effect
        glow_size = effect_settings.get('glow_size', 5)
        glow_color = effect_settings.get('glow_color', (0, 255, 255))
        
        for i in range(glow_size, 0, -1):
            alpha = int(255 * (i/glow_size))
            temp_glow = Image.new('RGBA', (text_width + i*2, text_height + i*2))
            temp_glow_draw = ImageDraw.Draw(temp_glow)
            temp_glow_draw.text((i, i), text, font=font, fill=(*glow_color, alpha))
            
            for _ in range(2):  # Blur iterations
                temp_glow = temp_glow.filter(ImageFilter.BLUR)
            
            draw.bitmap((x-i, y-i), temp_glow.convert('L'), fill=None)
        
        draw.text((x, y), text, font=font, fill=(255, 255, 255))
        
    elif effect_type == '3d':
        # 3D extruded text effect
        depth = effect_settings.get('depth', 5)
        light_angle = effect_settings.get('light_angle', 45)
        
        for i in range(1, depth+1):
            angle_color = (
                int(255 * math.cos(math.radians(light_angle))),
                int(255 * math.sin(math.radians(light_angle))),
                100
            )
            draw.text((x+i, y+i), text, font=font, fill=angle_color)
        
        draw.text((x, y), text, font=font, fill=(255, 255, 255))
        
    elif effect_type == 'colorful':
        main_color = effect_settings.get('main_color', get_random_color())
        outline_color = (0, 0, 0)
        
        outline_size = effect_settings.get('outline_size', 2)
        for ox in range(-outline_size, outline_size+1):
            for oy in range(-outline_size, outline_size+1):
                if ox != 0 or oy != 0:
                    draw.text((x+ox, y+oy), text, font=font, fill=outline_color)
        
        draw.text((x, y), text, font=font, fill=main_color)
        
    elif effect_type == 'full_random':
        main_color = get_random_color()
        outline_color = get_random_color()
        
        outline_size = effect_settings.get('outline_size', 2)
        for ox in range(-outline_size, outline_size+1):
            for oy in range(-outline_size, outline_size+1):
                if ox != 0 or oy != 0:
                    draw.text((x+ox, y+oy), text, font=font, fill=outline_color)
        
        draw.text((x, y), text, font=font, fill=main_color)
        
    else:  # Default/white styles
        shadow_offset = 3
        draw.text((x+shadow_offset, y+shadow_offset), text, font=font, fill=(25, 25, 25))
        
        if effect_type == "white_black_outline":
            outline_size = effect_settings.get('outline_size', 2)
            for ox in range(-outline_size, outline_size+1):
                for oy in range(-outline_size, outline_size+1):
                    if ox != 0 or oy != 0:
                        draw.text((x+ox, y+oy), text, font=font, fill=(0, 0, 0))
        
        draw.text((x, y), text, font=font, fill=(255, 255, 255))
    
    return effect_settings

def format_date(date_format: str = "%d %B %Y", show_day: bool = False) -> str:
    """Format current date with options"""
    today = datetime.datetime.now()
    formatted_date = today.strftime(date_format)
    
    if show_day:
        if today.hour >= 19:
            next_day = today + datetime.timedelta(days=1)
            day_name = next_day.strftime("%A")
            formatted_date += f" (Advance {day_name})"
        else:
            day_name = today.strftime("%A")
            formatted_date += f" ({day_name})"
    
    return formatted_date

def apply_overlay(image: Image.Image, overlay_path: str, size: float = 0.5) -> Image.Image:
    """Apply decorative overlay"""
    try:
        overlay = Image.open(overlay_path).convert("RGBA")
        new_size = (int(image.width * size), int(image.height * size))
        overlay = overlay.resize(new_size, Image.LANCZOS)
        
        max_x = max(20, image.width - overlay.width - 20)
        max_y = max(20, image.height - overlay.height - 20)
        x = random.randint(20, max_x) if max_x > 20 else 20
        y = random.randint(20, max_y) if max_y > 20 else 20
        
        image.paste(overlay, (x, y), overlay)
    except Exception as e:
        st.error(f"Error applying overlay: {str(e)}")
    return image

def generate_filename() -> str:
    """Generate unique filename"""
    now = datetime.datetime.now()
    future_minutes = random.randint(1, 10)
    future_time = now + datetime.timedelta(minutes=future_minutes)
    return f"Picsart_{future_time.strftime('%y-%m-%d_%H-%M-%S')}.jpg"

def get_watermark_position(img: Image.Image, watermark: Image.Image) -> Tuple[int, int]:
    """Get watermark position (90% bottom)"""
    x = random.choice([20, img.width - watermark.width - 20])
    y = img.height - watermark.height - 20
    return (x, y)

def enhance_image_quality(img: Image.Image) -> Image.Image:
    """Enhance image quality without altering original"""
    if img.mode != 'RGB':
        img = img.convert('RGB')
        
    # Apply sharpening
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(1.2)
    
    # Apply contrast enhancement
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.1)
    
    return img

def upscale_text_elements(img: Image.Image, scale_factor: int = 2) -> Image.Image:
    """Upscale text elements for better quality"""
    if scale_factor > 1:
        new_size = (img.width * scale_factor, img.height * scale_factor)
        img = img.resize(new_size, Image.LANCZOS)
    return img

def apply_halftone_effect(img: Image.Image, scale: int = 4) -> Image.Image:
    """Apply halftone effect to image"""
    img = img.convert('L')
    width, height = img.size
    img = img.resize((width//scale, height//scale))
    img = img.resize((width, height), Image.NEAREST)
    return img.convert('RGB')

def apply_vignette(img: Image.Image, intensity: float = 0.8) -> Image.Image:
    """Apply vignette effect"""
    width, height = img.size
    x = np.linspace(-1, 1, width)
    y = np.linspace(-1, 1, height)
    X, Y = np.meshgrid(x, y)
    R = np.sqrt(X**2 + Y**2)
    mask = 1 - np.clip(R * intensity, 0, 1)
    mask = (mask * 255).astype(np.uint8)
    mask_img = Image.fromarray(mask).convert('L')
    vignette = Image.new('RGB', (width, height), (0, 0, 0))
    img.paste(vignette, (0, 0), mask_img)
    return img

def apply_sketch_effect(img: Image.Image) -> Image.Image:
    """Convert image to pencil sketch"""
    img_gray = img.convert('L')
    img_invert = ImageOps.invert(img_gray)
    img_blur = img_invert.filter(ImageFilter.GaussianBlur(radius=3))
    return ImageOps.invert(img_blur)

def apply_oil_painting_effect(img: Image.Image, size: int = 7) -> Image.Image:
    """Apply oil painting effect"""
    img_arr = np.array(img)
    h, w = img_arr.shape[:2]
    oil_img = np.zeros_like(img_arr)
    
    for i in range(size//2, h-size//2):
        for j in range(size//2, w-size//2):
            region = img_arr[i-size//2:i+size//2+1, j-size//2:j+size//2+1]
            unique_colors, counts = np.unique(region.reshape(-1, 3), axis=0, return_counts=True)
            oil_img[i, j] = unique_colors[np.argmax(counts)]
    
    return Image.fromarray(oil_img)

def apply_watercolor_effect(img: Image.Image) -> Image.Image:
    """Apply watercolor painting effect"""
    img = img.filter(ImageFilter.SMOOTH_MORE)
    img = img.filter(ImageFilter.CONTOUR)
    img = Image.blend(img, img.filter(ImageFilter.GaussianBlur(1)), 0.5)
    return img

def apply_glitch_effect(img: Image.Image, intensity: float = 0.1) -> Image.Image:
    """Apply glitch effect"""
    img_arr = np.array(img)
    h, w = img_arr.shape[:2]
    
    # Channel shift
    shift = int(w * intensity)
    r, g, b = cv2.split(img_arr)
    r = np.roll(r, shift, axis=1)
    b = np.roll(b, -shift, axis=1)
    glitched = cv2.merge([r, g, b])
    
    # Scan lines
    for i in range(0, h, 2):
        glitched[i:i+1, :] = glitched[i:i+1, :] // 2
    
    return Image.fromarray(glitched)

def apply_pixel_art_effect(img: Image.Image, pixel_size: int = 8) -> Image.Image:
    """Convert image to pixel art"""
    width, height = img.size
    img = img.resize((width//pixel_size, height//pixel_size), Image.NEAREST)
    img = img.resize((width, height), Image.NEAREST)
    return img

def apply_rainbow_effect(img: Image.Image) -> Image.Image:
    """Apply rainbow color effect"""
    width, height = img.size
    rainbow = Image.new('RGB', (width, height))
    
    for y in range(height):
        hue = y / height
        r, g, b = [int(255 * c) for c in colorsys.hsv_to_rgb(hue, 1, 1)]
        rainbow.paste(Image.new('RGB', (width, 1), (r, g, b)), (0, y))
    
    return Image.blend(img, rainbow, 0.3)

def apply_light_leak_effect(img: Image.Image, leak_color: Tuple[int, int, int] = (255, 100, 0), opacity: float = 0.3) -> Image.Image:
    """Apply light leak effect"""
    width, height = img.size
    leak = Image.new('RGB', (width, height), leak_color)
    
    # Create gradient mask
    mask = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(mask)
    
    center_x = random.randint(0, width)
    center_y = random.randint(0, height)
    radius = max(width, height)
    
    for i in range(0, radius, radius//10):
        alpha = int(255 * (1 - i/radius) * opacity)
        draw.ellipse([(center_x-i, center_y-i), (center_x+i, center_y+i)], fill=alpha)
    
    return Image.composite(img, leak, mask)

def apply_film_grain_effect(img: Image.Image, intensity: float = 0.1) -> Image.Image:
    """Apply film grain effect"""
    img_arr = np.array(img)
    noise = np.random.normal(0, intensity * 255, img_arr.shape)
    noisy = np.clip(img_arr + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(noisy)

def apply_double_exposure_effect(img1: Image.Image, img2: Image.Image, blend_ratio: float = 0.5) -> Image.Image:
    """Create double exposure effect"""
    img2 = img2.resize(img1.size)
    return Image.blend(img1.convert('RGB'), img2.convert('RGB'), blend_ratio)

def apply_texture_overlay(img: Image.Image, texture: Image.Image, opacity: float = 0.5) -> Image.Image:
    """Overlay texture on image"""
    texture = texture.resize(img.size)
    return Image.blend(img.convert('RGB'), texture.convert('RGB'), opacity)

def apply_cartoon_effect(img: Image.Image) -> Image.Image:
    """Apply cartoon effect without OpenCV"""
    # Reduce colors
    reduced = img.quantize(colors=8, method=1)
    # Find edges
    gray = img.convert('L')
    edges = gray.filter(ImageFilter.FIND_EDGES)
    edges = edges.filter(ImageFilter.SMOOTH)
    edges = edges.point(lambda x: 0 if x < 150 else 255)
    # Combine
    cartoon = reduced.convert('RGB')
    cartoon.paste((0, 0, 0), (0, 0), edges)
    return cartoon

def apply_thermal_effect(img: Image.Image) -> Image.Image:
    """Apply thermal camera effect without OpenCV"""
    # Convert to grayscale
    gray = img.convert('L')
    # Apply color mapping
    arr = np.array(gray)
    # Simple thermal mapping: low values = blue, high values = red
    thermal = np.zeros((arr.shape[0], arr.shape[1], 3), dtype=np.uint8)
    thermal[:, :, 0] = np.clip(arr * 2, 0, 255)  # Red
    thermal[:, :, 1] = np.clip(arr * 0.5, 0, 255)  # Green
    thermal[:, :, 2] = np.clip(255 - arr, 0, 255)  # Blue
    return Image.fromarray(thermal)

def apply_parallax_effect(img: Image.Image, depth_map: Image.Image, intensity: float = 0.1) -> Image.Image:
    """Apply parallax scrolling effect"""
    img_arr = np.array(img)
    depth = np.array(depth_map.convert('L'))
    
    h, w = img_arr.shape[:2]
    shift = (depth * intensity).astype(np.int32)
    
    result = np.zeros_like(img_arr)
    for y in range(h):
        for x in range(w):
            new_x = x + shift[y, x]
            if 0 <= new_x < w:
                result[y, x] = img_arr[y, new_x]
    
    return Image.fromarray(result)

def apply_hdr_effect(img: Image.Image, strength: float = 1.5) -> Image.Image:
    """Apply HDR effect"""
    # Split into RGB channels
    r, g, b = img.split()
    
    # Enhance each channel
    r = ImageEnhance.Contrast(r).enhance(strength)
    g = ImageEnhance.Contrast(g).enhance(strength)
    b = ImageEnhance.Contrast(b).enhance(strength)
    
    # Merge back
    return Image.merge("RGB", (r, g, b))

def apply_magic_glow(img: Image.Image, glow_color: Tuple[int, int, int] = (255, 255, 0)) -> Image.Image:
    """Apply magical glow effect"""
    # Create a blurred version for glow
    blurred = img.filter(ImageFilter.GaussianBlur(10))
    
    # Create a solid color layer
    color_layer = Image.new('RGB', img.size, glow_color)
    
    # Blend with original
    result = Image.blend(img, color_layer, 0.3)
    result = Image.blend(result, blurred, 0.2)
    return result

def apply_crystal_effect(img: Image.Image) -> Image.Image:
    """Apply crystal refraction effect"""
    # Create displacement map
    width, height = img.size
    displacement = Image.new('L', (width, height))
    draw = ImageDraw.Draw(displacement)
    for i in range(0, width, 20):
        for j in range(0, height, 20):
            draw.ellipse([(i-10, j-10), (i+10, j+10)], fill=128)
    
    # Apply displacement
    return ImageChops.offset(img, 5, 5)

def apply_anime_effect(img: Image.Image) -> Image.Image:
    """Apply anime-style effect"""
    # Enhance colors
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(1.5)
    
    # Apply edge enhancement
    edges = img.filter(ImageFilter.FIND_EDGES)
    edges = edges.convert('L')
    edges = edges.point(lambda x: 0 if x < 100 else 255)
    
    # Combine with original
    result = img.copy()
    result.paste((0, 0, 0), (0, 0), edges)
    return result

def apply_golden_hour(img: Image.Image) -> Image.Image:
    """Apply golden hour warm effect"""
    # Create warm overlay
    overlay = Image.new('RGB', img.size, (255, 200, 50))
    return Image.blend(img, overlay, 0.3)

def apply_moonlight_effect(img: Image.Image) -> Image.Image:
    """Apply cool moonlight effect"""
    # Create cool overlay
    overlay = Image.new('RGB', img.size, (50, 100, 200))
    return Image.blend(img, overlay, 0.2)

def apply_vintage_effect(img: Image.Image) -> Image.Image:
    """Apply vintage photo effect"""
    # Sepia tone
    sepia = img.convert('RGB')
    r, g, b = sepia.split()
    r = r.point(lambda x: x * 0.9)
    g = g.point(lambda x: x * 0.7)
    b = b.point(lambda x: x * 0.4)
    sepia = Image.merge('RGB', (r, g, b))
    
    # Add vignette
    sepia = apply_vignette(sepia)
    
    # Add grain
    sepia = apply_film_grain_effect(sepia, 0.05)
    return sepia

def apply_cyberpunk_effect(img: Image.Image) -> Image.Image:
    """Apply cyberpunk neon effect"""
    # Increase contrast
    img = ImageEnhance.Contrast(img).enhance(1.5)
    
    # Boost blues and pinks
    r, g, b = img.split()
    b = ImageEnhance.Brightness(b).enhance(1.5)
    r = ImageEnhance.Brightness(r).enhance(1.3)
    return Image.merge('RGB', (r, g, b))

def apply_abstract_art(img: Image.Image) -> Image.Image:
    """Create abstract art effect"""
    # Apply multiple filters
    img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
    img = img.filter(ImageFilter.CONTOUR)
    img = ImageEnhance.Color(img).enhance(2.0)
    return img

def apply_mirror_effect(img: Image.Image) -> Image.Image:
    """Create mirror reflection effect"""
    width, height = img.size
    mirrored = Image.new('RGB', (width * 2, height))
    mirrored.paste(img, (0, 0))
    mirrored.paste(img.transpose(Image.FLIP_LEFT_RIGHT), (width, 0))
    return mirrored

def apply_kaleidoscope(img: Image.Image, segments: int = 6) -> Image.Image:
    """Create kaleidoscope effect"""
    # Crop to square
    size = min(img.size)
    img = img.crop((0, 0, size, size))
    
    # Create segment
    angle = 360 / segments
    segment = img.rotate(-angle / 2)
    segment = segment.crop((0, 0, size, size // 2))
    
    # Create full image
    result = Image.new('RGB', (size, size))
    for i in range(segments):
        rotated = segment.rotate(angle * i)
        result.paste(rotated, (0, 0))
    
    return result

def apply_liquid_effect(img: Image.Image, intensity: float = 5.0) -> Image.Image:
    """Apply liquid distortion effect"""
    width, height = img.size
    xm, ym = width / 2, height / 2
    
    # Create displacement map
    displacement = Image.new('L', (width, height))
    draw = ImageDraw.Draw(displacement)
    for y in range(height):
        for x in range(width):
            dx = x - xm
            dy = y - ym
            dist = math.sqrt(dx*dx + dy*dy)
            if dist == 0:
                dist = 1
            factor = (1 + math.sin(dist / intensity)) / 2
            value = int(255 * factor)
            draw.point((x, y), value)
    
    # Apply displacement
    return ImageChops.offset(img, 0, 0, displacement)

def apply_rain_effect(img: Image.Image) -> Image.Image:
    """Add rain effect to image"""
    # Create rain layer
    width, height = img.size
    rain = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(rain)
    
    # Draw rain streaks
    for _ in range(1000):
        x = random.randint(0, width)
        y = random.randint(0, height)
        length = random.randint(10, 30)
        draw.line([(x, y), (x, y+length)], fill=(200, 200, 255, 100), width=1)
    
    return Image.alpha_composite(img.convert('RGBA'), rain).convert('RGB')

def apply_snow_effect(img: Image.Image) -> Image.Image:
    """Add snow effect to image"""
    # Create snow layer
    width, height = img.size
    snow = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(snow)
    
    # Draw snowflakes
    for _ in range(500):
        x = random.randint(0, width)
        y = random.randint(0, height)
        size = random.randint(2, 6)
        draw.ellipse([(x, y), (x+size, y+size)], fill=(255, 255, 255, 200))
    
    return Image.alpha_composite(img.convert('RGBA'), snow).convert('RGB')

def apply_fire_frame(img: Image.Image) -> Image.Image:
    """Add animated fire frame effect (static version)"""
    width, height = img.size
    frame_size = 30
    fire_frame = Image.new('RGBA', (width + frame_size*2, height + frame_size*2), (0, 0, 0, 0))
    draw = ImageDraw.Draw(fire_frame)
    
    # Draw fire-like pattern
    for i in range(0, width + frame_size*2, 10):
        height_var = random.randint(5, frame_size)
        draw.rectangle([(i, 0), (i+10, height_var)], fill=(255, 100, 0, 200))
        draw.rectangle([(i, height + frame_size*2 - height_var), (i+10, height + frame_size*2)], 
                      fill=(255, 100, 0, 200))
    
    # Paste original image
    fire_frame.paste(img, (frame_size, frame_size))
    return fire_frame.convert('RGB')

def apply_emoji_stickers(img: Image.Image, emojis: List[str]) -> Image.Image:
    """Add emoji stickers to image"""
    # This is a placeholder - in a real app you'd use emoji images
    draw = ImageDraw.Draw(img)
    for _ in range(5):
        x = random.randint(20, img.width-40)
        y = random.randint(20, img.height-40)
        emoji = random.choice(emojis)
        font = ImageFont.truetype("arial.ttf", 40)
        draw.text((x, y), emoji, font=font, fill=(255, 255, 0))
    return img

def create_variant(original_img: Image.Image, settings: dict) -> Optional[Image.Image]:
    """Create image variant with applied effects"""
    img = original_img.copy()
    draw = ImageDraw.Draw(img)
    
    font = get_random_font()
    if font is None:
        return None
    
    texture_img = settings.get('texture_image', None)
    
    effect_settings = {
        'type': settings.get('text_effect', None),
        'use_texture': settings.get('use_texture', False),
        'outline_size': settings.get('outline_size', 2)
    }
    
    if settings['show_text']:
        font_main = font.font_variant(size=settings['main_size'])
        text = settings['greeting_type']
        text_width, text_height = get_text_size(draw, text, font_main)
        
        if settings['text_position'] == "top_center":
            text_x = (img.width - text_width) // 2
            text_y = 20
        elif settings['text_position'] == "bottom_center":
            text_x = (img.width - text_width) // 2
            text_y = img.height - text_height - 20
        else:  # random
            max_text_x = max(20, img.width - text_width - 20)
            text_x = random.randint(20, max_text_x) if max_text_x > 20 else 20
            text_y = random.randint(20, img.height - text_height - 20)
        
        effect_settings = apply_text_effect(
            draw, 
            (text_x, text_y), 
            text, 
            font_main,
            effect_settings,
            texture_img=texture_img
        )
    
    if settings['show_wish']:
        font_wish = font.font_variant(size=settings['wish_size'])
        wish_text = get_random_wish(settings['greeting_type'])
        wish_width, wish_height = get_text_size(draw, wish_text, font_wish)
        
        if settings['show_text']:
            wish_y = text_y + settings['main_size'] + random.randint(10, 30)
        else:
            wish_y = 20
        
        max_wish_x = max(20, img.width - wish_width - 20)
        wish_x = random.randint(20, max_wish_x) if max_wish_x > 20 else 20
        
        apply_text_effect(
            draw, 
            (wish_x, wish_y), 
            wish_text, 
            font_wish,
            effect_settings,
            texture_img=texture_img
        )
    
    if settings['show_date']:
        font_date = font.font_variant(size=settings['date_size'])
        
        if settings['date_format'] == "8 July 2025":
            date_text = format_date("%d %B %Y", settings['show_day'])
        elif settings['date_format'] == "28 January 2025":
            date_text = format_date("%d %B %Y", settings['show_day'])
        elif settings['date_format'] == "07/08/2025":
            date_text = format_date("%m/%d/%Y", settings['show_day'])
        else:
            date_text = format_date("%Y-%m-%d", settings['show_day'])
            
        date_width, date_height = get_text_size(draw, date_text, font_date)
        
        max_date_x = max(20, img.width - date_width - 20)
        date_x = random.randint(20, max_date_x) if max_date_x > 20 else 20
        date_y = max(20, img.height - date_height - 20)
        
        if settings['show_day'] and "(" in date_text:
            day_part = date_text[date_text.index("("):]
            day_width, _ = get_text_size(draw, day_part, font_date)
            if date_x + day_width > img.width - 20:
                date_x = img.width - day_width - 25
        
        apply_text_effect(
            draw, 
            (date_x, date_y), 
            date_text, 
            font_date,
            effect_settings,
            texture_img=texture_img
        )
    
    if settings['show_quote']:
        font_quote = font.font_variant(size=settings['quote_size'])
        quote_text = settings['quote_text']
        
        lines = [line.strip() for line in quote_text.split('\n') if line.strip()]
        
        total_height = 0
        line_heights = []
        line_widths = []
        
        for line in lines:
            w, h = get_text_size(draw, line, font_quote)
            line_heights.append(h)
            line_widths.append(w)
            total_height += h + 10
        
        quote_y = (img.height - total_height) // 2
        
        for i, line in enumerate(lines):
            line_x = (img.width - line_widths[i]) // 2
            apply_text_effect(
                draw, 
                (line_x, quote_y), 
                line, 
                font_quote,
                effect_settings,
                texture_img=texture_img
            )
            quote_y += line_heights[i] + 10
    
    if settings['use_watermark'] and settings['watermark_image']:
        watermark = settings['watermark_image'].copy()
        
        if settings['watermark_opacity'] < 1.0:
            alpha = watermark.split()[3]
            alpha = ImageEnhance.Brightness(alpha).enhance(settings['watermark_opacity'])
            watermark.putalpha(alpha)
        
        watermark.thumbnail((img.width//4, img.height//4))
        pos = get_watermark_position(img, watermark)
        img.paste(watermark, pos, watermark)
    
    if settings['use_coffee_pet'] and settings['selected_pet']:
        pet_path = os.path.join("assets/pets", settings['selected_pet'])
        if os.path.exists(pet_path):
            pet_img = Image.open(pet_path).convert("RGBA")
            pet_img = pet_img.resize(
                (int(img.width * settings['pet_size']), 
                int(img.height * settings['pet_size'] * (pet_img.height/pet_img.width))),
                Image.LANCZOS
            )
            x = img.width - pet_img.width - 20
            y = img.height - pet_img.height - 20
            img.paste(pet_img, (x, y), pet_img)
    
    # Apply additional effects
    if settings.get('apply_halftone', False):
        img = apply_halftone_effect(img)
    
    if settings.get('apply_vignette', False):
        img = apply_vignette(img)
    
    if settings.get('apply_sketch', False):
        img = apply_sketch_effect(img)
    
    if settings.get('apply_cartoon', False):
        img = apply_cartoon_effect(img)
    
    if settings.get('apply_anime', False):
        img = apply_anime_effect(img)
    
    if settings.get('apply_cyberpunk', False):
        img = apply_cyberpunk_effect(img)
    
    if settings.get('apply_vintage', False):
        img = apply_vintage_effect(img)
    
    if settings.get('apply_hdr', False):
        img = apply_hdr_effect(img)
    
    if settings.get('apply_magic_glow', False):
        img = apply_magic_glow(img)
    
    if settings.get('apply_rain', False):
        img = apply_rain_effect(img)
    
    if settings.get('apply_snow', False):
        img = apply_snow_effect(img)
    
    if settings.get('apply_golden_hour', False):
        img = apply_golden_hour(img)
    
    if settings.get('apply_moonlight', False):
        img = apply_moonlight_effect(img)
    
    img = enhance_image_quality(img)
    img = upscale_text_elements(img, scale_factor=2)
    
    return img.convert("RGB")

def adjust_font_size_to_fit(draw: ImageDraw.Draw, text: str, max_width: int, max_height: int, initial_size: int) -> ImageFont.FreeTypeFont:
    """Adjust font size to fit within dimensions"""
    font = None
    size = initial_size
    while size > 10:
        try:
            font = ImageFont.truetype("assets/fonts/default.ttf", size)
            text_width, text_height = get_text_size(draw, text, font)
            if text_width <= max_width and text_height <= max_height:
                break
        except:
            font = ImageFont.load_default()
            break
        size -= 2
    return font

# =================== MAIN APP ===================
if 'generated_images' not in st.session_state:
    st.session_state.generated_images = []
    
if 'watermark_groups' not in st.session_state:
    st.session_state.watermark_groups = {}

# Display features
st.markdown("""
    <div class='feature-card'>
        <h3>🌟 ULTRA PRO MAX FEATURES (40+)</h3>
        <ul>
            <li><span class='pro-badge'>NEW</span> Anime Style Effect</li>
            <li><span class='pro-badge'>NEW</span> Cyberpunk Neon Effect</li>
            <li><span class='pro-badge'>NEW</span> Vintage Photo Filter</li>
            <li><span class='pro-badge'>NEW</span> HDR Enhancement</li>
            <li><span class='pro-badge'>NEW</span> Magic Glow Effect</li>
            <li><span class='pro-badge'>NEW</span> Golden Hour Warmth</li>
            <li><span class='pro-badge'>NEW</span> Moonlight Cool Effect</li>
            <li><span class='pro-badge'>NEW</span> Rain & Snow Effects</li>
            <li><span class='pro-badge'>NEW</span> Fire Frame Decorations</li>
            <li><span class='pro-badge'>NEW</span> Emoji Stickers</li>
            <li>Smart Gradient Text Effects</li>
            <li>Multiple Watermark Support</li>
            <li>Advanced Text Positioning</li>
            <li>High Quality Text Rendering</li>
            <li>Custom Greeting Messages</li>
            <li>Date & Time Stamps</li>
            <li>Inspirational Quotes</li>
            <li>Pet & Coffee PNG Overlays</li>
            <li>Texture Overlays</li>
            <li>Batch Processing (100+ Images)</li>
            <li>Multiple Variants Generation</li>
            <li>Light Leak & Film Grain</li>
            <li>Double Exposure</li>
            <li>Cartoon Effect</li>
            <li>Pixel Art Converter</li>
            <li>And 15+ more effects...</li>
        </ul>
    </div>
""", unsafe_allow_html=True)

uploaded_images = st.file_uploader("📁 Upload Images (100+ at once)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

with st.sidebar:
    st.markdown("### ⚙️ ULTRA PRO SETTINGS")
    
    greeting_type = st.selectbox("Greeting Type", 
                               ["Good Morning", "Good Afternoon", "Good Evening", "Good Night", 
                                "Happy Birthday", "Merry Christmas", "Custom Greeting"])
    if greeting_type == "Custom Greeting":
        custom_greeting = st.text_input("Enter Custom Greeting", "Awesome Day!")
    
    generate_variants = st.checkbox("Generate 3 Variants per Photo", value=False)
    
    text_effect = st.selectbox(
        "Text Style",
        ["White Only", "White with Black Outline", "Gradient", "Neon", "3D", "Full Random", "Colorful"],
        index=0
    )
    
    # Text position options
    text_position = st.radio("Main Text Position", ["Top Center", "Bottom Center", "Random"], index=1)
    text_position = text_position.lower().replace(" ", "_")
    
    outline_size = st.slider("Text Outline Size", 1, 5, 2) if text_effect in ["White with Black Outline", "Gradient", "Neon", "3D", "Colorful"] else 2
    
    st.markdown("### 🎨 PRO TEXTURE OPTIONS")
    use_texture = st.checkbox("Use Texture for Text", value=False)
    texture_image = None
    
    if use_texture:
        texture_option = st.radio("Texture Source", ["From Uploaded Images", "Pre-made Texture"])
        
        if texture_option == "From Uploaded Images" and uploaded_images:
            texture_image = Image.open(uploaded_images[0]).convert("RGBA")
        elif texture_option == "Pre-made Texture":
            texture_files = list_files("assets/textures", [".png", ".jpg", ".jpeg"])
            if texture_files:
                selected_texture = st.selectbox("Select Texture", texture_files)
                texture_path = os.path.join("assets/textures", selected_texture)
                if os.path.exists(texture_path):
                    texture_image = Image.open(texture_path).convert("RGBA")
    
    show_text = st.checkbox("Show Greeting", value=True)
    if show_text:
        main_size = st.slider("Main Text Size", 10, 200, 90)
    
    show_wish = st.checkbox("Show Wish", value=True)
    if show_wish:
        wish_size = st.slider("Wish Text Size", 10, 200, 60)
    
    show_date = st.checkbox("Show Date", value=False)
    if show_date:
        date_size = st.slider("Date Text Size", 10, 200, 30)
        date_format = st.selectbox("Date Format", 
                                 ["8 July 2025", "28 January 2025", "07/08/2025", "2025-07-08"],
                                 index=0)
        show_day = st.checkbox("Show Day", value=False)
    
    show_quote = st.checkbox("Add Quote", value=False)
    if show_quote:
        quote_text = get_random_quote()
        quote_size = st.slider("Quote Text Size", 10, 100, 40)
    
    use_watermark = st.checkbox("Add Watermark", value=True)
    watermark_images = []
    
    if use_watermark:
        watermark_option = st.radio("Watermark Source", ["Pre-made", "Upload Your Own"])
        
        if watermark_option == "Pre-made":
            watermark_files = list_files("assets/logos", [".png", ".jpg", ".jpeg"])
            if watermark_files:
                selected_watermarks = st.multiselect("Select Watermark(s)", watermark_files, 
                                                   default=["wishful vibes.png", "happy vibes.png", "nature vibes.png"])
                for watermark_file in selected_watermarks:
                    watermark_path = os.path.join("assets/logos", watermark_file)
                    if os.path.exists(watermark_path):
                        watermark_images.append(Image.open(watermark_path).convert("RGBA"))
        else:
            uploaded_watermark = st.file_uploader("Upload Watermark", type=["png"], accept_multiple_files=True)
            if uploaded_watermark:
                for watermark in uploaded_watermark:
                    watermark_images.append(Image.open(watermark).convert("RGBA"))
        
        watermark_opacity = st.slider("Watermark Opacity", 0.1, 1.0, 1.0)
    
    use_overlay = st.checkbox("Use Pre-made Overlays", value=False)
    
    if use_overlay:
        overlay_theme = st.selectbox("Select Theme", ["Theme1", "Theme2"])
        random_overlay = st.checkbox("Random Overlay Selection", value=True)
        
        if not random_overlay:
            if greeting_type == "Good Morning":
                overlay_files = ["1.png", "2.png"]
            else:
                overlay_files = ["1.png", "3.png"]
        else:
            overlay_files = random.sample(["1.png", "2.png", "3.png", "4.png", "5.png"], 2)
        
        overlay_size = st.slider("Overlay Size", 0.1, 1.0, 0.5)
    
    st.markdown("---")
    st.markdown("### 🎭 PRO EFFECTS")
    col1, col2 = st.columns(2)
    with col1:
        apply_halftone = st.checkbox("Halftone Effect", value=False)
        apply_vignette = st.checkbox("Vignette Effect", value=False)
        apply_sketch = st.checkbox("Pencil Sketch", value=False)
        apply_cartoon = st.checkbox("Cartoon Effect", value=False)
        apply_anime = st.checkbox("Anime Style", value=False)
        
    with col2:
        apply_cyberpunk = st.checkbox("Cyberpunk", value=False)
        apply_vintage = st.checkbox("Vintage", value=False)
        apply_hdr = st.checkbox("HDR Enhancement", value=False)
        apply_magic_glow = st.checkbox("Magic Glow", value=False)
        
    st.markdown("### 🌦️ WEATHER EFFECTS")
    apply_rain = st.checkbox("Rain Effect", value=False)
    apply_snow = st.checkbox("Snow Effect", value=False)
    
    st.markdown("### ☀️ LIGHTING EFFECTS")
    apply_golden_hour = st.checkbox("Golden Hour", value=False)
    apply_moonlight = st.checkbox("Moonlight", value=False)
    
    st.markdown("---")
    st.markdown("### ☕🐾 PRO OVERLAYS")
    use_coffee_pet = st.checkbox("Enable Coffee & Pet PNG", value=False)
    if use_coffee_pet:
        pet_size = st.slider("PNG Size", 0.1, 1.0, 0.3)
        pet_files = list_files("assets/pets", [".png", ".jpg", ".jpeg"])
        selected_pet = st.selectbox("Select Pet PNG", ["Random"] + pet_files)
        
        if selected_pet == "Random":
            selected_pet = random.choice(pet_files) if pet_files else None
            
    st.markdown("### 🔥 SPECIAL EFFECTS")
    apply_fire_frame = st.checkbox("Fire Frame", value=False)
    apply_emoji = st.checkbox("Emoji Stickers", value=False)

if st.button("✨ ULTRA PRO GENERATE", key="generate"):
    if uploaded_images:
        with st.spinner("Processing images with ULTRA PRO quality..."):
            processed_images = []
            variant_images = []
            
            effect_mapping = {
                "White Only": "white_only",
                "White with Black Outline": "white_black_outline",
                "Gradient": "gradient",
                "Neon": "neon",
                "3D": "3d",
                "Full Random": "full_random",
                "Colorful": "colorful"
            }
            selected_effect = effect_mapping[text_effect]
            
            # Group images by watermark if multiple watermarks are selected
            watermark_groups = {}
            if len(watermark_images) > 1:
                group_size = len(uploaded_images) // len(watermark_images)
                for i, watermark in enumerate(watermark_images):
                    start_idx = i * group_size
                    end_idx = (i + 1) * group_size if i < len(watermark_images) - 1 else len(uploaded_images)
                    watermark_groups[f"Group {i+1}"] = {
                        'watermark': watermark,
                        'images': uploaded_images[start_idx:end_idx]
                    }
            else:
                watermark_groups["All Images"] = {
                    'watermark': watermark_images[0] if watermark_images else None,
                    'images': uploaded_images
                }
            
            st.session_state.watermark_groups = watermark_groups
            
            for group_name, group_data in watermark_groups.items():
                watermark = group_data['watermark']
                group_images = group_data['images']
                
                for uploaded_file in group_images:
                    try:
                        if uploaded_file is None:
                            continue
                            
                        img = Image.open(uploaded_file)
                        if img is None:
                            raise ValueError("Could not open image")
                            
                        img = img.convert("RGBA")
                        img = smart_crop(img)
                        img = enhance_image_quality(img)
                        
                        if use_overlay:
                            for overlay_file in overlay_files:
                                overlay_path = os.path.join("assets/overlays", overlay_theme, overlay_file)
                                if os.path.exists(overlay_path):
                                    img = apply_overlay(img, overlay_path, overlay_size)
                        
                        if generate_variants:
                            variants = []
                            for i in range(3):
                                settings = {
                                    'greeting_type': custom_greeting if greeting_type == "Custom Greeting" else greeting_type,
                                    'show_text': show_text,
                                    'main_size': main_size if show_text else 90,
                                    'text_position': text_position,
                                    'outline_size': outline_size,
                                    'show_wish': show_wish,
                                    'wish_size': wish_size if show_wish else 60,
                                    'show_date': show_date,
                                    'show_day': show_day if show_date else False,
                                    'date_size': date_size if show_date else 30,
                                    'date_format': date_format if show_date else "8 July 2025",
                                    'show_quote': show_quote,
                                    'quote_text': quote_text if show_quote else "",
                                    'quote_size': quote_size if show_quote else 40,
                                    'use_watermark': use_watermark,
                                    'watermark_image': watermark,
                                    'watermark_opacity': watermark_opacity if use_watermark else 1.0,
                                    'use_overlay': use_overlay,
                                    'overlay_files': overlay_files if use_overlay else [],
                                    'overlay_theme': overlay_theme if use_overlay else "",
                                    'overlay_size': overlay_size if use_overlay else 0.5,
                                    'use_coffee_pet': use_coffee_pet,
                                    'pet_size': pet_size if use_coffee_pet else 0.3,
                                    'selected_pet': selected_pet if use_coffee_pet else None,
                                    'text_effect': selected_effect,
                                    'use_texture': use_texture,
                                    'texture_image': texture_image,
                                    'apply_halftone': apply_halftone,
                                    'apply_vignette': apply_vignette,
                                    'apply_sketch': apply_sketch,
                                    'apply_cartoon': apply_cartoon,
                                    'apply_anime': apply_anime,
                                    'apply_cyberpunk': apply_cyberpunk,
                                    'apply_vintage': apply_vintage,
                                    'apply_hdr': apply_hdr,
                                    'apply_magic_glow': apply_magic_glow,
                                    'apply_rain': apply_rain,
                                    'apply_snow': apply_snow,
                                    'apply_golden_hour': apply_golden_hour,
                                    'apply_moonlight': apply_moonlight
                                }
                                
                                variant = create_variant(img, settings)
                                if variant is not None:
                                    variants.append((generate_filename(), variant))
                            variant_images.extend(variants)
                        else:
                            settings = {
                                'greeting_type': custom_greeting if greeting_type == "Custom Greeting" else greeting_type,
                                'show_text': show_text,
                                'main_size': main_size if show_text else 90,
                                'text_position': text_position,
                                'outline_size': outline_size,
                                'show_wish': show_wish,
                                'wish_size': wish_size if show_wish else 60,
                                'show_date': show_date,
                                'show_day': show_day if show_date else False,
                                'date_size': date_size if show_date else 30,
                                'date_format': date_format if show_date else "8 July 2025",
                                'show_quote': show_quote,
                                'quote_text': quote_text if show_quote else "",
                                'quote_size': quote_size if show_quote else 40,
                                'use_watermark': use_watermark,
                                'watermark_image': watermark,
                                'watermark_opacity': watermark_opacity if use_watermark else 1.0,
                                'use_overlay': use_overlay,
                                'overlay_files': overlay_files if use_overlay else [],
                                'overlay_theme': overlay_theme if use_overlay else "",
                                'overlay_size': overlay_size if use_overlay else 0.5,
                                'use_coffee_pet': use_coffee_pet,
                                'pet_size': pet_size if use_coffee_pet else 0.3,
                                'selected_pet': selected_pet if use_coffee_pet else None,
                                'text_effect': selected_effect,
                                'use_texture': use_texture,
                                'texture_image': texture_image,
                                'apply_halftone': apply_halftone,
                                'apply_vignette': apply_vignette,
                                'apply_sketch': apply_sketch,
                                'apply_cartoon': apply_cartoon,
                                'apply_anime': apply_anime,
                                'apply_cyberpunk': apply_cyberpunk,
                                'apply_vintage': apply_vintage,
                                'apply_hdr': apply_hdr,
                                'apply_magic_glow': apply_magic_glow,
                                'apply_rain': apply_rain,
                                'apply_snow': apply_snow,
                                'apply_golden_hour': apply_golden_hour,
                                'apply_moonlight': apply_moonlight
                            }
                            
                            processed_img = create_variant(img, settings)
                            if processed_img is not None:
                                processed_images.append((generate_filename(), processed_img))
                    
                    except Exception as e:
                        st.error(f"Error processing {uploaded_file.name}: {str(e)}")
                        continue

            st.session_state.generated_images = processed_images + variant_images
            
            if st.session_state.generated_images:
                st.success(f"Successfully processed {len(st.session_state.generated_images)} images with ULTRA PRO quality!")
            else:
                st.warning("No images were processed.")

if st.session_state.generated_images:
    # Create download buttons for each watermark group if multiple watermarks were used
    if len(st.session_state.watermark_groups) > 1:
        for group_name, group_data in st.session_state.watermark_groups.items():
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
                for filename, img in st.session_state.generated_images:
                    if img in group_data.get('images', []):
                        try:
                            if img.mode != 'RGB':
                                img = img.convert('RGB')
                            img_bytes = io.BytesIO()
                            img.save(img_bytes, format='JPEG', quality=100)
                            zip_file.writestr(filename, img_bytes.getvalue())
                        except Exception as e:
                            st.error(f"Error adding {filename} to zip: {str(e)}")
                            continue
            
            st.download_button(
                label=f"⬇️ Download {group_name} Photos",
                data=zip_buffer.getvalue(),
                file_name=f"{group_name.replace(' ', '_').lower()}_photos.zip",
                mime="application/zip"
            )
    
    # Main download all button
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
        for filename, img in st.session_state.generated_images:
            try:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='JPEG', quality=100)
                zip_file.writestr(filename, img_bytes.getvalue())
            except Exception as e:
                st.error(f"Error adding {filename} to zip: {str(e)}")
                continue
    
    st.download_button(
        label="⬇️ Download All Photos (ULTRA PRO QUALITY)",
        data=zip_buffer.getvalue(),
        file_name="ultra_pro_photos.zip",
        mime="application/zip"
    )
    
    st.markdown("""
        <div class='image-preview-container'>
            <h2 style='text-align: center; color: #FFFFFF; margin: 0;'>😇 ULTRA PRO RESULTS</h2>
        </div>
    """, unsafe_allow_html=True)
    
    cols_per_row = 3
    rows = (len(st.session_state.generated_images) // cols_per_row) + 1
    
    for row in range(rows):
        cols = st.columns(cols_per_row)
        for col in range(cols_per_row):
            idx = row * cols_per_row + col
            if idx < len(st.session_state.generated_images):
                filename, img = st.session_state.generated_images[idx]
                with cols[col]:
                    try:
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        img_bytes = io.BytesIO()
                        img.save(img_bytes, format='JPEG', quality=95)
                        img_bytes.seek(0)
                        st.image(img_bytes, use_container_width=True)
                        st.caption(filename)
                        
                        st.download_button(
                            label="⬇️ Download",
                            data=img_bytes.getvalue(),
                            file_name=filename,
                            mime="image/jpeg",
                            key=f"download_{idx}"
                        )
                    except Exception as e:
                        st.error(f"Error displaying {filename}: {str(e)}")
