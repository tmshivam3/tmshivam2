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
    bbox = draw.textbbox((0, 0), text, font=font, anchor="lt")
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def get_random_font():
    fonts = list_files("assets/fonts", [".ttf", ".otf"])
    if not fonts:
        return ImageFont.load_default()
    
    try:
        font_path = os.path.join("assets/fonts", random.choice(fonts))
        return ImageFont.truetype(font_path, 80)
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
    # 50% chance bottom (left/right corner), else random
    if random.random() < 0.5:
        x = random.choice([20, img.width - watermark.width - 20])
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
    
    img = ImageEnhance.Sharpness(img).enhance(1.5)
    img = ImageEnhance.Contrast(img).enhance(1.1)
    
    hist = img.histogram()
    if sum(hist[:100]) > sum(hist[-100:]):
        img = ImageEnhance.Brightness(img).enhance(1.1)
    
    return img

def apply_text_effect(draw, position, text, font, effect_settings, texture_img=None):
    x, y = position
    effect_type = effect_settings['type']
    main_color = effect_settings.get('main_color', (255, 255, 255))
    outline_color = effect_settings.get('outline_color', (0, 0, 0))
    
    # High quality rendering
    scale_factor = 2
    text_width, text_height = get_text_size(draw, text, font)
    temp_size = (text_width * scale_factor, text_height * scale_factor)

    if effect_settings.get('use_texture', False) and texture_img:
        temp_texture = texture_img.resize(
            (int(texture_img.width * scale_factor), 
             int(texture_img.height * scale_factor)),
            Image.LANCZOS
        )
        mask = Image.new("L", temp_size)
        mask_draw = ImageDraw.Draw(mask)
        temp_font = font.font_variant(size=font.size*scale_factor)
        mask_draw.text((0, 0), text, font=temp_font, fill=255)
        textured_text = Image.new("RGBA", temp_size)
        textured_text.paste(temp_texture, (0, 0), mask)
        textured_text = textured_text.resize((text_width, text_height), Image.LANCZOS)
        draw.bitmap((x, y), textured_text.convert("L"), fill=main_color)
        return effect_settings

    # Create high-res canvas
    temp_img = Image.new("RGBA", temp_size)
    temp_draw = ImageDraw.Draw(temp_img)
    temp_font = font.font_variant(size=font.size*scale_factor)

    if effect_type in ["white_black_outline", "full_random"]:
        outline_size = 2 * scale_factor
        for ox in range(-outline_size, outline_size+1, scale_factor//2):
            for oy in range(-outline_size, outline_size+1, scale_factor//2):
                if ox != 0 or oy != 0:
                    temp_draw.text(
                        (outline_size+ox, outline_size+oy), 
                        text, 
                        font=temp_font, 
                        fill=outline_color
                    )

    temp_draw.text((outline_size, outline_size), text, font=temp_font, fill=main_color)
    
    # Downscale with anti-aliasing
    temp_img = temp_img.resize((text_width, text_height), Image.LANCZOS)
    draw.bitmap((x, y), temp_img.convert("L"), fill=main_color)
    
    return effect_settings

def create_variant(original_img, settings):
    img = original_img.copy()
    draw = ImageDraw.Draw(img)
    font = get_random_font()
    
    texture_img = None
    if settings.get('use_texture', False) and settings.get('texture_image', None):
        texture_img = settings['texture_image']
    
    effect_settings = {
        'type': settings.get('text_effect', None),
        'use_texture': settings.get('use_texture', False),
        'main_color': (255, 255, 255)
    }
    
    if settings['show_text']:
        font_main = font.font_variant(size=90)
        text = settings['greeting_type']
        text_width, text_height = get_text_size(draw, text, font_main)
        
        max_text_x = max(20, img.width - text_width - 20)
        text_x = random.randint(20, max_text_x) if max_text_x > 20 else 20
        max_text_y = max(20, img.height // 3)
        text_y = random.randint(20, max_text_y) if max_text_y > 20 else 20
        
        effect_settings = apply_text_effect(
            draw, 
            (text_x, text_y), 
            text, 
            font_main,
            effect_settings,
            texture_img=texture_img
        )
    
    if settings['show_wish']:
        font_wish = font.font_variant(size=60)
        wish_text = get_random_wish(settings['greeting_type'])
        wish_width, wish_height = get_text_size(draw, wish_text, font_wish)
        
        if settings['show_text']:
            max_wish_x = max(20, img.width - wish_width - 20)
            wish_x = random.randint(20, max_wish_x) if max_wish_x > 20 else 20
            wish_y = text_y + 90 + random.randint(10, 30)
        else:
            max_wish_x = max(20, img.width - wish_width - 20)
            wish_x = random.randint(20, max_wish_x) if max_wish_x > 20 else 20
            max_wish_y = max(20, img.height // 2)
            wish_y = random.randint(20, max_wish_y) if max_wish_y > 20 else 20
        
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
    
    if settings['use_watermark'] and settings['watermark_image']:
        watermark = settings['watermark_image'].copy()
        
        if settings['watermark_opacity'] < 1.0:
            alpha = watermark.split()[3]
            alpha = ImageEnhance.Brightness(alpha).enhance(settings['watermark_opacity'])
            watermark.putalpha(alpha)
        
        watermark.thumbnail((img.width//4, img.height//4))
        pos = get_watermark_position(img, watermark)
        
        for _ in range(3):
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
    return img.convert("RGB")

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
        ["White Only", "White with Black Outline", "Full Random"],
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
    show_wish = st.checkbox("Show Wish", value=True)
    
    show_date = st.checkbox("Show Date", value=False)
    if show_date:
        date_size = st.slider("Date Text Size", 10, 200, 30)
        date_format = st.selectbox("Date Format", 
                                 ["8 July 2025", "28 January 2025", "07/08/2025", "2025-07-08"],
                                 index=0)
        show_day = st.checkbox("Show Day", value=False)
    
    use_watermark = st.checkbox("Add Watermark", value=True)
    watermark_image = None
    
    if use_watermark:
        watermark_files = list_files("assets/logos", [".png", ".jpg", ".jpeg"])
        if watermark_files:
            default_index = 0
            if "wishful vibes.png" in watermark_files:
                default_index = watermark_files.index("wishful vibes.png")
            selected_watermark = st.selectbox("Select Watermark", watermark_files, index=default_index)
            watermark_path = os.path.join("assets/logos", selected_watermark)
            if os.path.exists(watermark_path):
                watermark_image = Image.open(watermark_path).convert("RGBA")
        
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
                "Full Random": "full_random"
            }
            selected_effect = effect_mapping[text_effect]
            
            settings = {
                'greeting_type': greeting_type,
                'show_text': show_text,
                'show_wish': show_wish,
                'show_date': show_date,
                'show_day': show_day if show_date else False,
                'date_size': date_size if show_date else 30,
                'date_format': date_format if show_date else "8 July 2025",
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
                    img = Image.open(uploaded_file).convert("RGBA")
                    img = smart_crop(img)
                    img = enhance_image_quality(img)
                    
                    if use_overlay:
                        for overlay_file in overlay_files:
                            overlay_path = os.path.join("assets/overlays", overlay_theme, overlay_file)
                            if os.path.exists(overlay_path):
                                img = apply_overlay(img, overlay_path, overlay_size)
                    
                    if generate_variants:
                        for i in range(3):
                            variant = create_variant(img, settings)
                            variant_images.append((generate_filename(), variant))
                    else:
                        result = create_variant(img, settings)
                        processed_images.append((generate_filename(), result))
                
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
