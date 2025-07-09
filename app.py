import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps
import os
import io
import random
import datetime
import zipfile
import numpy as np
import sqlite3

# =================== SIMPLE DATABASE SETUP ===================
def init_db():
    conn = sqlite3.connect('app_data.db')
    c = conn.cursor()
    
    # Simple visitors table
    c.execute('''CREATE TABLE IF NOT EXISTS visitors 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    # Simple feedback table
    c.execute('''CREATE TABLE IF NOT EXISTS feedback
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                  name TEXT,
                  message TEXT,
                  contact TEXT)''')
    
    conn.commit()
    conn.close()

init_db()

# Track visitor count
def track_visitor():
    conn = sqlite3.connect('app_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO visitors DEFAULT VALUES")
    conn.commit()
    conn.close()

# Save feedback
def save_feedback(name, message, contact=""):
    conn = sqlite3.connect('app_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO feedback (name, message, contact) VALUES (?, ?, ?)",
             (name, message, contact))
    conn.commit()
    conn.close()

# Get visitor count
def get_visitor_count():
    conn = sqlite3.connect('app_data.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM visitors")
    count = c.fetchone()[0]
    conn.close()
    return count

# =================== CONFIG ===================
st.set_page_config(page_title="⚡ Instant Photo Generator", layout="wide")

# Track visitor on app load
track_visitor()

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
    .feedback-box {
        background-color: #1a1a1a;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
        border: 1px solid #ffff00;
    }
    .visitor-counter {
        background-color: #1a1a1a;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 15px;
        border: 1px solid #ffff00;
    }
    </style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
    <div style='background-color: #000000; padding: 15px; border-radius: 8px; margin-bottom: 20px; border: 2px solid #ffff00;'>
        <h1 style='text-align: center; color: #ffff00; margin: 0;'>⚡ Instant Photo Generator</h1>
    </div>
""", unsafe_allow_html=True)

# =================== VISITOR COUNTER ===================
visitor_count = get_visitor_count()
st.sidebar.markdown(f"""
    <div class="visitor-counter">
        <h3>👥 Total Visitors</h3>
        <h1>{visitor_count}</h1>
    </div>
""", unsafe_allow_html=True)

# =================== FEEDBACK FORM ===================
with st.sidebar:
    st.markdown("""
    <div class="feedback-box">
        <h3>💬 Send Feedback</h3>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("feedback_form"):
        name = st.text_input("Your Name")
        message = st.text_area("Your Message")
        contact = st.text_input("Your Contact (optional)")
        
        if st.form_submit_button("Send"):
            if name and message:
                save_feedback(name, message, contact)
                st.success("Thank you for your feedback!")
            else:
                st.warning("Please enter your name and message")

# =================== WHATSAPP BUTTON ===================
st.sidebar.markdown("""
<div style='margin-top: 20px;'>
    <a href="https://wa.me/919140588751" target="_blank" style="text-decoration: none;">
        <button style="background-color: #25D366; color: white; border: none; padding: 10px 15px; border-radius: 5px; cursor: pointer; width: 100%;">
            📱 WhatsApp Support
        </button>
    </a>
</div>
""", unsafe_allow_html=True)

# =================== UTILS ===================
# [Keep all your existing utility functions here unchanged]
# ... (all your existing utility functions remain the same)

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
        show_day = st.checkbox("Show Day", value=False)
    
    # Watermark settings
    use_watermark = st.checkbox("Add Watermark", value=True)
    watermark_image = None
    
    if use_watermark:
        watermark_option = st.radio("Watermark Source", ["Pre-made", "Upload Your Own"])
        
        if watermark_option == "Pre-made":
            available_watermarks = [
                "Think Tank TV.png",
                "Wishful Vibes.png",
                "Travellar Bharat.png",
                "Good Vibes.png",
                "naturevibes.png"
            ]
            selected_watermark = st.selectbox("Select Watermark", available_watermarks, index=1)
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
            st.image(img, use_column_width=True)
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
