import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps
import os
import io
import random
import datetime
import zipfile
import numpy as np

# =================== CONFIG ===================
st.set_page_config(page_title="⚡ Instant Photo Generator", layout="wide")

# Custom CSS for black/white/yellow theme
st.markdown("""
    <style>
    .main {
        background-color: #000000;
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
        background-color: #000000;
        color: white;
        border-right: 1px solid #ffff00;
    }
    .stSlider>div>div>div>div {
        background-color: #ffff00;
    }
    .stCheckbox>div>label {
        color: white !important;
    }
    .stSelectbox>div>div>select {
        color: white !important;
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
    </style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
    <div style='background-color: #000000; padding: 15px; border-radius: 8px; margin-bottom: 20px; border: 2px solid #ffff00;'>
        <h1 style='text-align: center; color: #ffff00; margin: 0;'>⚡ Instant Photo Generator</h1>
    </div>
""", unsafe_allow_html=True)

# =================== UTILS ===================
def list_files(folder, exts):
    if not os.path.exists(folder):
        return []
    return [f for f in os.listdir(folder) if any(f.lower().endswith(ext) for ext in exts)]

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
        return ImageFont.load_default()
    font_path = os.path.join("assets/fonts", random.choice(fonts))
    try:
        return ImageFont.truetype(font_path, 80)  # Default size 80
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

def get_random_color():
    # Bright colors that work well with effects
    colors = [
        (255, 255, 0),   # Yellow
        (255, 255, 255), # White
        (0, 255, 255),   # Cyan
        (255, 0, 255),   # Magenta
        (255, 165, 0),   # Orange
        (0, 255, 0),     # Green
        (255, 0, 0),     # Red
        (0, 0, 255)      # Blue
    ]
    return random.choice(colors)

def get_random_text_effect():
    # 40% chance of normal text, 60% chance of effect
    if random.random() < 0.4:
        return "none"
    else:
        return random.choice(["shadow", "outline", "both"])

def apply_text_effects(draw, position, text, font, color, effect=None):
    if effect is None:
        effect = get_random_text_effect()
    
    if effect == "shadow":
        shadow_offset = 3
        draw.text((position[0]+shadow_offset, position[1]+shadow_offset), 
                 text, font=font, fill=(0,0,0,128))
    elif effect == "outline":
        outline_size = 2
        for x in range(-outline_size, outline_size+1):
            for y in range(-outline_size, outline_size+1):
                if x != 0 or y != 0:  # Skip the center position
                    draw.text((position[0]+x, position[1]+y), text, font=font, fill=(0,0,0))
    elif effect == "both":
        shadow_offset = 3
        draw.text((position[0]+shadow_offset, position[1]+shadow_offset), 
                 text, font=font, fill=(0,0,0,128))
        outline_size = 2
        for x in range(-outline_size, outline_size+1):
            for y in range(-outline_size, outline_size+1):
                if x != 0 or y != 0:
                    draw.text((position[0]+x, position[1]+y), text, font=font, fill=(0,0,0))
    
    draw.text(position, text, font=font, fill=color)
    return effect

def format_date(date_format="%d %B %Y", show_day=False):
    today = datetime.datetime.now()
    formatted_date = today.strftime(date_format)
    
    if show_day:
        # Check if within 4-5 hours of next day (19:00-23:59)
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
        
        # Random position but within bounds
        max_x = max(20, image.width - overlay.width - 20)  # Ensure max_x >= 20
        max_y = max(20, image.height - overlay.height - 20)  # Ensure max_y >= 20
        x = random.randint(20, max_x) if max_x > 20 else 20
        y = random.randint(20, max_y) if max_y > 20 else 20
        
        image.paste(overlay, (x, y), overlay)
    except Exception as e:
        st.error(f"Error applying overlay: {str(e)}")
    return image

def generate_filename():
    now = datetime.datetime.now()
    # Use future time (current minute + random 1-10 minutes)
    future_minutes = random.randint(1, 10)
    future_time = now + datetime.timedelta(minutes=future_minutes)
    return f"Picsart_{future_time.strftime('%y-%m-%d_%H-%M-%S')}.jpg"

def get_watermark_position(img, watermark):
    # 70% chance to be at bottom, 30% chance to be random
    if random.random() < 0.7:
        # Bottom position (random left/right)
        x = random.choice([
            20,  # left
            max(20, img.width - watermark.width - 20)  # right (ensure >= 20)
        ])
        y = max(20, img.height - watermark.height - 20)  # ensure >= 20
    else:
        # Random position (avoid center)
        max_x = max(20, img.width - watermark.width - 20)  # ensure >= 20
        max_y = max(20, img.height - watermark.height - 20)  # ensure >= 20
        x = random.randint(20, max_x) if max_x > 20 else 20
        y = random.randint(20, max_y) if max_y > 20 else 20
    
    return (x, y)

def enhance_image_quality(img):
    """Enhance image quality with multiple filters"""
    # Convert to RGB if not already
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Apply sharpness
    img = ImageEnhance.Sharpness(img).enhance(1.5)
    
    # Apply contrast
    img = ImageEnhance.Contrast(img).enhance(1.1)
    
    # Apply brightness if needed
    hist = img.histogram()
    if sum(hist[:100]) > sum(hist[-100:]):  # More dark pixels than light
        img = ImageEnhance.Brightness(img).enhance(1.1)
    
    return img

def upscale_text_elements(img, scale_factor=2):
    """Upscale text elements in the image"""
    if scale_factor > 1:
        new_size = (img.width * scale_factor, img.height * scale_factor)
        img = img.resize(new_size, Image.LANCZOS)
    return img

def create_variant(original_img, settings, text_effect=None):
    """Create a variant of the original image with different text positions/effects"""
    img = original_img.copy()
    draw = ImageDraw.Draw(img)
    font = get_random_font()
    text_color = get_random_color()
    
    # Add main text
    if settings['show_text']:
        font_main = font.font_variant(size=settings['main_size'])
        text = settings['greeting_type']
        text_width, text_height = get_text_size(draw, text, font_main)
        
        # Varied positioning with bounds checking
        max_text_x = max(20, img.width - text_width - 20)
        text_x = random.randint(20, max_text_x) if max_text_x > 20 else 20
        max_text_y = max(20, img.height // 3)
        text_y = random.randint(20, max_text_y) if max_text_y > 20 else 20
        
        effect = apply_text_effects(draw, (text_x, text_y), text, font_main, text_color, text_effect)
    
    # Add wish text with same effect as main text
    if settings['show_wish']:
        font_wish = font.font_variant(size=settings['wish_size'])
        wish_text = get_random_wish(settings['greeting_type'])
        wish_width, wish_height = get_text_size(draw, wish_text, font_wish)
        
        # Position relative to main text or random
        if settings['show_text']:
            max_wish_x = max(20, img.width - wish_width - 20)
            wish_x = random.randint(20, max_wish_x) if max_wish_x > 20 else 20
            wish_y = text_y + settings['main_size'] + random.randint(10, 30)
        else:
            max_wish_x = max(20, img.width - wish_width - 20)
            wish_x = random.randint(20, max_wish_x) if max_wish_x > 20 else 20
            max_wish_y = max(20, img.height // 2)
            wish_y = random.randint(20, max_wish_y) if max_wish_y > 20 else 20
        
        apply_text_effects(draw, (wish_x, wish_y), wish_text, font_wish, text_color, effect)
    
    # Add date text with same effect
    if settings['show_date']:
        font_date = font.font_variant(size=settings['date_size'])
        
        # Format date based on selection
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
        date_y = max(20, img.height - date_height - 20)  # Bottom position
        
        # Ensure day text doesn't overlap
        if settings['show_day'] and "(" in date_text:
            day_part = date_text[date_text.index("("):]
            day_width, _ = get_text_size(draw, day_part, font_date)
            if date_x + day_width > img.width - 20:
                date_x = img.width - day_width - 25
        
        apply_text_effects(draw, (date_x, date_y), date_text, font_date, text_color, effect)
    
    # Add watermark if enabled
    if settings['use_watermark'] and settings['watermark_image']:
        watermark = settings['watermark_image'].copy()
        
        # Apply opacity
        if settings['watermark_opacity'] < 1.0:
            alpha = watermark.split()[3]
            alpha = ImageEnhance.Brightness(alpha).enhance(settings['watermark_opacity'])
            watermark.putalpha(alpha)
        
        # Resize proportionally
        watermark.thumbnail((img.width//4, img.height//4))
        
        # Get position (70% bottom, 30% random)
        pos = get_watermark_position(img, watermark)
        
        # Simple overlap avoidance
        for _ in range(3):  # Try 3 times to find non-overlapping position
            overlap = False
            if settings['show_text']:
                if (pos[0] < text_x + text_width and pos[0] + watermark.width > text_x and
                    pos[1] < text_y + text_height and pos[1] + watermark.height > text_y):
                    overlap = True
            if not overlap and settings['show_wish']:
                if (pos[0] < wish_x + wish_width and pos[0] + watermark.width > wish_x and
                    pos[1] < wish_y + wish_height and pos[1] + watermark.height > wish_y):
                    overlap = True
            if not overlap and settings['show_date']:
                if (pos[0] < date_x + date_width and pos[0] + watermark.width > date_x and
                    pos[1] < date_y + date_height and pos[1] + watermark.height > date_y):
                    overlap = True
            
            if not overlap:
                break
            else:
                pos = get_watermark_position(img, watermark)
        
        img.paste(watermark, pos, watermark)
    
    # Apply Coffee & Pet PNG if enabled
    if settings['use_coffee_pet'] and settings['selected_pet']:
        pet_path = os.path.join("assets/pets", settings['selected_pet'])
        if os.path.exists(pet_path):
            pet_img = Image.open(pet_path).convert("RGBA")
            pet_img = pet_img.resize(
                (int(img.width * settings['pet_size']), 
                int(img.height * settings['pet_size'] * (pet_img.height/pet_img.width))),
                Image.LANCZOS
            )
            # Position at bottom right
            x = img.width - pet_img.width - 20
            y = img.height - pet_img.height - 20
            img.paste(pet_img, (x, y), pet_img)
    
    # Apply quality enhancements
    img = enhance_image_quality(img)
    
    # Upscale text elements
    img = upscale_text_elements(img, scale_factor=2)
    
    return img.convert("RGB")

def adjust_font_size_to_fit(draw, text, max_width, max_height, initial_size):
    """Adjust font size to fit within specified dimensions"""
    font = None
    size = initial_size
    while size > 10:  # Minimum font size
        try:
            font = ImageFont.truetype("assets/fonts/default.ttf", size)
            text_width, text_height = get_text_size(draw, text, font)
            if text_width <= max_width and text_height <= max_height:
                break
        except:
            font = ImageFont.load_default()
            break
        size -= 2  # Decrease by 2 points each iteration
    return font

# =================== MAIN APP ===================
# Store generated images in session state to persist after download
if 'generated_images' not in st.session_state:
    st.session_state.generated_images = []

uploaded_images = st.file_uploader("📁 Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# Settings sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    # Greeting type
    greeting_type = st.selectbox("Greeting Type", ["Good Morning", "Good Afternoon", "Good Evening", "Good Night"])
    
    # Variant option
    generate_variants = st.checkbox("Generate 3 Variants per Photo", value=False)
    
    # Text settings
    show_text = st.checkbox("Show Greeting", value=True)
    if show_text:
        main_size = st.slider("Main Text Size", 10, 200, 80)  # Default 80, range 10-200
    
    show_wish = st.checkbox("Show Wish", value=True)
    if show_wish:
        wish_size = st.slider("Wish Text Size", 10, 200, 50)  # Default 50, range 10-200
    
    show_date = st.checkbox("Show Date", value=False)  # Default unchecked
    if show_date:
        date_size = st.slider("Date Text Size", 10, 200, 30)  # Range 10-200
        date_format = st.selectbox("Date Format", 
                                 ["8 July 2025", "28 January 2025", "07/08/2025", "2025-07-08"],
                                 index=0)
        show_day = st.checkbox("Show Day", value=False)  # Default unchecked
    
    # Watermark settings
    use_watermark = st.checkbox("Add Watermark", value=True)  # Default checked now
    watermark_image = None
    
    if use_watermark:
        watermark_option = st.radio("Watermark Source", ["Pre-made", "Upload Your Own"])
        
        if watermark_option == "Pre-made":
            available_watermarks = [
                "Think Tank TV.png",
                "Wishful Vibes.png",  # This will be selected by default
                "Travellar Bharat.png",
                "Good Vibes.png",
                "naturevibes.png"  # Added new logo
            ]
            selected_watermark = st.selectbox("Select Watermark", available_watermarks, index=1)  # Wishful Vibes selected by default
            watermark_path = os.path.join("assets/logos", selected_watermark)
            if os.path.exists(watermark_path):
                watermark_image = Image.open(watermark_path).convert("RGBA")
        else:
            uploaded_watermark = st.file_uploader("Upload Watermark", type=["png"])
            if uploaded_watermark:
                watermark_image = Image.open(uploaded_watermark).convert("RGBA")
        
        watermark_opacity = st.slider("Watermark Opacity", 0.1, 1.0, 0.7)
    
    # Overlay settings
    use_overlay = st.checkbox("Use Pre-made Overlays", value=False)
    
    if use_overlay:
        overlay_theme = st.selectbox("Select Theme", ["Theme1", "Theme2"])
        
        # Random overlay selection
        random_overlay = st.checkbox("Random Overlay Selection", value=True)
        
        if not random_overlay:
            if greeting_type == "Good Morning":
                overlay_files = ["1.png", "2.png"]
            else:
                overlay_files = ["1.png", "3.png"]
        else:
            overlay_files = random.sample(["1.png", "2.png", "3.png", "4.png", "5.png"], 2)
        
        overlay_size = st.slider("Overlay Size", 0.1, 1.0, 0.5)
    
    # Coffee & Pet PNG Section
    st.markdown("---")
    st.markdown("### ☕🐾 Coffee & Pet PNG")
    use_coffee_pet = st.checkbox("Enable Coffee & Pet PNG", value=False)
    if use_coffee_pet:
        pet_size = st.slider("PNG Size", 0.1, 1.0, 0.3)
        
        # Get available pet PNGs from assets/pets folder
        pet_files = list_files("assets/pets", [".png", ".jpg", ".jpeg"])
        selected_pet = st.selectbox("Select Pet PNG", ["Random"] + pet_files)
        
        if selected_pet == "Random":
            selected_pet = random.choice(pet_files) if pet_files else None

# Process button at the top
if st.button("✨ Generate Photos", key="generate"):
    if uploaded_images:
        with st.spinner("Processing images..."):
            processed_images = []
            variant_images = []
            
            settings = {
                'greeting_type': greeting_type,
                'show_text': show_text,
                'main_size': main_size if show_text else 80,
                'show_wish': show_wish,
                'wish_size': wish_size if show_wish else 50,
                'show_date': show_date,
                'show_day': show_day if show_date else False,
                'date_size': date_size if show_date else 30,
                'date_format': date_format if show_date else "8 July 2025",
                'use_watermark': use_watermark,
                'watermark_image': watermark_image,
                'watermark_opacity': watermark_opacity if use_watermark else 0.7,
                'use_overlay': use_overlay,
                'overlay_files': overlay_files if use_overlay else [],
                'overlay_theme': overlay_theme if use_overlay else "",
                'overlay_size': overlay_size if use_overlay else 0.5,
                'use_coffee_pet': use_coffee_pet,
                'pet_size': pet_size if use_coffee_pet else 0.3,
                'selected_pet': selected_pet if use_coffee_pet else None
            }
            
            for uploaded_file in uploaded_images:
                try:
                    img = Image.open(uploaded_file).convert("RGBA")
                    
                    # Auto crop to 3:4 ratio
                    img = smart_crop(img)
                    
                    # Auto enhance
                    img = enhance_image_quality(img)
                    
                    # Apply overlays if enabled
                    if use_overlay:
                        for overlay_file in overlay_files:
                            overlay_path = os.path.join("assets/overlays", overlay_theme, overlay_file)
                            img = apply_overlay(img, overlay_path, overlay_size)
                    
                    if generate_variants:
                        # Create 3 variants with consistent text effects
                        text_effect = get_random_text_effect()
                        variants = []
                        for i in range(3):
                            variant = create_variant(img, settings, text_effect)
                            variants.append((generate_filename(), variant))
                        variant_images.extend(variants)
                    else:
                        # Create single version
                        draw = ImageDraw.Draw(img)
                        font = get_random_font()
                        text_color = get_random_color()
                        
                        # Add main text with consistent effect
                        if show_text:
                            font_main = font.font_variant(size=main_size)
                            text = greeting_type
                            text_width, text_height = get_text_size(draw, text, font_main)
                            
                            # Adjust font size if text is too wide
                            if text_width > img.width - 40:
                                font_main = adjust_font_size_to_fit(draw, text, img.width - 40, img.height//3, main_size)
                                text_width, text_height = get_text_size(draw, text, font_main)
                            
                            text_x = (img.width - text_width) // 2
                            text_y = 20  # Top position
                            
                            effect = apply_text_effects(draw, (text_x, text_y), text, font_main, text_color)
                        
                        # Add wish text with same effect
                        if show_wish:
                            font_wish = font.font_variant(size=wish_size)
                            wish_text = get_random_wish(greeting_type)
                            wish_width, wish_height = get_text_size(draw, wish_text, font_wish)
                            
                            # Adjust font size if text is too wide
                            if wish_width > img.width - 40:
                                font_wish = adjust_font_size_to_fit(draw, wish_text, img.width - 40, img.height//3, wish_size)
                                wish_width, wish_height = get_text_size(draw, wish_text, font_wish)
                            
                            wish_x = (img.width - wish_width) // 2
                            wish_y = text_y + main_size + 20 if show_text else 20
                            
                            apply_text_effects(draw, (wish_x, wish_y), wish_text, font_wish, text_color, effect)
                        
                        # Add date text with same effect
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
                            
                            # Adjust font size if text is too wide
                            if date_width > img.width - 40:
                                font_date = adjust_font_size_to_fit(draw, date_text, img.width - 40, img.height//3, date_size)
                                date_width, date_height = get_text_size(draw, date_text, font_date)
                            
                            date_x = (img.width - date_width) // 2
                            date_y = img.height - date_height - 20  # Bottom position
                            
                            # Adjust position if day text is too long
                            if show_day and "(" in date_text:
                                day_part = date_text[date_text.index("("):]
                                day_width, _ = get_text_size(draw, day_part, font_date)
                                if date_x + day_width > img.width - 20:
                                    date_x = img.width - day_width - 25
                            
                            apply_text_effects(draw, (date_x, date_y), date_text, font_date, text_color, effect)
                        
                        # Add watermark if enabled
                        if use_watermark and watermark_image:
                            watermark = watermark_image.copy()
                            
                            if watermark_opacity < 1.0:
                                alpha = watermark.split()[3]
                                alpha = ImageEnhance.Brightness(alpha).enhance(watermark_opacity)
                                watermark.putalpha(alpha)
                            
                            watermark.thumbnail((img.width//4, img.height//4))
                            pos = get_watermark_position(img, watermark)
                            
                            # Simple overlap avoidance
                            text_areas = []
                            if show_text:
                                text_areas.append((text_x, text_y, text_x + text_width, text_y + text_height))
                            if show_wish:
                                text_areas.append((wish_x, wish_y, wish_x + wish_width, wish_y + wish_height))
                            if show_date:
                                text_areas.append((date_x, date_y, date_x + date_width, date_y + date_height))
                            
                            for _ in range(3):
                                overlap = False
                                for (x1, y1, x2, y2) in text_areas:
                                    if (pos[0] < x2 and pos[0] + watermark.width > x1 and
                                        pos[1] < y2 and pos[1] + watermark.height > y1):
                                        overlap = True
                                        break
                                
                                if not overlap:
                                    break
                                else:
                                    pos = get_watermark_position(img, watermark)
                            
                            img.paste(watermark, pos, watermark)
                        
                        # Apply Coffee & Pet PNG if enabled
                        if use_coffee_pet and selected_pet:
                            pet_path = os.path.join("assets/pets", selected_pet)
                            if os.path.exists(pet_path):
                                pet_img = Image.open(pet_path).convert("RGBA")
                                pet_img = pet_img.resize(
                                    (int(img.width * pet_size), 
                                    int(img.height * pet_size * (pet_img.height/pet_img.width))),
                                    Image.LANCZOS
                                )
                                # Position at bottom right
                                x = img.width - pet_img.width - 20
                                y = img.height - pet_img.height - 20
                                img.paste(pet_img, (x, y), pet_img)
                        
                        # Final quality enhancements
                        img = enhance_image_quality(img)
                        img = upscale_text_elements(img, scale_factor=2)
                        
                        processed_images.append((generate_filename(), img))
                
                except Exception as e:
                    st.error(f"Error processing {uploaded_file.name}: {str(e)}")
                    continue

            # Store all images in session state
            st.session_state.generated_images = processed_images + variant_images
            
            # Display results
            if st.session_state.generated_images:
                st.success(f"Successfully processed {len(st.session_state.generated_images)} images!")
            else:
                st.warning("No images were processed successfully.")
    else:
        st.warning("Please upload at least one image.")

# Display previews with individual download options
if st.session_state.generated_images:
    # Create zip file
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
        for filename, img in st.session_state.generated_images:
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG', quality=95)
            zip_file.writestr(filename, img_bytes.getvalue())
    
    # Download button for all
    st.download_button(
        label="⬇️ Download All Photos",
        data=zip_buffer.getvalue(),
        file_name="generated_photos.zip",
        mime="application/zip"
    )
    
    # Show previews with individual download options
    st.markdown("### 📸 Preview")
    cols = st.columns(3)
    
    for i, (filename, img) in enumerate(st.session_state.generated_images[:9]):  # Show max 9 previews
        with cols[i % 3]:
            st.image(img, use_container_width=True)
            st.caption(filename)
            
            # Individual download button
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG', quality=95)
            st.download_button(
                label="⬇️ Download",
                data=img_bytes.getvalue(),
                file_name=filename,
                mime="image/jpeg",
                key=f"download_{i}"
                )
