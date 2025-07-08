import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageOps, ImageFilter
import os
import io
import random
import datetime
import zipfile
import numpy as np

# =================== CONFIG ===================
st.set_page_config(page_title="⚡ Ultra Image Processor", layout="wide")

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
    .feature-card {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #ffff00;
    }
    </style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
    <div style='background-color: #000000; padding: 20px; border-radius: 12px; border: 2px solid #ffff00; margin-bottom: 20px;'>
        <h1 style='text-align: center; color: #ffff00; margin: 0;'>⚡ Ultra Image Processor</h1>
        <p style='text-align: center; color: #ffffff; margin: 5px 0 0 0;'>Professional Bulk Image Processing</p>
    </div>
""", unsafe_allow_html=True)

# =================== UTILS ===================
def get_text_size(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def center_crop(img, target_ratio=3/4):
    w, h = img.size
    if w/h > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        return img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        return img.crop((0, top, w, top + new_h))

def list_files(folder, exts):
    if not os.path.exists(folder):
        return []
    return [f for f in os.listdir(folder) if any(f.lower().endswith(ext) for ext in exts)]

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
        ]
    }
    return random.choice(wishes.get(greeting_type, ["Have a nice day!"]))

def get_random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def add_text_with_effects(draw, position, text, font, shadow=True):
    text_color = get_random_color()
    shadow_color = get_random_color()
    
    if shadow and random.choice([True, False]):
        shadow_offset = random.randint(2, 5)
        draw.text((position[0]+shadow_offset, position[1]+shadow_offset), 
                 text, font=font, fill=shadow_color)
    
    draw.text(position, text, font=font, fill=text_color)

def place_watermark(img, logo, opacity=1.0):
    w, h = img.size
    logo_w, logo_h = logo.size
    
    # Position options (top-left, top-right, bottom-left, bottom-right, center)
    positions = [
        (20, 20), 
        (w - logo_w - 20, 20),
        (20, h - logo_h - 20),
        (w - logo_w - 20, h - logo_h - 20),
        ((w - logo_w)//2, (h - logo_h)//2)
    ]
    
    # Choose random position
    x, y = random.choice(positions)
    
    # Apply opacity
    watermark = logo.copy()
    if opacity < 1.0:
        alpha = watermark.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
        watermark.putalpha(alpha)
    
    img.paste(watermark, (x, y), watermark)
    return img

def apply_random_effect(image):
    effect = random.choice(['sharpen', 'contrast', 'brightness', 'saturation'])
    
    if effect == 'sharpen':
        return image.filter(ImageFilter.SHARPEN)
    elif effect == 'contrast':
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(random.uniform(0.9, 1.2))
    elif effect == 'brightness':
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(random.uniform(0.9, 1.1))
    elif effect == 'saturation':
        enhancer = ImageEnhance.Color(image)
        return enhancer.enhance(random.uniform(0.9, 1.2))
    return image

# =================== MAIN PAGE ===================
col1, col2 = st.columns([3, 1])

with col1:
    uploaded_images = st.file_uploader("📁 Upload Images (JPEG, PNG)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    
    # Process button at the top
    if st.button("⚡ Process Images", key="process_button"):
        if uploaded_images:
            results = []
            progress_bar = st.progress(0)
            
            for idx, image_file in enumerate(uploaded_images):
                try:
                    # Update progress
                    progress_bar.progress((idx + 1) / len(uploaded_images))
                    
                    # Open image
                    image = Image.open(image_file).convert("RGBA")
                    
                    # Apply cropping
                    image = center_crop(image)
                    w, h = image.size
                    
                    # Apply random enhancement
                    image = apply_random_effect(image)
                    
                    # Prepare for drawing
                    draw = ImageDraw.Draw(image)
                    
                    # Get random font for this image
                    font = get_random_font()
                    if font is None:
                        font = ImageFont.load_default()
                    
                    # Add main text
                    if st.session_state.show_text:
                        font_main = font.font_variant(size=st.session_state.text_size)
                        text = st.session_state.greeting_type
                        
                        # Get text size
                        text_width, text_height = get_text_size(draw, text, font_main)
                        
                        # Random position
                        text_x = random.randint(20, max(20, w - text_width - 20))
                        text_y = random.randint(20, max(20, h - text_height - 50))
                        
                        # Add text with random effects
                        add_text_with_effects(draw, (text_x, text_y), text, font_main)
                    
                    # Add wish text
                    if st.session_state.show_wish:
                        font_wish = font.font_variant(size=st.session_state.wish_size)
                        wish_text = get_random_wish(st.session_state.greeting_type)
                        
                        # Position below main text
                        wish_x = random.randint(20, max(20, w - text_width - 20))
                        wish_y = text_y + st.session_state.text_size + 10
                        
                        # Add wish with random effects
                        add_text_with_effects(draw, (wish_x, wish_y), wish_text, font_wish)
                    
                    # Add watermark
                    if st.session_state.use_watermark and st.session_state.watermark_image:
                        watermark = st.session_state.watermark_image.copy()
                        watermark_size = min(w, h) // 4
                        watermark.thumbnail((watermark_size, watermark_size))
                        image = place_watermark(image, watermark, st.session_state.watermark_opacity)
                    
                    # Convert to RGB for JPEG
                    final = image.convert("RGB")
                    results.append((image_file.name, final))
                
                except Exception as e:
                    st.error(f"Error processing {image_file.name}: {str(e)}")
            
            progress_bar.empty()
            
            if results:
                st.success(f"✅ Processed {len(results)} images successfully!")
                
                # Display results
                st.markdown("### Processed Images")
                cols = st.columns(3)
                for idx, (name, img) in enumerate(results):
                    with cols[idx % 3]:
                        st.image(img, caption=name, use_column_width=True)
                        
                        # Download button for each image
                        img_bytes = io.BytesIO()
                        img.save(img_bytes, format="JPEG", quality=95)
                        st.download_button(
                            label=f"⬇️ Download {name}",
                            data=img_bytes.getvalue(),
                            file_name=f"processed_{name}",
                            mime="image/jpeg",
                            key=f"dl_{idx}"
                        )
                
                # ZIP download
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for name, img in results:
                        img_bytes = io.BytesIO()
                        img.save(img_bytes, format="JPEG", quality=95)
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

# =================== SIDEBAR SETTINGS ===================
with st.sidebar:
    st.markdown("""
        <div style='background-color: #000000; padding: 15px; border-radius: 10px; margin-bottom: 20px; border: 2px solid #ffff00;'>
            <h3 style='color: #ffff00; text-align: center; margin: 0;'>⚙️ Settings</h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Store settings in session state
    st.session_state.greeting_type = st.selectbox("Greeting Type", ["Good Morning", "Good Night", "Happy Birthday", "Thank You"])
    st.session_state.show_text = st.checkbox("Show Main Text", value=True)
    st.session_state.show_wish = st.checkbox("Show Sub Wish", value=True)
    
    if st.session_state.show_text:
        st.session_state.text_size = st.slider("Main Text Size", 20, 100, 40)
    if st.session_state.show_wish:
        st.session_state.wish_size = st.slider("Wish Text Size", 10, 60, 20)
    
    st.session_state.use_watermark = st.checkbox("Add Watermark", value=False)
    if st.session_state.use_watermark:
        watermark_file = st.file_uploader("Upload Watermark (PNG)", type=["png"])
        if watermark_file:
            st.session_state.watermark_image = Image.open(watermark_file).convert("RGBA")
        st.session_state.watermark_opacity = st.slider("Watermark Opacity", 0.1, 1.0, 0.7)

# =================== RIGHT SIDE FEATURES ===================
with col2:
    st.markdown("""
        <div style='background-color: #000000; padding: 15px; border-radius: 10px; margin-bottom: 20px; border: 2px solid #ffff00;'>
            <h3 style='color: #ffff00; text-align: center; margin: 0;'>✨ Features</h3>
        </div>
    """, unsafe_allow_html=True)
    
    features = [
        "Center Cropping",
        "Auto Text Placement",
        "Random Effects",
        "Bulk Processing",
        "High Quality Output",
        "Smart Watermarking",
        "Multiple Greeting Types",
        "Dynamic Color Selection",
        "Auto Image Enhancement",
        "Custom Font Support",
        "Fast Processing"
    ]
    
    for feature in features:
        st.markdown(f"""
            <div class="feature-card">
                <h4>{feature}</h4>
            </div>
        """, unsafe_allow_html=True)

# =================== FOOTER ===================
st.markdown("""
    <div style='text-align: center; color: #666666; margin-top: 50px; font-size: 0.9em;'>
        <p>⚡ Ultra Image Processor | © 2023</p>
    </div>
""", unsafe_allow_html=True)
