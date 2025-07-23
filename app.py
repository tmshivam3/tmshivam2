import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps, ImageChops
import os
import io
import random
import datetime
import zipfile
import numpy as np
import textwrap
import math
import colorsys
import traceback
import base64
import requests

# =================== CONFIG ===================
st.set_page_config(page_title="⚡ ULTIMATE IMAGE & TEXT EDITOR v4 ⚡", layout="wide", initial_sidebar_state="expanded")

# --- Directory Setup ---
FONT_DIR = "assets/fonts"
LOGO_DIR = "assets/logos"
PET_DIR = "assets/pets"
EMOJI_DIR = "assets/emojis"
TEXTURE_DIR = "assets/textures"
FRAMES_DIR = "assets/frames"
BACKGROUNDS_DIR = "assets/backgrounds" # For random backgrounds

# Ensure directories exist
for d in [FONT_DIR, LOGO_DIR, PET_DIR, EMOJI_DIR, TEXTURE_DIR, FRAMES_DIR, BACKGROUNDS_DIR]:
    os.makedirs(d, exist_ok=True)

# =================== CUSTOM CSS ===================
st.markdown("""
    <style>
    .main {
        background-color: #0a0a0a; /* Dark background */
        color: #ffffff; /* White text */
    }
    .header-container {
        background: linear-gradient(135deg, #1a1a1a 0%, #000000 100%);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 25px;
        border: 2px solid #ffcc00; /* Gold/Yellow border */
        box-shadow: 0 0 20px rgba(255, 204, 0, 0.5);
        text-align: center;
    }
    .image-preview-container {
        background-color: #121212;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid #333333;
        display: flex;
        justify-content: center;
        align-items: center;
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
        background-color: #1a1a1a; /* Darker sidebar */
        color: #ffffff;
        border-right: 1px solid #333333;
    }
    .stSlider>div>div>div>div {
        background-color: #ffcc00; /* Slider fill color */
    }
    .stCheckbox>div>label {
        color: #ffffff !important;
    }
    .stSelectbox>div>div>select, .stTextInput>div>div>input {
        background-color: #1a1a1a;
        color: #ffffff !important;
        border: 1px solid #333333;
        border-radius: 5px;
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
    /* Two-sidebar like layout (left sidebar actual, right controls simulated) */
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .css-1d391kg { /* This targets the main content area */
        flex-direction: row-reverse; /* Pushes content to the right, sidebar on left */
    }
    </style>
""", unsafe_allow_html=True)

# =================== UTILS ===================

@st.cache_data
def list_files(folder: str, exts: List[str]) -> List[str]:
    """List files in folder with given extensions"""
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
        return []
    files = os.listdir(folder)
    return [f for f in files
           if any(f.lower().endswith(ext.lower()) for ext in exts)]

@st.cache_data
def get_font_path(font_name):
    """Returns the full path for a font file."""
    font_map = {
        "Poppins-Bold": "Poppins-Bold.ttf",
        "OpenSans-Bold": "OpenSans-Bold.ttf",
        "Roboto-Bold": "Roboto-Bold.ttf",
        "Arial-Bold": "Arial-Bold.ttf",
        "TimesNewRoman-Bold": "TimesNewRoman-Bold.ttf",
        "DancingScript-Bold": "DancingScript-Bold.ttf",
        "Montserrat-Bold": "Montserrat-Bold.ttf",
        "IndieFlower": "IndieFlower.ttf",
        "Pacifico": "Pacifico.ttf",
        "Lobster": "Lobster-Regular.ttf",
        "PermanentMarker": "PermanentMarker-Regular.ttf",
    }
    filename = font_map.get(font_name, "Poppins-Bold.ttf") # Default font
    return os.path.join(FONT_DIR, filename)

@st.cache_data
def get_random_font_path():
    """Get a random font from assets/fonts"""
    fonts = list_files(FONT_DIR, [".ttf", ".otf"])
    if not fonts:
        return None # Indicate no custom fonts
    return os.path.join(FONT_DIR, random.choice(fonts))

@st.cache_data
def get_logo_path(logo_name):
    """Returns the full path for a logo file."""
    logo_map = {
        "Logo 1": "logo1.png",
        "Logo 2": "logo2.png",
        "Logo 3": "logo3.png",
    }
    filename = logo_map.get(logo_name)
    return os.path.join(LOGO_DIR, filename) if filename else None

@st.cache_data
def get_pet_path(pet_name):
    """Returns the full path for a pet image file."""
    pet_map = {
        "Coffee Pet 1": "coffee_pet1.png",
        "Coffee Pet 2": "coffee_pet2.png",
    }
    filename = pet_map.get(pet_name)
    return os.path.join(PET_DIR, filename) if filename else None

@st.cache_data
def get_emoji_path(emoji_name):
    """Returns the full path for an emoji image file."""
    # Assuming emoji files are named consistently, e.g., "emoji_heart.png"
    return os.path.join(EMOJI_DIR, f"emoji_{emoji_name.lower().replace(' ', '_')}.png")

@st.cache_data
def get_texture_path(texture_name):
    """Returns the full path for a texture image file."""
    texture_map = {
        "Wood Grain": "texture_wood.png",
        "Marble": "texture_marble.png",
        "Metal Grid": "texture_metal.png",
        "Rough Paper": "texture_paper.png",
        "Abstract Dots": "texture_dots.png",
    }
    filename = texture_map.get(texture_name)
    return os.path.join(TEXTURE_DIR, filename) if filename else None

@st.cache_data
def get_frame_path(frame_name):
    """Returns the full path for a frame image file."""
    frame_map = {
        "Simple Rectangle": "frame_simple.png",
        "Ornate Gold": "frame_ornate_gold.png",
        "Floral Vine": "frame_floral.png",
        "Distressed Wood": "frame_distressed_wood.png",
        "Polaroid": "frame_polaroid.png"
    }
    filename = frame_map.get(frame_name)
    return os.path.join(FRAMES_DIR, filename) if filename else None

@st.cache_data
def get_random_background_path():
    """Returns a random background image path."""
    backgrounds = list_files(BACKGROUNDS_DIR, [".jpg", ".jpeg", ".png"])
    if not backgrounds:
        return None
    return os.path.join(BACKGROUNDS_DIR, random.choice(backgrounds))

def get_random_bright_color():
    """Generates a random bright color suitable for gradients."""
    h = random.uniform(0, 1)
    s = random.uniform(0.7, 1.0) # High saturation
    v = random.uniform(0.8, 1.0) # High brightness
    r, g, b = [int(x * 255) for x in colorsys.hsv_to_rgb(h, s, v)]
    return (r, g, b)

def hex_to_rgb(hex_color):
    if hex_color is None:
        return (0, 0, 0)
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb_color):
    return '#%02x%02x%02x' % rgb_color

def get_font_size_for_image(img_width, base_size=50):
    return int(base_size * (img_width / 1000))

def get_wrapping_width(img_width, font_size, multiplier=0.8):
    # This is a rough estimate; PIL textwrap doesn't work directly with pixel widths easily.
    # It estimates character count based on average char width.
    avg_char_width = font_size * 0.6 # rough approximation
    return int((img_width * multiplier) / avg_char_width)


def get_text_size(draw: ImageDraw.Draw, text: str, font: ImageFont.FreeTypeFont) -> Tuple[int, int]:
    """Get text dimensions with None check"""
    if not text:
        return 0, 0
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def get_random_wish(greeting_type: str) -> str:
    """Get random wish based on greeting type"""
    wishes = {
        "Good Morning": [
            "Rise and shine! A new day is a new opportunity!", "Good morning! Make today amazing!",
            "Morning blessings! Hope your day is filled with joy!", "New day, new blessings! Seize the day!",
            "Wake up with determination! Go to bed with satisfaction!", "Every sunrise is a new chapter! Write a beautiful story today!",
            "Morning is the perfect time to start something new!", "The early morning has gold in its mouth!",
            "A new day is a new chance to be better than yesterday!", "Morning is wonderful! Embrace the beauty of a fresh start!",
            "The sun is a daily reminder that we too can rise again!", "Today's morning brings new strength, new thoughts, and new possibilities!",
            "Morning is the time when the whole world starts anew!", "Every sunrise is an invitation for us to arise and brighten someone's day!",
            "Good morning! May your coffee be strong and your day be productive!", "Start your day with a smile! It sets the tone for the whole day!",
            "Morning is not just time, it's an opportunity! Make it count!", "Let the morning sunshine fill your heart with warmth and positivity!",
            "A beautiful morning begins with a beautiful mindset!", "Good morning! May your day be as bright as your smile!"
        ],
        "Good Afternoon": [
            "Enjoy your afternoon! Hope it's productive!", "Afternoon delights! Take a break and refresh!",
            "Sunshine and smiles! Hope your afternoon is great!", "Perfect day ahead! Make the most of your afternoon!",
            "Afternoon is the perfect time to accomplish great things!", "Hope your day is going well! Keep up the good work!",
            "Afternoon blessings! May your energy be renewed!", "Take a deep breath! You're doing great this afternoon!",
            "The afternoon is a bridge between morning and evening! Make it count!", "Good afternoon! Time to refuel and recharge!",
            "Hope your afternoon is filled with productivity and joy!", "Afternoon is the perfect time for a fresh start!",
            "Keep going! The day is still full of possibilities!", "Good afternoon! May your focus be sharp and your tasks be light!",
            "The afternoon sun brings warmth and energy! Use it wisely!", "Halfway there! Keep up the good work and finish strong!",
            "Good afternoon! May your second half of the day be even better than the first!", "Embrace the tranquility of the afternoon!",
            "The afternoon is a sweet time for rest or renewed effort!", "Good afternoon! Recharge, reflect, and rejoice!"
        ],
        "Good Evening": [
            "Beautiful sunset!", "Evening serenity!", "Twilight magic!", "Peaceful evening!",
            "Unwind and relax! Enjoy your evening!", "Evening blessings! Hope you had a great day!",
            "The day is done! Time to chill!", "Good evening! May your night be restful!",
            "The moon rises, and so does new hope! Good evening!", "As the day fades, let your worries fade too!",
            "Good evening! May your evening be filled with warmth and joy!", "Wrap up your day with peace and quiet!",
            "Evening is the time to unwind from daily stress!", "Good evening! Time to enjoy the quiet moments!",
            "The evening is a beautiful time for introspection!", "Good evening! May your night be calm and peaceful!",
            "Wishing you a peaceful and cozy evening!", "Good evening! Relax and recharge for tomorrow!",
            "The best part of the day, good evening!", "Good evening! May your dreams be sweet!"
        ],
        "Good Night": [
            "Sweet dreams!", "Sleep tight!", "Night night!", "Rest well!",
            "Good night! May your sleep be peaceful!", "Dream big! Good night!",
            "Close your eyes and drift to dreamland!", "Good night! See you in the morning!",
            "May your dreams be filled with happiness!", "Good night! Until the sun rises again!",
            "Stars are shining, time for sleeping!", "Good night! Wishing you peaceful rest!",
            "Rest your mind and body! Good night!", "Good night! May your worries fade with the day!",
            "Sleep well and wake up refreshed!", "Good night! Thank you for a wonderful day!",
            "May your sleep be deep and undisturbed!", "Good night! Sending you peaceful vibes!",
            "The day is over, time for dreams!", "Good night! See you in the morning with new energy!"
        ],
        "Birthday Wish": [
            "Happy Birthday! Wishing you a day filled with happiness!", "Many happy returns of the day! Happy Birthday!",
            "Happy Birthday! May all your wishes come true!", "Wishing you a fantastic Birthday!",
            "Happy Birthday! Have a wonderful celebration!", "Cheers to another year! Happy Birthday!",
            "Happy Birthday! May your day be as special as you are!", "Wishing you joy and laughter on your Birthday!",
            "Happy Birthday! Celebrate big!", "Wishing you a year of happiness and success! Happy Birthday!",
            "Happy Birthday! May your day be filled with love!", "Wishing you all the best on your Birthday!",
            "Happy Birthday! Enjoy every moment!", "May your Birthday be truly special!",
            "Happy Birthday! Here's to many more!", "Wishing you a delightful Birthday!",
            "Happy Birthday! May your day be bright and beautiful!", "Happy Birthday! Have an amazing day!",
            "Wishing you a very joyful Birthday!", "Happy Birthday! Make it a memorable one!"
        ],
        "Anniversary Wish": [
            "Happy Anniversary! Wishing you many more years of love!", "Happy Anniversary! Cheers to your everlasting love!",
            "Wishing you a Happy Anniversary!", "Happy Anniversary! May your love story continue to inspire!",
            "Happy Anniversary! Celebrating your beautiful journey!", "To a wonderful couple, Happy Anniversary!",
            "Happy Anniversary! May your bond grow stronger each year!", "Wishing you a day filled with cherished memories!",
            "Happy Anniversary! Here's to love, laughter, and happiness!", "Happy Anniversary! A perfect day for a perfect couple!",
            "Happy Anniversary! May your love shine brighter!", "Wishing you a truly special Anniversary!",
            "Happy Anniversary! Forever and always!", "Happy Anniversary! Celebrating your incredible love!",
            "Wishing you endless love and happiness! Happy Anniversary!", "Happy Anniversary! You two are truly special!",
            "Happy Anniversary! May your love story be eternal!", "Happy Anniversary! Enjoy your special day!",
            "Wishing you a joyous Anniversary!", "Happy Anniversary! May your journey together be beautiful!"
        ],
        "Motivation Quote": [
            "Believe you can and you're halfway there.", "The only way to do great work is to love what you do.",
            "Success is not final, failure is not fatal: it is the courage to continue that counts.", "The future belongs to those who believe in the beauty of their dreams.",
            "Don't watch the clock; do what it does. Keep going.", "The best way to predict the future is to create it.",
            "It always seems impossible until it's done.", "Strive not to be a success, but rather to be of value.",
            "The mind is everything. What you think you become.", "Your time is limited, don't waste it living someone else's life.",
            "The journey of a thousand miles begins with a single step.", "Opportunities don't happen, you create them.",
            "The harder you work for something, the greater you'll feel when you achieve it.", "Dream it. Wish it. Do it.",
            "Do one thing every day that scares you.", "Push yourself, because no one else is going to do it for you.",
            "Great things never come from comfort zones.", "The future depends on what you do today.",
            "The only limit to our realization of tomorrow will be our doubts of today.", "The best revenge is massive success."
        ],
        "Inspirational Quote": [
            "The only impossible journey is the one you never begin.", "Life is what happens when you're busy making other plans.",
            "The purpose of our lives is to be happy.", "Live as if you were to die tomorrow. Learn as if you were to live forever.",
            "Change your thoughts and you change your world.", "What you get by achieving your goals is not as important as what you become by achieving your goals.",
            "The most difficult thing is the decision to act, the rest is merely tenacity.", "Every artist was first an amateur.",
            "Happiness is not something ready made. It comes from your own actions.", "The best way to find yourself is to lose yourself in the service of others.",
            "If you want to live a happy life, tie it to a goal, not to people or things.", "Keep your eyes on the stars, and your feet on the ground.",
            "The only true wisdom is in knowing you know nothing.", "Nothing is impossible, the word itself says 'I'm possible'!",
            "The only way to do great work is to love what you do.", "The bad news is time flies. The good news is you're the pilot.",
            "You are never too old to set another goal or to dream a new dream.", "To live is the rarest thing in the world. Most people exist, that is all.",
            "Darkness cannot drive out darkness; only light can do that. Hate cannot drive out hate; only love can do that.",
            "The only thing we have to fear is fear itself."
        ]
    }
    return random.choice(wishes.get(greeting_type, ["Have a nice day!"]))

# =================== TEXT RENDERING FUNCTIONS WITH EFFECTS ===================

def draw_text_with_outline(draw, text, font, position, fill_color, outline_color, outline_width, align="center"):
    x, y = position
    # Draw outline
    if outline_width > 0:
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if (dx, dy) != (0, 0): # Avoid drawing center twice for outline
                    draw.text((x + dx, y + dy), text, font=font, fill=outline_color, align=align)
    # Draw main text
    draw.text((x, y), text, font=font, fill=fill_color, align=align)

def draw_gradient_text(draw, text, font, position, start_color, end_color, outline_color, outline_width, align="center"):
    x, y = position
    text_width, text_height = get_text_size(draw, text, font)

    if text_width == 0 or text_height == 0: return # Avoid error on empty text

    # Create a temporary image for the text mask
    mask_img = Image.new("L", (text_width, text_height), 0)
    mask_draw = ImageDraw.Draw(mask_img)
    mask_draw.text((0, 0), text, font=font, fill=255)

    # Create a gradient image
    gradient_img = Image.new("RGB", (text_width, text_height))
    draw_gradient = ImageDraw.Draw(gradient_img)
    for i in range(text_width):
        r = int(start_color[0] + (end_color[0] - start_color[0]) * (i / text_width))
        g = int(start_color[1] + (end_color[1] - start_color[1]) * (i / text_width))
        b = int(start_color[2] + (end_color[2] - start_color[2]) * (i / text_width))
        draw_gradient.line([(i, 0), (i, text_height)], fill=(r, g, b))

    # Apply the text mask to the gradient
    gradient_text_img = Image.composite(gradient_img, Image.new("RGB", (text_width, text_height), (0,0,0)), mask_img)

    # For alignment, we need to adjust the paste position based on text_width
    paste_x = x
    if align == "center":
        paste_x = x - text_width // 2
    elif align == "right":
        paste_x = x - text_width
    
    # Draw outline first using the main draw object
    if outline_width > 0:
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if (dx, dy) != (0, 0):
                    draw.text((x + dx, y + dy), text, font=font, fill=outline_color, align=align)

    # Paste the gradient text
    draw.paste(gradient_text_img, (paste_x, y), mask=mask_img)

def draw_neon_text(draw, text, font, position, color, glow_color, outline_color, outline_width, align="center"):
    x, y = position
    text_width, text_height = get_text_size(draw, text, font)

    if text_width == 0 or text_height == 0: return

    # Create text layer
    text_img = Image.new('RGBA', (text_width + 20, text_height + 20), (0,0,0,0)) # Add padding for blur
    text_draw = ImageDraw.Draw(text_img)
    
    # Adjust position for the new text_img canvas, centralizing
    text_x = 10
    text_y = 10
    
    # Draw outline first on the temp image
    if outline_width > 0:
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if (dx, dy) != (0, 0):
                    text_draw.text((text_x + dx, text_y + dy), text, font=font, fill=outline_color, align=align)

    # Draw main text on the temp image
    text_draw.text((text_x, text_y), text, font=font, fill=color, align=align)

    # Apply blur for glow effect
    glow_img = text_img.filter(ImageFilter.GaussianBlur(radius=random.randint(3, 8))) # Random blur radius for "peak randomness"
    # Further enhance glow by increasing alpha
    glow_img = Image.composite(glow_img.filter(ImageFilter.BoxBlur(random.randint(1, 3))), Image.new('RGBA', glow_img.size, (0,0,0,0)), glow_img.getchannel('A').point(lambda i: i * random.uniform(1.5, 2.5))) # Random alpha multiplier

    # Tint the glow
    r, g, b = glow_color
    tinted_glow = Image.new('RGBA', glow_img.size, (r,g,b,0))
    tinted_glow.putalpha(glow_img.getchannel('A'))

    # Combine glow and text_img
    final_text_render = Image.alpha_composite(tinted_glow, text_img)

    # Calculate paste position on original image
    paste_x = x
    paste_y = y
    if align == "center":
        paste_x = x - (text_width // 2) - 10 # Adjust for padding
    elif align == "right":
        paste_x = x - text_width - 10 # Adjust for padding
    
    # Ensure paste_x, paste_y are within image bounds
    paste_x = max(0, min(paste_x, draw.im.size[0] - final_text_render.size[0]))
    paste_y = max(0, min(paste_y, draw.im.size[1] - final_text_render.size[1]))

    draw.im.paste(final_text_render, (paste_x, paste_y), final_text_render)


def draw_3d_text(draw, text, font, position, fill_color, outline_color, outline_width, depth_color, depth=5, align="center"):
    x, y = position
    # Draw depth layers
    for i in range(depth, 0, -1):
        draw.text((x + i, y + i), text, font=font, fill=depth_color, align=align)

    # Draw outline
    if outline_width > 0:
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if (dx, dy) != (0, 0):
                    draw.text((x + dx, y + dy), text, font=font, fill=outline_color, align=align)

    # Draw main text
    draw.text((x, y), text, font=font, fill=fill_color, align=align)

def draw_textured_text(draw, text, font, position, texture_path, outline_color, outline_width, align="center"):
    x, y = position
    text_width, text_height = get_text_size(draw, text, font)

    if text_width == 0 or text_height == 0: return

    # Create a mask for the text
    mask_img = Image.new("L", (text_width, text_height), 0)
    mask_draw = ImageDraw.Draw(mask_img)
    mask_draw.text((0, 0), text, font=font, fill=255)

    # Load and resize texture
    try:
        texture_img = Image.open(texture_path).convert("RGB")
        texture_img = texture_img.resize((text_width, text_height), Image.LANCZOS)
    except Exception:
        st.warning("Texture file not found or corrupted. Using solid color instead for textured text.")
        texture_img = Image.new("RGB", (text_width, text_height), (150,150,150)) # Default grey if texture fails

    # Apply the mask to the texture
    textured_text = Image.composite(texture_img, Image.new("RGB", (text_width, text_height), (0,0,0)), mask_img)

    # Paste the textured text onto the main image
    paste_x = x
    if align == "center":
        paste_x = x - text_width // 2
    elif align == "right":
        paste_x = x - text_width
    
    # Draw outline first if needed
    if outline_width > 0:
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if (dx, dy) != (0, 0):
                    draw.text((x + dx, y + dy), text, font=font, fill=outline_color, align=align)
    
    draw.paste(textured_text, (paste_x, y), mask=mask_img)

def draw_glitch_text(draw, text, font, position, fill_color, outline_color, outline_width, align="center"):
    x, y = position
    num_layers = random.randint(2, 5) # Random number of glitch layers
    for _ in range(num_layers):
        offset_x = random.randint(-8, 8) # Increased randomness for glitch
        offset_y = random.randint(-8, 8)
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), random.randint(100, 200)) # Semi-transparent random color
        draw_text_with_outline(draw, text, font, (x + offset_x, y + offset_y), color, outline_color, outline_width, align)
    draw_text_with_outline(draw, text, font, position, fill_color, outline_color, outline_width, align) # Draw original on top

def draw_stroked_text(draw, text, font, position, fill_color, stroke_color, stroke_width, align="center"):
    # PIL draw.text has a stroke_width argument in newer versions, but for compatibility
    # and more control, we'll draw the stroke manually or simulate with outline.
    draw_text_with_outline(draw, text, font, position, fill_color, stroke_color, stroke_width, align)

# Map text effects to functions
TEXT_EFFECT_FUNCTIONS = {
    "Normal": draw_text_with_outline,
    "Outline": draw_text_with_outline, # Same as normal but relies on outline color/width
    "Gradient": draw_gradient_text,
    "Neon Glow": draw_neon_text,
    "3D": draw_3d_text,
    "Textured": draw_textured_text,
    "Glitch": draw_glitch_text,
    "Stroked": draw_stroked_text,
}

# =================== IMAGE PROCESSING FUNCTIONS ===================

def apply_image_enhancement(img: Image.Image, enhancement_type: str, factor: float) -> Image.Image:
    if enhancement_type == "Brightness":
        return ImageEnhance.Brightness(img).enhance(factor)
    elif enhancement_type == "Contrast":
        return ImageEnhance.Contrast(img).enhance(factor)
    elif enhancement_type == "Sharpness":
        return ImageEnhance.Sharpness(img).enhance(factor)
    elif enhancement_type == "Color":
        return ImageEnhance.Color(img).enhance(factor)
    return img

def apply_image_filter(img: Image.Image, filter_type: str) -> Image.Image:
    if filter_type == "BLUR":
        return img.filter(ImageFilter.BLUR)
    elif filter_type == "CONTOUR":
        return img.filter(ImageFilter.CONTOUR)
    elif filter_type == "EMBOSS":
        return img.filter(ImageFilter.EMBOSS)
    elif filter_type == "SHARPEN":
        return img.filter(ImageFilter.SHARPEN)
    elif filter_type == "SMOOTH":
        return img.filter(ImageFilter.SMOOTH)
    elif filter_type == "DETAIL":
        return img.filter(ImageFilter.DETAIL)
    elif filter_type == "EDGE_ENHANCE":
        return img.filter(ImageFilter.EDGE_ENHANCE)
    elif filter_type == "FIND_EDGES":
        return img.filter(ImageFilter.FIND_EDGES)
    return img

def apply_color_effect(img: Image.Image, effect_type: str) -> Image.Image:
    if effect_type == "Grayscale":
        return ImageOps.grayscale(img)
    elif effect_type == "Sepia":
        # Simple sepia: R = (R*0.393)+(G*0.769)+(B*0.189), G = (R*0.349)+(G*0.686)+(B*0.168), B = (R*0.272)+(G*0.534)+(B*0.131)
        sepia_matrix = (
            0.393, 0.769, 0.189, 0,
            0.349, 0.686, 0.168, 0,
            0.272, 0.534, 0.131, 0
        )
        return img.convert("RGB", sepia_matrix)
    elif effect_type == "Invert":
        return ImageOps.invert(img.convert("RGB"))
    elif effect_type == "Solarize":
        return ImageOps.solarize(img.convert("RGB"))
    elif effect_type == "Posterize":
        return ImageOps.posterize(img.convert("RGB"), random.randint(2, 6)) # Random levels
    elif effect_type == "Colorize (Random)":
        # Apply a random hue shift, maintaining lightness/saturation
        h, s, v = img.convert("HSV").split()
        random_hue_offset = random.randint(0, 255)
        h_array = np.array(h)
        h_array = (h_array + random_hue_offset) % 256
        h = Image.fromarray(np.uint8(h_array))
        return Image.merge("HSV", (h, s, v)).convert("RGB")
    return img

def apply_image_transform(img: Image.Image, transform_type: str, angle: int = 0) -> Image.Image:
    if transform_type == "Rotate":
        return img.rotate(angle, expand=True)
    elif transform_type == "Flip (Vertical)":
        return ImageOps.flip(img)
    elif transform_type == "Mirror (Horizontal)":
        return ImageOps.mirror(img)
    return img

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

def add_image_overlay(base_img: Image.Image, overlay_path: str, position_type: str, x_offset: int, y_offset: int, size_factor: float = 1.0, opacity: float = 1.0) -> Image.Image:
    try:
        overlay_img = Image.open(overlay_path).convert("RGBA")
        
        # Resize overlay
        original_width, original_height = overlay_img.size
        new_width = int(original_width * size_factor)
        new_height = int(original_height * size_factor)
        if new_width == 0: new_width = 1 # Prevent zero division
        if new_height == 0: new_height = 1
        overlay_img = overlay_img.resize((new_width, new_height), Image.LANCZOS)

        # Apply opacity
        if opacity < 1.0:
            alpha = overlay_img.split()[3]
            alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
            overlay_img.putalpha(alpha)

        # Calculate position
        img_width, img_height = base_img.size
        overlay_width, overlay_height = overlay_img.size

        if position_type == "Center":
            paste_x = (img_width - overlay_width) // 2 + x_offset
            paste_y = (img_height - overlay_height) // 2 + y_offset
        elif position_type == "Top-Left":
            paste_x = x_offset
            paste_y = y_offset
        elif position_type == "Top-Right":
            paste_x = img_width - overlay_width + x_offset
            paste_y = y_offset
        elif position_type == "Bottom-Left":
            paste_x = x_offset
            paste_y = img_height - overlay_height + y_offset
        elif position_type == "Bottom-Right":
            paste_x = img_width - overlay_width + x_offset
            paste_y = img_height - overlay_height + y_offset
        elif position_type == "Random":
            paste_x = random.randint(0, max(0, img_width - overlay_width))
            paste_y = random.randint(0, max(0, img_height - overlay_height))
        else: # Manual
            paste_x = x_offset
            paste_y = y_offset
        
        # Ensure coordinates are within bounds
        paste_x = max(0, min(paste_x, img_width - overlay_width))
        paste_y = max(0, min(paste_y, img_height - overlay_height))

        # Create a blank RGBA image to paste the base_img onto, if base_img is not RGBA
        if base_img.mode != 'RGBA':
            base_img_rgba = base_img.convert('RGBA')
        else:
            base_img_rgba = base_img.copy()

        base_img_rgba.paste(overlay_img, (paste_x, paste_y), overlay_img)
        return base_img_rgba

    except Exception as e:
        st.error(f"Error adding overlay: {e}. Please check the overlay file.")
        return base_img

def apply_frame(base_img: Image.Image, frame_path: str, frame_thickness: int = 20, blend_opacity: float = 1.0) -> Image.Image:
    try:
        frame_img = Image.open(frame_path).convert("RGBA")
        
        # Ensure frame_img is suitable (e.g., has transparent areas for overlay)
        # If it's a solid image, it will just cover.
        
        # Resize frame to match base image
        frame_img = frame_img.resize(base_img.size, Image.LANCZOS)
        
        # Apply opacity
        if blend_opacity < 1.0:
            alpha = frame_img.split()[3]
            alpha = ImageEnhance.Brightness(alpha).enhance(blend_opacity)
            frame_img.putalpha(alpha)

        # Composite frame onto the base image
        if base_img.mode != 'RGBA':
            base_img = base_img.convert('RGBA')
        
        # For frames, we want to overlay. Image.alpha_composite works best for RGBA on RGBA.
        # If the frame has transparent areas, the base_img will show through.
        final_img = Image.alpha_composite(base_img, frame_img)
        return final_img

    except Exception as e:
        st.error(f"Error applying frame: {e}. Please check the frame file.")
        return base_img

# This function is a placeholder for actual background removal.
# A real implementation would involve a robust ML model or an API.
def remove_background_placeholder(img: Image.Image) -> Image.Image:
    st.info("Background removal is a complex task. This is a placeholder function.")
    st.info("For a real solution, consider integrating an external API (e.g., remove.bg) or an ML model (e.g., U-Net).")
    # For demonstration, we'll just make the image slightly transparent or grayscale
    img_rgba = img.convert("RGBA")
    # Make all pixels slightly transparent as a "background removed" visual cue
    # alpha = img_rgba.split()[3]
    # alpha = ImageEnhance.Brightness(alpha).enhance(0.8) # 80% opaque
    # img_rgba.putalpha(alpha)
    # Or simply return the image as is, or with a solid background as a demo
    # For now, just convert to RGBA, making transparent if it was originally opaque background (e.g. white becomes transparent)
    datas = img_rgba.getdata()
    newData = []
    for item in datas:
        # Change all white (ish) pixels to transparent. This is a very crude "background removal".
        if item[0] > 200 and item[1] > 200 and item[2] > 200: # Example for white-ish background
            newData.append((255, 255, 255, 0)) # Make transparent
        else:
            newData.append(item)
    img_rgba.putdata(newData)
    return img_rgba

# =================== MAIN APP LOGIC ===================

if 'original_image' not in st.session_state:
    st.session_state.original_image = None
if 'processed_image' not in st.session_state:
    st.session_state.processed_image = None
if 'text_positions' not in st.session_state:
    st.session_state.text_positions = {} # {text_id: (x, y)}
if 'image_variants' not in st.session_state:
    st.session_state.image_variants = []

def get_current_image():
    return st.session_state.processed_image if st.session_state.processed_image else st.session_state.original_image

def save_image_to_session(img):
    st.session_state.processed_image = img

def clear_all():
    st.session_state.original_image = None
    st.session_state.processed_image = None
    st.session_state.text_positions = {}
    st.session_state.image_variants = []
    st.rerun()

# --- HEADER ---
st.markdown("""
    <div class='header-container'>
        <h1 style='color: #ffcc00; margin: 0;'>⚡ ULTIMATE IMAGE & TEXT EDITOR v4 ⚡</h1>
        <p style='color: #ccc;'>एक कॉम्पैक्ट पैकेज में Deepseek और Gemini की सभी सुविधाएँ!</p>
    </div>
""", unsafe_allow_html=True)

# --- LEFT SIDEBAR: Deepseek Features (Image Upload & Basic Adjustments) ---
with st.sidebar:
    st.header("🖼️ इमेज अपलोड और मूल समायोजन")
    
    uploaded_files = st.file_uploader("अपनी इमेज अपलोड करें (JPG, PNG)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    if uploaded_files:
        if len(uploaded_files) > 1:
            st.session_state.multi_images_mode = True
            st.info(f"{len(uploaded_files)} इमेज अपलोड की गईं। बैच प्रोसेसिंग मोड सक्रिय।")
            if 'original_image_list' not in st.session_state:
                st.session_state.original_image_list = []
                st.session_state.processed_image_list = []
                for u_file in uploaded_files:
                    img = Image.open(u_file).convert("RGB")
                    st.session_state.original_image_list.append(img)
                    st.session_state.processed_image_list.append(img.copy())
            
            selected_image_idx = st.selectbox(
                "संपादित करने के लिए इमेज चुनें:",
                list(range(len(uploaded_files))),
                format_func=lambda idx: f"Image {idx + 1}: {uploaded_files[idx].name}"
            )
            st.session_state.original_image = st.session_state.original_image_list[selected_image_idx]
            st.session_state.processed_image = st.session_state.processed_image_list[selected_image_idx]

        else:
            st.session_state.multi_images_mode = False
            uploaded_file = uploaded_files[0]
            if st.session_state.original_image is None or st.session_state.original_image.tobytes() != Image.open(uploaded_file).convert("RGB").tobytes():
                st.session_state.original_image = Image.open(uploaded_file).convert("RGB")
                st.session_state.processed_image = st.session_state.original_image.copy()
                st.session_state.text_positions = {} # Clear text positions on new image upload
                st.session_state.image_variants = []
                st.success("इमेज सफलतापूर्वक अपलोड हुई!")
    
    if st.session_state.original_image:
        st.subheader("इमेज एन्हांसमेंट")
        enhance_type = st.selectbox("एन्हांसमेंट प्रकार", ["None", "Brightness", "Contrast", "Sharpness", "Color"])
        enhance_factor = st.slider("एन्हांसमेंट फैक्टर", 0.0, 2.0, 1.0, 0.05) if enhance_type != "None" else 1.0

        st.subheader("इमेज फिल्टर्स")
        filter_type = st.selectbox("फ़िल्टर प्रकार", ["None", "BLUR", "CONTOUR", "EMBOSS", "SHARPEN", "SMOOTH", "DETAIL", "EDGE_ENHANCE", "FIND_EDGES"])
        
        st.subheader("कलर इफेक्ट्स")
        color_effect = st.selectbox("कलर इफेक्ट", ["None", "Grayscale", "Sepia", "Invert", "Solarize", "Posterize", "Colorize (Random)"])
        
        st.subheader("इमेज ट्रांसफॉर्मेशन")
        transform_type = st.selectbox("ट्रांसफॉर्मेशन प्रकार", ["None", "Rotate", "Flip (Vertical)", "Mirror (Horizontal)"])
        rotation_angle = st.slider("घुमाव का कोण", 0, 360, 0, 5) if transform_type == "Rotate" else 0

        crop_ratio_options = {"None": None, "3:4": 3/4, "4:3": 4/3, "1:1 (Square)": 1/1, "16:9": 16/9, "9:16": 9/16}
        selected_crop_ratio_label = st.selectbox("स्मार्ट क्रॉप अनुपात", list(crop_ratio_options.keys()))
        crop_target_ratio = crop_ratio_options[selected_crop_ratio_label]
        
        if st.button("इमेज पर बदलाव लागू करें"):
            current_img = st.session_state.original_image.copy()
            if enhance_type != "None":
                current_img = apply_image_enhancement(current_img, enhance_type, enhance_factor)
            if filter_type != "None":
                current_img = apply_image_filter(current_img, filter_type)
            if color_effect != "None":
                current_img = apply_color_effect(current_img, color_effect)
            if transform_type != "None":
                current_img = apply_image_transform(current_img, transform_type, rotation_angle)
            if crop_target_ratio:
                current_img = smart_crop(current_img, crop_target_ratio)
            
            save_image_to_session(current_img)
            st.success("इमेज पर बदलाव लागू हो गए हैं!")
            st.session_state.text_positions = {} # Reset text positions on major image changes
            st.rerun() # Rerun to update the main display

        # Background Removal (Placeholder)
        st.subheader("बैकग्राउंड रिमूवर")
        if st.button("बैकग्राउंड हटाएँ (प्रयोगात्मक)"):
            if get_current_image():
                st.session_state.processed_image = remove_background_placeholder(get_current_image())
                st.success("बैकग्राउंड हटाने का प्रयास किया गया।")
                st.rerun()
            else:
                st.warning("बैकग्राउंड हटाने के लिए पहले एक इमेज अपलोड करें।")
        
        st.subheader("बैच प्रोसेसिंग")
        if st.session_state.multi_images_mode and st.session_state.processed_image_list:
            st.info("आपने मल्टीपल इमेज अपलोड की हैं।")
            st.markdown("---")
            st.subheader("वर्तमान इमेज पर लागू इफेक्ट्स:")
            st.write(f"इन्हांसमेंट: {enhance_type} (Factor: {enhance_factor})")
            st.write(f"फ़िल्टर: {filter_type}")
            st.write(f"कलर इफेक्ट: {color_effect}")
            st.write(f"ट्रांसफॉर्मेशन: {transform_type} (Angle: {rotation_angle})")
            st.write(f"क्रॉप अनुपात: {selected_crop_ratio_label}")
            
            if st.button("सभी इमेजेस पर लागू करें और डाउनलोड करें"):
                if st.session_state.original_image_list:
                    output_zip = io.BytesIO()
                    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
                        for i, original_img in enumerate(st.session_state.original_image_list):
                            progress_bar = st.progress(0, text=f"इमेज {i+1}/{len(st.session_state.original_image_list)} प्रोसेस हो रही है...")
                            processed_batch_img = original_img.copy()

                            if enhance_type != "None":
                                processed_batch_img = apply_image_enhancement(processed_batch_img, enhance_type, enhance_factor)
                            if filter_type != "None":
                                processed_batch_img = apply_image_filter(processed_batch_img, filter_type)
                            if color_effect != "None":
                                processed_batch_img = apply_color_effect(processed_batch_img, color_effect)
                            if transform_type != "None":
                                processed_batch_img = apply_image_transform(processed_batch_img, transform_type, rotation_angle)
                            if crop_target_ratio:
                                processed_batch_img = smart_crop(processed_batch_img, crop_target_ratio)
                            
                            # Integrate text/overlay features for batch processing if needed (complex, currently not implemented for batch)
                            # This part would require careful state management for each image's text/overlay.
                            # For simplicity, batch applies only image adjustments.

                            img_byte_arr = io.BytesIO()
                            processed_batch_img.save(img_byte_arr, format="PNG")
                            zf.writestr(f"processed_image_{i+1}.png", img_byte_arr.getvalue())
                            progress_bar.progress((i + 1) / len(st.session_state.original_image_list), text=f"इमेज {i+1}/{len(st.session_state.original_image_list)} प्रोसेस हो रही है...")
                    st.success("सभी इमेजेस सफलतापूर्वक प्रोसेस की गईं!")
                    st.download_button(
                        label="प्रोसेस्ड इमेजेस डाउनलोड करें (ZIP)",
                        data=output_zip.getvalue(),
                        file_name="processed_images.zip",
                        mime="application/zip"
                    )
                else:
                    st.warning("बैच प्रोसेसिंग के लिए कोई इमेज अपलोड नहीं की गई है।")
        else:
            if st.button("सभी इमेजेस रीसेट करें"):
                clear_all()
    
# --- MAIN CONTENT AREA ---
st.markdown("<div class='main-content'>", unsafe_allow_html=True) # Custom class for potential right alignment

col1, col2 = st.columns([3, 2]) # Image preview on left, Text/Overlay controls on right

with col1:
    st.subheader("आपकी इमेज प्रीव्यू")
    current_image = get_current_image()
    if current_image:
        st.image(current_image, use_column_width=True, caption="संपादित इमेज")
        
        # Download button for single image
        buf = io.BytesIO()
        current_image.save(buf, format="PNG")
        byte_im = buf.getvalue()
        st.download_button(
            label="डाउनलोड इमेज",
            data=byte_im,
            file_name="edited_image.png",
            mime="image/png"
        )
    else:
        st.info("कृपया शुरुआत करने के लिए साइडबार से एक इमेज अपलोड करें।")
        # Suggest random image if no image is uploaded
        if st.button("रैंडम बैकग्राउंड के साथ शुरू करें"):
            random_bg_path = get_random_background_path()
            if random_bg_path:
                try:
                    st.session_state.original_image = Image.open(random_bg_path).convert("RGB")
                    st.session_state.processed_image = st.session_state.original_image.copy()
                    st.success("रैंडम बैकग्राउंड इमेज अपलोड हुई!")
                    st.rerun()
                except Exception as e:
                    st.error(f"रैंडम बैकग्राउंड लोड करने में त्रुटि: {e}")
            else:
                st.warning("रैंडम बैकग्राउंड उपलब्ध नहीं हैं। कृपया 'assets/backgrounds' फोल्डर में इमेज जोड़ें।")


with col2: # Right-side controls (Gemini Features)
    st.subheader("✍️ टेक्स्ट और ओवरले प्रभाव")

    with st.expander("टेक्स्ट जोड़ें और संपादित करें", expanded=True):
        text_input = st.text_area("टेक्स्ट दर्ज करें", value=st.session_state.get('last_text_input', ""), key="text_input")
        st.session_state.last_text_input = text_input # Save for persistence
        
        col_font, col_size = st.columns(2)
        with col_font:
            font_files = list_files(FONT_DIR, [".ttf", ".otf"])
            font_options = ["Poppins-Bold", "OpenSans-Bold", "Roboto-Bold", "Arial-Bold", "TimesNewRoman-Bold", "DancingScript-Bold", "Montserrat-Bold", "IndieFlower", "Pacifico", "Lobster", "PermanentMarker"] + [f.split('.')[0] for f in font_files if f.split('.')[0] not in ["Poppins-Bold", "OpenSans-Bold", "Roboto-Bold", "Arial-Bold", "TimesNewRoman-Bold", "DancingScript-Bold", "Montserrat-Bold", "IndieFlower", "Pacifico", "Lobster", "PermanentMarker"]]
            selected_font_name = st.selectbox("फ़ॉन्ट चुनें", font_options, index=font_options.index("Poppins-Bold") if "Poppins-Bold" in font_options else 0)
            custom_font_path = get_font_path(selected_font_name) if selected_font_name in ["Poppins-Bold", "OpenSans-Bold", "Roboto-Bold", "Arial-Bold", "TimesNewRoman-Bold", "DancingScript-Bold", "Montserrat-Bold", "IndieFlower", "Pacifico", "Lobster", "PermanentMarker"] else os.path.join(FONT_DIR, selected_font_name + ".ttf")

            if st.button("रैंडम फ़ॉन्ट"):
                random_font = get_random_font_path()
                if random_font:
                    st.session_state.random_font_path = random_font
                    st.info(f"रैंडम फ़ॉन्ट: {os.path.basename(random_font)}")
                else:
                    st.warning("कोई कस्टम फ़ॉन्ट नहीं मिला। 'assets/fonts' में फ़ॉन्ट जोड़ें।")

            font_to_use = st.session_state.get('random_font_path') if st.session_state.get('random_font_path') else custom_font_path
            try:
                if font_to_use and os.path.exists(font_to_use):
                    font_obj = ImageFont.truetype(font_to_use, get_font_size_for_image(current_image.width if current_image else 1000))
                else:
                    font_obj = ImageFont.load_default()
            except Exception:
                st.warning("चयनित फ़ॉन्ट लोड करने में त्रुटि। डिफ़ॉल्ट फ़ॉन्ट का उपयोग किया जा रहा है।")
                font_obj = ImageFont.load_default()

        with col_size:
            font_size = st.slider("फ़ॉन्ट साइज़", 10, 200, 50)
            font_obj = ImageFont.truetype(font_to_use, font_size) if font_to_use and os.path.exists(font_to_use) else ImageFont.load_default()


        text_color = st.color_picker("टेक्स्ट कलर", "#FFFFFF")
        text_align = st.selectbox("टेक्स्ट अलाइनमेंट", ["center", "left", "right"])

        text_effect = st.selectbox("टेक्स्ट इफेक्ट", list(TEXT_EFFECT_FUNCTIONS.keys()))

        outline_color = st.color_picker("आउटलाइन कलर", "#000000")
        outline_width = st.slider("आउटलाइन चौड़ाई", 0, 10, 2)

        if text_effect == "Gradient":
            gradient_start_color = st.color_picker("ग्रेडिएंट स्टार्ट कलर", rgb_to_hex(get_random_bright_color()))
            gradient_end_color = st.color_picker("ग्रेडिएंट एंड कलर", rgb_to_hex(get_random_bright_color()))
        if text_effect == "Neon Glow":
            glow_color = st.color_picker("ग्लो कलर", rgb_to_hex(get_random_bright_color()))
        if text_effect == "3D":
            depth_color = st.color_picker("डेप्थ कलर", "#555555")
            depth_amount = st.slider("डेप्थ मात्रा", 1, 20, 5)
        if text_effect == "Textured":
            texture_files = list_files(TEXTURE_DIR, [".png", ".jpg", ".jpeg"])
            texture_options = ["None"] + [f.split('.')[0] for f in texture_files]
            selected_texture_name = st.selectbox("टेक्सचर चुनें", texture_options)
            texture_path_selected = get_texture_path(selected_texture_name) if selected_texture_name != "None" else None
        
        if st.button("टेक्स्ट रैंडमाइज़ करें"):
            st.session_state.random_text_color = rgb_to_hex(get_random_bright_color())
            st.session_state.random_outline_color = rgb_to_hex(get_random_bright_color())
            st.session_state.random_glow_color = rgb_to_hex(get_random_bright_color())
            st.session_state.random_gradient_start = rgb_to_hex(get_random_bright_color())
            st.session_state.random_gradient_end = rgb_to_hex(get_random_bright_color())
            st.session_state.random_depth_color = rgb_to_hex(get_random_bright_color())
            st.session_state.random_font_path = get_random_font_path()
            st.session_state.random_font_size = random.randint(30, 150)
            st.rerun() # Rerun to apply random values to widgets

        # Apply random values if they exist in session state
        text_color = st.session_state.get('random_text_color', text_color)
        outline_color = st.session_state.get('random_outline_color', outline_color)
        glow_color = st.session_state.get('random_glow_color', glow_color)
        gradient_start_color = st.session_state.get('random_gradient_start', gradient_start_color)
        gradient_end_color = st.session_state.get('random_gradient_end', gradient_end_color)
        depth_color = st.session_state.get('random_depth_color', depth_color)
        font_size = st.session_state.get('random_font_size', font_size)

        # Quote Maker integration
        st.markdown("---")
        st.subheader("कोट मेकर")
        greeting_type = st.selectbox("कोट/शुभकामना का प्रकार", [
            "None", "Good Morning", "Good Afternoon", "Good Evening", "Good Night",
            "Birthday Wish", "Anniversary Wish", "Motivation Quote", "Inspirational Quote"
        ])
        if greeting_type != "None" and st.button(f"{greeting_type} के लिए कोट जनरेट करें"):
            generated_quote = get_random_wish(greeting_type)
            st.session_state.text_input_for_quote = generated_quote # Update text input directly
            st.session_state.last_text_input = generated_quote # Also save for persistence
            st.info(f"जनरेटेड कोट: {generated_quote}")
            st.rerun() # Rerun to update the text_area

        # Use the generated quote if available
        text_to_render = st.session_state.get('text_input_for_quote', text_input)
        # Clear the temporary state after using it to avoid re-applying on next interaction
        if 'text_input_for_quote' in st.session_state:
            del st.session_state.text_input_for_quote

        # Text Position
        st.markdown("---")
        st.subheader("टेक्स्ट पोजीशनिंग")
        text_pos_type = st.radio("टेक्स्ट पोजीशन", ["Manual", "Top-Left", "Top-Right", "Center", "Bottom-Left", "Bottom-Right", "Random"])
        x_pos, y_pos = st.session_state.text_positions.get('main_text', (50, 50))
        if text_pos_type == "Manual":
            x_pos = st.slider("X पोजीशन", 0, current_image.width if current_image else 1000, x_pos)
            y_pos = st.slider("Y पोजीशन", 0, current_image.height if current_image else 1000, y_pos)
        
        if st.button("टेक्स्ट लागू करें"):
            if current_image and text_to_render:
                processed_img = current_image.copy()
                draw = ImageDraw.Draw(processed_img)

                wrapping_width = get_wrapping_width(processed_img.width, font_size)
                wrapped_text = textwrap.fill(text_to_render, width=wrapping_width)

                # Get the function for the selected effect
                effect_function = TEXT_EFFECT_FUNCTIONS.get(text_effect, draw_text_with_outline)

                # Prepare arguments based on effect
                kwargs = {
                    "draw": draw,
                    "text": wrapped_text,
                    "font": font_obj,
                    "position": (x_pos, y_pos),
                    "fill_color": hex_to_rgb(text_color),
                    "outline_color": hex_to_rgb(outline_color),
                    "outline_width": outline_width,
                    "align": text_align
                }

                if text_effect == "Gradient":
                    kwargs["start_color"] = hex_to_rgb(gradient_start_color)
                    kwargs["end_color"] = hex_to_rgb(gradient_end_color)
                elif text_effect == "Neon Glow":
                    kwargs["glow_color"] = hex_to_rgb(glow_color)
                elif text_effect == "3D":
                    kwargs["depth_color"] = hex_to_rgb(depth_color)
                    kwargs["depth"] = depth_amount
                elif text_effect == "Textured":
                    if texture_path_selected:
                        kwargs["texture_path"] = texture_path_selected
                    else:
                        st.warning("टेक्सचर्ड इफेक्ट के लिए कोई टेक्सचर नहीं चुना गया है।")
                        # Fallback to normal text if texture is not selected
                        effect_function = draw_text_with_outline
                        kwargs["fill_color"] = hex_to_rgb(text_color)
                elif text_effect == "Stroked":
                    kwargs["stroke_color"] = hex_to_rgb(outline_color) # Outline acts as stroke
                    kwargs["stroke_width"] = outline_width

                # Handle dynamic positioning for non-manual types
                if text_pos_type != "Manual":
                    text_w, text_h = get_text_size(draw, wrapped_text, font_obj)
                    img_w, img_h = processed_img.size
                    
                    if text_pos_type == "Top-Left":
                        x_pos, y_pos = 0, 0
                    elif text_pos_type == "Top-Right":
                        x_pos, y_pos = img_w - text_w, 0
                    elif text_pos_type == "Center":
                        x_pos, y_pos = (img_w - text_w) // 2, (img_h - text_h) // 2
                    elif text_pos_type == "Bottom-Left":
                        x_pos, y_pos = 0, img_h - text_h
                    elif text_pos_type == "Bottom-Right":
                        x_pos, y_pos = img_w - text_w, img_h - text_h
                    elif text_pos_type == "Random":
                        x_pos = random.randint(0, max(0, img_w - text_w))
                        y_pos = random.randint(0, max(0, img_h - text_h))
                    kwargs["position"] = (x_pos, y_pos)

                # Call the effect function
                effect_function(**kwargs)
                
                st.session_state.text_positions['main_text'] = (x_pos, y_pos) # Save position
                save_image_to_session(processed_img)
                st.success("टेक्स्ट सफलतापूर्वक जोड़ा गया!")
                st.rerun()
            else:
                st.warning("कृपया पहले एक इमेज अपलोड करें और टेक्स्ट दर्ज करें।")

    with st.expander("इमेज ओवरले और फ्रेम्स", expanded=True):
        st.subheader("लोगो ओवरले")
        logo_files = list_files(LOGO_DIR, [".png", ".jpg"])
        logo_options = ["None"] + [f.split('.')[0] for f in logo_files]
        selected_logo_name = st.selectbox("लोगो चुनें", logo_options)
        logo_path_selected = get_logo_path(selected_logo_name) if selected_logo_name != "None" else None

        st.subheader("पेट ओवरले")
        pet_files = list_files(PET_DIR, [".png", ".jpg"])
        pet_options = ["None"] + [f.split('.')[0] for f in pet_files]
        selected_pet_name = st.selectbox("पेट इमेज चुनें", pet_options)
        pet_path_selected = get_pet_path(selected_pet_name) if selected_pet_name != "None" else None

        st.subheader("इमोजी ओवरले")
        emoji_files = list_files(EMOJI_DIR, [".png"])
        emoji_options = ["None"] + [f.split('.')[0] for f in emoji_files]
        selected_emoji_name = st.selectbox("इमोजी चुनें", emoji_options)
        emoji_path_selected = get_emoji_path(selected_emoji_name) if selected_emoji_name != "None" else None

        # General overlay controls
        overlay_size_factor = st.slider("ओवरले साइज़ फैक्टर", 0.1, 2.0, 0.5, 0.05)
        overlay_opacity = st.slider("ओवरले ओपेसिटी", 0.1, 1.0, 1.0, 0.05)
        overlay_pos_type = st.radio("ओवरले पोजीशन", ["Center", "Top-Left", "Top-Right", "Bottom-Left", "Bottom-Right", "Random"])
        overlay_x_offset = st.slider("ओवरले X ऑफसेट", -200, 200, 0)
        overlay_y_offset = st.slider("ओवरले Y ऑफसेट", -200, 200, 0)

        if st.button("ओवरले लागू करें"):
            if current_image:
                processed_img = current_image.copy()
                if logo_path_selected:
                    processed_img = add_image_overlay(processed_img, logo_path_selected, overlay_pos_type, overlay_x_offset, overlay_y_offset, overlay_size_factor, overlay_opacity)
                if pet_path_selected:
                    processed_img = add_image_overlay(processed_img, pet_path_selected, overlay_pos_type, overlay_x_offset, overlay_y_offset, overlay_size_factor, overlay_opacity)
                if emoji_path_selected:
                    processed_img = add_image_overlay(processed_img, emoji_path_selected, overlay_pos_type, overlay_x_offset, overlay_y_offset, overlay_size_factor, overlay_opacity)
                
                save_image_to_session(processed_img)
                st.success("ओवरले सफलतापूर्वक जोड़े गए!")
                st.rerun()
            else:
                st.warning("ओवरले जोड़ने के लिए पहले एक इमेज अपलोड करें।")

        st.markdown("---")
        st.subheader("फ्रेम/बॉर्डर")
        frame_files = list_files(FRAMES_DIR, [".png", ".jpg"])
        frame_options = ["None"] + [f.split('.')[0] for f in frame_files]
        selected_frame_name = st.selectbox("फ्रेम चुनें", frame_options)
        frame_path_selected = get_frame_path(selected_frame_name) if selected_frame_name != "None" else None
        
        frame_opacity = st.slider("फ्रेम ओपेसिटी", 0.1, 1.0, 1.0, 0.05, key="frame_opacity")

        if st.button("फ्रेम लागू करें"):
            if current_image and frame_path_selected:
                processed_img = current_image.copy()
                processed_img = apply_frame(processed_img, frame_path_selected, blend_opacity=frame_opacity)
                save_image_to_session(processed_img)
                st.success("फ्रेम सफलतापूर्वक लागू हुआ!")
                st.rerun()
            else:
                st.warning("फ्रेम लागू करने के लिए पहले एक इमेज अपलोड करें और एक फ्रेम चुनें।")

st.markdown("</div>", unsafe_allow_html=True) # Close main-content div

# --- Footer ---
st.markdown("""
    <div class='fixed-bottom'>
        <p style='color: #888; font-size: 0.8em; margin: 0;'>
            Developed with ❤️ using Streamlit, Deepseek features, and Gemini enhancements.
        </p>
    </div>
""", unsafe_allow_html=True)
