import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageOps, ImageFilter
import os
import io
import random
import datetime
import zipfile
import numpy as np
import cv2
from collections import Counter

# =================== CONFIG ===================
st.set_page_config(page_title="⚡ Bulk Image Generator Pro", layout="wide", page_icon="⚡")

# Custom CSS for clean look
st.markdown("""
    <style>
    .main {
        background-color: #ffffff;
    }
    .stButton>button {
        background-color: #000000;
        color: #ffff00;
        border: 2px solid #ffff00;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #ffff00 !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
    }
    .sidebar .sidebar-content {
        background-color: #000000;
        color: white;
    }
    .sidebar .sidebar-content .stSelectbox, .sidebar .sidebar-content .stTextInput {
        background-color: #111111;
        color: white;
    }
    .stTextInput>div>div>input {
        color: white !important;
    }
    .stSelectbox>div>div>select {
        color: white !important;
    }
    .stSlider>div>div>div>div {
        background-color: #ffff00;
    }
    .stCheckbox>label {
        color: white !important;
    }
    .stProgress>div>div>div>div {
        background-color: #ffff00;
    }
    .feature-card {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #ffff00;
    }
    .feature-card h4 {
        color: #000000;
        margin-top: 0;
    }
    </style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
    <div style='background-color: #000000; padding: 20px; border-radius: 12px; border: 2px solid #ffff00;'>
        <h1 style='text-align: center; color: #ffff00; margin: 0;'>⚡ Bulk Image Generator Pro</h1>
        <p style='text-align: center; color: #ffffff; margin: 5px 0 0 0;'>Process 100+ Images in One Click</p>
    </div>
""", unsafe_allow_html=True)

# =================== UTILS ===================
def list_files(folder, exts):
    if not os.path.exists(folder):
        return []
    return [f for f in os.listdir(folder) if any(f.lower().endswith(ext) for ext in exts]

def get_dominant_color(image):
    # Resize to speed up processing
    image = image.copy()
    image.thumbnail((100, 100))
    
    # Convert to RGB if needed
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Get colors
    colors = image.getcolors(maxcolors=10000)
    if not colors:
        return (255, 255, 255)
    
    # Get dominant color
    colors.sort(reverse=True)
    dominant_color = colors[0][1]
    return dominant_color

def get_text_color(bg_color):
    # Calculate luminance
    r, g, b = bg_color
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    
    # Return black or white depending on luminance
    return (0, 0, 0) if luminance > 0.5 else (255, 255, 255)

def smart_crop(img, target_ratio=3/4):
    # Convert to OpenCV format
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    img_np = np.array(img)
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    
    # Detect faces or objects
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    
    if len(faces) > 0:
        # If faces detected, center crop around them
        x, y, w, h = faces[0]
        center_x, center_y = x + w//2, y + h//2
    else:
        # Otherwise use saliency detection
        saliency = cv2.saliency.StaticSaliencyFineGrained_create()
        (success, saliencyMap) = saliency.computeSaliency(gray)
        if success:
            center_y, center_x = np.unravel_index(np.argmax(saliencyMap), saliencyMap.shape)
        else:
            center_x, center_y = img.width//2, img.height//2
    
    # Calculate crop based on target ratio
    w, h = img.size
    if w/h > target_ratio:
        new_w = int(h * target_ratio)
        left = max(0, min(center_x - new_w//2, w - new_w))
        return img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = max(0, min(center_y - new_h//2, h - new_h))
        return img.crop((0, top, w, top + new_h))

def safe_randint(a, b):
    if a > b:
        a, b = b, a
    return random.randint(a, b)

def get_random_font(font_folder="assets/fonts"):
    fonts = list_files(font_folder, [".ttf", ".otf"])
    if not fonts:
        return None
    font_path = os.path.join(font_folder, random.choice(fonts))
    try:
        return ImageFont.truetype(font_path, 60)
    except:
        return None

def get_random_wish(greeting_type):
    wishes = {
        "Good Morning": [
            "Have a great day!", "Rise and shine!", "Make today amazing!",
            "Good morning, sunshine!", "Start your day with smile!",
            "Morning blessings to you!", "Seize the day!", "Enjoy your morning!",
            "Wake up and be awesome!", "Another beautiful day begins!"
        ],
        "Good Night": [
            "Sweet dreams!", "Sleep tight!", "Night night!",
            "Dream wonderful dreams!", "Rest well!", 
            "Good night, sleep well!", "Time to recharge!",
            "Tomorrow is a new day!", "Peaceful sleep!", 
            "Stars are shining for you!"
        ],
        "Happy Birthday": [
            "Many happy returns!", "Best wishes!", "Enjoy your special day!",
            "Celebrate you!", "Make a wish!", "Party time!", 
            "Happy birthday champ!", "Another year wiser!", 
            "Birthday blessings!", "Cake time!"
        ],
        "Thank You": [
            "Much appreciated!", "Grateful for you!", "Thanks a million!",
            "You're awesome!", "Big thanks!", "Deeply grateful!",
            "Thanks for everything!", "Appreciate you!", 
            "Thank you kindly!", "Forever thankful!"
        ],
        "Congratulations": [
            "Well done!", "You did it!", "Amazing achievement!",
            "Proud of you!", "Bravo!", "Fantastic work!",
            "Celebrate success!", "You rock!", "Incredible job!",
            "Standing ovation!"
        ]
    }
    return random.choice(wishes.get(greeting_type, ["Have a nice day!"]))

def get_random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def get_random_gradient():
    color1 = get_random_color()
    color2 = get_random_color()
    return [color1, color2]

def add_text_with_effects(draw, position, text, font, image_width, shadow=True):
    text_color = get_random_color()
    shadow_color = get_random_color()
    
    # Random effects
    shadow = random.choice([True, False])
    outline = random.choice([True, False])
    gradient = random.choice([True, False])
    
    if shadow:
        shadow_offset = random.randint(2, 5)
        draw.text((position[0]+shadow_offset, position[1]+shadow_offset), 
                 text, font=font, fill=shadow_color)
    
    if outline:
        outline_thickness = random.randint(1, 3)
        for x in range(-outline_thickness, outline_thickness+1):
            for y in range(-outline_thickness, outline_thickness+1):
                draw.text((position[0]+x, position[1]+y), text, font=font, fill=(0, 0, 0))
    
    draw.text(position, text, font=font, fill=text_color)

def place_watermark_smart(img, logo, opacity=1.0):
    w, h = img.size
    logo_w, logo_h = logo.size
    
    # Detect important areas
    img_np = np.array(img.convert('RGB'))
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    
    # Find empty space
    edges = cv2.Canny(gray, 100, 200)
    kernel = np.ones((5,5), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)
    
    # Find best position (minimum edges)
    min_energy = float('inf')
    best_pos = (0, 0)
    
    positions = [
        (20, 20),  # Top-left
        (w - logo_w - 20, 20),  # Top-right
        (20, h - logo_h - 20),  # Bottom-left
        (w - logo_w - 20, h - logo_h - 20),  # Bottom-right
        ((w - logo_w) // 2, (h - logo_h) // 2)  # Center
    ]
    
    for x, y in positions:
        if x < 0 or y < 0 or x + logo_w > w or y + logo_h > h:
            continue
        
        patch = edges[y:y+logo_h, x:x+logo_w]
        energy = np.sum(patch)
        
        if energy < min_energy:
            min_energy = energy
            best_pos = (x, y)
    
    # Apply watermark with opacity
    watermark = logo.copy()
    if opacity < 1.0:
        alpha = watermark.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
        watermark.putalpha(alpha)
    
    img.paste(watermark, best_pos, watermark)
    return img

def apply_random_effect(image):
    effect = random.choice([
        'vignette', 'blur', 'sharpen', 'contrast', 
        'brightness', 'saturation', 'grayscale', 
        'sepia', 'border', 'polaroid'
    ])
    
    if effect == 'vignette':
        return apply_vignette(image, random.uniform(0.5, 0.9))
    elif effect == 'blur':
        return apply_blur(image, random.uniform(0.5, 2.0))
    elif effect == 'sharpen':
        return apply_sharpen(image, random.uniform(1.0, 2.0))
    elif effect == 'contrast':
        return apply_contrast(image, random.uniform(0.8, 1.5))
    elif effect == 'brightness':
        return apply_brightness(image, random.uniform(0.8, 1.3))
    elif effect == 'saturation':
        return apply_saturation(image, random.uniform(0.5, 1.5))
    elif effect == 'grayscale':
        return apply_grayscale(image)
    elif effect == 'sepia':
        return apply_sepia(image)
    elif effect == 'border':
        return add_border(image, random.randint(5, 20), get_random_color())
    elif effect == 'polaroid':
        return apply_polaroid_effect(image, rotation=random.randint(-10, 10))
    return image

def apply_vignette(image, intensity=0.8):
    width, height = image.size
    x = np.linspace(-1, 1, width)
    y = np.linspace(-1, 1, height)
    X, Y = np.meshgrid(x, y)
    R = np.sqrt(X**2 + Y**2)
    mask = 1 - np.clip(R * intensity, 0, 1)
    mask = (mask * 255).astype(np.uint8)
    vignette = Image.fromarray(mask, mode='L')
    vignette = vignette.resize((width, height))
    
    if image.mode == 'RGBA':
        r, g, b, a = image.split()
        rgb_image = Image.merge('RGB', (r, g, b))
        result = Image.composite(rgb_image, Image.new('RGB', image.size, 'black'), vignette)
        r, g, b = result.split()
        return Image.merge('RGBA', (r, g, b, a))
    else:
        return Image.composite(image, Image.new(image.mode, image.size, 'black'), vignette)

def apply_blur(image, radius=2):
    return image.filter(ImageFilter.GaussianBlur(radius))

def apply_sharpen(image, factor=1.5):
    return image.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))

def apply_contrast(image, factor=1.5):
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(factor)

def apply_brightness(image, factor=1.2):
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(factor)

def apply_saturation(image, factor=1.3):
    enhancer = ImageEnhance.Color(image)
    return enhancer.enhance(factor)

def apply_sepia(image):
    sepia_filter = np.array([
        [0.393, 0.769, 0.189],
        [0.349, 0.686, 0.168],
        [0.272, 0.534, 0.131]
    ])
    img_array = np.array(image)
    sepia_img = np.dot(img_array, sepia_filter.T)
    sepia_img = np.clip(sepia_img, 0, 255).astype(np.uint8)
    return Image.fromarray(sepia_img)

def apply_polaroid_effect(image, background_color='white', border_size=20, rotation=5):
    image_with_border = add_border(image, border_size=border_size, color=background_color)
    image_rotated = image_with_border.rotate(rotation, expand=True, fillcolor=background_color)
    return add_shadow(image_rotated)

def add_shadow(image, offset=(10, 10), shadow_color=(0, 0, 0, 100), border=30, blur_radius=15):
    width, height = image.size
    new_width = width + abs(offset[0]) + 2 * border
    new_height = height + abs(offset[1]) + 2 * border
    
    shadow_layer = Image.new('RGBA', (new_width, new_height), (0, 0, 0, 0))
    shadow_left = border + max(offset[0], 0)
    shadow_top = border + max(offset[1], 0)
    
    shadow = Image.new('RGBA', (width, height), shadow_color)
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur_radius))
    shadow_layer.paste(shadow, (shadow_left, shadow_top))
    
    img_left = border - min(offset[0], 0)
    img_top = border - min(offset[1], 0)
    
    shadow_layer.paste(image, (img_left, img_top), image if image.mode == 'RGBA' else None)
    return shadow_layer

# =================== MAIN PAGE ===================
col1, col2 = st.columns([3, 1])

with col1:
    uploaded_images = st.file_uploader("📁 Upload Images (JPEG, PNG)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# =================== SIDEBAR SETTINGS ===================
with st.sidebar:
    st.markdown("""
        <div style='background-color: #000000; padding: 15px; border-radius: 10px; margin-bottom: 20px; border: 2px solid #ffff00;'>
            <h3 style='color: #ffff00; text-align: center; margin: 0;'>⚙️ Settings</h3>
        </div>
    """, unsafe_allow_html=True)
    
    with st.expander("📝 Text Options", expanded=True):
        greeting_type = st.selectbox("Greeting Type", ["Good Morning", "Good Night", "Happy Birthday", "Thank You", "Congratulations"])
        show_text = st.checkbox("Show Main Text", value=True)
        show_wish = st.checkbox("Show Sub Wish", value=True)
        show_date = st.checkbox("Show Date", value=False)
        
        if show_text:
            main_size = st.slider("Main Text Size", 10, 100, 40)
        if show_wish:
            wish_size = st.slider("Wish Text Size", 10, 60, 20)
    
    with st.expander("💧 Watermark Options", expanded=False):
        use_watermark = st.checkbox("Add Watermark", value=True)
        if use_watermark:
            watermark_opacity = st.slider("Watermark Opacity", 0.1, 1.0, 0.7)
            watermark_size = st.slider("Watermark Size", 5, 30, 15)
            
            # Watermark upload
            watermark_file = st.file_uploader("Upload Watermark (PNG)", type=["png"])
            if watermark_file:
                watermark_image = Image.open(watermark_file).convert("RGBA")
            else:
                watermark_image = None
    
    with st.expander("🎨 Image Effects", expanded=False):
        enhance_quality = st.checkbox("Auto Enhance Quality", value=True)
        apply_random_effects = st.checkbox("Apply Random Effects", value=True)
        crop_method = st.selectbox("Crop Method", ["Smart Crop", "Center Crop"])
    
    with st.expander("💾 Output Options", expanded=False):
        output_quality = st.slider("Output Quality", 80, 100, 95)
        output_format = st.selectbox("Output Format", ["JPEG", "PNG"])

# =================== RIGHT SIDE FEATURES ===================
with col2:
    st.markdown("""
        <div style='background-color: #000000; padding: 15px; border-radius: 10px; margin-bottom: 20px; border: 2px solid #ffff00;'>
            <h3 style='color: #ffff00; text-align: center; margin: 0;'>✨ Features</h3>
        </div>
    """, unsafe_allow_html=True)
    
    features = [
        "Smart Object Detection",
        "Auto Text Placement",
        "Random Effects Engine",
        "Bulk Processing",
        "High Quality Output",
        "Smart Watermarking",
        "Multiple Greeting Types",
        "Dynamic Color Selection",
        "Auto Image Enhancement",
        "Custom Font Support",
        "Non-Destructive Editing",
        "Fast Processing"
    ]
    
    for feature in features:
        st.markdown(f"""
            <div class="feature-card">
                <h4>{feature}</h4>
            </div>
        """, unsafe_allow_html=True)

# =================== PROCESSING ===================
results = []
if st.button("⚡ Process Images", key="process_button"):
    if uploaded_images:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        with st.spinner("🚀 Processing images... Please wait..."):
            total_images = len(uploaded_images)
            for idx, image_file in enumerate(uploaded_images):
                try:
                    # Update progress
                    progress = (idx + 1) / total_images
                    progress_bar.progress(progress)
                    status_text.text(f"Processing {idx + 1}/{total_images} ({int(progress * 100)}%)")
                    
                    # Open image
                    image = Image.open(image_file).convert("RGBA")
                    
                    # Apply cropping
                    if crop_method == "Smart Crop":
                        image = smart_crop(image)
                    else:
                        image = crop_to_3_4(image)
                    
                    w, h = image.size
                    
                    # Apply random effects
                    if apply_random_effects:
                        image = apply_random_effect(image)
                    
                    # Enhance quality
                    if enhance_quality:
                        image = apply_sharpen(image, 1.2)
                        image = apply_contrast(image, 1.1)
                    
                    # Prepare for drawing
                    draw = ImageDraw.Draw(image)
                    
                    # Get random font for this image
                    font = get_random_font()
                    if font is None:
                        font = ImageFont.load_default()
                    
                    # Draw main text
                    if show_text:
                        font_main = font.font_variant(size=main_size)
                        text = greeting_type
                        
                        # Smart text positioning
                        text_width, text_height = draw.textsize(text, font=font_main)
                        text_x = random.randint(50, max(50, w - text_width - 50))
                        text_y = random.randint(50, max(50, h - text_height - 150))
                        
                        # Add text with random effects
                        add_text_with_effects(draw, (text_x, text_y), text, font_main, w)
                    
                    # Draw sub wish
                    if show_wish:
                        font_wish = font.font_variant(size=wish_size)
                        wish_text = get_random_wish(greeting_type)
                        
                        # Position below main text
                        wish_x = random.randint(50, max(50, w - text_width - 50))
                        wish_y = text_y + main_size + 20
                        
                        # Add wish with random effects
                        add_text_with_effects(draw, (wish_x, wish_y), wish_text, font_wish, w)
                    
                    # Draw date
                    if show_date:
                        font_date = font.font_variant(size=wish_size)
                        today = datetime.datetime.now().strftime("%d %B %Y")
                        date_width, date_height = draw.textsize(today, font=font_date)
                        date_x = w - date_width - 50
                        date_y = h - date_height - 50
                        draw.text((date_x, date_y), today, font=font_date, fill=get_random_color())
                    
                    # Add watermark
                    if use_watermark and watermark_image:
                        # Resize watermark
                        watermark = watermark_image.copy()
                        watermark_size_px = int(min(w, h) * watermark_size / 100)
                        watermark.thumbnail((watermark_size_px, watermark_size_px))
                        
                        # Place smart watermark
                        image = place_watermark_smart(image, watermark, watermark_opacity)
                    
                    # Convert to output format
                    if output_format == "JPEG":
                        final = image.convert("RGB")
                        ext = "jpg"
                    else:
                        final = image
                        ext = "png"
                    
                    results.append((f"{os.path.splitext(image_file.name)[0]}_processed.{ext}", final))
                
                except Exception as e:
                    st.error(f"❌ Error processing {image_file.name}: {str(e)}")
        
        progress_bar.empty()
        status_text.empty()
        st.success(f"✅ Successfully processed {len(results)} images!")
        
        # Display results in a grid
        st.markdown("## Processed Images")
        cols = st.columns(3)
        for idx, (name, img) in enumerate(results):
            with cols[idx % 3]:
                st.image(img, caption=name, use_column_width=True)
                
                # Create download button for each image
                img_bytes = io.BytesIO()
                if output_format == "JPEG":
                    img.save(img_bytes, format="JPEG", quality=output_quality)
                    mime = "image/jpeg"
                else:
                    img.save(img_bytes, format="PNG", compress_level=9-output_quality//10)
                    mime = "image/png"
                
                st.download_button(
                    label=f"⬇️ Download {name}",
                    data=img_bytes.getvalue(),
                    file_name=name,
                    mime=mime,
                    key=f"dl_{idx}"
                )
        
        # Create ZIP archive
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for name, img in results:
                img_bytes = io.BytesIO()
                if output_format == "JPEG":
                    img.save(img_bytes, format="JPEG", quality=output_quality)
                else:
                    img.save(img_bytes, format="PNG", compress_level=9-output_quality//10)
                zipf.writestr(name, img_bytes.getvalue())
        
        st.download_button(
            label="📦 Download All as ZIP",
            data=zip_buffer.getvalue(),
            file_name="processed_images.zip",
            mime="application/zip",
            key="dl_all"
        )
    else:
        st.warning("⚠️ Please upload at least one image to process.")

# =================== FOOTER ===================
st.markdown("""
    <div style='text-align: center; color: #666666; margin-top: 50px; font-size: 0.9em;'>
        <p>⚡ Bulk Image Generator Pro | © 2023</p>
    </div>
""", unsafe_allow_html=True)
