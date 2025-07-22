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

# Custom CSS for black/yellow theme
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

# Main header
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
        "The morning sun\ninspires confidence\nand optimism."
    ]
    return random.choice(quotes)

def get_random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

def get_gradient_colors():
    # Define gradient color combinations
    gradients = [
        [(255, 255, 255), (255, 255, 0)],  # White to Yellow
        [(255, 255, 255), (0, 255, 0)],    # White to Green
        [(255, 255, 255), (255, 0, 0)],     # White to Red
        [(255, 255, 255), (0, 0, 255)],     # White to Blue
        [(255, 255, 255), (255, 0, 255)],   # White to Pink
        [(255, 255, 0), (255, 255, 255)],   # Yellow to White
        [(255, 0, 0), (255, 255, 255)],    # Red to White
        [(0, 255, 0), (255, 255, 255)],    # Green to White
        [(0, 0, 255), (255, 255, 255)],    # Blue to White
        [(255, 0, 255), (255, 255, 255)]   # Pink to White
    ]
    return random.choice(gradients)

def get_multi_gradient_colors():
    # Define multi-color gradient combinations
    gradients = [
        [(255, 255, 255), (255, 255, 0), (255, 0, 0)],  # White-Yellow-Red
        [(255, 255, 255), (0, 255, 0), (0, 0, 255)],    # White-Green-Blue
        [(255, 0, 0), (255, 255, 0), (0, 255, 0)],      # Red-Yellow-Green
        [(255, 0, 255), (0, 255, 255), (255, 255, 0)],  # Pink-Cyan-Yellow
        [(255, 255, 255), (255, 192, 203), (255, 0, 255)], # White-Pink-Purple
        [(255, 0, 0), (255, 255, 255), (0, 0, 255)],    # Red-White-Blue
        [(0, 0, 255), (255, 255, 255), (255, 0, 0)],    # Blue-White-Red
        [(255, 255, 0), (0, 255, 0), (0, 255, 255)]     # Yellow-Green-Cyan
    ]
    return random.choice(gradients)

def create_gradient_mask(width, height, colors, direction='horizontal'):
    """Create a gradient mask with given colors"""
    if width <= 0 or height <= 0:
        return Image.new('RGB', (1, 1), colors[0])
    
    base = Image.new('RGB', (width, height), colors[0])
    if len(colors) == 1:
        return base
    
    draw = ImageDraw.Draw(base)
    if direction == 'horizontal':
        for i in range(width):
            ratio = i / width
            r = int(colors[0][0] * (1 - ratio) + colors[-1][0] * ratio)
            g = int(colors[0][1] * (1 - ratio) + colors[-1][1] * ratio)
            b = int(colors[0][2] * (1 - ratio) + colors[-1][2] * ratio)
            draw.line([(i, 0), (i, height)], fill=(r, g, b))
    else:  # vertical
        for i in range(height):
            ratio = i / height
            r = int(colors[0][0] * (1 - ratio) + colors[-1][0] * ratio)
            g = int(colors[0][1] * (1 - ratio) + colors[-1][1] * ratio)
            b = int(colors[0][2] * (1 - ratio) + colors[-1][2] * ratio)
            draw.line([(0, i), (width, i)], fill=(r, g, b))
    
    return base

def safe_outline_filter(mask, size=2):
    """Apply outline filter safely"""
    if size <= 0:
        return mask
    
    try:
        return mask.filter(ImageFilter.MaxFilter(size))
    except:
        # Fallback for small images
        new_mask = mask.copy()
        for x in range(mask.width):
            for y in range(mask.height):
                if mask.getpixel((x, y)) > 0:
                    for dx in range(-size, size+1):
                        for dy in range(-size, size+1):
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < mask.width and 0 <= ny < mask.height:
                                if new_mask.getpixel((nx, ny)) == 0:
                                    new_mask.putpixel((nx, ny), 128)
        return new_mask.point(lambda p: 255 if p > 0 else 0)

def apply_text_effect(draw, position, text, font, effect_settings, texture_img=None):
    x, y = position
    effect_type = effect_settings['type']
    text_width, text_height = get_text_size(draw, text, font)
    
    # Ensure minimum size for text
    if text_width <= 0 or text_height <= 0:
        return effect_settings
    
    # Create a temporary image for advanced effects
    temp_img = Image.new('RGBA', (text_width + 20, text_height + 20), (0, 0, 0, 0))
    temp_draw = ImageDraw.Draw(temp_img)
    
    # Set colors based on effect type
    if effect_type == 'gradient':
        colors = get_gradient_colors()
        outline_color = (0, 0, 0)  # Black outline
    elif effect_type == 'multi_gradient':
        colors = get_multi_gradient_colors()
        outline_color = (0, 0, 0)  # Black outline
    elif effect_type == 'colorful':
        main_color = effect_settings.get('main_color', get_random_color())
        outline_color = (0, 0, 0)  # Black outline
    elif effect_type == 'full_random':
        main_color = get_random_color()
        outline_color = get_random_color()
    else:  # Default/white styles
        main_color = (255, 255, 255)  # White
        outline_color = (0, 0, 0)  # Black
    
    shadow_color = (25, 25, 25)  # Dark shadow
    
    # Apply texture if enabled
    if effect_settings.get('use_texture', False) and texture_img:
        mask = Image.new("L", (text_width, text_height))
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.text((0, 0), text, font=font, fill=255)
        texture = texture_img.resize(mask.size)
        textured_text = Image.new("RGBA", mask.size)
        textured_text.paste(texture, (0, 0), mask)
        draw.bitmap((x, y), textured_text.convert("L"), fill=main_color)
        return effect_settings
    
    # For gradient effects
    if effect_type in ['gradient', 'multi_gradient']:
        # Create text mask
        mask = Image.new('L', (text_width + 20, text_height + 20), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.text((10, 10), text, font=font, fill=255)
        
        # Create gradient
        gradient = create_gradient_mask(text_width + 20, text_height + 20, colors)
        
        # Apply outline
        outline_size = 2
        outline_mask = Image.new('L', (text_width + 20 + outline_size*2, text_height + 20 + outline_size*2), 0)
        outline_draw = ImageDraw.Draw(outline_mask)
        outline_draw.text((10 + outline_size, 10 + outline_size), text, font=font, fill=255)
        
        # Dilate for outline (with safety check)
        outline_mask = safe_outline_filter(outline_mask, outline_size)
        
        # Paste outline
        outline_img = Image.new('RGBA', outline_mask.size, (0, 0, 0, 0))
        outline_draw = ImageDraw.Draw(outline_img)
        outline_draw.bitmap((0, 0), outline_mask, fill=outline_color)
        
        # Paste gradient text
        text_img = Image.new('RGBA', mask.size, (0, 0, 0, 0))
        text_img.paste(gradient, (0, 0), mask)
        
        # Combine and paste onto main image
        combined = Image.new('RGBA', outline_img.size, (0, 0, 0, 0))
        combined.alpha_composite(outline_img)
        combined.alpha_composite(text_img, (outline_size, outline_size))
        
        draw.bitmap((x - outline_size, y - outline_size), combined)
        return effect_settings
    
    # Apply shadow
    shadow_offset = 3
    temp_draw.text((10 + shadow_offset, 10 + shadow_offset), text, font=font, fill=shadow_color)
    
    # Apply outline if needed
    if effect_type in ["white_black_outline", "colorful", "full_random", "gradient"]:
        outline_size = 2
        for ox in range(-outline_size, outline_size+1):
            for oy in range(-outline_size, outline_size+1):
                if ox != 0 or oy != 0:
                    temp_draw.text((10 + ox, 10 + oy), text, font=font, fill=outline_color)
    
    # Apply main text
    temp_draw.text((10, 10), text, font=font, fill=main_color)
    
    # Paste onto main image
    draw.bitmap((x - 10, y - 10), temp_img)
    
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
    if random.random() < 0.5:
        if random.random() < 0.5:
            x = 20
        else:
            x = img.width - watermark.width - 20
        y = img.height - watermark.height - 20
    else:
        max_x = max(20, img.width - watermark.width - 20)
        max_y = max(20, img.height - watermark.height - 20)
        x = random.randint(20, max_x) if max_x > 20 else 20
        y = random.randint(20, max_y) if max_y > 20 else 20
    return (x, y)
        
def enhance_image_quality(img):
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    try:
        img = ImageEnhance.Sharpness(img).enhance(1.5)
        img = ImageEnhance.Contrast(img).enhance(1.1)
        
        hist = img.histogram()
        if sum(hist[:100]) > sum(hist[-100:]):
            img = ImageEnhance.Brightness(img).enhance(1.1)
    except Exception as e:
        st.error(f"Error enhancing image: {str(e)}")
    
    return img

def upscale_text_elements(img, scale_factor=2):
    if scale_factor > 1:
        try:
            new_size = (img.width * scale_factor, img.height * scale_factor)
            img = img.resize(new_size, Image.LANCZOS)
        except Exception as e:
            st.error(f"Error upscaling image: {str(e)}")
    return img

def create_variant(original_img, settings):
    try:
        img = original_img.copy()
        draw = ImageDraw.Draw(img)
        
        font = get_random_font()
        if font is None:
            return None
        
        texture_img = settings.get('texture_image', None)
        
        effect_settings = {
            'type': settings.get('text_effect', None),
            'use_texture': settings.get('use_texture', False)
        }
        
        if settings['show_text']:
            font_main = font.font_variant(size=settings['main_size'])
            text = settings['greeting_type']
            text_width, text_height = get_text_size(draw, text, font_main)
            
            # Position handling based on selection
            if settings['text_position'] == "Top Center":
                text_x = (img.width - text_width) // 2
                text_y = 20
            elif settings['text_position'] == "Bottom Center":
                text_x = (img.width - text_width) // 2
                text_y = img.height - text_height - 20
            else:  # Random
                text_x = random.randint(20, max(20, img.width - text_width - 20))
                text_y = random.randint(20, max(20, img.height - text_height - 20))
            
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
        
        if settings['use_watermark'] and settings['watermark_images']:
            for watermark_image in settings['watermark_images']:
                if random.random() < 0.5:  # 50% chance to apply each watermark
                    watermark = watermark_image.copy()
                    
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
    except Exception as e:
        st.error(f"Error creating variant: {str(e)}")
        return None

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
    st.session_state.watermark_groups = {}

uploaded_images = st.file_uploader("📁 Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    greeting_type = st.selectbox("Greeting Type", ["Good Morning", "Good Afternoon", "Good Evening", "Good Night"])
    generate_variants = st.checkbox("Generate 3 Variants per Photo", value=False)
    
    text_effect = st.selectbox(
        "Text Style",
        ["White Only", "White with Black Outline", "Full Random", "Colorful", "Gradient", "Multi-Gradient"],
        index=0
    )
    
    # Text position option
    text_position = st.radio("Main Text Position", ["Top Center", "Bottom Center", "Random"], index=1)
    
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
                # Allow multiple selection
                selected_watermarks = st.multiselect(
                    "Select Watermark(s)", 
                    watermark_files,
                    default=["wishful vibes.png", "happy vibes.png", "good vibes.png"] if "wishful vibes.png" in watermark_files else watermark_files[:1]
                )
                for selected_watermark in selected_watermarks:
                    watermark_path = os.path.join("assets/logos", selected_watermark)
                    if os.path.exists(watermark_path):
                        watermark_images.append(Image.open(watermark_path).convert("RGBA"))
        else:
            uploaded_watermarks = st.file_uploader("Upload Watermark(s)", type=["png"], accept_multiple_files=True)
            if uploaded_watermarks:
                for uploaded_watermark in uploaded_watermarks:
                    watermark_images.append(Image.open(uploaded_watermark).convert("RGBA"))
        
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
                "Colorful": "colorful",
                "Gradient": "gradient",
                "Multi-Gradient": "multi_gradient"
            }
            selected_effect = effect_mapping[text_effect]
            
            settings = {
                'greeting_type': greeting_type,
                'show_text': show_text,
                'main_size': main_size if show_text else 90,
                'text_position': text_position,
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
                'watermark_images': watermark_images,
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
            
            # Reset watermark groups
            st.session_state.watermark_groups = {wm_idx: [] for wm_idx in range(len(watermark_images))}
            
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
                    
                    if generate_variants:
                        variants = []
                        for i in range(3):
                            variant = create_variant(img, settings)
                            if variant is not None:
                                variants.append((generate_filename(), variant))
                        variant_images.extend(variants)
                    else:
                        draw = ImageDraw.Draw(img)
                        font = get_random_font()
                        if font is None:
                            st.error(f"Failed to load any fonts for {uploaded_file.name}")
                            continue
                        
                        effect_settings = {
                            'type': selected_effect,
                            'use_texture': use_texture
                        }
                        
                        if show_text:
                            font_main = font.font_variant(size=main_size)
                            text = greeting_type
                            text_width, text_height = get_text_size(draw, text, font_main)
                            
                            if text_width > img.width - 40:
                                font_main = adjust_font_size_to_fit(draw, text, img.width - 40, img.height//3, main_size)
                                text_width, text_height = get_text_size(draw, text, font_main)
                            
                            # Position handling based on selection
                            if text_position == "Top Center":
                                text_x = (img.width - text_width) // 2
                                text_y = 20
                            elif text_position == "Bottom Center":
                                text_x = (img.width - text_width) // 2
                                text_y = img.height - text_height - 20
                            else:  # Random
                                text_x = random.randint(20, max(20, img.width - text_width - 20))
                                text_y = random.randint(20, max(20, img.height - text_height - 20))
                            
                            effect_settings = apply_text_effect(
                                draw, 
                                (text_x, text_y), 
                                text, 
                                font_main,
                                effect_settings,
                                texture_img=texture_image
                            )
                        
                        if show_wish:
                            font_wish = font.font_variant(size=wish_size)
                            wish_text = get_random_wish(greeting_type)
                            wish_width, wish_height = get_text_size(draw, wish_text, font_wish)
                            
                            if wish_width > img.width - 40:
                                font_wish = adjust_font_size_to_fit(draw, wish_text, img.width - 40, img.height//3, wish_size)
                                wish_width, wish_height = get_text_size(draw, wish_text, font_wish)
                            
                            wish_x = random.randint(20, max(20, img.width - wish_width - 20))
                            wish_y = text_y + main_size + 20 if show_text else 20
                            
                            apply_text_effect(
                                draw, 
                                (wish_x, wish_y), 
                                wish_text, 
                                font_wish,
                                effect_settings,
                                texture_img=texture_image
                            )
                        
                        if show_date:
                            font_date = font.font_variant(size=date_size)
                            
                            if date_format == "8 July 2025":
                                date_text = format_date("%d %B %Y", show_day)
                            elif date_format == "28 January 2025":
                                date_text = format_date("%d %B %Y", show_day)
                            elif date_format == "07/08/2025":
                                date_text = format_date("%m/%d/%Y", show_day)
                            else:
                                date_text = format_date("%Y-%m-%d", show_day)
                                
                            date_width, date_height = get_text_size(draw, date_text, font_date)
                            
                            if date_width > img.width - 40:
                                font_date = adjust_font_size_to_fit(draw, date_text, img.width - 40, img.height//3, date_size)
                                date_width, date_height = get_text_size(draw, date_text, font_date)
                            
                            date_x = random.randint(20, max(20, img.width - date_width - 20))
                            date_y = img.height - date_height - 20
                            
                            if show_day and "(" in date_text:
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
                                texture_img=texture_image
                            )
                        
                        if show_quote:
                            font_quote = font.font_variant(size=quote_size)
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
                                    texture_img=texture_image
                                )
                                quote_y += line_heights[i] + 10
                        
                        if use_watermark and watermark_images:
                            # Randomly select one watermark for this image
                            selected_wm_idx = random.randint(0, len(watermark_images)-1)
                            watermark = watermark_images[selected_wm_idx].copy()
                            
                            if watermark_opacity < 1.0:
                                alpha = watermark.split()[3]
                                alpha = ImageEnhance.Brightness(alpha).enhance(watermark_opacity)
                                watermark.putalpha(alpha)
                            
                            watermark.thumbnail((img.width//4, img.height//4))
                            pos = get_watermark_position(img, watermark)
                            img.paste(watermark, pos, watermark)
                            
                            # Add to watermark group
                            filename = generate_filename()
                            st.session_state.watermark_groups[selected_wm_idx].append((filename, img))
                        
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
                        
                        filename = generate_filename()
                        processed_images.append((filename, img))
                        
                        # If not using watermark grouping, add to general list
                        if not use_watermark or not watermark_images:
                            st.session_state.generated_images.append((filename, img))
                
                except Exception as e:
                    st.error(f"Error processing {uploaded_file.name}: {str(e)}")
                    continue

            # Combine all images
            if use_watermark and watermark_images:
                # Add all watermark group images to main list
                for wm_idx, images in st.session_state.watermark_groups.items():
                    st.session_state.generated_images.extend(images)
            else:
                st.session_state.generated_images = processed_images + variant_images
            
            if st.session_state.generated_images:
                st.success(f"Successfully processed {len(st.session_state.generated_images)} images!")
            else:
                st.warning("No images were processed.")

if st.session_state.generated_images:
    # Create a zip buffer for all images
    zip_buffer_all = io.BytesIO()
    with zipfile.ZipFile(zip_buffer_all, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
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
    
    # Create zip buffers for each watermark group if applicable
    zip_buffers = {}
    if use_watermark and watermark_images:
        for wm_idx, images in st.session_state.watermark_groups.items():
            if images:  # Only create if there are images in this group
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
                    for filename, img in images:
                        try:
                            if img.mode != 'RGB':
                                img = img.convert('RGB')
                            img_bytes = io.BytesIO()
                            img.save(img_bytes, format='JPEG', quality=100)
                            zip_file.writestr(filename, img_bytes.getvalue())
                        except Exception as e:
                            st.error(f"Error adding {filename} to zip: {str(e)}")
                            continue
                zip_buffers[wm_idx] = zip_buffer
    
    # Download buttons
    st.download_button(
        label="⬇️ Download All Photos",
        data=zip_buffer_all.getvalue(),
        file_name="all_generated_photos.zip",
        mime="application/zip"
    )
    
    # Add download buttons for each watermark group if applicable
    if use_watermark and watermark_images:
        for wm_idx, zip_buffer in zip_buffers.items():
            if wm_idx < len(watermark_images):
                wm_name = f"watermark_{wm_idx+1}"
                if watermark_images[wm_idx].filename:
                    wm_name = os.path.splitext(os.path.basename(watermark_images[wm_idx].filename))[0]
                st.download_button(
                    label=f"⬇️ Download {wm_name} Photos",
                    data=zip_buffer.getvalue(),
                    file_name=f"{wm_name}_photos.zip",
                    mime="application/zip"
                )
    
    st.markdown("""
        <div class='image-preview-container'>
            <h2 style='text-align: center; color: #FFFFFF; margin: 0;'>😇 Niche Dekho </h2>
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
