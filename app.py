import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps
import os
import io
import random
import datetime
import zipfile
import numpy as np
import logging

# =================== CONFIG ===================
st.set_page_config(page_title="⚡ EDIT 100+ IMAGE IN ONE CLICK", layout="wide")

# Custom CSS for black/yellow theme with specific areas having black background
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
    }
    .sidebar .sidebar-content {
        background-color: #ffffff;
        color: black;
        border-right: 1px solid #ffff00;
    }
    .stSlider>div>div>div>div {
        background-color: #ffff00;
    }
    .stCheckbox>div>label {
        color: black !important;
    }
    .stSelectbox>div>div>select {
        color: black !important;
    }
    .stImage>img {
        border: 2px solid #ffff00;
        border-radius: 8px;
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
        background-color: #f0f0f0;
        border-radius: 5px;
    }
    .quote-slider {
        margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Main header with black background
st.markdown("""
    <div class='header-container'>
        <h1 style='text-align: center; color: #ffff00; margin: 0;' class='glowing-text'>⚡ EDIT 100+ IMAGE IN ONE CLICK</h1>
    </div>
""", unsafe_allow_html=True)

# =================== UTILS ===================
def list_files(folder, exts):
    """List files in folder with given extensions"""
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
        return []
    return [f for f in os.listdir(folder) 
           if any(f.lower().endswith(ext.lower()) for ext in exts)]

def smart_crop(img, target_ratio=3/4):
    w, h = img.size
    if w/h > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        return img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        return img.crop((0, top, w, top + new_h))

def get_text_size(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def get_random_font():
    fonts = list_files("assets/fonts", [".ttf", ".otf"])
    if not fonts:
        return None  # Return None if no fonts available
    
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            font_path = os.path.join("assets/fonts", random.choice(fonts))
            if os.path.exists(font_path):
                return ImageFont.truetype(font_path, 80)
        except Exception as e:
            logging.warning(f"Failed to load font (attempt {attempt+1}): {str(e)}")
            continue
    
    return None  # Return None if all attempts fail

def get_random_wish(greeting_type):
    wishes = {
        "Good Morning": ["Rise and shine!", "Make today amazing!", "Morning blessings!", "New day, new blessings!"],
        "Good Afternoon": ["Enjoy your day!", "Afternoon delights!", "Sunshine and smiles!", "Perfect day ahead!"],
        "Good Evening": ["Beautiful sunset!", "Evening serenity!", "Twilight magic!", "Peaceful evening!"],
        "Good Night": ["Sweet dreams!", "Sleep tight!", "Night night!", "Rest well!"]
    }
    return random.choice(wishes.get(greeting_type, ["Have a nice day!"]))

def get_random_quote():
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
        "Every sunrise is an invitation\nfor us to arise\nand brighten someone's day.",
        "The first hour of the morning\nis the rudder of the day.",
        "Morning is the time\nto plan your day\nand make it count.",
        "Wake up with a smile\nand chase your dreams\nwith passion.",
        "Morning is the best time\nto be thankful\nfor all you have.",
        "A beautiful morning begins\nwith a beautiful mindset.",
        "The morning breeze\nhas secrets to tell you.",
        "Morning is the time\nwhen everything\nis possible again.",
        "Each morning we are born again.\nWhat we do today\nmatters most.",
        "Morning is the key to the day\nand the secret to productivity.",
        "The morning sun\ninspires confidence\nand optimism.",
        "Start your day\nwith a grateful heart\nand positive thoughts.",
        "Morning is the perfect time\nto reflect and\nset intentions.",
        "The morning light\nfills the world\nwith hope and possibilities.",
        "A good morning starts\nthe night before\nwith gratitude.",
        "Morning is the time\nto plant the seeds\nof a productive day.",
        "The morning is the mother\nof every\nsuccessful day.",
        "Wake up with hope,\ngo to bed\nwith satisfaction.",
        "Morning is the time\nto fuel your\nbody and soul.",
        "The morning hour\nhas gold\nin its hand.",
        "Every morning is\na fresh start,\na new chance to get it right.",
        "Morning is the time\nto set the tone\nfor the rest of the day.",
        "The morning sun is\nnature's way of saying\n'one more chance'.",
        "Morning is the time\nto be inspired\nand take action.",
        "A positive morning\nleads to\na productive day.",
        "Morning is the perfect time\nto focus\non your goals.",
        "The morning light\nbrings clarity\nand new perspectives.",
        "Morning is the best time\nto connect\nwith yourself.",
        "Start your morning\nwith purpose and\nwatch your day transform.",
        "Morning is the time\nto nourish your\nmind, body and spirit.",
        "The morning is\nthe most important\npart of the day.",
        "Morning is the time\nto be grateful\nfor another day of life.",
        "A disciplined morning routine\ncreates a\nsuccessful life.",
        "Morning is the time\nto set your intentions\nand make them happen.",
        "The morning is when\nthe magic happens\nfor successful people.",
        "Morning is the perfect time\nto work\non your dreams.",
        "Morning is the time\nto build the life\nyou want to live.",
        "The morning is\nthe foundation\nof a productive day.",
        "Morning is the time\nto focus on\nwhat truly matters.",
        "A mindful morning\nleads to\na meaningful day.",
        "Morning is the best time\nto invest\nin yourself.",
        "The morning is your opportunity\nto create\nthe day you want.",
        "Morning is the time\nto align your actions\nwith your goals.",
        "A peaceful morning\nleads to\na productive day.",
        "Morning is the perfect time\nto practice\ngratitude.",
        "The morning is when\nchampions\nare made.",
        "Morning is the time\nto take control\nof your day.",
        "A strong morning routine\nbuilds a\nstrong life.",
        "Morning is the time\nto focus on progress,\nnot perfection.",
        "The morning is your chance\nto start fresh\nevery day.",
        "Morning is the best time\nto work on your\nmost important goals.",
        "Morning is the time\nto fuel your success\nfor the day.",
        "A powerful morning\ncreates a\npowerful day.",
        "Morning is the perfect time\nto visualize\nyour success.",
        "The morning is when\nthe seeds of success\nare planted.",
        "Morning is the time\nto build momentum\nfor your day.",
        "A focused morning\nleads to\na fulfilled day.",
        "Morning is the best time\nto work on your\npersonal growth.",
        "The morning is your opportunity\nto design your\nperfect day.",
        "Morning is the time\nto take action\ntoward your dreams.",
        "A productive morning\nleads to\na productive life.",
        "Morning is the perfect time\nto strengthen\nyour mindset.",
        "The morning is when\nyou set the tone\nfor your entire day.",
        "Morning is the time\nto make progress\non what matters most.",
        "A successful morning\nleads to\na successful day.",
        "Morning is the best time\nto invest in\nyour future self.",
        "The morning is your chance\nto create\nthe life you want.",
        "Morning is the time\nto build habits\nthat lead to success.",
        "A motivated morning\nleads to\nan accomplished day.",
        "Morning is the perfect time\nto work on\nyour priorities.",
        "The morning is when\nlegends are made\nthrough daily discipline.",
        "Morning is the time\nto take steps\ntoward your goals.",
        "A consistent morning routine\nbuilds an\nextraordinary life.",
        "Morning is the best time\nto develop your\nskills and talents.",
        "The morning is your opportunity\nto become\nyour best self.",
        "Morning is the time\nto create\nthe day you desire.",
        "A purposeful morning\nleads to\na purposeful life.",
        "Morning is the perfect time\nto work on\nyour vision.",
        "The morning is when\nsuccessful people do\ntheir most important work.",
        "Morning is the time\nto build the foundation\nfor your success.",
        "A dedicated morning routine\ncreates an\nexceptional life.",
        "Morning is the best time\nto focus on\nself-improvement.",
        "The morning is your chance\nto make progress\nevery single day.",
        "Morning is the time\nto develop the discipline\nof success.",
        "A winning morning\nleads to\na winning day.",
        "Morning is the perfect time\nto practice the habits\nof excellence.",
        "The morning is when\nordinary people do\nextraordinary things.",
        "Morning is the time\nto take massive action\ntoward your dreams.",
        "A strong morning\ncreates a\nstrong character.",
        "Morning is the best time\nto work on your\npersonal development.",
        "The morning is your opportunity\nto become the person\nyou want to be.",
        "Morning is the time\nto build the life\nof your dreams.",
        "A disciplined morning\nleads to\na disciplined life.",
        "Morning is the perfect time\nto focus on your\nlong-term goals.",
        "The morning is when\nchampions are made\nthrough daily effort.",
        "Morning is the time\nto take control\nof your destiny.",
        "A productive morning routine\nleads to\na productive life.",
        "Morning is the best time\nto work on your\nmost important projects.",
        "The morning is your chance\nto make today\nbetter than yesterday."
    ]
    return random.choice(quotes)

def get_random_color():
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

def apply_text_effect(draw, position, text, font, effect_settings, texture_img=None):
    x, y = position
    effect_type = effect_settings['type']
    
    if effect_type == 'colorful':
        main_color = effect_settings.get('main_color', get_random_color())
        outline_color = (0, 0, 0)  # Always black for outline in colorful mode
        shadow_color = (25, 25, 25)  # 90% black shadow
    elif effect_type == 'full_random':
        # For full random, we'll use the same color for all text in the image
        main_color = effect_settings.get('main_color', (255, 255, 255))  # Always white for main text
        outline_color = effect_settings.get('outline_color', (0, 0, 0))  # Always black for outline
        shadow_color = (25, 25, 25)  # 90% black shadow
    else:
        main_color = effect_settings.get('main_color', (255, 255, 255))
        outline_color = effect_settings.get('outline_color', (0, 0, 0))
        shadow_color = (25, 25, 25)  # 90% black shadow
    
    if effect_settings.get('use_texture', False) and texture_img:
        mask = Image.new("L", (font.getsize(text)[0], font.getsize(text)[1]))
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.text((0, 0), text, font=font, fill=255)
        texture = texture_img.resize(mask.size)
        textured_text = Image.new("RGBA", mask.size)
        textured_text.paste(texture, (0, 0), mask)
        draw.bitmap((x, y), textured_text.convert("L"), fill=(255, 255, 255))
        return effect_settings
    
    # Apply shadow (90% black)
    shadow_offset = 3
    draw.text((x+shadow_offset, y+shadow_offset), text, font=font, fill=shadow_color)
    
    if effect_type == "white_only":
        draw.text((x, y), text, font=font, fill=main_color)
    elif effect_type == "white_black_outline" or effect_type == "colorful":
        outline_size = 2
        for ox in range(-outline_size, outline_size+1):
            for oy in range(-outline_size, outline_size+1):
                if ox != 0 or oy != 0:
                    draw.text((x+ox, y+oy), text, font=font, fill=outline_color)
        draw.text((x, y), text, font=font, fill=main_color)
    elif effect_type == "full_random":
        # 50% chance for white or white with black outline
        if random.random() < 0.5:
            draw.text((x, y), text, font=font, fill=main_color)
        else:
            outline_size = 2
            for ox in range(-outline_size, outline_size+1):
                for oy in range(-outline_size, outline_size+1):
                    if ox != 0 or oy != 0:
                        draw.text((x+ox, y+oy), text, font=font, fill=outline_color)
            draw.text((x, y), text, font=font, fill=main_color)
    
    return effect_settings

def format_date(date_format="%d %B %Y", show_day=False):
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

def apply_overlay(image, overlay_path, size=0.5):
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

def generate_filename():
    now = datetime.datetime.now()
    future_minutes = random.randint(1, 10)
    future_time = now + datetime.timedelta(minutes=future_minutes)
    return f"Picsart_{future_time.strftime('%y-%m-%d_%H-%M-%S')}.jpg"

def get_watermark_position(img, watermark):
    # Always place watermark at top
    x = random.choice([20, max(20, img.width - watermark.width - 20)])
    y = 20
    return (x, y)

def enhance_image_quality(img):
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    img = ImageEnhance.Sharpness(img).enhance(1.5)
    img = ImageEnhance.Contrast(img).enhance(1.1)
    
    hist = img.histogram()
    if sum(hist[:100]) > sum(hist[-100:]):
        img = ImageEnhance.Brightness(img).enhance(1.1)
    
    return img

def upscale_text_elements(img, scale_factor=2):
    if scale_factor > 1:
        new_size = (img.width * scale_factor, img.height * scale_factor)
        img = img.resize(new_size, Image.LANCZOS)
    return img

def create_variant(original_img, settings):
    img = original_img.copy()
    draw = ImageDraw.Draw(img)
    
    # Get font - if None, return None to indicate failure
    font = get_random_font()
    if font is None:
        return None
    
    texture_img = None
    if settings.get('use_texture', False) and settings.get('texture_image', None):
        texture_img = settings['texture_image']
    
    effect_settings = {
        'type': settings.get('text_effect', None),
        'use_texture': settings.get('use_texture', False)
    }
    
    if effect_settings['type'] == 'full_random':
        # For full random, we'll use the same color for all text in the image
        effect_settings['main_color'] = (255, 255, 255)  # Always white for main text
        effect_settings['outline_color'] = (0, 0, 0)  # Always black for outline
    elif effect_settings['type'] == 'colorful':
        effect_settings['main_color'] = get_random_color()
        effect_settings['outline_color'] = (0, 0, 0)
    
    if settings['show_text']:
        font_main = font.font_variant(size=settings['main_size'])
        text = settings['greeting_type']
        text_width, text_height = get_text_size(draw, text, font_main)
        
        max_text_x = max(20, img.width - text_width - 20)
        text_x = random.randint(20, max_text_x) if max_text_x > 20 else 20
        text_y = 20  # Always at top
        
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
            max_wish_x = max(20, img.width - wish_width - 20)
            wish_x = random.randint(20, max_wish_x) if max_wish_x > 20 else 20
            wish_y = text_y + settings['main_size'] + random.randint(10, 30)
        else:
            max_wish_x = max(20, img.width - wish_width - 20)
            wish_x = random.randint(20, max_wish_x) if max_wish_x > 20 else 20
            wish_y = 20  # Always at top if no main text
        
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
        font_quote = font.font_variant(size=settings['quote_size'])  # Same font as main text
        quote_text = settings['quote_text']
        
        # Split the quote into lines
        lines = quote_text.split('\n')
        
        # Calculate total height needed
        total_height = 0
        line_heights = []
        for line in lines:
            _, line_height = get_text_size(draw, line, font_quote)
            line_heights.append(line_height)
            total_height += line_height
        
        # Calculate starting y position to center vertically
        quote_y = (img.height - total_height) // 2
        
        # Render each line
        for i, line in enumerate(lines):
            line_width, _ = get_text_size(draw, line, font_quote)
            max_quote_x = max(20, img.width - line_width - 20)
            quote_x = random.randint(20, max_quote_x) if max_quote_x > 20 else 20
            
            apply_text_effect(
                draw, 
                (quote_x, quote_y), 
                line, 
                font_quote,
                effect_settings,
                texture_img=texture_img
            )
            quote_y += line_heights[i] + 5  # Add small spacing between lines
    
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
    
    img = enhance_image_quality(img)
    img = upscale_text_elements(img, scale_factor=2)
    
    return img.convert("RGB")

def adjust_font_size_to_fit(draw, text, max_width, max_height, initial_size):
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

uploaded_images = st.file_uploader("📁 Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    greeting_type = st.selectbox("Greeting Type", ["Good Morning", "Good Afternoon", "Good Evening", "Good Night"])
    generate_variants = st.checkbox("Generate 3 Variants per Photo", value=False)
    
    text_effect = st.selectbox(
        "Text Style",
        ["White Only", "White with Black Outline", "Full Random", "Colorful"],
        index=0
    )
    
    st.markdown("### 🎨 Texture Options")
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
        main_size = st.slider("Main Text Size", 10, 200, 90)  # Default 90
    
    show_wish = st.checkbox("Show Wish", value=True)
    if show_wish:
        wish_size = st.slider("Wish Text Size", 10, 200, 60)  # Default 60
    
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
        quote_size = st.slider("Quote Text Size", 10, 100, 40)  # Changed default from 30 to 40
    
    use_watermark = st.checkbox("Add Watermark", value=True)
    watermark_image = None
    
    if use_watermark:
        watermark_option = st.radio("Watermark Source", ["Pre-made", "Upload Your Own"])
        
        if watermark_option == "Pre-made":
            watermark_files = list_files("assets/logos", [".png", ".jpg", ".jpeg"])
            if watermark_files:
                # Default to "wishful vibes.png" if available
                default_index = 0
                if "wishful vibes.png" in watermark_files:
                    default_index = watermark_files.index("wishful vibes.png")
                selected_watermark = st.selectbox("Select Watermark", watermark_files, index=default_index)
                watermark_path = os.path.join("assets/logos", selected_watermark)
                if os.path.exists(watermark_path):
                    watermark_image = Image.open(watermark_path).convert("RGBA")
                else:
                    st.error(f"Watermark file not found: {watermark_path}")
            else:
                st.warning("No watermarks found in assets/logos folder")
        else:
            uploaded_watermark = st.file_uploader("Upload Watermark", type=["png"])
            if uploaded_watermark:
                watermark_image = Image.open(uploaded_watermark).convert("RGBA")
        
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
    st.markdown("### ☕🐾 Coffee & Pet PNG")
    use_coffee_pet = st.checkbox("Enable Coffee & Pet PNG", value=False)
    if use_coffee_pet:
        pet_size = st.slider("PNG Size", 0.1, 1.0, 0.3)
        pet_files = list_files("assets/pets", [".png", ".jpg", ".jpeg"])
        selected_pet = st.selectbox("Select Pet PNG", ["Random"] + pet_files)
        
        if selected_pet == "Random":
            selected_pet = random.choice(pet_files) if pet_files else None

if st.button("✨ Generate Photos", key="generate"):
    if uploaded_images:
        with st.spinner("Processing images..."):
            processed_images = []
            variant_images = []
            
            effect_mapping = {
                "White Only": "white_only",
                "White with Black Outline": "white_black_outline",
                "Full Random": "full_random",
                "Colorful": "colorful"
            }
            selected_effect = effect_mapping[text_effect]
            
            settings = {
                'greeting_type': greeting_type,
                'show_text': show_text,
                'main_size': main_size if show_text else 90,  # Default 90
                'show_wish': show_wish,
                'wish_size': wish_size if show_wish else 60,  # Default 60
                'show_date': show_date,
                'show_day': show_day if show_date else False,
                'date_size': date_size if show_date else 30,
                'date_format': date_format if show_date else "8 July 2025",
                'show_quote': show_quote,
                'quote_text': quote_text if show_quote else "",
                'quote_size': quote_size if show_quote else 40,  # Changed default from 30 to 40
                'use_watermark': use_watermark,
                'watermark_image': watermark_image,
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
                'texture_image': texture_image
            }
            
            for uploaded_file in uploaded_images:
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
                            else:
                                st.warning(f"Overlay file not found: {overlay_path}")
                    
                    if generate_variants:
                        variants = []
                        for i in range(3):
                            variant = create_variant(img, settings)
                            if variant is not None:  # Only add if font selection succeeded
                                variants.append((generate_filename(), variant))
                        variant_images.extend(variants)
                    else:
                        draw = ImageDraw.Draw(img)
                        font = get_random_font()
                        if font is None:
                            st.error(f"Failed to load any fonts for {uploaded_file.name}. Please check your fonts folder.")
                            continue
                        
                        effect_settings = {
                            'type': selected_effect,
                            'use_texture': use_texture
                        }
                        
                        if selected_effect == 'full_random':
                            effect_settings['main_color'] = (255, 255, 255)  # Always white for main text
                            effect_settings['out texture_img=texture_image
                                )
                                quote_y += line_heights[i] + 5  # Add small spacing between lines
                        
                        if use_watermark and watermark_image:
                            watermark = watermark_image.copy()
                            
                            if watermark_opacity < 1.0:
                                alpha = watermark.split()[3]
                                alpha = ImageEnhance.Brightness(alpha).enhance(watermark_opacity)
                                watermark.putalpha(alpha)
                            
                            watermark.thumbnail((img.width//4, img.height//4))
                            pos = get_watermark_position(img, watermark)
                            img.paste(watermark, pos, watermark)
                        
                        if use_coffee_pet and selected_pet:
                            pet_path = os.path.join("assets/pets", selected_pet)
                            if os.path.exists(pet_path):
                                pet_img = Image.open(pet_path).convert("RGBA")
                                pet_img = pet_img.resize(
                                    (int(img.width * pet_size), 
                                    int(img.height * pet_size * (pet_img.height/pet_img.width))),
                                    Image.LANCZOS
                                )
                                x = img.width - pet_img.width - 20
                                y = img.height - pet_img.height - 20
                                img.paste(pet_img, (x, y), pet_img)
                        
                        img = enhance_image_quality(img)
                        img = upscale_text_elements(img, scale_factor=2)
                        
                        processed_images.append((generate_filename(), img))
                
                except Exception as e:
                    st.error(f"Error processing {uploaded_file.name}: {str(e)}")
                    continue

            st.session_state.generated_images = processed_images + variant_images
            
            if st.session_state.generated_images:
                st.success(f"Successfully processed {len(st.session_state.generated_images)} images!")
            else:
                st.warning("No images were processed successfully.")
    else:
        st.warning("Please upload at least one image.")

if st.session_state.generated_images:
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
        for filename, img in st.session_state.generated_images:
            try:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='JPEG', quality=95)
                zip_file.writestr(filename, img_bytes.getvalue())
            except Exception as e:
                st.error(f"Error adding {filename} to zip: {str(e)}")
                continue
    
    st.download_button(
        label="⬇️ Download All Photos",
        data=zip_buffer.getvalue(),
        file_name="generated_photos.zip",
        mime="application/zip"
    )
    
    st.markdown("""
        <div class='image-preview-container'>
            <h2 style='text-align: center; color: #ffff00; margin: 0;'>📸 Preview</h2>
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
                        st.image(img_bytes, use_column_width=True)
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
