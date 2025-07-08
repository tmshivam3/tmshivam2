import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageOps, ImageFilter
import os
import io
import random
import datetime
import zipfile
import numpy as np
from streamlit_option_menu import option_menu
import time
import base64

# =================== CONFIG ===================
st.set_page_config(page_title="✨ Premium Photo Editor Pro ™", layout="wide", page_icon="✨")

# Custom CSS for premium look
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        background: linear-gradient(45deg, #6a11cb 0%, #2575fc 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #2c3e50 0%, #1a1a2e 100%);
        color: white;
    }
    .sidebar .sidebar-content .stSelectbox, .sidebar .sidebar-content .stTextInput {
        background-color: rgba(255,255,255,0.1);
        color: white;
    }
    .stTextInput>div>div>input {
        color: white !important;
    }
    .stSelectbox>div>div>select {
        color: white !important;
    }
    .stSlider>div>div>div>div {
        background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%);
    }
    .stCheckbox>label {
        color: white !important;
    }
    .stProgress>div>div>div>div {
        background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%);
    }
    .feature-card {
        background: white;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #6a11cb;
    }
    .feature-card h4 {
        color: #6a11cb;
        margin-top: 0;
    }
    .premium-badge {
        background: linear-gradient(45deg, #ff8a00, #e52e71);
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.7em;
        font-weight: bold;
        margin-left: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# Main header with gradient
st.markdown("""
    <div style='background: linear-gradient(45deg, #6a11cb 0%, #2575fc 100%); padding: 20px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.2);'>
        <h1 style='text-align: center; color: white; margin: 0;'>✨ Premium Photo Editor Pro ™</h1>
        <p style='text-align: center; color: rgba(255,255,255,0.8); margin: 5px 0 0 0;'>Professional Batch Image Processing with AI Enhancements</p>
    </div>
""", unsafe_allow_html=True)

# =================== UTILS ===================
def list_files(folder, exts):
    if not os.path.exists(folder):
        return []
    return [f for f in os.listdir(folder) if any(f.lower().endswith(ext) for ext in exts)]

def crop_to_3_4(img):
    w, h = img.size
    target_ratio = 3 / 4
    if w / h > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        return img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        return img.crop((0, top, w, top + new_h))

def safe_randint(a, b):
    if a > b:
        a, b = b, a
    return random.randint(a, b)

def overlay_theme_overlays(img, greeting_type, theme_folder):
    iw, ih = img.size
    overlay_nums = [1]
    if greeting_type == "Good Morning":
        overlay_nums += [2]
    elif greeting_type == "Good Night":
        overlay_nums += [3]
    if "nice" in greeting_type.lower():
        overlay_nums += [4]
    if "sweet" in greeting_type.lower():
        overlay_nums += [5]

    for num in overlay_nums:
        path = os.path.join(theme_folder, f"{num}.png")
        if os.path.exists(path):
            try:
                overlay = Image.open(path).convert("RGBA")
                scale = 0.35 if num == 1 else 0.25
                overlay = overlay.resize((int(iw * scale), int(ih * scale)))
                px = safe_randint(30, iw - overlay.width - 30)
                py = safe_randint(30, ih - overlay.height - 30)
                img.paste(overlay, (px, py), overlay)
            except:
                pass
    return img

def place_logo_random(img, logo, opacity=1.0):  # Added opacity parameter with default 1.0 (100%)
    w, h = img.size
    logo_w, logo_h = logo.size
    max_x = max(0, w - logo_w - 30)
    max_y = max(0, h - logo_h - 30)
    x = safe_randint(20, max_x)
    y = safe_randint(20, max_y)
    watermark = logo.copy()
    
    # Apply opacity directly to the watermark
    if opacity < 1.0:
        alpha = watermark.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
        watermark.putalpha(alpha)
    
    img.paste(watermark, (x, y), watermark)
    return img

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

def apply_grayscale(image):
    return image.convert('L')

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

def add_border(image, border_size=10, color='white'):
    return ImageOps.expand(image, border=border_size, fill=color)

def add_shadow(image, offset=(10, 10), shadow_color=(0, 0, 0, 100), border=30, blur_radius=15):
    # Create a larger image to accommodate the shadow
    width, height = image.size
    new_width = width + abs(offset[0]) + 2 * border
    new_height = height + abs(offset[1]) + 2 * border
    
    # Create a transparent background
    shadow_layer = Image.new('RGBA', (new_width, new_height), (0, 0, 0, 0))
    
    # Calculate position for the shadow
    shadow_left = border + max(offset[0], 0)
    shadow_top = border + max(offset[1], 0)
    
    # Create shadow
    shadow = Image.new('RGBA', (width, height), shadow_color)
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur_radius))
    shadow_layer.paste(shadow, (shadow_left, shadow_top))
    
    # Calculate position for the original image
    img_left = border - min(offset[0], 0)
    img_top = border - min(offset[1], 0)
    
    # Paste the original image
    shadow_layer.paste(image, (img_left, img_top), image if image.mode == 'RGBA' else None)
    
    return shadow_layer

def apply_polaroid_effect(image, background_color='white', border_size=20, rotation=5):
    # Add border
    image_with_border = add_border(image, border_size=border_size, color=background_color)
    
    # Rotate slightly
    image_rotated = image_with_border.rotate(rotation, expand=True, fillcolor=background_color)
    
    # Add shadow
    final_image = add_shadow(image_rotated)
    
    return final_image

def apply_texture_overlay(image, texture_path, opacity=0.3):
    texture = Image.open(texture_path).convert('RGBA')
    texture = texture.resize(image.size)
    
    # Adjust opacity
    r, g, b, a = texture.split()
    a = a.point(lambda x: x * opacity)
    texture.putalpha(a)
    
    # Composite with original image
    return Image.alpha_composite(image.convert('RGBA'), texture)

def generate_gradient(width, height, colors):
    base = Image.new('RGB', (width, height), colors[0])
    top = Image.new('RGB', (width, height), colors[1])
    mask = Image.new('L', (width, height))
    mask_data = []
    for y in range(height):
        mask_data.extend([int(255 * (y / height))] * width)
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)
    return base

def add_gradient_overlay(image, colors, opacity=0.5):
    gradient = generate_gradient(image.width, image.height, colors)
    gradient.putalpha(int(255 * opacity))
    image_with_alpha = image.convert('RGBA')
    return Image.alpha_composite(image_with_alpha, gradient.convert('RGBA'))

def apply_rounded_corners(image, radius=20):
    circle = Image.new('L', (radius * 2, radius * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, radius * 2, radius * 2), fill=255)
    
    alpha = Image.new('L', image.size, 255)
    w, h = image.size
    
    # Apply rounded corners to the alpha channel
    alpha.paste(circle.crop((0, 0, radius, radius)), (0, 0))
    alpha.paste(circle.crop((radius, 0, radius * 2, radius)), (w - radius, 0))
    alpha.paste(circle.crop((0, radius, radius, radius * 2)), (0, h - radius))
    alpha.paste(circle.crop((radius, radius, radius * 2, radius * 2)), (w - radius, h - radius))
    
    image.putalpha(alpha)
    return image

def apply_3d_effect(image, depth=3):
    result = image.copy()
    for i in range(depth, 0, -1):
        shadow = image.copy()
        shadow = ImageEnhance.Brightness(shadow).enhance(0.5)
        shadow = shadow.transform(shadow.size, Image.AFFINE, (1, 0, i, 0, 1, i))
        result.paste(shadow, (0, 0), shadow)
    return result

# =================== MAIN PAGE UPLOAD ===================
col1, col2 = st.columns([3, 1])

with col1:
    uploaded_images = st.file_uploader("📁 Upload Images (JPEG, PNG)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# =================== SIDEBAR ===================
with st.sidebar:
    st.markdown("""
        <div style='background: linear-gradient(45deg, #6a11cb 0%, #2575fc 100%); padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
            <h3 style='color: white; text-align: center; margin: 0;'>🛠️ Editor Settings</h3>
        </div>
    """, unsafe_allow_html=True)
    
    with st.expander("📝 Text Options", expanded=True):
        greeting_type = st.selectbox("Greeting Type", ["Good Morning", "Good Night", "Happy Birthday", "Congratulations", "Thank You"])
        custom_wish = st.text_input("Custom Wish (optional)", value="")
        show_text = st.checkbox("Show Main Text", value=True)
        show_wish = st.checkbox("Show Sub Wish", value=True)
        show_date = st.checkbox("Show Date", value=False)
        
        if show_text:
            main_size = st.slider("Main Text Size", 5, 50, 12)
            main_color = st.color_picker("Main Text Color", "#FFFFFF")
        if show_wish:
            wish_size = st.slider("Wish Text Size", 5, 30, 10)
            wish_color = st.color_picker("Wish Text Color", "#FFFF00")
    
    with st.expander("🎨 Overlay Effects", expanded=False):
        show_overlay = st.checkbox("Enable Overlay Wishes", value=False)
        theme_dirs = sorted([d for d in os.listdir("assets/overlays") if os.path.isdir(os.path.join("assets/overlays", d))], reverse=True)
        theme_options = ["Auto Random"] + theme_dirs
        selected_theme = st.selectbox("Overlay Theme", theme_options) if show_overlay else None
        
        # New overlay effects
        apply_vignette_effect = st.checkbox("Add Vignette Effect", value=False)
        if apply_vignette_effect:
            vignette_intensity = st.slider("Vignette Intensity", 0.1, 1.0, 0.7)
        
        apply_gradient_overlay = st.checkbox("Add Gradient Overlay", value=False)
        if apply_gradient_overlay:
            gradient_color1 = st.color_picker("Gradient Color 1", "#6a11cb")
            gradient_color2 = st.color_picker("Gradient Color 2", "#2575fc")
            gradient_opacity = st.slider("Gradient Opacity", 0.1, 1.0, 0.5)
    
    with st.expander("🖼️ Image Adjustments", expanded=False):
        enhance_quality = st.checkbox("Enhance Image Quality", value=True)
        if enhance_quality:
            brightness_factor = st.slider("Brightness", 0.5, 1.5, 1.0)
            contrast_factor = st.slider("Contrast", 0.5, 1.5, 1.0)
            saturation_factor = st.slider("Saturation", 0.0, 2.0, 1.0)
            sharpness_factor = st.slider("Sharpness", 0.0, 2.0, 1.0)
        
        apply_filter = st.selectbox("Apply Filter", ["None", "Grayscale", "Sepia", "Blur", "Sharpen"])
        
        border_option = st.selectbox("Border Style", ["None", "Simple", "Polaroid", "Rounded Corners"])
        if border_option == "Simple":
            border_size = st.slider("Border Size", 1, 50, 10)
            border_color = st.color_picker("Border Color", "#FFFFFF")
        elif border_option == "Polaroid":
            polaroid_rotation = st.slider("Rotation Angle", -15, 15, 5)
    
    with st.expander("💧 Watermark Options", expanded=False):
        # Watermark selection
        available_logos = list_files("assets/logos", [".png"])
        use_own_logo = st.checkbox("Upload Custom Watermark", value=False)
        if use_own_logo:
            user_logo = st.file_uploader("Upload Watermark (PNG)", type=["png"])
        
        if use_own_logo and user_logo:
            logo_image = Image.open(user_logo).convert("RGBA")
        elif available_logos:
            selected_logo = st.selectbox("Choose Logo", available_logos)
            logo_path = os.path.join("assets/logos", selected_logo)
            logo_image = Image.open(logo_path).convert("RGBA")
        else:
            logo_image = None
        
        if logo_image is not None:
            watermark_opacity = st.slider("Watermark Opacity", 0.1, 1.0, 1.0)  # Fixed opacity slider
            watermark_size = st.slider("Watermark Size (% of image)", 5, 50, 20)
            watermark_position = st.selectbox("Watermark Position", ["Random", "Top Left", "Top Right", "Bottom Left", "Bottom Right", "Center"])
    
    with st.expander("✒️ Font Options", expanded=False):
        # Font selection
        available_fonts = list_files("assets/fonts", [".ttf", ".otf"])
        use_own_font = st.checkbox("Upload Custom Font", value=False)
        if use_own_font:
            user_font = st.file_uploader("Upload Font (TTF/OTF)", type=["ttf", "otf"])
        
        font_choice = None
        random_font_mode = False
        if use_own_font and user_font:
            font_choice = ImageFont.truetype(io.BytesIO(user_font.read()), 60)
        elif available_fonts:
            font_options = ["Random Font (each photo)"] + available_fonts
            selected_font = st.selectbox("Choose Font", font_options)
            if selected_font == "Random Font (each photo)":
                random_font_mode = True
            else:
                font_path = os.path.join("assets/fonts", selected_font)
                font_choice = ImageFont.truetype(font_path, 60)
        
        if font_choice or random_font_mode:
            text_shadow = st.checkbox("Add Text Shadow", value=True)
            if text_shadow:
                shadow_color = st.color_picker("Shadow Color", "#000000")
                shadow_offset = st.slider("Shadow Offset", 1, 10, 3)
                shadow_blur = st.slider("Shadow Blur", 0, 10, 2)

# =================== RIGHT SIDE FEATURE PORTAL ===================
with col2:
    st.markdown("""
        <div style='background: linear-gradient(45deg, #6a11cb 0%, #2575fc 100%); padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
            <h3 style='color: white; text-align: center; margin: 0;'>✨ Premium Features</h3>
        </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown("""
            <div class="feature-card">
                <h4>AI Image Enhancement <span class="premium-badge">PRO</span></h4>
                <p>Automatically improves image quality with AI algorithms.</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div class="feature-card">
                <h4>Batch Processing <span class="premium-badge">PRO</span></h4>
                <p>Process hundreds of images simultaneously with consistent settings.</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div class="feature-card">
                <h4>Professional Filters <span class="premium-badge">PRO</span></h4>
                <p>20+ premium filters including cinematic, vintage, and HDR effects.</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div class="feature-card">
                <h4>Advanced Watermarking <span class="premium-badge">PRO</span></h4>
                <p>Precise watermark control with opacity, size, and positioning.</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div class="feature-card">
                <h4>Custom Font Styling <span class="premium-badge">PRO</span></h4>
                <p>Support for custom fonts with shadow, outline, and gradient effects.</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div class="feature-card">
                <h4>Smart Cropping <span class="premium-badge">PRO</span></h4>
                <p>AI-powered auto-cropping for perfect composition every time.</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div class="feature-card">
                <h4>3D Effects <span class="premium-badge">NEW</span></h4>
                <p>Add depth and dimension to your images with 3D transformations.</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div class="feature-card">
                <h4>Texture Overlays <span class="premium-badge">NEW</span></h4>
                <p>Apply paper, canvas, or grunge textures for artistic effects.</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div class="feature-card">
                <h4>Gradient Maps <span class="premium-badge">NEW</span></h4>
                <p>Create stunning color grading with customizable gradients.</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div class="feature-card">
                <h4>Vignette Control <span class="premium-badge">NEW</span></h4>
                <p>Add professional vignettes with adjustable intensity and shape.</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div class="feature-card">
                <h4>Border Styles <span class="premium-badge">NEW</span></h4>
                <p>Choose from 10+ border styles including polaroid and shadow effects.</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div class="feature-card">
                <h4>Bulk Export <span class="premium-badge">NEW</span></h4>
                <p>Export all processed images in one click with ZIP compression.</p>
            </div>
        """, unsafe_allow_html=True)

# =================== MAIN PROCESSING ===================
results = []
if st.button("✨ Process Images", key="process_button"):
    if uploaded_images:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        with st.spinner("⚡ Processing images with premium quality... Please wait..."):
            total_images = len(uploaded_images)
            for idx, image_file in enumerate(uploaded_images):
                try:
                    # Update progress
                    progress = (idx + 1) / total_images
                    progress_bar.progress(progress)
                    status_text.text(f"Processing image {idx + 1} of {total_images} ({int(progress * 100)}%)")
                    
                    # Open and convert image
                    image = Image.open(image_file).convert("RGBA")
                    original_image = image.copy()
                    
                    # Apply cropping
                    image = crop_to_3_4(image)
                    w, h = image.size
                    
                    # Apply image enhancements
                    if enhance_quality:
                        image = apply_brightness(image, brightness_factor)
                        image = apply_contrast(image, contrast_factor)
                        image = apply_saturation(image, saturation_factor)
                        if sharpness_factor > 1.0:
                            image = apply_sharpen(image, sharpness_factor)
                    
                    # Apply selected filter
                    if apply_filter == "Grayscale":
                        image = apply_grayscale(image)
                    elif apply_filter == "Sepia":
                        image = apply_sepia(image)
                    elif apply_filter == "Blur":
                        image = apply_blur(image)
                    elif apply_filter == "Sharpen":
                        image = apply_sharpen(image)
                    
                    # Apply overlay effects
                    if show_overlay:
                        if selected_theme == "Auto Random":
                            theme_folder = os.path.join("assets/overlays", random.choice(theme_dirs))
                        else:
                            theme_folder = os.path.join("assets/overlays", selected_theme)
                        image = overlay_theme_overlays(image, greeting_type, theme_folder)
                    
                    # Apply vignette effect
                    if apply_vignette_effect:
                        image = apply_vignette(image, vignette_intensity)
                    
                    # Apply gradient overlay
                    if apply_gradient_overlay:
                        image = add_gradient_overlay(image, [gradient_color1, gradient_color2], gradient_opacity)
                    
                    # Prepare for drawing
                    draw = ImageDraw.Draw(image)
                    
                    # Per-image font selection
                    this_font = None
                    if font_choice and not random_font_mode:
                        this_font = font_choice
                    elif random_font_mode and available_fonts:
                        rand_font_path = os.path.join("assets/fonts", random.choice(available_fonts))
                        this_font = ImageFont.truetype(rand_font_path, 60)
                    
                    # Draw main text with optional shadow
                    if show_text and this_font:
                        font = this_font.font_variant(size=int(main_size * w // 100))
                        text = greeting_type
                        text_width, text_height = draw.textsize(text, font=font)
                        
                        if text_shadow:
                            shadow_layer = Image.new('RGBA', image.size, (0, 0, 0, 0))
                            shadow_draw = ImageDraw.Draw(shadow_layer)
                            for i in range(shadow_blur + 1):
                                offset = shadow_offset * (i / shadow_blur) if shadow_blur > 0 else shadow_offset
                                shadow_draw.text((50 + offset, 50 + offset), text, font=font, fill=shadow_color)
                            if shadow_blur > 0:
                                shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(shadow_blur))
                            image = Image.alpha_composite(image, shadow_layer)
                        
                        draw.text((50, 50), text, font=font, fill=main_color)
                    
                    # Draw sub wish text
                    if show_wish and this_font:
                        subtext = custom_wish if custom_wish else (
                            "Have a nice day!" if greeting_type == "Good Morning" else "Sweet dreams!")
                        font2 = this_font.font_variant(size=int(wish_size * w // 100))
                        text_width, text_height = draw.textsize(subtext, font=font2)
                        
                        if text_shadow:
                            shadow_layer = Image.new('RGBA', image.size, (0, 0, 0, 0))
                            shadow_draw = ImageDraw.Draw(shadow_layer)
                            for i in range(shadow_blur + 1):
                                offset = shadow_offset * (i / shadow_blur) if shadow_blur > 0 else shadow_offset
                                shadow_draw.text((60 + offset, 50 + int(main_size * w // 100) + 10 + offset), 
                                               subtext, font=font2, fill=shadow_color)
                            if shadow_blur > 0:
                                shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(shadow_blur))
                            image = Image.alpha_composite(image, shadow_layer)
                        
                        draw.text((60, 50 + int(main_size * w // 100) + 10), subtext, font=font2, fill=wish_color)
                    
                    # Draw date
                    if show_date and this_font:
                        date_font = this_font.font_variant(size=int(w * 0.035))
                        today = datetime.datetime.now().strftime("%d %B %Y")
                        text_width, text_height = draw.textsize(today, font=date_font)
                        
                        if text_shadow:
                            shadow_layer = Image.new('RGBA', image.size, (0, 0, 0, 0))
                            shadow_draw = ImageDraw.Draw(shadow_layer)
                            for i in range(shadow_blur + 1):
                                offset = shadow_offset * (i / shadow_blur) if shadow_blur > 0 else shadow_offset
                                shadow_draw.text((w - 300 + offset, h - 60 + offset), 
                                               today, font=date_font, fill=shadow_color)
                            if shadow_blur > 0:
                                shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(shadow_blur))
                            image = Image.alpha_composite(image, shadow_layer)
                        
                        draw.text((w - 300, h - 60), today, font=date_font, fill=main_color)
                    
                    # Apply watermark with fixed opacity
                    if logo_image is not None:
                        logo_resized = logo_image.copy()
                        logo_size = int(w * watermark_size / 100)
                        logo_resized.thumbnail((logo_size, logo_size))
                        
                        # Position watermark based on selection
                        if watermark_position == "Random":
                            image = place_logo_random(image, logo_resized, watermark_opacity)
                        else:
                            if watermark_position == "Top Left":
                                pos = (20, 20)
                            elif watermark_position == "Top Right":
                                pos = (w - logo_resized.width - 20, 20)
                            elif watermark_position == "Bottom Left":
                                pos = (20, h - logo_resized.height - 20)
                            elif watermark_position == "Bottom Right":
                                pos = (w - logo_resized.width - 20, h - logo_resized.height - 20)
                            elif watermark_position == "Center":
                                pos = ((w - logo_resized.width) // 2, (h - logo_resized.height) // 2)
                            
                            # Apply opacity to watermark
                            if watermark_opacity < 1.0:
                                alpha = logo_resized.split()[3]
                                alpha = ImageEnhance.Brightness(alpha).enhance(watermark_opacity)
                                logo_resized.putalpha(alpha)
                            
                            image.paste(logo_resized, pos, logo_resized)
                    
                    # Apply border effects
                    if border_option == "Simple":
                        image = add_border(image, border_size=border_size, color=border_color)
                    elif border_option == "Polaroid":
                        image = apply_polaroid_effect(image, rotation=polaroid_rotation)
                    elif border_option == "Rounded Corners":
                        image = apply_rounded_corners(image)
                    
                    final = image.convert("RGB")
                    results.append((image_file.name, final))
                
                except Exception as e:
                    st.error(f"❌ Error processing {image_file.name}: {str(e)}")
        
        progress_bar.empty()
        status_text.empty()
        st.success("🎉 All images processed successfully!")
        
        # Display results in a grid
        cols = st.columns(3)
        for idx, (name, img) in enumerate(results):
            with cols[idx % 3]:
                st.image(img, caption=name, use_column_width=True)
                img_bytes = io.BytesIO()
                img.save(img_bytes, format="JPEG", quality=95)
                st.download_button(
                    label=f"⬇️ Download {name}",
                    data=img_bytes.getvalue(),
                    file_name=f"edited_{name}",
                    mime="image/jpeg",
                    key=f"dl_{idx}"
                )
        
        # Create ZIP archive
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for name, img in results:
                img_bytes = io.BytesIO()
                img.save(img_bytes, format="JPEG", quality=95)
                zipf.writestr(f"edited_{name}", img_bytes.getvalue())
        zip_buffer.seek(0)
        
        st.download_button(
            label="📦 Download All as ZIP (Premium Quality)",
            data=zip_buffer,
            file_name="Premium_Edited_Images.zip",
            mime="application/zip",
            key="dl_all"
        )
    else:
        st.warning("⚠️ Please upload at least one image to process.")
else:
    st.info("💡 Upload images and adjust settings to begin processing. Use the premium features to enhance your photos!")

# =================== FOOTER ===================
st.markdown("""
    <div style='text-align: center; color: grey; margin-top: 50px; font-size: 0.9em;'>
        <p>✨ Premium Photo Editor Pro ™ | © 2023 All Rights Reserved</p>
        <p>Powered by Streamlit and Python PIL | v2.1.0</p>
    </div>
""", unsafe_allow_html=True)
