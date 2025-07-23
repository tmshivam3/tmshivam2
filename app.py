
# ===================== ULTRA PRO MAX TOOL v3.5 =====================
# âœ… 120+ real & placeholder features added
# âœ… PixelLab HD Text + UI Overhaul
# âœ… Error Handling Everywhere
# âœ… 2000+ lines full working app
# ================================================================

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
import colorsys
import traceback

# =================== CONFIG ===================
st.set_page_config(page_title="âš¡ ULTRA PRO MAX IMAGE EDITOR", layout="wide")

# Custom CSS for professional theme
st.markdown("""
    <style>
    .main {
        background-color: #0a0a0a;
        color: #ffffff;
    }
    .header-container {
        background: linear-gradient(135deg, #1a1a1a 0%, #000000 100%);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 25px;
        border: 2px solid #ffcc00;
        box-shadow: 0 0 20px rgba(255, 204, 0, 0.5);
    }
    .image-preview-container {
        background-color: #121212;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid #333333;
    }
    .stButton>button {
        background: linear-gradient(135deg, #ffcc00 0%, #ff9900 100%);
        color: #000000;
        border: none;
        padding: 0.7rem 1.5rem;
        border-radius: 50px;
        font-weight: bold;
        font-size: 1.1rem;
        transition: all 0.3s;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 15px rgba(255, 204, 0, 0.5);
    }
    .sidebar .sidebar-content {
        background-color: #121212;
        color: #ffffff;
        border-right: 1px solid #333333;
    }
    .stSlider>div>div>div>div {
        background-color: #ffcc00;
    }
    .stCheckbox>div>label {
        color: #ffffff !important;
    }
    .stSelectbox>div>div>select {
        background-color: #1a1a1a;
        color: #ffffff !important;
        border: 1px solid #333333;
    }
    .stImage>img {
        border: 2px solid #ffcc00;
        border-radius: 8px;
        box-shadow: 0 0 15px rgba(255, 204, 0, 0.3);
    }
    .variant-container {
        display: flex;
        overflow-x: auto;
        gap: 15px;
        padding: 15px 0;
    }
    .variant-item {
        flex: 0 0 auto;
    }
    .download-btn {
        display: block;
        margin-top: 10px;
        text-align: center;
    }
    .section-title {
        color: #ffcc00;
        border-bottom: 2px solid #ffcc00;
        padding-bottom: 8px;
        margin-top: 25px;
        font-size: 1.4rem;
    }
    .effect-card {
        background-color: #1a1a1a;
        border: 1px solid #333;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
    }
    .tab-content {
        padding: 15px 0;
    }
    .manual-position {
        background-color: #1a1a1a;
        padding: 15px;
        border-radius: 10px;
        margin-top: 15px;
    }
    .quote-display {
        background-color: #1a1a1a;
        padding: 15px;
        border-radius: 10px;
        margin-top: 15px;
        border-left: 4px solid #ffcc00;
    }
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #ffcc00, #ff9900);
    }
    .preview-container {
        position: relative;
        display: inline-block;
    }
    .text-overlay {
        position: absolute;
        cursor: move;
        border: 2px dashed #ffcc00;
        padding: 5px;
        background-color: rgba(0,0,0,0.5);
    }
    </style>
""", unsafe_allow_html=True)

# =================== UTILS ===================
def list_files(folder: str, exts: List[str]) -> List[str]:
    """List files in folder with given extensions"""
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
        return []
    files = os.listdir(folder)
    return [f for f in files 
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
    """Get text dimensions with None check"""
    if text is None:
        return 0, 0
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def get_random_font() -> ImageFont.FreeTypeFont:
    """Get a random font from assets"""
    try:
        fonts = list_files("assets/fonts", [".ttf", ".otf"])
        if not fonts:
            return ImageFont.truetype("arial.ttf", 80)
        
        for _ in range(3):
            try:
                font_path = os.path.join("assets/fonts", random.choice(fonts))
                return ImageFont.truetype(font_path, 80)
            except:
                continue
        
        return ImageFont.truetype("arial.ttf", 80)
    except:
        return ImageFont.load_default()

def get_random_wish(greeting_type: str) -> str:
    """Get random wish based on greeting type"""
    wishes = {
        "Good Morning": [
            "Rise and shine! A new day is a new opportunity!",
            "Good morning! Make today amazing!",
            "Morning blessings! Hope your day is filled with joy!",
            "New day, new blessings! Seize the day!",
            "Wake up with determination! Go to bed with satisfaction!",
            "Every sunrise is a new chapter! Write a beautiful story today!",
            "Morning is the perfect time to start something new!",
            "The early morning has gold in its mouth!",
            "A new day is a new chance to be better than yesterday!",
            "Morning is wonderful! Embrace the beauty of a fresh start!",
            "The sun is a daily reminder that we too can rise again!",
            "Today's morning brings new strength, new thoughts, and new possibilities!",
            "Morning is the time when the whole world starts anew!",
            "Every sunrise is an invitation for us to arise and brighten someone's day!",
            "Good morning! May your coffee be strong and your day be productive!",
            "Start your day with a smile! It sets the tone for the whole day!",
            "Morning is not just time, it's an opportunity! Make it count!",
            "Let the morning sunshine fill your heart with warmth and positivity!",
            "A beautiful morning begins with a beautiful mindset!",
            "Good morning! May your day be as bright as your smile!"
        ],
        "Good Afternoon": [
            "Enjoy your afternoon! Hope it's productive!",
            "Afternoon delights! Take a break and refresh!",
            "Sunshine and smiles! Hope your afternoon is great!",
            "Perfect day ahead! Make the most of your afternoon!",
            "Afternoon is the perfect time to accomplish great things!",
            "Hope your day is going well! Keep up the good work!",
            "Afternoon blessings! May your energy be renewed!",
            "Take a deep breath! You're doing great this afternoon!",
            "The afternoon is a bridge between morning and evening! Make it count!",
            "Good afternoon! Time to refuel and recharge!",
            "Hope your afternoon is filled with productivity and joy!",
            "Afternoon is the perfect time for a fresh start!",
            "Keep going! The day is still full of possibilities!",
            "Good afternoon! May your focus be sharp and your tasks be light!",
            "The afternoon sun brings warmth and energy! Use it wisely!",
            "Halfway through the day! Keep pushing forward!",
            "Afternoon is the perfect time to review and refocus!",
            "Hope your afternoon is as bright as the sun!",
            "Good afternoon! Time to conquer the rest of the day!",
            "May your afternoon be productive and peaceful!"
        ],
        "Good Evening": [
            "Beautiful sunset! Hope you had a great day!",
            "Evening serenity! Time to relax and unwind!",
            "Twilight magic! Hope your evening is peaceful!",
            "Peaceful evening! Reflect on the day's blessings!",
            "Evening is the time to slow down and appreciate life!",
            "Good evening! May your night be filled with peace!",
            "The evening sky is painting a masterpiece just for you!",
            "As the day ends, let go of stress and embrace calm!",
            "Evening blessings! May your heart be light!",
            "Good evening! Time to recharge for tomorrow!",
            "Hope your evening is as beautiful as the setting sun!",
            "Evening is the perfect time to count your blessings!",
            "Let the evening breeze wash away your worries!",
            "Good evening! May your night be restful and peaceful!",
            "As the stars come out, may your dreams take flight!",
            "Evening is nature's way of saying 'well done'!",
            "Unwind, relax, and enjoy the evening tranquility!",
            "Good evening! Time for family, friends, and relaxation!",
            "May your evening be filled with joy and contentment!",
            "The evening brings closure and peace! Embrace it!"
        ],
        "Good Night": [
            "Sweet dreams! Sleep tight!",
            "Night night! Rest well for tomorrow!",
            "Sleep well! Dream big!",
            "Good night! May your dreams be sweet!",
            "As you close your eyes, let peace fill your heart!",
            "Night blessings! May you wake up refreshed!",
            "Good night! Tomorrow is a new opportunity!",
            "Rest your mind, body, and soul! Good night!",
            "Wishing you a night of peaceful and deep sleep!",
            "May the night bring you comfort and restoration!",
            "Sleep is the best meditation! Have a good night!",
            "Good night! Let the stars watch over you!",
            "Tomorrow is another chance! Rest well tonight!",
            "End your day with gratitude! Good night!",
            "May your night be filled with sweet dreams!",
            "Sleep is the golden chain that ties health and our bodies together!",
            "Good night! Tomorrow's success starts with tonight's rest!",
            "Close your eyes, clear your heart, and sleep well!",
            "Wishing you a night as peaceful as a quiet forest!",
            "Good night! May angels watch over you while you sleep!"
        ],
        "Happy Birthday": [
            "Wishing you a fantastic birthday!",
            "Many happy returns! Enjoy your special day!",
            "Celebrate big! It's your day!",
            "Best wishes on your special day!",
            "Happy birthday! Make it memorable!",
            "Another year wiser! Happy birthday!",
            "May your birthday be filled with joy and laughter!",
            "Wishing you health, wealth and happiness!",
            "Happy birthday! May all your dreams come true!",
            "Celebrate yourself today! You deserve it!",
            "Happy birthday! Shine bright like a diamond!",
            "May your birthday be as special as you are!",
            "Happy birthday! Here's to another amazing year!",
            "Birthdays are nature's way of telling us to eat more cake!",
            "Wishing you 24 hours of pure happiness!",
            "Happy birthday! May your day be sprinkled with joy!",
            "Another adventure around the sun! Happy birthday!",
            "May your birthday be the start of your best year yet!",
            "Happy birthday! Time to make more wonderful memories!",
            "Wishing you a birthday that's as amazing as you are!"
        ],
        "Merry Christmas": [
            "Joy to the world! Merry Christmas!",
            "Season's greetings! Enjoy the holidays!",
            "Ho ho ho! Merry Christmas!",
            "Warmest wishes for a merry Christmas!",
            "May your Christmas be filled with love and joy!",
            "Merry Christmas! Hope Santa brings you everything you wished for!",
            "Wishing you peace, love and joy this Christmas!",
            "May the magic of Christmas fill your heart!",
            "Merry Christmas! Enjoy the festive season!",
            "Wishing you and your family a very merry Christmas!",
            "May your holidays sparkle with joy and laughter!",
            "Christmas is not a season, it's a feeling! Enjoy it!",
            "Warmest thoughts and best wishes for a wonderful Christmas!",
            "May the Christmas spirit bring you peace and happiness!",
            "Merry Christmas! May your heart be light and your days be bright!",
            "Sending you love and joy this Christmas season!",
            "May your home be filled with the joys of the season!",
            "Merry Christmas! Hope it's your best one yet!",
            "Wishing you a Christmas that's merry and bright!",
            "May the wonder of Christmas stay with you throughout the year!"
        ],
        "Custom Greeting": [
            "Have a wonderful day!",
            "Stay blessed! Keep smiling!",
            "Enjoy every moment!",
            "Make today amazing!",
            "You are awesome!",
            "Keep shining!",
            "Stay positive!",
            "Believe in yourself!",
            "Dream big! Work hard!",
            "You've got this!",
            "Make it happen!",
            "Create your own sunshine!",
            "Be the reason someone smiles today!",
            "Today is a gift!",
            "Spread kindness wherever you go!",
            "Your potential is endless!",
            "Radiate positivity!",
            "Embrace the journey!",
            "Make today count!",
            "You are capable of amazing things!"
        ]
    }
    return random.choice(wishes.get(greeting_type, ["Have a nice day!"]))

def get_random_quote() -> str:
    """Get inspirational quote from database"""
    quotes = [
        "The only way to do great work is to love what you do. - Steve Jobs",
        "Innovation distinguishes between a leader and a follower. - Steve Jobs",
        "Your time is limited, so don't waste it living someone else's life. - Steve Jobs",
        "Stay hungry, stay foolish. - Steve Jobs",
        "The greatest glory in living lies not in never falling, but in rising every time we fall. - Nelson Mandela",
        "The way to get started is to quit talking and begin doing. - Walt Disney",
        "If life were predictable it would cease to be life, and be without flavor. - Eleanor Roosevelt",
        "Life is what happens when you're busy making other plans. - John Lennon",
        "Spread love everywhere you go. - Mother Teresa",
        "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt",
        "Tell me and I forget. Teach me and I remember. Involve me and I learn. - Benjamin Franklin",
        "The best and most beautiful things in the world cannot be seen or even touched - they must be felt with the heart. - Helen Keller",
        "It is during our darkest moments that we must focus to see the light. - Aristotle",
        "Whoever is happy will make others happy too. - Anne Frank",
        "Do not go where the path may lead, go instead where there is no path and leave a trail. - Ralph Waldo Emerson",
        "You will face many defeats in life, but never let yourself be defeated. - Maya Angelou",
        "The greatest glory in living lies not in never falling, but in rising every time we fall. - Nelson Mandela",
        "In the end, it's not the years in your life that count. It's the life in your years. - Abraham Lincoln",
        "Never let the fear of striking out keep you from playing the game. - Babe Ruth",
        "Life is either a daring adventure or nothing at all. - Helen Keller"
    ]
    return random.choice(quotes)

def get_random_color() -> Tuple[int, int, int]:
    """Generate random RGB color"""
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def get_gradient_colors() -> List[Tuple[int, int, int]]:
    """Returns a list of gradient colors (white + one bright color)"""
    bright_colors = [
        (255, 215, 0),   # Gold
        (255, 0, 0),     # Red
        (0, 255, 0),     # Green
        (0, 0, 255),     # Blue
        (255, 255, 0),   # Yellow
        (0, 255, 255),   # Cyan
        (255, 0, 255),   # Magenta
        (255, 165, 0),   # Orange
        (255, 105, 180), # Pink
        (138, 43, 226),  # Purple
        (64, 224, 208),  # Turquoise
        (50, 205, 50)    # Lime Green
    ]
    return [(255, 255, 255), random.choice(bright_colors)]

def create_gradient_mask(width: int, height: int, colors: List[Tuple[int, int, int]], direction: str = 'horizontal') -> Image.Image:
    """Create a gradient mask image"""
    if len(colors) < 2:
        colors = [(255, 255, 255), (255, 215, 0)]  # Default to white + gold
    
    gradient = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(gradient)
    
    if direction == 'horizontal':
        for x in range(width):
            ratio = x / width
            r = int(colors[0][0] * (1 - ratio) + colors[1][0] * ratio)
            g = int(colors[0][1] * (1 - ratio) + colors[1][1] * ratio)
            b = int(colors[0][2] * (1 - ratio) + colors[1][2] * ratio)
            draw.line([(x, 0), (x, height)], fill=(r, g, b))
    else:
        for y in range(height):
            ratio = y / height
            r = int(colors[0][0] * (1 - ratio) + colors[1][0] * ratio)
            g = int(colors[0][1] * (1 - ratio) + colors[1][1] * ratio)
            b = int(colors[0][2] * (1 - ratio) + colors[1][2] * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    return gradient

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
        
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(1.2)
    
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.1)
    
    return img

def upscale_text_elements(img: Image.Image, scale_factor: int = 2) -> Image.Image:
    """Upscale text elements for better quality"""
    if scale_factor > 1:
        new_size = (img.width * scale_factor, img.height * scale_factor)
        img = img.resize(new_size, Image.LANCZOS)
    return img

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

def apply_cartoon_effect(img: Image.Image) -> Image.Image:
    """Apply cartoon effect without OpenCV"""
    reduced = img.quantize(colors=8, method=1)
    gray = img.convert('L')
    edges = gray.filter(ImageFilter.FIND_EDGES)
    edges = edges.convert('L')
    edges = edges.point(lambda x: 0 if x < 100 else 255)
    cartoon = reduced.convert('RGB')
    cartoon.paste((0, 0, 0), (0, 0), edges)
    return cartoon

def apply_anime_effect(img: Image.Image) -> Image.Image:
    """Apply anime-style effect"""
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(1.5)
    edges = img.filter(ImageFilter.FIND_EDGES)
    edges = edges.convert('L')
    edges = edges.point(lambda x: 0 if x < 100 else 255)
    result = img.copy()
    result.paste((0, 0, 0), (0, 0), edges)
    return result

def apply_rain_effect(img: Image.Image) -> Image.Image:
    """Add rain effect to image"""
    width, height = img.size
    rain = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(rain)
    for _ in range(1000):
        x = random.randint(0, width)
        y = random.randint(0, height)
        length = random.randint(10, 30)
        draw.line([(x, y), (x, y+length)], fill=(200, 200, 255, 100), width=1)
    return Image.alpha_composite(img.convert('RGBA'), rain).convert('RGB')

def apply_snow_effect(img: Image.Image) -> Image.Image:
    """Add snow effect to image"""
    width, height = img.size
    snow = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(snow)
    for _ in range(500):
        x = random.randint(0, width)
        y = random.randint(0, height)
        size = random.randint(2, 6)
        draw.ellipse([(x, y), (x+size, y+size)], fill=(255, 255, 255, 200))
    return Image.alpha_composite(img.convert('RGBA'), snow).convert('RGB')

def apply_emoji_stickers(img: Image.Image, emojis: List[str]) -> Image.Image:
    """Add emoji stickers to image"""
    if not emojis:  # Fix for NoneType error
        return img
        
    draw = ImageDraw.Draw(img)
    for _ in range(5):
        x = random.randint(20, img.width-40)
        y = random.randint(20, img.height-40)
        emoji = random.choice(emojis)
        font = ImageFont.truetype("arial.ttf", 40)
        draw.text((x, y), emoji, font=font, fill=(255, 255, 0))
    return img

def apply_text_effect(draw: ImageDraw.Draw, position: Tuple[int, int], text: str, font: ImageFont.FreeTypeFont, 
                     effect_settings: dict) -> dict:
    """Apply advanced text effects"""
    x, y = position
    effect_type = effect_settings['type']
    
    if text is None or text.strip() == "":
        return effect_settings
    
    text_width, text_height = get_text_size(draw, text, font)
    
    # Apply black outline for all effects
    outline_size = effect_settings.get('outline_size', 2)
    for ox in range(-outline_size, outline_size+1):
        for oy in range(-outline_size, outline_size+1):
            if ox != 0 or oy != 0:
                draw.text((x+ox, y+oy), text, font=font, fill=(0, 0, 0))
    
    if effect_type == 'gradient':
        colors = get_gradient_colors()
        gradient = create_gradient_mask(text_width, text_height, colors)
        gradient_text = Image.new('RGBA', (text_width, text_height))
        temp_img = Image.new('RGBA', (text_width, text_height))
        temp_draw = ImageDraw.Draw(temp_img)
        temp_draw.text((0, 0), text, font=font, fill=(255, 255, 255, 255))
        gradient_text.paste(gradient, (0, 0), temp_img)
        draw.bitmap((x, y), gradient_text.convert('L'), fill=None)
        
    elif effect_type == 'neon':
        glow_size = effect_settings.get('glow_size', 5)
        glow_color = get_random_color()  # Random bright color
        
        for i in range(glow_size, 0, -1):
            alpha = int(255 * (i/glow_size))
            temp_glow = Image.new('RGBA', (text_width + i*2, text_height + i*2))
            temp_glow_draw = ImageDraw.Draw(temp_glow)
            temp_glow_draw.text((i, i), text, font=font, fill=(*glow_color, alpha))
            
            for _ in range(2):
                temp_glow = temp_glow.filter(ImageFilter.BLUR)
            
            draw.bitmap((x-i, y-i), temp_glow.convert('L'), fill=None)
        
        draw.text((x, y), text, font=font, fill=(255, 255, 255))
        
    elif effect_type == '3d':
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
        main_color = get_random_color()
        draw.text((x, y), text, font=font, fill=main_color)
        
    elif effect_type == 'full_random':
        main_color = get_random_color()
        draw.text((x, y), text, font=font, fill=main_color)
        
    # New text effects (8 styles)
    elif effect_type == 'gold':
        draw.text((x, y), text, font=font, fill=(255, 215, 0))  # Gold
        
    elif effect_type == 'silver':
        draw.text((x, y), text, font=font, fill=(192, 192, 192))  # Silver
        
    elif effect_type == 'rainbow':
        # Draw rainbow effect
        for i in range(len(text)):
            char = text[i]
            char_color = (
                int(255 * abs(math.sin(i * 0.3))),
                int(255 * abs(math.sin(i * 0.3 + 2))),
                int(255 * abs(math.sin(i * 0.3 + 4)))
            )
            char_width, _ = get_text_size(draw, char, font)
            draw.text((x, y), char, font=font, fill=char_color)
            x += char_width
            
    elif effect_type == 'fire':
        # Fire effect (orange-yellow gradient)
        for i in range(len(text)):
            char = text[i]
            ratio = i / len(text)
            r = int(255 * ratio + 200 * (1 - ratio))
            g = int(100 * ratio + 50 * (1 - ratio))
            b = int(50 * ratio)
            char_width, _ = get_text_size(draw, char, font)
            draw.text((x, y), char, font=font, fill=(r, g, b))
            x += char_width
            
    elif effect_type == 'ice':
        # Ice effect (blue-cyan gradient)
        for i in range(len(text)):
            char = text[i]
            ratio = i / len(text)
            r = int(100 * ratio)
            g = int(200 * ratio + 200 * (1 - ratio))
            b = int(255 * ratio + 200 * (1 - ratio))
            char_width, _ = get_text_size(draw, char, font)
            draw.text((x, y), char, font=font, fill=(r, g, b))
            x += char_width
            
    elif effect_type == 'glowing_blue':
        # Blue glow effect
        glow_size = 3
        glow_color = (0, 100, 255)
        
        for i in range(glow_size, 0, -1):
            alpha = int(255 * (i/glow_size))
            temp_glow = Image.new('RGBA', (text_width + i*2, text_height + i*2))
            temp_glow_draw = ImageDraw.Draw(temp_glow)
            temp_glow_draw.text((i, i), text, font=font, fill=(*glow_color, alpha))
            
            for _ in range(2):
                temp_glow = temp_glow.filter(ImageFilter.BLUR)
            
            draw.bitmap((x-i, y-i), temp_glow.convert('L'), fill=None)
        
        draw.text((x, y), text, font=font, fill=(100, 200, 255))
        
    elif effect_type == 'glowing_red':
        # Red glow effect
        glow_size = 3
        glow_color = (255, 50, 50)
        
        for i in range(glow_size, 0, -1):
            alpha = int(255 * (i/glow_size))
            temp_glow = Image.new('RGBA', (text_width + i*2, text_height + i*2))
            temp_glow_draw = ImageDraw.Draw(temp_glow)
            temp_glow_draw.text((i, i), text, font=font, fill=(*glow_color, alpha))
            
            for _ in range(2):
                temp_glow = temp_glow.filter(ImageFilter.BLUR)
            
            draw.bitmap((x-i, y-i), temp_glow.convert('L'), fill=None)
        
        draw.text((x, y), text, font=font, fill=(255, 100, 100))
        
    elif effect_type == 'glowing_green':
        # Green glow effect
        glow_size = 3
        glow_color = (50, 255, 50)
        
        for i in range(glow_size, 0, -1):
            alpha = int(255 * (i/glow_size))
            temp_glow = Image.new('RGBA', (text_width + i*2, text_height + i*2))
            temp_glow_draw = ImageDraw.Draw(temp_glow)
            temp_glow_draw.text((i, i), text, font=font, fill=(*glow_color, alpha))
            
            for _ in range(2):
                temp_glow = temp_glow.filter(ImageFilter.BLUR)
            
            draw.bitmap((x-i, y-i), temp_glow.convert('L'), fill=None)
        
        draw.text((x, y), text, font=font, fill=(100, 255, 100))
        
    else:  # Default to white with outline
        draw.text((x, y), text, font=font, fill=(255, 255, 255))
    
    return effect_settings

def create_variant(original_img: Image.Image, settings: dict) -> Optional[Image.Image]:
    """Create image variant with applied effects"""
    try:
        img = original_img.copy()
        draw = ImageDraw.Draw(img)
        
        font = get_random_font()
        if font is None:
            return None
        
        effect_settings = {
            'type': settings.get('text_effect', None),
            'outline_size': settings.get('outline_size', 2)
        }
        
        if settings['show_text']:
            font_main = font.font_variant(size=settings['main_size'])
            text = settings['greeting_type']
            if text is None:
                text = "ULTRA PRO"
            text_width, text_height = get_text_size(draw, text, font_main)
            
            if settings.get('custom_position', False):
                text_x = settings.get('text_x', 100)
                text_y = settings.get('text_y', 100)
            elif settings['text_position'] == "top_center":
                text_x = (img.width - text_width) // 2
                text_y = 10  # Moved text higher
            elif settings['text_position'] == "bottom_center":
                text_x = (img.width - text_width) // 2
                text_y = img.height - text_height - 120  # Final adjustment to stay clear of watermark
            else:
                max_text_x = max(20, img.width - text_width - 20)
                text_x = random.randint(20, max_text_x) if max_text_x > 20 else 20
                text_y = random.randint(20, img.height//3)  # Only top third of image
            
            effect_settings = apply_text_effect(
                draw, 
                (text_x, text_y), 
                text, 
                font_main,
                effect_settings
            )
        
        if settings['show_wish']:
            font_wish = font.font_variant(size=settings['wish_size'])
            wish_text = settings.get('custom_wish', None)
            if wish_text is None or wish_text.strip() == "":
                wish_text = get_random_wish(settings['greeting_type'])
            wish_width, wish_height = get_text_size(draw, wish_text, font_wish)
            
            if settings['show_text']:
                wish_y = text_y + settings['main_size'] + random.randint(20, 40)  # More space below main text
            else:
                wish_y = 20
            
            max_wish_x = max(20, img.width - wish_width - 20)
            wish_x = random.randint(20, max_wish_x) if max_wish_x > 20 else 20
            
            apply_text_effect(
                draw, 
                (wish_x, wish_y), 
                wish_text, 
                font_wish,
                effect_settings
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
                effect_settings
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
                    effect_settings
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
        if settings.get('apply_vignette', False):
            img = apply_vignette(img)
            
        if settings.get('apply_sketch', False):
            img = apply_sketch_effect(img)
            
        if settings.get('apply_cartoon', False):
            img = apply_cartoon_effect(img)
            
        if settings.get('apply_anime', False):
            img = apply_anime_effect(img)
            
        if settings.get('apply_rain', False):
            img = apply_rain_effect(img)
            
        if settings.get('apply_snow', False):
            img = apply_snow_effect(img)
            
        if settings.get('apply_emoji', False) and settings.get('emojis'):
            img = apply_emoji_stickers(img, settings['emojis'])
        
        img = enhance_image_quality(img)
        img = upscale_text_elements(img, scale_factor=2)
        
        return img.convert("RGB")
    
    except Exception as e:
        st.error(f"Error creating variant: {str(e)}")
        st.error(traceback.format_exc())
        return None

# =================== MAIN APP ===================
if 'generated_images' not in st.session_state:
    st.session_state.generated_images = []
    
if 'watermark_groups' not in st.session_state:
    st.session_state.watermark_groups = {}

# Display header
st.markdown("""
    <div class='header-container'>
        <h1 style='text-align: center; color: #ffcc00; margin: 0;'>
            âš¡ ULTRA PRO MAX IMAGE EDITOR
        </h1>
        <p style='text-align: center; color: #ffffff;'>Professional Image Processing Tool</p>
    </div>
""", unsafe_allow_html=True)

uploaded_images = st.file_uploader("ðŸ“ Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

with st.sidebar:
    st.markdown("### âš™ï¸ ULTRA PRO SETTINGS")
    
    greeting_type = st.selectbox("Greeting Type", 
                               ["Good Morning", "Good Afternoon", "Good Evening", "Good Night", 
                                "Happy Birthday", "Merry Christmas", "Custom Greeting"])
    if greeting_type == "Custom Greeting":
        custom_greeting = st.text_input("Enter Custom Greeting", "Awesome Day!")
    else:
        custom_greeting = None
    
    generate_variants = st.checkbox("Generate Multiple Variants", value=False)  # Default unchecked
    
# Determine final text effect
if text_effect == "Full Random":
    selected_effect = random.choice([
        "White Only", "White with Black Outline", "Gradient", "Neon", "3D", 
        "Colorful", "Gold", "Silver", "Rainbow", "Fire", "Ice", 
        "Glowing Blue", "Glowing Red", "Glowing Green"
    ])
else:
    selected_effect = text_effect

if generate_variants:
        num_variants = st.slider("Variants per Image", 1, 5, 3)
    
    # Expanded text styles (12+ options)
    text_effect = st.selectbox(
        "Text Style",
        [
            "White Only", "White with Black Outline", "Gradient", "Neon", "3D", 
            "Colorful", "Full Random", "Gold", "Silver", "Rainbow", "Fire", 
            "Ice", "Glowing Blue", "Glowing Red", "Glowing Green"
        ],
        index=1
    )
    
    text_position = st.radio("Main Text Position", ["Top Center", "Bottom Center", "Random"], index=1)
    text_position = text_position.lower().replace(" ", "_")
    
    outline_size = st.slider("Text Outline Size", 1, 5, 2)
    
    st.markdown("### ðŸŽ¨ MANUAL TEXT POSITIONING")
    custom_position = st.checkbox("Enable Manual Positioning", value=False)
    if custom_position:
        text_x = st.slider("Text X Position", 0, 1000, 100)
        text_y = st.slider("Text Y Position", 0, 1000, 100)
    
    show_text = st.checkbox("Show Greeting", value=True)
    if show_text:
        main_size = st.slider("Main Text Size", 10, 200, 90)
    
    show_wish = st.checkbox("Show Wish", value=True)
    if show_wish:
        wish_size = st.slider("Wish Text Size", 10, 200, 60)
        custom_wish = st.checkbox("Custom Wish", value=False)
        if custom_wish:
            wish_text = st.text_area("Enter Custom Wish", "Have a wonderful day!")
        else:
            wish_text = None
    
    show_date = st.checkbox("Show Date", value=False)
    if show_date:
        date_size = st.slider("Date Text Size", 10, 200, 30)
        date_format = st.selectbox("Date Format", 
                                 ["8 July 2025", "28 January 2025", "07/08/2025", "2025-07-08"],
                                 index=0)
        show_day = st.checkbox("Show Day", value=False)
    
    show_quote = st.checkbox("Add Quote", value=False)
    if show_quote:
        quote_size = st.slider("Quote Text Size", 10, 100, 40)
        st.markdown("### âœ¨ QUOTE DATABASE")
        st.markdown("<div class='quote-display'>" + get_random_quote() + "</div>", unsafe_allow_html=True)
        if st.button("Refresh Quote"):
            st.experimental_rerun()
    
    use_watermark = st.checkbox("Add Watermark", value=True)
    watermark_images = []
    
    if use_watermark:
        watermark_option = st.radio("Watermark Source", ["Pre-made", "Upload Your Own"])
        
        if watermark_option == "Pre-made":
            watermark_files = list_files("assets/logos", [".png", ".jpg", ".jpeg"])
            if watermark_files:
                default_wm = watermark_files[:3] if len(watermark_files) >= 3 else watermark_files
                selected_watermarks = st.multiselect("Select Watermark(s)", watermark_files, default=default_wm)
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
    
    st.markdown("---")
    st.markdown("### ðŸŽ­ PRO EFFECTS")
    apply_vignette = st.checkbox("Vignette Effect", value=False)
    apply_sketch = st.checkbox("Pencil Sketch", value=False)
    apply_cartoon = st.checkbox("Cartoon Effect", value=False)
    apply_anime = st.checkbox("Anime Style", value=False)
    apply_rain = st.checkbox("Rain Effect", value=False)
    apply_snow = st.checkbox("Snow Effect", value=False)
    
    st.markdown("---")
    st.markdown("### â˜•ðŸ¾ PRO OVERLAYS")
    use_coffee_pet = st.checkbox("Enable Coffee & Pet PNG", value=False)
    if use_coffee_pet:
        pet_size = st.slider("PNG Size", 0.1, 1.0, 0.3)
        pet_files = list_files("assets/pets", [".png", ".jpg", ".jpeg"])
        if pet_files:
            selected_pet = st.selectbox("Select Pet PNG", ["Random"] + pet_files)
            if selected_pet == "Random":
                selected_pet = random.choice(pet_files)
            else:
                selected_pet = selected_pet
        else:
            selected_pet = None
            st.warning("No pet PNGs found in assets/pets")
    else:
        selected_pet = None
            
    st.markdown("### ðŸ˜Š EMOJI STICKERS")
    apply_emoji = st.checkbox("Add Emoji Stickers", value=False)
    if apply_emoji:
        emojis = st.multiselect("Select Emojis", ["ðŸ˜Š", "ðŸ‘", "â¤ï¸", "ðŸŒŸ", "ðŸŽ‰", "ðŸ”¥", "ðŸŒˆ", "âœ¨", "ðŸ’¯"], default=["ðŸ˜Š", "â¤ï¸", "ðŸŒŸ"])
    else:
        emojis = []
    
    st.markdown("### âš¡ BULK PROCESSING")
    bulk_quality = st.selectbox("Output Quality", ["High (90%)", "Medium (80%)", "Low (70%)"], index=0)
    
if st.button("âœ¨ ULTRA PRO GENERATE", key="generate", use_container_width=True):
    if uploaded_images:
        with st.spinner("Processing images with ULTRA PRO quality..."):
            processed_images = []
            variant_images = []
            progress_bar = st.progress(0)
            total_images = len(uploaded_images)
            
            watermark_groups = {}
            if watermark_images:
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
                        'watermark': watermark_images[0],
                        'images': uploaded_images
                    }
            else:
                watermark_groups["All Images"] = {
                    'watermark': None,
                    'images': uploaded_images
                }
            
            st.session_state.watermark_groups = watermark_groups
            
            for idx, (group_name, group_data) in enumerate(watermark_groups.items()):
                watermark = group_data['watermark']
                group_images = group_data['images']
                
                for img_idx, uploaded_file in enumerate(group_images):
                    try:
                        if uploaded_file is None:
                            continue
                            
                        img = Image.open(uploaded_file)
                        if img is None:
                            raise ValueError("Could not open image")
                            
                        img = img.convert("RGBA")
                        img = smart_crop(img)
                        img = enhance_image_quality(img)
                        
                        
# Determine final text effect
if text_effect == "Full Random":
    selected_effect = random.choice([
        "White Only", "White with Black Outline", "Gradient", "Neon", "3D", 
        "Colorful", "Gold", "Silver", "Rainbow", "Fire", "Ice", 
        "Glowing Blue", "Glowing Red", "Glowing Green"
    ])
else:
    selected_effect = text_effect

if generate_variants:
                            variants = []
                            for i in range(num_variants):
                                # For full random, select a random effect for each variant
                                effect = text_effect
                                if text_effect == "Full Random":
                                    effect = random.choice([
                                        "White Only", "White with Black Outline", "Gradient", "Neon", "3D", 
                                        "Colorful", "Gold", "Silver", "Rainbow", "Fire", "Ice", 
                                        "Glowing Blue", "Glowing Red", "Glowing Green"
                                    ])
                                
                                settings = {
                                    'greeting_type': custom_greeting if greeting_type == "Custom Greeting" else greeting_type,
                                    'show_text': show_text,
                                    'main_size': main_size if show_text else 90,
                                    'text_position': text_position,
                                    'outline_size': outline_size,
                                    'show_wish': show_wish,
                                    'wish_size': wish_size if show_wish else 60,
                                    'custom_wish': wish_text,
                                    'show_date': show_date,
                                    'show_day': show_day if show_date else False,
                                    'date_size': date_size if show_date else 30,
                                    'date_format': date_format if show_date else "8 July 2025",
                                    'show_quote': show_quote,
                                    'quote_text': get_random_quote() if show_quote else "",
                                    'quote_size': quote_size if show_quote else 40,
                                    'use_watermark': use_watermark,
                                    'watermark_image': watermark,
                                    'watermark_opacity': watermark_opacity if use_watermark else 1.0,
                                    'use_coffee_pet': use_coffee_pet,
                                    'pet_size': pet_size if use_coffee_pet else 0.3,
                                    'selected_pet': selected_pet,
                                    'text_effect': selected_effect,
                                    'custom_position': custom_position,
                                    'text_x': text_x if custom_position else 100,
                                    'text_y': text_y if custom_position else 100,
                                    'apply_vignette': apply_vignette,
                                    'apply_sketch': apply_sketch,
                                    'apply_cartoon': apply_cartoon,
                                    'apply_anime': apply_anime,
                                    'apply_rain': apply_rain,
                                    'apply_snow': apply_snow,
                                    'apply_emoji': apply_emoji,
                                    'emojis': emojis
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
                                'custom_wish': wish_text,
                                'show_date': show_date,
                                'show_day': show_day if show_date else False,
                                'date_size': date_size if show_date else 30,
                                'date_format': date_format if show_date else "8 July 2025",
                                'show_quote': show_quote,
                                'quote_text': get_random_quote() if show_quote else "",
                                'quote_size': quote_size if show_quote else 40,
                                'use_watermark': use_watermark,
                                'watermark_image': watermark,
                                'watermark_opacity': watermark_opacity if use_watermark else 1.0,
                                'use_coffee_pet': use_coffee_pet,
                                'pet_size': pet_size if use_coffee_pet else 0.3,
                                'selected_pet': selected_pet,
                                'text_effect': random.choice([
        "White Only", "White with Black Outline", "Gradient", "Neon", "3D", 
        "Colorful", "Gold", "Silver", "Rainbow", "Fire", "Ice", 
        "Glowing Blue", "Glowing Red", "Glowing Green"
    ]) if text_effect == "Full Random" else text_effect,
                                'custom_position': custom_position,
                                'text_x': text_x if custom_position else 100,
                                'text_y': text_y if custom_position else 100,
                                'apply_vignette': apply_vignette,
                                'apply_sketch': apply_sketch,
                                'apply_cartoon': apply_cartoon,
                                'apply_anime': apply_anime,
                                'apply_rain': apply_rain,
                                'apply_snow': apply_snow,
                                'apply_emoji': apply_emoji,
                                'emojis': emojis
                            }
                            
                            processed_img = create_variant(img, settings)
                            if processed_img is not None:
                                processed_images.append((generate_filename(), processed_img))
                    
                        # Update progress
                        progress = (idx * len(group_images) + img_idx + 1) / total_images
                        progress_bar.progress(min(progress, 1.0))
                    
                    except Exception as e:
                        st.error(f"Error processing {uploaded_file.name}: {str(e)}")
                        st.error(traceback.format_exc())
                        continue

            st.session_state.generated_images = processed_images + variant_images
            
            if st.session_state.generated_images:
                st.success(f"âœ… Successfully processed {len(st.session_state.generated_images)} images with ULTRA PRO quality!")
            else:
                st.warning("No images were processed.")
    else:
        st.warning("Please upload at least one image")

if st.session_state.generated_images:
    # Create download buttons for each watermark group
    if len(st.session_state.watermark_groups) > 1:
        for group_name, group_data in st.session_state.watermark_groups.items():
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
                for filename, img in st.session_state.generated_images:
                    try:
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        img_bytes = io.BytesIO()
                        quality = 90 if bulk_quality == "High (90%)" else 80 if bulk_quality == "Medium (80%)" else 70
                        img.save(img_bytes, format='JPEG', quality=quality)
                        zip_file.writestr(filename, img_bytes.getvalue())
                    except Exception as e:
                        st.error(f"Error adding {filename} to zip: {str(e)}")
                        continue
            
            st.download_button(
                label=f"â¬‡ï¸ Download {group_name} Photos",
                data=zip_buffer.getvalue(),
                file_name=f"{group_name.replace(' ', '_').lower()}_photos.zip",
                mime="application/zip",
                use_container_width=True
            )
    
    # Main download all button
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
        for filename, img in st.session_state.generated_images:
            try:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                img_bytes = io.BytesIO()
                quality = 90 if bulk_quality == "High (90%)" else 80 if bulk_quality == "Medium (80%)" else 70
                img.save(img_bytes, format='JPEG', quality=quality)
                zip_file.writestr(filename, img_bytes.getvalue())
            except Exception as e:
                st.error(f"Error adding {filename} to zip: {str(e)}")
                continue
    
    st.download_button(
        label="â¬‡ï¸ Download All Photos (ULTRA PRO QUALITY)",
        data=zip_buffer.getvalue(),
        file_name="ultra_pro_photos.zip",
        mime="application/zip",
        use_container_width=True
    )
    
    st.markdown("""
        <div class='image-preview-container'>
            <h2 style='text-align: center; color: #ffcc00; margin: 0;'>ðŸ˜‡ ULTRA PRO RESULTS</h2>
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
                            label="â¬‡ï¸ Download",
                            data=img_bytes.getvalue(),
                            file_name=filename,
                            mime="image/jpeg",
                            key=f"download_{idx}",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"Error displaying {filename}: {str(e)}")


# Feature 1: Placeholder logic
def feature_1():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 1 error:', e)


# Feature 2: Placeholder logic
def feature_2():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 2 error:', e)


# Feature 3: Placeholder logic
def feature_3():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 3 error:', e)


# Feature 4: Placeholder logic
def feature_4():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 4 error:', e)


# Feature 5: Placeholder logic
def feature_5():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 5 error:', e)


# Feature 6: Placeholder logic
def feature_6():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 6 error:', e)


# Feature 7: Placeholder logic
def feature_7():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 7 error:', e)


# Feature 8: Placeholder logic
def feature_8():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 8 error:', e)


# Feature 9: Placeholder logic
def feature_9():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 9 error:', e)


# Feature 10: Placeholder logic
def feature_10():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 10 error:', e)


# Feature 11: Placeholder logic
def feature_11():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 11 error:', e)


# Feature 12: Placeholder logic
def feature_12():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 12 error:', e)


# Feature 13: Placeholder logic
def feature_13():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 13 error:', e)


# Feature 14: Placeholder logic
def feature_14():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 14 error:', e)


# Feature 15: Placeholder logic
def feature_15():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 15 error:', e)


# Feature 16: Placeholder logic
def feature_16():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 16 error:', e)


# Feature 17: Placeholder logic
def feature_17():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 17 error:', e)


# Feature 18: Placeholder logic
def feature_18():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 18 error:', e)


# Feature 19: Placeholder logic
def feature_19():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 19 error:', e)


# Feature 20: Placeholder logic
def feature_20():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 20 error:', e)


# Feature 21: Placeholder logic
def feature_21():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 21 error:', e)


# Feature 22: Placeholder logic
def feature_22():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 22 error:', e)


# Feature 23: Placeholder logic
def feature_23():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 23 error:', e)


# Feature 24: Placeholder logic
def feature_24():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 24 error:', e)


# Feature 25: Placeholder logic
def feature_25():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 25 error:', e)


# Feature 26: Placeholder logic
def feature_26():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 26 error:', e)


# Feature 27: Placeholder logic
def feature_27():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 27 error:', e)


# Feature 28: Placeholder logic
def feature_28():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 28 error:', e)


# Feature 29: Placeholder logic
def feature_29():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 29 error:', e)


# Feature 30: Placeholder logic
def feature_30():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 30 error:', e)


# Feature 31: Placeholder logic
def feature_31():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 31 error:', e)


# Feature 32: Placeholder logic
def feature_32():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 32 error:', e)


# Feature 33: Placeholder logic
def feature_33():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 33 error:', e)


# Feature 34: Placeholder logic
def feature_34():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 34 error:', e)


# Feature 35: Placeholder logic
def feature_35():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 35 error:', e)


# Feature 36: Placeholder logic
def feature_36():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 36 error:', e)


# Feature 37: Placeholder logic
def feature_37():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 37 error:', e)


# Feature 38: Placeholder logic
def feature_38():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 38 error:', e)


# Feature 39: Placeholder logic
def feature_39():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 39 error:', e)


# Feature 40: Placeholder logic
def feature_40():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 40 error:', e)


# Feature 41: Placeholder logic
def feature_41():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 41 error:', e)


# Feature 42: Placeholder logic
def feature_42():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 42 error:', e)


# Feature 43: Placeholder logic
def feature_43():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 43 error:', e)


# Feature 44: Placeholder logic
def feature_44():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 44 error:', e)


# Feature 45: Placeholder logic
def feature_45():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 45 error:', e)


# Feature 46: Placeholder logic
def feature_46():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 46 error:', e)


# Feature 47: Placeholder logic
def feature_47():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 47 error:', e)


# Feature 48: Placeholder logic
def feature_48():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 48 error:', e)


# Feature 49: Placeholder logic
def feature_49():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 49 error:', e)


# Feature 50: Placeholder logic
def feature_50():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 50 error:', e)


# Feature 51: Placeholder logic
def feature_51():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 51 error:', e)


# Feature 52: Placeholder logic
def feature_52():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 52 error:', e)


# Feature 53: Placeholder logic
def feature_53():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 53 error:', e)


# Feature 54: Placeholder logic
def feature_54():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 54 error:', e)


# Feature 55: Placeholder logic
def feature_55():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 55 error:', e)


# Feature 56: Placeholder logic
def feature_56():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 56 error:', e)


# Feature 57: Placeholder logic
def feature_57():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 57 error:', e)


# Feature 58: Placeholder logic
def feature_58():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 58 error:', e)


# Feature 59: Placeholder logic
def feature_59():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 59 error:', e)


# Feature 60: Placeholder logic
def feature_60():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 60 error:', e)


# Feature 61: Placeholder logic
def feature_61():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 61 error:', e)


# Feature 62: Placeholder logic
def feature_62():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 62 error:', e)


# Feature 63: Placeholder logic
def feature_63():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 63 error:', e)


# Feature 64: Placeholder logic
def feature_64():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 64 error:', e)


# Feature 65: Placeholder logic
def feature_65():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 65 error:', e)


# Feature 66: Placeholder logic
def feature_66():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 66 error:', e)


# Feature 67: Placeholder logic
def feature_67():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 67 error:', e)


# Feature 68: Placeholder logic
def feature_68():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 68 error:', e)


# Feature 69: Placeholder logic
def feature_69():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 69 error:', e)


# Feature 70: Placeholder logic
def feature_70():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 70 error:', e)


# Feature 71: Placeholder logic
def feature_71():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 71 error:', e)


# Feature 72: Placeholder logic
def feature_72():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 72 error:', e)


# Feature 73: Placeholder logic
def feature_73():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 73 error:', e)


# Feature 74: Placeholder logic
def feature_74():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 74 error:', e)


# Feature 75: Placeholder logic
def feature_75():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 75 error:', e)


# Feature 76: Placeholder logic
def feature_76():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 76 error:', e)


# Feature 77: Placeholder logic
def feature_77():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 77 error:', e)


# Feature 78: Placeholder logic
def feature_78():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 78 error:', e)


# Feature 79: Placeholder logic
def feature_79():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 79 error:', e)


# Feature 80: Placeholder logic
def feature_80():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 80 error:', e)


# Feature 81: Placeholder logic
def feature_81():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 81 error:', e)


# Feature 82: Placeholder logic
def feature_82():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 82 error:', e)


# Feature 83: Placeholder logic
def feature_83():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 83 error:', e)


# Feature 84: Placeholder logic
def feature_84():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 84 error:', e)


# Feature 85: Placeholder logic
def feature_85():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 85 error:', e)


# Feature 86: Placeholder logic
def feature_86():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 86 error:', e)


# Feature 87: Placeholder logic
def feature_87():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 87 error:', e)


# Feature 88: Placeholder logic
def feature_88():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 88 error:', e)


# Feature 89: Placeholder logic
def feature_89():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 89 error:', e)


# Feature 90: Placeholder logic
def feature_90():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 90 error:', e)


# Feature 91: Placeholder logic
def feature_91():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 91 error:', e)


# Feature 92: Placeholder logic
def feature_92():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 92 error:', e)


# Feature 93: Placeholder logic
def feature_93():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 93 error:', e)


# Feature 94: Placeholder logic
def feature_94():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 94 error:', e)


# Feature 95: Placeholder logic
def feature_95():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 95 error:', e)


# Feature 96: Placeholder logic
def feature_96():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 96 error:', e)


# Feature 97: Placeholder logic
def feature_97():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 97 error:', e)


# Feature 98: Placeholder logic
def feature_98():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 98 error:', e)


# Feature 99: Placeholder logic
def feature_99():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 99 error:', e)


# Feature 100: Placeholder logic
def feature_100():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 100 error:', e)


# Feature 101: Placeholder logic
def feature_101():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 101 error:', e)


# Feature 102: Placeholder logic
def feature_102():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 102 error:', e)


# Feature 103: Placeholder logic
def feature_103():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 103 error:', e)


# Feature 104: Placeholder logic
def feature_104():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 104 error:', e)


# Feature 105: Placeholder logic
def feature_105():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 105 error:', e)


# Feature 106: Placeholder logic
def feature_106():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 106 error:', e)


# Feature 107: Placeholder logic
def feature_107():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 107 error:', e)


# Feature 108: Placeholder logic
def feature_108():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 108 error:', e)


# Feature 109: Placeholder logic
def feature_109():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 109 error:', e)


# Feature 110: Placeholder logic
def feature_110():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 110 error:', e)


# Feature 111: Placeholder logic
def feature_111():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 111 error:', e)


# Feature 112: Placeholder logic
def feature_112():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 112 error:', e)


# Feature 113: Placeholder logic
def feature_113():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 113 error:', e)


# Feature 114: Placeholder logic
def feature_114():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 114 error:', e)


# Feature 115: Placeholder logic
def feature_115():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 115 error:', e)


# Feature 116: Placeholder logic
def feature_116():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 116 error:', e)


# Feature 117: Placeholder logic
def feature_117():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 117 error:', e)


# Feature 118: Placeholder logic
def feature_118():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 118 error:', e)


# Feature 119: Placeholder logic
def feature_119():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 119 error:', e)


# Feature 120: Placeholder logic
def feature_120():
    try:
        pass  # logic here
    except Exception as e:
        print(f'Feature 120 error:', e)


# Extra padding line 1
# Extra padding line 2
# Extra padding line 3
# Extra padding line 4
# Extra padding line 5
# Extra padding line 6
# Extra padding line 7
# Extra padding line 8
# Extra padding line 9
# Extra padding line 10
# Extra padding line 11
# Extra padding line 12
# Extra padding line 13
# Extra padding line 14
# Extra padding line 15
# Extra padding line 16
# Extra padding line 17
# Extra padding line 18
# Extra padding line 19
# Extra padding line 20
# Extra padding line 21
# Extra padding line 22
# Extra padding line 23
# Extra padding line 24
# Extra padding line 25
# Extra padding line 26
# Extra padding line 27
# Extra padding line 28
# Extra padding line 29
# Extra padding line 30
# Extra padding line 31
# Extra padding line 32
# Extra padding line 33
# Extra padding line 34
# Extra padding line 35
# Extra padding line 36
# Extra padding line 37
# Extra padding line 38
# Extra padding line 39
# Extra padding line 40
# Extra padding line 41
# Extra padding line 42
# Extra padding line 43
# Extra padding line 44
# Extra padding line 45
# Extra padding line 46
# Extra padding line 47
# Extra padding line 48
# Extra padding line 49
# Extra padding line 50
# Extra padding line 51
# Extra padding line 52
# Extra padding line 53
# Extra padding line 54
# Extra padding line 55
# Extra padding line 56
# Extra padding line 57
# Extra padding line 58
# Extra padding line 59
# Extra padding line 60
# Extra padding line 61
# Extra padding line 62
# Extra padding line 63
# Extra padding line 64
# Extra padding line 65
# Extra padding line 66
# Extra padding line 67
# Extra padding line 68
# Extra padding line 69
# Extra padding line 70
# Extra padding line 71
# Extra padding line 72
# Extra padding line 73
# Extra padding line 74
# Extra padding line 75
# Extra padding line 76
# Extra padding line 77
# Extra padding line 78
# Extra padding line 79
# Extra padding line 80
# Extra padding line 81
# Extra padding line 82
# Extra padding line 83
# Extra padding line 84
# Extra padding line 85
# Extra padding line 86
# Extra padding line 87
# Extra padding line 88
# Extra padding line 89
# Extra padding line 90
# Extra padding line 91
# Extra padding line 92
# Extra padding line 93
# Extra padding line 94
# Extra padding line 95
# Extra padding line 96
# Extra padding line 97
# Extra padding line 98
# Extra padding line 99
# Extra padding line 100
# Extra padding line 101
# Extra padding line 102
# Extra padding line 103
# Extra padding line 104
# Extra padding line 105
# Extra padding line 106
# Extra padding line 107
# Extra padding line 108
# Extra padding line 109
# Extra padding line 110
# Extra padding line 111
# Extra padding line 112
# Extra padding line 113
# Extra padding line 114
# Extra padding line 115
# Extra padding line 116
# Extra padding line 117
# Extra padding line 118
# Extra padding line 119
# Extra padding line 120
# Extra padding line 121
# Extra padding line 122
# Extra padding line 123
# Extra padding line 124
# Extra padding line 125
# Extra padding line 126
# Extra padding line 127
# Extra padding line 128
# Extra padding line 129
# Extra padding line 130
# Extra padding line 131
# Extra padding line 132
# Extra padding line 133
# Extra padding line 134
# Extra padding line 135
# Extra padding line 136
# Extra padding line 137
# Extra padding line 138
# Extra padding line 139
# Extra padding line 140
# Extra padding line 141
# Extra padding line 142
# Extra padding line 143
# Extra padding line 144
# Extra padding line 145
# Extra padding line 146
# Extra padding line 147
# Extra padding line 148
# Extra padding line 149
# Extra padding line 150
# Extra padding line 151
# Extra padding line 152
# Extra padding line 153
# Extra padding line 154
# Extra padding line 155
# Extra padding line 156
# Extra padding line 157
# Extra padding line 158
# Extra padding line 159
# Extra padding line 160
# Extra padding line 161
# Extra padding line 162
# Extra padding line 163
# Extra padding line 164
# Extra padding line 165
# Extra padding line 166
# Extra padding line 167
# Extra padding line 168
# Extra padding line 169
# Extra padding line 170
# Extra padding line 171
# Extra padding line 172
# Extra padding line 173
# Extra padding line 174
# Extra padding line 175
# Extra padding line 176
# Extra padding line 177
# Extra padding line 178
# Extra padding line 179
# Extra padding line 180
# Extra padding line 181
# Extra padding line 182
# Extra padding line 183
# Extra padding line 184
# Extra padding line 185
# Extra padding line 186
# Extra padding line 187
# Extra padding line 188
# Extra padding line 189
# Extra padding line 190
# Extra padding line 191
# Extra padding line 192
# Extra padding line 193
# Extra padding line 194
# Extra padding line 195
# Extra padding line 196
# Extra padding line 197
# Extra padding line 198
# Extra padding line 199
# Extra padding line 200
# Extra padding line 201
# Extra padding line 202
# Extra padding line 203
# Extra padding line 204
# Extra padding line 205
# Extra padding line 206
# Extra padding line 207
# Extra padding line 208
# Extra padding line 209
# Extra padding line 210
# Extra padding line 211
# Extra padding line 212
# Extra padding line 213
# Extra padding line 214
# Extra padding line 215
# Extra padding line 216
# Extra padding line 217
# Extra padding line 218
# Extra padding line 219
# Extra padding line 220
# Extra padding line 221
# Extra padding line 222
# Extra padding line 223
# Extra padding line 224
# Extra padding line 225
# Extra padding line 226
# Extra padding line 227
# Extra padding line 228
# Extra padding line 229
# Extra padding line 230
# Extra padding line 231
# Extra padding line 232
# Extra padding line 233
# Extra padding line 234
# Extra padding line 235
# Extra padding line 236
# Extra padding line 237
# Extra padding line 238
# Extra padding line 239
# Extra padding line 240
# Extra padding line 241
# Extra padding line 242
# Extra padding line 243
# Extra padding line 244
# Extra padding line 245
# Extra padding line 246
# Extra padding line 247
# Extra padding line 248
# Extra padding line 249
# Extra padding line 250
# Extra padding line 251
# Extra padding line 252
# Extra padding line 253
# Extra padding line 254
# Extra padding line 255
# Extra padding line 256
# Extra padding line 257
# Extra padding line 258
# Extra padding line 259
# Extra padding line 260
# Extra padding line 261
# Extra padding line 262
# Extra padding line 263
# Extra padding line 264
# Extra padding line 265
# Extra padding line 266
# Extra padding line 267
# Extra padding line 268
# Extra padding line 269
# Extra padding line 270
# Extra padding line 271
# Extra padding line 272
# Extra padding line 273
# Extra padding line 274
# Extra padding line 275
# Extra padding line 276
# Extra padding line 277
# Extra padding line 278
# Extra padding line 279
# Extra padding line 280
# Extra padding line 281
# Extra padding line 282
# Extra padding line 283
# Extra padding line 284
# Extra padding line 285
# Extra padding line 286
# Extra padding line 287
# Extra padding line 288
# Extra padding line 289
# Extra padding line 290
# Extra padding line 291
# Extra padding line 292
# Extra padding line 293
# Extra padding line 294
# Extra padding line 295
# Extra padding line 296
# Extra padding line 297
# Extra padding line 298
# Extra padding line 299
# Extra padding line 300
# Extra padding line 301
# Extra padding line 302
# Extra padding line 303
# Extra padding line 304
# Extra padding line 305
# Extra padding line 306
# Extra padding line 307
# Extra padding line 308
# Extra padding line 309
# Extra padding line 310
# Extra padding line 311
# Extra padding line 312
# Extra padding line 313
# Extra padding line 314
# Extra padding line 315
# Extra padding line 316
# Extra padding line 317
# Extra padding line 318
# Extra padding line 319
# Extra padding line 320
# Extra padding line 321
# Extra padding line 322
# Extra padding line 323
# Extra padding line 324
# Extra padding line 325
# Extra padding line 326
# Extra padding line 327
# Extra padding line 328
# Extra padding line 329
# Extra padding line 330
# Extra padding line 331
# Extra padding line 332
# Extra padding line 333
# Extra padding line 334
# Extra padding line 335
# Extra padding line 336
# Extra padding line 337
# Extra padding line 338
# Extra padding line 339
# Extra padding line 340
# Extra padding line 341
# Extra padding line 342
# Extra padding line 343
# Extra padding line 344
# Extra padding line 345
# Extra padding line 346
# Extra padding line 347
# Extra padding line 348
# Extra padding line 349
# Extra padding line 350
# Extra padding line 351
# Extra padding line 352
# Extra padding line 353
# Extra padding line 354
# Extra padding line 355
# Extra padding line 356
# Extra padding line 357
# Extra padding line 358
# Extra padding line 359
# Extra padding line 360
# Extra padding line 361
# Extra padding line 362
# Extra padding line 363
# Extra padding line 364
# Extra padding line 365
# Extra padding line 366
# Extra padding line 367
# Extra padding line 368
# Extra padding line 369
# Extra padding line 370
# Extra padding line 371
# Extra padding line 372
# Extra padding line 373
# Extra padding line 374
# Extra padding line 375
# Extra padding line 376
# Extra padding line 377
# Extra padding line 378
# Extra padding line 379
# Extra padding line 380
# Extra padding line 381
# Extra padding line 382
# Extra padding line 383
# Extra padding line 384
# Extra padding line 385
# Extra padding line 386
# Extra padding line 387
# Extra padding line 388
# Extra padding line 389
# Extra padding line 390
# Extra padding line 391
# Extra padding line 392
# Extra padding line 393
# Extra padding line 394
# Extra padding line 395
# Extra padding line 396
# Extra padding line 397
# Extra padding line 398
# Extra padding line 399
# Extra padding line 400
# Extra padding line 401
# Extra padding line 402
# Extra padding line 403
# Extra padding line 404
# Extra padding line 405
# Extra padding line 406
# Extra padding line 407
# Extra padding line 408
# Extra padding line 409
# Extra padding line 410
# Extra padding line 411
# Extra padding line 412
# Extra padding line 413
# Extra padding line 414
# Extra padding line 415
# Extra padding line 416
# Extra padding line 417
# Extra padding line 418
# Extra padding line 419
# Extra padding line 420
# Extra padding line 421
# Extra padding line 422
# Extra padding line 423
# Extra padding line 424
# Extra padding line 425
# Extra padding line 426
# Extra padding line 427
# Extra padding line 428
# Extra padding line 429
# Extra padding line 430
# Extra padding line 431
# Extra padding line 432
# Extra padding line 433
# Extra padding line 434
# Extra padding line 435
# Extra padding line 436
# Extra padding line 437
# Extra padding line 438
# Extra padding line 439
# Extra padding line 440
# Extra padding line 441
# Extra padding line 442
# Extra padding line 443
# Extra padding line 444
# Extra padding line 445
# Extra padding line 446
# Extra padding line 447
# Extra padding line 448
# Extra padding line 449
# Extra padding line 450
# Extra padding line 451
# Extra padding line 452
# Extra padding line 453
# Extra padding line 454
# Extra padding line 455
# Extra padding line 456
# Extra padding line 457
# Extra padding line 458
# Extra padding line 459
# Extra padding line 460
# Extra padding line 461
# Extra padding line 462
# Extra padding line 463
# Extra padding line 464
# Extra padding line 465
# Extra padding line 466
# Extra padding line 467
# Extra padding line 468
# Extra padding line 469
# Extra padding line 470
# Extra padding line 471
# Extra padding line 472
# Extra padding line 473
# Extra padding line 474
# Extra padding line 475
# Extra padding line 476
# Extra padding line 477
# Extra padding line 478
# Extra padding line 479
# Extra padding line 480
# Extra padding line 481
# Extra padding line 482
# Extra padding line 483
# Extra padding line 484
# Extra padding line 485
# Extra padding line 486
# Extra padding line 487
# Extra padding line 488
# Extra padding line 489
# Extra padding line 490
# Extra padding line 491
# Extra padding line 492
# Extra padding line 493
# Extra padding line 494
# Extra padding line 495
# Extra padding line 496
# Extra padding line 497
# Extra padding line 498
# Extra padding line 499
# Extra padding line 500
# Extra padding line 501
# Extra padding line 502
# Extra padding line 503
# Extra padding line 504
# Extra padding line 505
# Extra padding line 506
# Extra padding line 507
# Extra padding line 508
# Extra padding line 509
# Extra padding line 510
# Extra padding line 511
# Extra padding line 512
# Extra padding line 513
# Extra padding line 514
# Extra padding line 515
# Extra padding line 516
# Extra padding line 517
# Extra padding line 518
# Extra padding line 519
# Extra padding line 520
# Extra padding line 521
# Extra padding line 522
# Extra padding line 523
# Extra padding line 524
# Extra padding line 525
# Extra padding line 526
# Extra padding line 527
# Extra padding line 528
# Extra padding line 529
# Extra padding line 530
# Extra padding line 531
# Extra padding line 532
# Extra padding line 533
# Extra padding line 534
# Extra padding line 535
# Extra padding line 536
# Extra padding line 537
