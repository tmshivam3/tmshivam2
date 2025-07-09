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
    .coffee-pet-section {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: #000000;
        padding: 10px;
        border-top: 1px solid #ffff00;
        z-index: 100;
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

def apply_text_effects(draw, position, text, font, color):
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

def format_date(date_format="%d %B %Y", include_day=False):
    today = datetime.datetime.now()
    
    # Check if we're within 4-5 hours of next day (for "Advance" feature)
    next_day = today + datetime.timedelta(days=1)
    time_to_next_day = (next_day.replace(hour=0, minute=0, second=0) - today.replace(hour=0, minute=0, second=0)
    show_advance_day = time_to_next_day.total_seconds() <= 5 * 3600  # 5 hours
    
    if include_day:
        day_format = "%A"  # Full weekday name
        if show_advance_day:
            return today.strftime(date_format), f"Advance {next_day.strftime(day_format)}"
        return today.strftime(date_format), today.strftime(day_format)
    return today.strftime(date_format)

def apply_overlay(image, overlay_path, size=0.5):
    try:
        overlay = Image.open(overlay_path).convert("RGBA")
        new_size = (int(image.width * size), int(image.height * size))
        overlay = overlay.resize(new_size)
        
        # Random position but within bounds
        max_x = image.width - overlay.width - 20
        max_y = image.height - overlay.height - 20
        x = random.randint(20, max_x)
        y = random.randint(20, max_y)
        
        image.paste(overlay, (x, y), overlay)
    except Exception as e:
        st.error(f"Error applying overlay: {str(e)}")
    return image

def generate_filename(index=None):
    now = datetime.datetime.now()
    # Generate future time (current time + 2-10 minutes)
    future_minutes = random.randint(2, 10)
    future_time = now + datetime.timedelta(minutes=future_minutes)
    
    if index is not None:
        return f"Picsart_{future_time.strftime('%y-%m-%d_%H-%M-%S')}_v{index+1}.jpg"
    return f"Picsart_{future_time.strftime('%y-%m-%d_%H-%M-%S')}.jpg"

def get_watermark_position(img, watermark):
    # 70% chance to be at bottom, 30% chance to be random
    if random.random() < 0.7:
        # Bottom position (random left/right)
        x = random.choice([
            20,  # left
            img.width - watermark.width - 20  # right
        ])
        y = img.height - watermark.height - 20
    else:
        # Random position (avoid center)
        max_x = img.width - watermark.width - 20
        max_y = img.height - watermark.height - 20
        x = random.randint(20, max_x)
        y = random.randint(20, max_y)
    
    return (x, y)

def enhance_image_quality(img):
    """Enhance image quality with multiple techniques"""
    # Convert to RGB if not already
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Enhance contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.2)
    
    # Enhance sharpness
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(1.5)
    
    # Enhance color
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(1.1)
    
    return img

def scale_text_for_sharpness(img, scale_factor=2):
    """Scale up text elements for better sharpness"""
    # This would be applied to text layers in the image
    # In a real implementation, we'd need to identify text regions
    # For now, we'll just scale up the whole image and then downscale
    original_size = img.size
    scaled_size = (img.width * scale_factor, img.height * scale_factor)
    
    # Scale up with high-quality resampling
    img = img.resize(scaled_size, Image.LANCZOS)
    
    # Scale back down with anti-aliasing
    img = img.resize(original_size, Image.LANCZOS)
    
    return img

def create_variant(original_img, settings):
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
        
        # Varied positioning
        text_x = random.randint(20, img.width - text_width - 20)
        text_y = random.randint(20, img.height // 3)
        
        apply_text_effects(draw, (text_x, text_y), text, font_main, text_color)
    
    # Add wish text
    if settings['show_wish']:
        font_wish = font.font_variant(size=settings['wish_size'])
        wish_text = get_random_wish(settings['greeting_type'])
        wish_width, wish_height = get_text_size(draw, wish_text, font_wish)
        
        # Position relative to main text or random
        if settings['show_text']:
            wish_x = random.randint(20, img.width - wish_width - 20)
            wish_y = text_y + settings['main_size'] + random.randint(10, 30)
        else:
            wish_x = random.randint(20, img.width - wish_width - 20)
            wish_y = random.randint(20, img.height // 2)
        
        apply_text_effects(draw, (wish_x, wish_y), wish_text, font_wish, text_color)
    
    # Add date text
    if settings['show_date']:
        font_date = font.font_variant(size=settings['date_size'])
        
        # Format date based on selection
        if settings['date_format'] == "8 July 2025":
            date_text, day_text = format_date("%d %B %Y", settings['show_day'])
        elif settings['date_format'] == "28 January 2025":
            date_text, day_text = format_date("%d %B %Y", settings['show_day'])
        elif settings['date_format'] == "07/08/2025":
            date_text, day_text = format_date("%m/%d/%Y", settings['show_day'])
        else:
            date_text, day_text = format_date("%Y-%m-%d", settings['show_day'])
            
        date_width, date_height = get_text_size(draw, date_text, font_date)
        
        # Position date at bottom
        date_x = random.randint(20, img.width - date_width - 20)
        date_y = img.height - date_height - 20  # Bottom position
        
        apply_text_effects(draw, (date_x, date_y), date_text, font_date, text_color)
        
        # Add day text if enabled
        if settings['show_day']:
            font_day = font.font_variant(size=settings['date_size'] + 10)  # Slightly larger than date
            day_width, day_height = get_text_size(draw, day_text, font_day)
            
            # Position day above date, not centered
            day_x = random.randint(20, img.width - day_width - 20)
            day_y = date_y - day_height - 10
            
            # Ensure day doesn't overlap with other elements
            for _ in range(5):  # Try 5 positions
                overlap = False
                if settings['show_text'] and (day_x < text_x + text_width and day_x + day_width > text_x and
                                           day_y < text_y + text_height and day_y + day_height > text_y):
                    overlap = True
                if not overlap and settings['show_wish']:
                    if (day_x < wish_x + wish_width and day_x + day_width > wish_x and
                        day_y < wish_y + wish_height and day_y + day_height > wish_y):
                        overlap = True
                
                if not overlap:
                    break
                else:
                    day_x = random.randint(20, img.width - day_width - 20)
                    day_y = date_y - day_height - 10
            
            apply_text_effects(draw, (day_x, day_y), day_text, font_day, text_color)
    
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
    if settings['use_coffee_pet'] and settings['coffee_pet_image']:
        pet_img = settings['coffee_pet_image'].copy()
        
        # Resize based on slider
        pet_size = int(min(img.width, img.height) * settings['coffee_pet_size'])
        pet_img = pet_img.resize((pet_size, pet_size))
        
        # Position at bottom (random left/right)
        pet_x = random.choice([
            20,  # left
            img.width - pet_size - 20  # right
        ])
        pet_y = img.height - pet_size - 20
        
        img.paste(pet_img, (pet_x, pet_y), pet_img)
    
    return img.convert("RGB")

# =================== MAIN APP ===================
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
        show_day = st.checkbox("Show Day", value=False)  # Day checkbox
    
    # Watermark settings
    use_watermark = st.checkbox("Add Watermark", value=False)
    watermark_image = None
    
    if use_watermark:
        watermark_option = st.radio("Watermark Source", ["Pre-made", "Upload Your Own"])
        
        if watermark_option == "Pre-made":
            available_watermarks = [
                "Think Tank TV.png",
                "Wishful Vibes.png",
                "Travellar Bharat.png",
                "Good Vibes.png"
            ]
            selected_watermark = st.selectbox("Select Watermark", available_watermarks)
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

# Coffee & Pet PNG section (fixed at bottom)
with st.container():
    st.markdown('<div class="coffee-pet-section">', unsafe_allow_html=True)
    use_coffee_pet = st.checkbox("Coffee&Pet PNG", value=False, key="coffee_pet_checkbox")
    
    coffee_pet_image = None
    if use_coffee_pet:
        # Load available pet PNGs
        pet_files = list_files("assets/pets", [".png", ".jpg", ".jpeg"])
        
        col1, col2 = st.columns(2)
        with col1:
            coffee_pet_size = st.slider("Pet Size", 0.1, 0.5, 0.2, key="pet_size_slider")
        
        with col2:
            if pet_files:
                selected_pet = st.selectbox("Select Pet", pet_files, key="pet_select")
                if selected_pet:
                    pet_path = os.path.join("assets/pets", selected_pet)
                    coffee_pet_image = Image.open(pet_path).convert("RGBA")
                
                if st.button("Random Select", key="random_pet"):
                    selected_pet = random.choice(pet_files)
                    pet_path = os.path.join("assets/pets", selected_pet)
                    coffee_pet_image = Image.open(pet_path).convert("RGBA")
            else:
                st.warning("No pet PNGs found in assets/pets folder")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Process button at the top
if st.button("✨ Generate Photos", key="generate"):
    if uploaded_images:
        with st.spinner("Processing images..."):
            processed_images = []
            variant_images = []
            
            settings = {
                'greeting_type': greeting_type,
                'show_text': show_text,
                'main_size': main_size,
                'show_wish': show_wish,
                'wish_size': wish_size,
                'show_date': show_date,
                'date_size': date_size if show_date else 30,
                'date_format': date_format if show_date else "8 July 2025",
                'show_day': show_day if show_date else False,
                'use_watermark': use_watermark,
                'watermark_image': watermark_image,
                'watermark_opacity': watermark_opacity if use_watermark else 0.7,
                'use_overlay': use_overlay,
                'overlay_files': overlay_files if use_overlay else [],
                'overlay_theme': overlay_theme if use_overlay else "",
                'overlay_size': overlay_size if use_overlay else 0.5,
                'use_coffee_pet': use_coffee_pet,
                'coffee_pet_image': coffee_pet_image,
                'coffee_pet_size': coffee_pet_size if use_coffee_pet else 0.2
            }
            
            for uploaded_file in uploaded_images:
                try:
                    img = Image.open(uploaded_file).convert("RGBA")
                    
                    # Auto crop to 3:4 ratio
                    img = smart_crop(img)
                    
                    # Enhance image quality
                    img = enhance_image_quality(img)
                    
                    # Apply overlays if enabled
                    if use_overlay:
                        for overlay_file in overlay_files:
                            overlay_path = os.path.join("assets/overlays", overlay_theme, overlay_file)
                            img = apply_overlay(img, overlay_path, overlay_size)
                    
                    if generate_variants:
                        # Create 3 variants
                        variants = []
                        for i in range(3):
                            variant = create_variant(img, settings)
                            # Scale text for sharpness
                            variant = scale_text_for_sharpness(variant, 2)
                            variants.append((generate_filename(i), variant))
                        variant_images.extend(variants)
                    else:
                        # Create single version
                        draw = ImageDraw.Draw(img)
                        font = get_random_font()
                        text_color = get_random_color()
                        
                        # Add main text
                        if show_text:
                            font_main = font.font_variant(size=main_size)
                            text = greeting_type
                            text_width, text_height = get_text_size(draw, text, font_main)
                            
                            text_x = (img.width - text_width) // 2
                            text_y = 20  # Top position
                            
                            apply_text_effects(draw, (text_x, text_y), text, font_main, text_color)
                        
                        # Add wish text
                        if show_wish:
                            font_wish = font.font_variant(size=wish_size)
                            wish_text = get_random_wish(greeting_type)
                            wish_width, wish_height = get_text_size(draw, wish_text, font_wish)
                            
                            wish_x = (img.width - wish_width) // 2
                            wish_y = text_y + main_size + 20 if show_text else 20
                            
                            apply_text_effects(draw, (wish_x, wish_y), wish_text, font_wish, text_color)
                        
                        # Add date text
                        if show_date:
                            font_date = font.font_variant(size=date_size)
                            
                            if date_format == "8 July 2025":
                                date_text, day_text = format_date("%d %B %Y", show_day)
                            elif date_format == "28 January 2025":
                                date_text, day_text = format_date("%d %B %Y", show_day)
                            elif date_format == "07/08/2025":
                                date_text, day_text = format_date("%m/%d/%Y", show_day)
                            else:
                                date_text, day_text = format_date("%Y-%m-%d", show_day)
                                
                            date_width, date_height = get_text_size(draw, date_text, font_date)
                            
                            date_x = (img.width - date_width) // 2
                            date_y = img.height - date_height - 20  # Bottom position
                            
                            apply_text_effects(draw, (date_x, date_y), date_text, font_date, text_color)
                            
                            # Add day text if enabled
                            if show_day:
                                font_day = font.font_variant(size=date_size + 10)
                                day_width, day_height = get_text_size(draw, day_text, font_day)
                                
                                # Position day above date, not centered
                                day_x = random.randint(20, img.width - day_width - 20)
                                day_y = date_y - day_height - 10
                                
                                apply_text_effects(draw, (day_x, day_y), day_text, font_day, text_color)
                        
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
                                
                                if not overlap:
                                    break
                                else:
                                    pos = get_watermark_position(img, watermark)
                            
                            img.paste(watermark, pos, watermark)
                        
                        # Add Coffee & Pet PNG if enabled
                        if use_coffee_pet and coffee_pet_image:
                            pet_img = coffee_pet_image.copy()
                            
                            # Resize based on slider
                            pet_size = int(min(img.width, img.height) * coffee_pet_size)
                            pet_img = pet_img.resize((pet_size, pet_size))
                            
                            # Position at bottom (random left/right)
                            pet_x = random.choice([
                                20,  # left
                                img.width - pet_size - 20  # right
                            ])
                            pet_y = img.height - pet_size - 20
                            
                            img.paste(pet_img, (pet_x, pet_y), pet_img)
                        
                        # Scale text for sharpness
                        img = scale_text_for_sharpness(img, 2)
                        
                        processed_images.append((generate_filename(), img.convert("RGB")))
                
                except Exception as e:
                    st.error(f"Error processing {uploaded_file.name}: {str(e)}")
                    continue
            
            # Display and download results
            if generate_variants and variant_images:
                st.success(f"Generated {len(variant_images)} variants!")
                
                # Group variants by original image
                variant_groups = {}
                for name, img in variant_images:
                    base_name = name.split('_v')[0]
                    if base_name not in variant_groups:
                        variant_groups[base_name] = []
                    variant_groups[base_name].append((name, img))
                
                # Display each group
                for base_name, variants in variant_groups.items():
                    st.markdown(f"**Variants for {base_name}**")
                    cols = st.columns(len(variants))
                    for idx, (name, img) in enumerate(variants):
                        with cols[idx]:
                            st.image(img, use_column_width=True)
                            st.caption(name)
                
                # Download all button
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
                    for name, img in variant_images:
                        img_bytes = io.BytesIO()
                        img.save(img_bytes, format='JPEG', quality=95)
                        zip_file.writestr(name, img_bytes.getvalue())
                
                st.download_button(
                    label="📥 Download All Variants",
                    data=zip_buffer.getvalue(),
                    file_name="generated_variants.zip",
                    mime="application/zip"
                )
            
            elif processed_images:
                st.success(f"Processed {len(processed_images)} images!")
                
                # Display images
                cols = st.columns(min(3, len(processed_images)))
                for idx, (name, img) in enumerate(processed_images):
                    with cols[idx % 3]:
                        st.image(img, use_column_width=True)
                        st.caption(name)
                
                # Download all button
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
                    for name, img in processed_images:
                        img_bytes = io.BytesIO()
                        img.save(img_bytes, format='JPEG', quality=95)
                        zip_file.writestr(name, img_bytes.getvalue())
                
                st.download_button(
                    label="📥 Download All",
                    data=zip_buffer.getvalue(),
                    file_name="generated_images.zip",
                    mime="application/zip"
                )
    else:
        st.warning("Please upload at least one image")
