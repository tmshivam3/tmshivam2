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
st.set_page_config(page_title="✨ ULTRA PRO MAX IMAGE EDITOR", layout="wide", page_icon="🎨")

# Custom CSS for premium look
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #1a1a1a 0%, #000000 100%);
        color: #ffffff;
    }
    .header-container {
        background: linear-gradient(135deg, #1a1a1a 0%, #000000 100%);
        padding: 20px;
        border-radius: 15px;
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
        background: linear-gradient(135deg, #1a1a1a 0%, #000000 100%);
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
    .feature-card {
        border: 1px solid #ffcc00;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        background: linear-gradient(135deg, #1a1a1a 0%, #000000 100%);
        color: #ffffff;
        box-shadow: 0 0 15px rgba(255, 204, 0, 0.2);
    }
    .pro-badge {
        background-color: #ffcc00;
        color: #000;
        padding: 3px 10px;
        border-radius: 15px;
        font-size: 0.9em;
        font-weight: bold;
        margin-left: 8px;
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
    """Returns a list of gradient colors (white + any truly random color)"""
    white = (255, 255, 255)
    random_color = (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255)
    )
    return [white, random_color]


def create_gradient_mask(width: int, height: int, colors: List[Tuple[int, int, int]], direction: str = 'horizontal') -> Image.Image:
    """Create a gradient mask image"""
    if len(colors) < 2:
        colors = [(255, 255, 255), (255, 0, 0)]  # Default to white + red if not enough colors
    
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

def get_watermark_position(img: Image.Image, watermark: Image.Image, text_areas: list) -> Tuple[int, int]:
    """Get watermark position avoiding text areas"""
    for _ in range(20):  # Try multiple times to find a non-overlapping position
        x = random.choice([20, img.width - watermark.width - 20])
        y = random.choice([20, img.height - watermark.height - 20])
        
        # Check if watermark overlaps with any text area
        overlap = False
        watermark_rect = (x, y, x + watermark.width, y + watermark.height)
        
        for text_rect in text_areas:
            if (watermark_rect[0] < text_rect[2] and watermark_rect[2] > text_rect[0] and
                watermark_rect[1] < text_rect[3] and watermark_rect[3] > text_rect[1]):
                overlap = True
                break
        
        if not overlap:
            return (x, y)
    
    # If no non-overlapping position found, return bottom position
    return (20, img.height - watermark.height - 20)

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
    """Apply advanced text effects with 20+ styles"""
    x, y = position
    effect_type = effect_settings['type']
    
    if text is None or text.strip() == "":
        return effect_settings
    
    text_width, text_height = get_text_size(draw, text, font)
    
    # Store text rectangle for watermark avoidance
    text_rect = (x, y, x + text_width, y + text_height)
    effect_settings.setdefault('text_areas', []).append(text_rect)
    
    if effect_type == 'gradient':
        colors = get_gradient_colors()
        gradient = create_gradient_mask(text_width, text_height, colors)
        gradient_text = Image.new('RGBA', (text_width, text_height))
        temp_img = Image.new('RGBA', (text_width, text_height))
        temp_draw = ImageDraw.Draw(temp_img)
        temp_draw.text((0, 0), text, font=font, fill=(255, 255, 255, 255))
        gradient_text.paste(gradient, (0, 0), temp_img)
        
        outline_size = effect_settings.get('outline_size', 2)
        for ox in range(-outline_size, outline_size+1):
            for oy in range(-outline_size, outline_size+1):
                if ox != 0 or oy != 0:
                    draw.text((x+ox, y+oy), text, font=font, fill=(0, 0, 0))
        
        draw.bitmap((x, y), gradient_text.convert('L'), fill=None)
        
    elif effect_type == 'neon':
        glow_size = effect_settings.get('glow_size', 5)
        glow_color = effect_settings.get('glow_color', (0, 255, 255))
        
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
        
    elif effect_type == 'gold':
        colors = [(255, 215, 0), (218, 165, 32)]  # Gold gradient
        gradient = create_gradient_mask(text_width, text_height, colors)
        gradient_text = Image.new('RGBA', (text_width, text_height))
        temp_img = Image.new('RGBA', (text_width, text_height))
        temp_draw = ImageDraw.Draw(temp_img)
        temp_draw.text((0, 0), text, font=font, fill=(255, 255, 255, 255))
        gradient_text.paste(gradient, (0, 0), temp_img)
        
        outline_size = 3
        for ox in range(-outline_size, outline_size+1):
            for oy in range(-outline_size, outline_size+1):
                if ox != 0 or oy != 0:
                    draw.text((x+ox, y+oy), text, font=font, fill=(0, 0, 0))
        
        draw.bitmap((x, y), gradient_text.convert('L'), fill=None)
        
    elif effect_type == 'silver':
        colors = [(192, 192, 192), (105, 105, 105)]  # Silver gradient
        gradient = create_gradient_mask(text_width, text_height, colors)
        gradient_text = Image.new('RGBA', (text_width, text_height))
        temp_img = Image.new('RGBA', (text_width, text_height))
        temp_draw = ImageDraw.Draw(temp_img)
        temp_draw.text((0, 0), text, font=font, fill=(255, 255, 255, 255))
        gradient_text.paste(gradient, (0, 0), temp_img)
        
        outline_size = 3
        for ox in range(-outline_size, outline_size+1):
            for oy in range(-outline_size, outline_size+1):
                if ox != 0 or oy != 0:
                    draw.text((x+ox, y+oy), text, font=font, fill=(0, 0, 0))
        
        draw.bitmap((x, y), gradient_text.convert('L'), fill=None)
        
    elif effect_type == 'rainbow':
        colors = [
            (255, 0, 0),    # Red
            (255, 165, 0),  # Orange
            (255, 255, 0),  # Yellow
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (75, 0, 130),   # Indigo
            (238, 130, 238) # Violet
        ]
        gradient = Image.new('RGB', (text_width, text_height))
        draw_gradient = ImageDraw.Draw(gradient)
        
        for i in range(text_width):
            ratio = i / text_width
            color_index = ratio * (len(colors) - 1)
            idx1 = int(color_index)
            idx2 = min(idx1 + 1, len(colors) - 1)
            frac = color_index - idx1
            
            r = int(colors[idx1][0] * (1 - frac) + colors[idx2][0] * frac)
            g = int(colors[idx1][1] * (1 - frac) + colors[idx2][1] * frac)
            b = int(colors[idx1][2] * (1 - frac) + colors[idx2][2] * frac)
            
            draw_gradient.line([(i, 0), (i, text_height)], fill=(r, g, b))
        
        rainbow_text = Image.new('RGBA', (text_width, text_height))
        temp_img = Image.new('RGBA', (text_width, text_height))
        temp_draw = ImageDraw.Draw(temp_img)
        temp_draw.text((0, 0), text, font=font, fill=(255, 255, 255, 255))
        rainbow_text.paste(gradient, (0, 0), temp_img)
        
        outline_size = 2
        for ox in range(-outline_size, outline_size+1):
            for oy in range(-outline_size, outline_size+1):
                if ox != 0 or oy != 0:
                    draw.text((x+ox, y+oy), text, font=font, fill=(0, 0, 0))
        
        draw.bitmap((x, y), rainbow_text.convert('L'), fill=None)
        
    elif effect_type == 'fire':
        colors = [(255, 0, 0), (255, 165, 0), (255, 255, 0)]  # Fire colors
        gradient = Image.new('RGB', (text_width, text_height))
        draw_gradient = ImageDraw.Draw(gradient)
        
        for i in range(text_height):
            ratio = i / text_height
            color_index = ratio * (len(colors) - 1)
            idx1 = int(color_index)
            idx2 = min(idx1 + 1, len(colors) - 1)
            frac = color_index - idx1
            
            r = int(colors[idx1][0] * (1 - frac) + colors[idx2][0] * frac)
            g = int(colors[idx1][1] * (1 - frac) + colors[idx2][1] * frac)
            b = int(colors[idx1][2] * (1 - frac) + colors[idx2][2] * frac)
            
            draw_gradient.line([(0, i), (text_width, i)], fill=(r, g, b))
        
        fire_text = Image.new('RGBA', (text_width, text_height))
        temp_img = Image.new('RGBA', (text_width, text_height))
        temp_draw = ImageDraw.Draw(temp_img)
        temp_draw.text((0, 0), text, font=font, fill=(255, 255, 255, 255))
        fire_text.paste(gradient, (0, 0), temp_img)
        
        draw.bitmap((x, y), fire_text.convert('L'), fill=None)
        
    elif effect_type == 'ice':
        colors = [(173, 216, 230), (240, 248, 255)]  # Ice colors
        gradient = create_gradient_mask(text_width, text_height, colors, 'vertical')
        ice_text = Image.new('RGBA', (text_width, text_height))
        temp_img = Image.new('RGBA', (text_width, text_height))
        temp_draw = ImageDraw.Draw(temp_img)
        temp_draw.text((0, 0), text, font=font, fill=(255, 255, 255, 255))
        ice_text.paste(gradient, (0, 0), temp_img)
        
        outline_size = 2
        for ox in range(-outline_size, outline_size+1):
            for oy in range(-outline_size, outline_size+1):
                if ox != 0 or oy != 0:
                    draw.text((x+ox, y+oy), text, font=font, fill=(0, 0, 128))
        
        draw.bitmap((x, y), ice_text.convert('L'), fill=None)
        
    elif effect_type == 'metal':
        # Metallic effect with bevel
        # Draw shadow
        shadow_color = (50, 50, 50)
        draw.text((x+2, y+2), text, font=font, fill=shadow_color)
        
        # Draw highlight
        highlight_color = (200, 200, 200)
        draw.text((x-1, y-1), text, font=font, fill=highlight_color)
        
        # Draw main metallic text
        metallic_color = (150, 150, 150)
        draw.text((x, y), text, font=font, fill=metallic_color)
        
    elif effect_type == 'glow_purple':
        glow_size = 8
        glow_color = (138, 43, 226)  # Purple
        
        for i in range(glow_size, 0, -1):
            alpha = int(255 * (i/glow_size))
            temp_glow = Image.new('RGBA', (text_width + i*2, text_height + i*2))
            temp_glow_draw = ImageDraw.Draw(temp_glow)
            temp_glow_draw.text((i, i), text, font=font, fill=(*glow_color, alpha))
            
            for _ in range(3):
                temp_glow = temp_glow.filter(ImageFilter.BLUR)
            
            draw.bitmap((x-i, y-i), temp_glow.convert('L'), fill=None)
        
        draw.text((x, y), text, font=font, fill=(255, 255, 255))
        
    elif effect_type == 'comic':
        # Thick black outline with bright fill
        outline_size = 4
        for ox in range(-outline_size, outline_size+1):
            for oy in range(-outline_size, outline_size+1):
                if ox != 0 or oy != 0:
                    draw.text((x+ox, y+oy), text, font=font, fill=(0, 0, 0))
        
        draw.text((x, y), text, font=font, fill=(255, 255, 0))  # Yellow fill
        
    elif effect_type == 'vintage':
        # Vintage brown with shadow
        shadow_offset = 2
        draw.text((x+shadow_offset, y+shadow_offset), text, font=font, fill=(101, 67, 33))
        draw.text((x, y), text, font=font, fill=(139, 69, 19))
        
    elif effect_type == 'sci_fi':
        # Sci-fi blue with glow
        glow_size = 6
        glow_color = (0, 191, 255)  # Deep sky blue
        
        for i in range(glow_size, 0, -1):
            alpha = int(200 * (i/glow_size))
            temp_glow = Image.new('RGBA', (text_width + i*2, text_height + i*2))
            temp_glow_draw = ImageDraw.Draw(temp_glow)
            temp_glow_draw.text((i, i), text, font=font, fill=(*glow_color, alpha))
            
            for _ in range(2):
                temp_glow = temp_glow.filter(ImageFilter.BLUR)
            
            draw.bitmap((x-i, y-i), temp_glow.convert('L'), fill=None)
        
        draw.text((x, y), text, font=font, fill=(0, 255, 255))
        
    elif effect_type == 'elegant':
        # Thin white text with subtle shadow
        shadow_offset = 1
        draw.text((x+shadow_offset, y+shadow_offset), text, font=font, fill=(40, 40, 40))
        draw.text((x, y), text, font=font, fill=(255, 255, 255))
        
    elif effect_type == 'grunge':
        # Grunge style with irregular outline
        # Create irregular outline
        offsets = [(-2, -2), (-2, 2), (2, -2), (2, 2), (0, -2), (0, 2), (-2, 0), (2, 0)]
        for ox, oy in offsets:
            draw.text((x+ox, y+oy), text, font=font, fill=(50, 50, 50))
        
        # Main text with texture effect
        for i in range(3):
            offset_x = random.randint(-1, 1)
            offset_y = random.randint(-1, 1)
            draw.text((x+offset_x, y+offset_y), text, font=font, fill=(150, 75, 0))
        
        draw.text((x, y), text, font=font, fill=(200, 100, 0))
        
    elif effect_type == 'sticker':
        # Sticker effect with white border
        border_size = 5
        # Draw background
        draw.rectangle([x-border_size, y-border_size, x+text_width+border_size, y+text_height+border_size], 
                      fill=(255, 255, 255))
        # Draw text
        draw.text((x, y), text, font=font, fill=(255, 0, 0))
        
    elif effect_type == 'chrome':
        # Chrome effect
        colors = [(200, 200, 200), (100, 100, 100), (240, 240, 240)]
        gradient = Image.new('RGB', (text_width, text_height))
        draw_gradient = ImageDraw.Draw(gradient)
        
        for i in range(text_height):
            ratio = i / text_height
            color_index = ratio * (len(colors) - 1)
            idx1 = int(color_index)
            idx2 = min(idx1 + 1, len(colors) - 1)
            frac = color_index - idx1
            
            r = int(colors[idx1][0] * (1 - frac) + colors[idx2][0] * frac)
            g = int(colors[idx1][1] * (1 - frac) + colors[idx2][1] * frac)
            b = int(colors[idx1][2] * (1 - frac) + colors[idx2][2] * frac)
            
            draw_gradient.line([(0, i), (text_width, i)], fill=(r, g, b))
        
        chrome_text = Image.new('RGBA', (text_width, text_height))
        temp_img = Image.new('RGBA', (text_width, text_height))
        temp_draw = ImageDraw.Draw(temp_img)
        temp_draw.text((0, 0), text, font=font, fill=(255, 255, 255, 255))
        chrome_text.paste(gradient, (0, 0), temp_img)
        
        draw.bitmap((x, y), chrome_text.convert('L'), fill=None)
        
    elif effect_type == 'hologram':
        # Hologram effect with rainbow colors
        colors = [
            (255, 0, 0),    # Red
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (255, 0, 255)   # Magenta
        ]
        angle = random.randint(0, 360)
        
        for i, char in enumerate(text):
            char_width, char_height = get_text_size(draw, char, font)
            offset_x = sum(get_text_size(draw, text[:i], font)[0] for _ in range(1))[0]
            
            # Calculate color based on position and angle
            ratio = (math.sin(math.radians(angle + i*20)) + 1) / 2
            color_index = int(ratio * (len(colors) - 1))
            color = colors[color_index]
            
            draw.text((x+offset_x, y), char, font=font, fill=color)
        
    elif effect_type == 'luxury_gold':
        # Luxury gold with black outline
        outline_size = 3
        for ox in range(-outline_size, outline_size+1):
            for oy in range(-outline_size, outline_size+1):
                if ox != 0 or oy != 0:
                    draw.text((x+ox, y+oy), text, font=font, fill=(0, 0, 0))
        
        # Draw gradient gold
        colors = [(212, 175, 55), (245, 223, 77)]  # Gold colors
        gradient = create_gradient_mask(text_width, text_height, colors)
        gold_text = Image.new('RGBA', (text_width, text_height))
        temp_img = Image.new('RGBA', (text_width, text_height))
        temp_draw = ImageDraw.Draw(temp_img)
        temp_draw.text((0, 0), text, font=font, fill=(255, 255, 255, 255))
        gold_text.paste(gradient, (0, 0), temp_img)
        
        draw.bitmap((x, y), gold_text.convert('L'), fill=None)
        
    elif effect_type == 'neon_pink':
        glow_size = 6
        glow_color = (255, 20, 147)  # Deep pink
        
        for i in range(glow_size, 0, -1):
            alpha = int(255 * (i/glow_size))
            temp_glow = Image.new('RGBA', (text_width + i*2, text_height + i*2))
            temp_glow_draw = ImageDraw.Draw(temp_glow)
            temp_glow_draw.text((i, i), text, font=font, fill=(*glow_color, alpha))
            
            for _ in range(2):
                temp_glow = temp_glow.filter(ImageFilter.BLUR)
            
            draw.bitmap((x-i, y-i), temp_glow.convert('L'), fill=None)
        
        draw.text((x, y), text, font=font, fill=(255, 105, 180))  # Hot pink
        
    elif effect_type == 'cyberpunk':
        # Cyberpunk style with blue and pink
        # Draw blue shadow
        draw.text((x+3, y+3), text, font=font, fill=(0, 255, 255))
        # Draw pink text
        draw.text((x, y), text, font=font, fill=(255, 0, 255))
        
    elif effect_type == 'bubble':
        # Bubble text with white outline and gradient fill
        outline_size = 3
        for ox in range(-outline_size, outline_size+1):
            for oy in range(-outline_size, outline_size+1):
                if ox != 0 or oy != 0:
                    draw.text((x+ox, y+oy), text, font=font, fill=(255, 255, 255))
        
# Gradient fill (white + random color)
colors = get_gradient_colors()  # Use random white + color
gradient = create_gradient_mask(text_width, text_height, colors)
bubble_text = Image.new('RGBA', (text_width, text_height))
temp_img = Image.new('RGBA', (text_width, text_height))
temp_draw = ImageDraw.Draw(temp_img)
temp_draw.text((0, 0), text, font=font, fill=(255, 255, 255, 255))
bubble_text.paste(gradient, (0, 0), temp_img)

# Paste full colored gradient text (not just mask)
img_with_text = Image.new("RGBA", draw.im.size)
img_with_text.paste(bubble_text, (x, y), temp_img)
draw.im.paste(img_with_text, (0, 0), img_with_text)
     
    elif effect_type == 'space':
        # Space effect with stars
        # Draw text
        draw.text((x, y), text, font=font, fill=(255, 255, 255))
        
        # Add stars
        for _ in range(50):
            star_x = random.randint(x, x + text_width)
            star_y = random.randint(y, y + text_height)
            size = random.randint(1, 3)
            draw.ellipse([(star_x, star_y), (star_x+size, star_y+size)], fill=(255, 255, 255))
        
    else:  # Default effect (white with black outline)
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
            'outline_size': settings.get('outline_size', 2),
            'text_areas': []
        }
        
        # Adjust main text position to be higher
        text_position_adjustment = 0.1  # 10% higher
        
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
                text_y = max(20, int(img.height * text_position_adjustment))
            elif settings['text_position'] == "bottom_center":
                text_x = (img.width - text_width) // 2
                text_y = img.height - text_height - max(20, int(img.height * 0.2))
            else:
                max_text_x = max(20, img.width - text_width - 20)
                text_x = random.randint(20, max_text_x) if max_text_x > 20 else 20
                text_y = max(20, int(img.height * text_position_adjustment))
            
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
                wish_y = text_y + settings['main_size'] + random.randint(10, 30)
            else:
                wish_y = max(20, int(img.height * text_position_adjustment))
            
            max_wish_x = max(20, img.width - wish_width - 20)
            wish_x = random.randint(20, max_wish_x) if max_wish_x > 20 else 20
            
            effect_settings = apply_text_effect(
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
            date_y = img.height - date_height - 30  # Leave space for watermark
            
            if settings['show_day'] and "(" in date_text:
                day_part = date_text[date_text.index("("):]
                day_width, _ = get_text_size(draw, day_part, font_date)
                if date_x + day_width > img.width - 20:
                    date_x = img.width - day_width - 25
            
            effect_settings = apply_text_effect(
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
                effect_settings = apply_text_effect(
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
            pos = get_watermark_position(img, watermark, effect_settings['text_areas'])
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

# Display features
st.markdown("""
    <div class='header-container'>
        <h1 style='text-align: center; color: #ffcc00; margin: 0;'>
            ✨ ULTRA PRO MAX IMAGE EDITOR
        </h1>
        <p style='text-align: center; color: #ffffff;'>Professional Image Processing with 50+ Premium Features</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <div class='feature-card'>
        <h3>🎨 ULTRA PRO FEATURES</h3>
        <div style="column-count: 3; column-gap: 20px;">
            <p>✅ 20+ Text Effects</p>
            <p>✅ Smart Watermark Placement</p>
            <p>✅ Gradient Text Styles</p>
            <p>✅ Custom Text Positioning</p>
            <p>✅ Neon & 3D Effects</p>
            <p>✅ Gold/Silver Text</p>
            <p>✅ Rainbow Text</p>
            <p>✅ Fire & Ice Effects</p>
            <p>✅ Vintage & Grunge Styles</p>
            <p>✅ Comic & Sticker Text</p>
            <p>✅ Chrome & Metal Effects</p>
            <p>✅ Hologram Text</p>
            <p>✅ Luxury Gold Text</p>
            <p>✅ Cyberpunk Style</p>
            <p>✅ Bubble Text</p>
            <p>✅ Space Text Effect</p>
            <p>✅ Anime Style Effect</p>
            <p>✅ Cartoon Effect</p>
            <p>✅ Pencil Sketch</p>
            <p>✅ Rain & Snow Effects</p>
            <p>✅ Emoji Stickers</p>
            <p>✅ Multiple Watermarks</p>
            <p>✅ Custom Greeting Messages</p>
            <p>✅ Date & Time Stamps</p>
            <p>✅ Pet & Coffee PNG Overlays</p>
            <p>✅ Vignette Effect</p>
            <p>✅ Batch Processing</p>
            <p>✅ Multiple Variants</p>
            <p>✅ High-Quality Output</p>
            <p>✅ Custom Wishes</p>
            <p>✅ Quote Database</p>
        </div>
    </div>
""", unsafe_allow_html=True)

uploaded_images = st.file_uploader("📁 Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

with st.sidebar:
    st.markdown("### ⚙️ ULTRA PRO SETTINGS")
    
    greeting_type = st.selectbox("Greeting Type", 
                               ["Good Morning", "Good Afternoon", "Good Evening", "Good Night", 
                                "Happy Birthday", "Merry Christmas", "Custom Greeting"])
    if greeting_type == "Custom Greeting":
        custom_greeting = st.text_input("Enter Custom Greeting", "Awesome Day!")
    else:
        custom_greeting = None
    
    generate_variants = st.checkbox("Generate Multiple Variants", value=False)
    if generate_variants:
        num_variants = st.slider("Variants per Image", 1, 5, 3)
    
    text_effect = st.selectbox(
        "Text Style",
        [
            "White Only", "White with Black Outline", "Gradient", "Neon", "3D", 
            "Gold", "Silver", "Rainbow", "Fire", "Ice", "Metal", "Glow Purple", 
            "Comic", "Vintage", "Sci-fi", "Elegant", "Grunge", "Sticker", 
            "Chrome", "Hologram", "Luxury Gold", "Neon Pink", "Cyberpunk", 
            "Bubble", "Space"
        ],
        index=2
    )
    
    text_position = st.radio("Main Text Position", ["Top Center", "Bottom Center", "Random"], index=1)
    text_position = text_position.lower().replace(" ", "_")
    
    outline_size = st.slider("Text Outline Size", 1, 5, 2) if text_effect in [
        "White with Black Outline", "Gradient", "Neon", "3D", "Gold", "Silver", 
        "Comic", "Vintage", "Ice", "Bubble", "Luxury Gold"] else 2
    
    st.markdown("### 📐 MANUAL TEXT POSITIONING")
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
        st.markdown("### ✨ QUOTE DATABASE")
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
    st.markdown("### 🎨 PRO EFFECTS")
    apply_vignette = st.checkbox("Vignette Effect", value=False)
    apply_sketch = st.checkbox("Pencil Sketch", value=False)
    apply_cartoon = st.checkbox("Cartoon Effect", value=False)
    apply_anime = st.checkbox("Anime Style", value=False)
    apply_rain = st.checkbox("Rain Effect", value=False)
    apply_snow = st.checkbox("Snow Effect", value=False)
    
    st.markdown("---")
    st.markdown("### ☕ PRO OVERLAYS")
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
            
    st.markdown("### 😊 EMOJI STICKERS")
    apply_emoji = st.checkbox("Add Emoji Stickers", value=False)
    if apply_emoji:
        emojis = st.multiselect("Select Emojis", ["😊", "👍", "❤️", "🌟", "🎉", "🔥", "🌄", "✨", "💯"], default=["😊", "❤️", "🌟"])
    else:
        emojis = []
    
    st.markdown("### 🚀 BULK PROCESSING")
    bulk_quality = st.selectbox("Output Quality", ["High (90%)", "Medium (80%)", "Low (70%)"], index=0)
    
if st.button("✨ ULTRA PRO GENERATE", key="generate", use_container_width=True):
    if uploaded_images:
        with st.spinner("Processing images with ULTRA PRO quality..."):
            processed_images = []
            variant_images = []
            progress_bar = st.progress(0)
            total_images = len(uploaded_images)
            
            effect_mapping = {
                "White Only": "white_only",
                "White with Black Outline": "white_black_outline",
                "Gradient": "gradient",
                "Neon": "neon",
                "3D": "3d",
                "Gold": "gold",
                "Silver": "silver",
                "Rainbow": "rainbow",
                "Fire": "fire",
                "Ice": "ice",
                "Metal": "metal",
                "Glow Purple": "glow_purple",
                "Comic": "comic",
                "Vintage": "vintage",
                "Sci-fi": "sci_fi",
                "Elegant": "elegant",
                "Grunge": "grunge",
                "Sticker": "sticker",
                "Chrome": "chrome",
                "Hologram": "hologram",
                "Luxury Gold": "luxury_gold",
                "Neon Pink": "neon_pink",
                "Cyberpunk": "cyberpunk",
                "Bubble": "bubble",
                "Space": "space"
            }
            selected_effect = effect_mapping[text_effect]
            
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
                        
                        if generate_variants:
                            variants = []
                            for i in range(num_variants):
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
                st.success(f"✅ Successfully processed {len(st.session_state.generated_images)} images with ULTRA PRO quality!")
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
                label=f"⬇️ Download {group_name} Photos",
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
        label="⬇️ Download All Photos (ULTRA PRO QUALITY)",
        data=zip_buffer.getvalue(),
        file_name="ultra_pro_photos.zip",
        mime="application/zip",
        use_container_width=True
    )
    
    st.markdown("""
        <div class='image-preview-container'>
            <h2 style='text-align: center; color: #ffcc00; margin: 0;'>🎨 ULTRA PRO RESULTS</h2>
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
                            key=f"download_{idx}",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"Error displaying {filename}: {str(e)}")
