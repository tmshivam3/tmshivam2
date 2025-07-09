import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps
import os
import io
import random
import datetime
import zipfile
import numpy as np
import time

# =================== CONFIG ===================
st.set_page_config(page_title="⚡ Ultra HD Photo Generator", layout="wide")

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
    </style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
    <div style='background-color: #000000; padding: 15px; border-radius: 8px; margin-bottom: 20px; border: 2px solid #ffff00;'>
        <h1 style='text-align: center; color: #ffff00; margin: 0;'>⚡ Ultra HD Photo Generator</h1>
    </div>
""", unsafe_allow_html=True)

# =================== UTILS ===================
def list_files(folder, exts):
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
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

def get_random_color():
    colors = [
        (255, 255, 0), (255, 255, 255), (0, 255, 255),
        (255, 0, 255), (255, 165, 0), (0, 255, 0),
        (255, 0, 0), (0, 0, 255)
    ]
    return random.choice(colors)

def get_random_text_effect():
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
                if x != 0 or y != 0:
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

def format_date(date_format="%d %B %Y"):
    today = datetime.datetime.now()
    return today.strftime(date_format)

def apply_overlay(image, overlay_path, size=0.5):
    try:
        overlay = Image.open(overlay_path).convert("RGBA")
        # Upscale overlay to HD quality
        overlay = overlay.resize((1080, 1349), Image.LANCZOS)
        new_size = (int(image.width * size), int(image.height * size))
        overlay = overlay.resize(new_size, Image.LANCZOS)
        
        max_x = image.width - overlay.width - 20
        max_y = image.height - overlay.height - 20
        x = random.randint(20, max_x)
        y = random.randint(20, max_y)
        
        image.paste(overlay, (x, y), overlay)
    except Exception as e:
        st.error(f"Error applying overlay: {str(e)}")
    return image

def generate_filename(base_time, index=None):
    # Add time gap between photos (2-4 minutes)
    time_gap = random.randint(120, 240)  # 2-4 minutes in seconds
    new_time = base_time + datetime.timedelta(seconds=time_gap)
    
    if index is not None:
        return f"Picsart_{new_time.strftime('%y-%m-%d_%H-%M-%S-%f')[:-3]}_v{index+1}.png"
    return f"Picsart_{new_time.strftime('%y-%m-%d_%H-%M-%S-%f')[:-3]}.png"

def get_watermark_position(img, watermark):
    if random.random() < 0.7:
        x = random.choice([20, img.width - watermark.width - 20])
        y = img.height - watermark.height - 20
    else:
        max_x = img.width - watermark.width - 20
        max_y = img.height - watermark.height - 20
        x = random.randint(20, max_x)
        y = random.randint(20, max_y)
    return (x, y)

def create_variant(original_img, settings, base_time):
    img = original_img.copy()
    draw = ImageDraw.Draw(img)
    font = get_random_font()
    text_color = get_random_color()
    
    # Enhance text quality
    font = ImageFont.truetype(font.path, font.size * 2)  # Double font size for HD
    
    if settings['show_text']:
        font_main = font.font_variant(size=settings['main_size']*2)  # HD scaling
        text = settings['greeting_type']
        text_width, text_height = get_text_size(draw, text, font_main)
        
        text_x = random.randint(20, img.width - text_width - 20)
        text_y = random.randint(20, img.height // 3)
        
        apply_text_effects(draw, (text_x, text_y), text, font_main, text_color)
    
    if settings['show_wish']:
        font_wish = font.font_variant(size=settings['wish_size']*2)  # HD scaling
        wish_text = get_random_wish(settings['greeting_type'])
        wish_width, wish_height = get_text_size(draw, wish_text, font_wish)
        
        if settings['show_text']:
            wish_x = random.randint(20, img.width - wish_width - 20)
            wish_y = text_y + settings['main_size'] + random.randint(10, 30)
        else:
            wish_x = random.randint(20, img.width - wish_width - 20)
            wish_y = random.randint(20, img.height // 2)
        
        apply_text_effects(draw, (wish_x, wish_y), wish_text, font_wish, text_color)
    
    if settings['show_date']:
        font_date = font.font_variant(size=settings['date_size']*2)  # HD scaling
        
        if settings['date_format'] == "8 July 2025":
            date_text = format_date("%d %B %Y")
        elif settings['date_format'] == "28 January 2025":
            date_text = format_date("%d %B %Y")
        elif settings['date_format'] == "07/08/2025":
            date_text = format_date("%m/%d/%Y")
        else:
            date_text = format_date("%Y-%m-%d")
            
        date_width, date_height = get_text_size(draw, date_text, font_date)
        
        date_x = random.randint(20, img.width - date_width - 20)
        date_y = img.height - date_height - 20
        
        apply_text_effects(draw, (date_x, date_y), date_text, font_date, text_color)
    
    if settings['use_watermark'] and settings['watermark_image']:
        watermark = settings['watermark_image'].copy()
        
        if settings['watermark_opacity'] < 1.0:
            alpha = watermark.split()[3]
            alpha = ImageEnhance.Brightness(alpha).enhance(settings['watermark_opacity'])
            watermark.putalpha(alpha)
        
        watermark.thumbnail((img.width//4, img.height//4), Image.LANCZOS)
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
    
    return img.convert("RGB")

# =================== MAIN APP ===================
uploaded_images = st.file_uploader("📁 Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# Settings sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    greeting_type = st.selectbox("Greeting Type", ["Good Morning", "Good Afternoon", "Good Evening", "Good Night"])
    
    generate_variants = st.checkbox("Generate 3 Variants per Photo", value=False)
    
    show_text = st.checkbox("Show Greeting", value=True)
    if show_text:
        main_size = st.slider("Main Text Size", 10, 200, 80)
    
    show_wish = st.checkbox("Show Wish", value=True)
    if show_wish:
        wish_size = st.slider("Wish Text Size", 10, 200, 50)
    
    show_date = st.checkbox("Show Date", value=False)
    if show_date:
        date_size = st.slider("Date Text Size", 10, 200, 30)
        date_format = st.selectbox("Date Format", 
                                 ["8 July 2025", "28 January 2025", "07/08/2025", "2025-07-08"],
                                 index=0)
    
    use_watermark = st.checkbox("Add Watermark", value=False)
    watermark_image = None
    
    if use_watermark:
        watermark_option = st.radio("Watermark Source", ["Pre-made", "Upload Your Own"])
        
        if watermark_option == "Pre-made":
            # Include all available watermarks dynamically
            available_watermarks = list_files("assets/logos", [".png", ".jpg", ".jpeg"])
            if not available_watermarks:
                st.warning("No watermarks found in assets/logos folder")
            else:
                selected_watermark = st.selectbox("Select Watermark", available_watermarks)
                watermark_path = os.path.join("assets/logos", selected_watermark)
                if os.path.exists(watermark_path):
                    watermark_image = Image.open(watermark_path).convert("RGBA")
        else:
            uploaded_watermark = st.file_uploader("Upload Watermark", type=["png"])
            if uploaded_watermark:
                watermark_image = Image.open(uploaded_watermark).convert("RGBA")
                # Save uploaded watermark for future use
                os.makedirs("assets/logos", exist_ok=True)
                watermark_image.save(f"assets/logos/{uploaded_watermark.name}")
        
        watermark_opacity = st.slider("Watermark Opacity", 0.1, 1.0, 0.7)
    
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

# Font uploader
with st.sidebar:
    st.markdown("### 🆕 Upload Assets")
    uploaded_font = st.file_uploader("Upload New Font (.ttf/.otf)", type=["ttf", "otf"])
    if uploaded_font:
        os.makedirs("assets/fonts", exist_ok=True)
        with open(f"assets/fonts/{uploaded_font.name}", "wb") as f:
            f.write(uploaded_font.getbuffer())
        st.success(f"Font {uploaded_font.name} uploaded successfully!")

# Process button
if st.button("✨ Generate Ultra HD Photos", key="generate"):
    if uploaded_images:
        with st.spinner("Processing images in Ultra HD..."):
            processed_images = []
            variant_images = []
            base_time = datetime.datetime.now()
            
            settings = {
                'greeting_type': greeting_type,
                'show_text': show_text,
                'main_size': main_size,
                'show_wish': show_wish,
                'wish_size': wish_size,
                'show_date': show_date,
                'date_size': date_size if show_date else 30,
                'date_format': date_format if show_date else "8 July 2025",
                'use_watermark': use_watermark,
                'watermark_image': watermark_image,
                'watermark_opacity': watermark_opacity if use_watermark else 0.7,
                'use_overlay': use_overlay,
                'overlay_files': overlay_files if use_overlay else [],
                'overlay_theme': overlay_theme if use_overlay else "",
                'overlay_size': overlay_size if use_overlay else 0.5
            }
            
            for uploaded_file in uploaded_images:
                try:
                    img = Image.open(uploaded_file).convert("RGBA")
                    
                    # Upscale original image to HD
                    img = img.resize((1080, 1349), Image.LANCZOS)
                    img = smart_crop(img)
                    
                    # Ultra HD enhancement
                    img = ImageEnhance.Contrast(img).enhance(1.2)
                    img = ImageEnhance.Sharpness(img).enhance(2.0)
                    img = ImageEnhance.Color(img).enhance(1.1)
                    
                    if use_overlay:
                        for overlay_file in overlay_files:
                            overlay_path = os.path.join("assets/overlays", overlay_theme, overlay_file)
                            img = apply_overlay(img, overlay_path, overlay_size)
                    
                    if generate_variants:
                        variants = []
                        for i in range(3):
                            variant = create_variant(img, settings, base_time)
                            variants.append((generate_filename(base_time, i), variant))
                            base_time += datetime.timedelta(seconds=random.randint(120, 240))
                        variant_images.extend(variants)
                    else:
                        draw = ImageDraw.Draw(img)
                        font = get_random_font()
                        # HD font scaling
                        font = ImageFont.truetype(font.path, font.size * 2)
                        text_color = get_random_color()
                        
                        if show_text:
                            font_main = font.font_variant(size=main_size*2)
                            text = greeting_type
                            text_width, text_height = get_text_size(draw, text, font_main)
                            
                            text_x = (img.width - text_width) // 2
                            text_y = 20
                            
                            apply_text_effects(draw, (text_x, text_y), text, font_main, text_color)
                        
                        if show_wish:
                            font_wish = font.font_variant(size=wish_size*2)
                            wish_text = get_random_wish(greeting_type)
                            wish_width, wish_height = get_text_size(draw, wish_text, font_wish)
                            
                            wish_x = (img.width - wish_width) // 2
                            wish_y = text_y + main_size + 20 if show_text else 20
                            
                            apply_text_effects(draw, (wish_x, wish_y), wish_text, font_wish, text_color)
                        
                        if show_date:
                            font_date = font.font_variant(size=date_size*2)
                            
                            if date_format == "8 July 2025":
                                date_text = format_date("%d %B %Y")
                            elif date_format == "28 January 2025":
                                date_text = format_date("%d %B %Y")
                            elif date_format == "07/08/2025":
                                date_text = format_date("%m/%d/%Y")
                            else:
                                date_text = format_date("%Y-%m-%d")
                                
                            date_width, date_height = get_text_size(draw, date_text, font_date)
                            
                            date_x = (img.width - date_width) // 2
                            date_y = img.height - date_height - 20
                            
                            apply_text_effects(draw, (date_x, date_y), date_text, font_date, text_color)
                        
                        if use_watermark and watermark_image:
                            watermark = watermark_image.copy()
                            
                            if watermark_opacity < 1.0:
                                alpha = watermark.split()[3]
                                alpha = ImageEnhance.Brightness(alpha).enhance(watermark_opacity)
                                watermark.putalpha(alpha)
                            
                            watermark.thumbnail((img.width//4, img.height//4), Image.LANCZOS)
                            pos = get_watermark_position(img, watermark)
                            
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
                        
                        processed_images.append((generate_filename(base_time), img.convert("RGB")))
                        base_time += datetime.timedelta(seconds=random.randint(120, 240))
                
                except Exception as e:
                    st.error(f"Error processing {uploaded_file.name}: {str(e)}")
            
            if generate_variants:
                st.session_state.variant_images = variant_images
            else:
                st.session_state.processed_images = processed_images
            st.success(f"✅ Generated {len(variant_images if generate_variants else processed_images)} Ultra HD photos!")

# Display results
if 'processed_images' in st.session_state and st.session_state.processed_images:
    cols = st.columns(3)
    for idx, (name, img) in enumerate(st.session_state.processed_images):
        with cols[idx % 3]:
            st.image(img)
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="PNG", quality=100, optimize=True)
            st.download_button(
                label=f"⬇️ {name}",
                data=img_bytes.getvalue(),
                file_name=name,
                mime="image/png",
                key=f"dl_{idx}"
            )
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for name, img in st.session_state.processed_images:
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="PNG", quality=100, optimize=True)
            zipf.writestr(name, img_bytes.getvalue())
    
    st.download_button(
        label="📦 Download All (PNG)",
        data=zip_buffer.getvalue(),
        file_name="Ultra_HD_Photos.zip",
        mime="application/zip"
    )

elif 'variant_images' in st.session_state and st.session_state.variant_images:
    variant_groups = {}
    for name, img in st.session_state.variant_images:
        base_name = name.rsplit('_v', 1)[0]
        if base_name not in variant_groups:
            variant_groups[base_name] = []
        variant_groups[base_name].append((name, img))
    
    for base_name, variants in variant_groups.items():
        st.markdown(f"### Variants for {base_name}")
        
        st.markdown("""
        <div class="variant-container">
        """, unsafe_allow_html=True)
        
        for idx, (name, img) in enumerate(variants):
            st.markdown(f"""
            <div class="variant-item">
            """, unsafe_allow_html=True)
            
            st.image(img, width=300)
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="PNG", quality=100, optimize=True)
            st.download_button(
                label=f"⬇️ Variant {idx+1}",
                data=img_bytes.getvalue(),
                file_name=name,
                mime="image/png",
                key=f"vdl_{name}"
            )
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for name, img in st.session_state.variant_images:
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="PNG", quality=100, optimize=True)
            zipf.writestr(name, img_bytes.getvalue())
    
    st.download_button(
        label="📦 Download All Variants (PNG)",
        data=zip_buffer.getvalue(),
        file_name="Ultra_HD_Variants.zip",
        mime="application/zip"
                       )
