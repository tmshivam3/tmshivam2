import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import os
import io
import random
import datetime
import zipfile

# =================== CONFIG ===================
st.set_page_config(page_title="🖼️ Edit Photo in Bulk Tool ™", layout="wide")

st.markdown("""
    <h1 style='text-align: center; color: black; background: #fff176; padding: 15px; border-radius: 12px;'>🖼️ Edit Photo in Bulk Tool ™</h1>
    <h4 style='text-align: center; color: grey;'>Apply Greetings, Watermarks, Fonts, Wishes, Overlays & More</h4>
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

def place_logo_random(img, logo):
    w, h = img.size
    logo_w, logo_h = logo.size
    max_x = max(0, w - logo_w - 30)
    max_y = max(0, h - logo_h - 30)
    x = safe_randint(20, max_x)
    y = safe_randint(20, max_y)
    opacity = random.uniform(0.45, 1.0)
    watermark = logo.copy()
    watermark = ImageEnhance.Brightness(watermark).enhance(opacity)
    img.paste(watermark, (x, y), watermark)
    return img

# =================== MAIN PAGE UPLOAD ===================
uploaded_images = st.file_uploader("📁 Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# =================== SIDEBAR ===================
st.sidebar.header("🛠️ Tool Settings")

greeting_type = st.sidebar.selectbox("Greeting Type", ["Good Morning", "Good Night"])
custom_wish = st.sidebar.text_input("Wish (optional)", value="")
show_text = st.sidebar.checkbox("Show Main Text", value=True)
show_wish = st.sidebar.checkbox("Show Sub Wish", value=True)
show_date = st.sidebar.checkbox("Show Date", value=False)

main_size = st.sidebar.slider("Main Text Size", 5, 25, 12) if show_text else None
wish_size = st.sidebar.slider("Wish Text Size", 5, 20, 10) if show_wish else None

show_overlay = st.sidebar.checkbox("Enable Overlay Wishes", value=False)
theme_dirs = sorted([d for d in os.listdir("assets/overlays") if os.path.isdir(os.path.join("assets/overlays", d))], reverse=True)
theme_options = ["Auto Random"] + theme_dirs
selected_theme = st.sidebar.selectbox("Overlay Theme", theme_options) if show_overlay else None

# Font selection
available_fonts = list_files("assets/fonts", [".ttf", ".otf"])
use_own_font = st.sidebar.checkbox("Upload Own Font")
if use_own_font:
    user_font = st.sidebar.file_uploader("Upload TTF/OTF Font", type=["ttf", "otf"])

font_choice = None
random_font_mode = False
if use_own_font and user_font:
    font_choice = ImageFont.truetype(io.BytesIO(user_font.read()), 60)
elif available_fonts:
    font_options = ["Random Font (each photo)"] + available_fonts
    selected_font = st.sidebar.selectbox("Choose Font", font_options)
    if selected_font == "Random Font (each photo)":
        random_font_mode = True
    else:
        font_path = os.path.join("assets/fonts", selected_font)
        font_choice = ImageFont.truetype(font_path, 60)

# Watermark selection
available_logos = list_files("assets/logos", [".png"])
use_own_logo = st.sidebar.checkbox("Upload Own Watermark")
if use_own_logo:
    user_logo = st.sidebar.file_uploader("Upload Watermark PNG", type=["png"])

logo_image = None
if use_own_logo and user_logo:
    logo_image = Image.open(user_logo).convert("RGBA")
elif available_logos:
    selected_logo = st.sidebar.selectbox("Choose Logo", available_logos)
    logo_path = os.path.join("assets/logos", selected_logo)
    logo_image = Image.open(logo_path).convert("RGBA")

# =================== MAIN ===================
results = []
if st.button("✅ Generate Images"):
    if uploaded_images:
        with st.spinner("🔄 Processing images... Please wait..."):
            for idx, image_file in enumerate(uploaded_images):
                try:
                    image = Image.open(image_file).convert("RGBA")
                    image = crop_to_3_4(image)
                    w, h = image.size

                    if show_overlay:
                        if selected_theme == "Auto Random":
                            theme_folder = os.path.join("assets/overlays", random.choice(theme_dirs))
                        else:
                            theme_folder = os.path.join("assets/overlays", selected_theme)
                        image = overlay_theme_overlays(image, greeting_type, theme_folder)

                    draw = ImageDraw.Draw(image)
                    color = random.choice([(255, 255, 255), (255, 255, 0), (255, 0, 0), (128, 0, 255)])

                    # Per-image font selection
                    this_font = None
                    if font_choice and not random_font_mode:
                        this_font = font_choice
                    elif random_font_mode and available_fonts:
                        rand_font_path = os.path.join("assets/fonts", random.choice(available_fonts))
                        this_font = ImageFont.truetype(rand_font_path, 60)

                    if show_text and this_font:
                        font = this_font.font_variant(size=int(main_size * w // 100))
                        draw.text((50, 50), greeting_type, font=font, fill=color)

                    if show_wish and this_font:
                        subtext = custom_wish if custom_wish else (
                            "Have a nice day!" if greeting_type == "Good Morning" else "Sweet dreams!")
                        font2 = this_font.font_variant(size=int(wish_size * w // 100))
                        draw.text((60, 50 + int(main_size * w // 100) + 10), subtext, font=font2, fill=color)

                    if show_date and this_font:
                        date_font = this_font.font_variant(size=int(w * 0.035))
                        today = datetime.datetime.now().strftime("%d %B %Y")
                        draw.text((w - 300, h - 60), today, font=date_font, fill=color)

                    if logo_image:
                        logo_resized = logo_image.copy()
                        logo_resized.thumbnail((int(w * 0.2), int(h * 0.2)))
                        image = place_logo_random(image, logo_resized)

                    final = image.convert("RGB")
                    results.append((image_file.name, final))

                except Exception as e:
                    st.error(f"❌ Error on {image_file.name}: {e}")

        st.success("✅ All images generated!")
        for name, img in results:
            st.image(img, caption=name, use_container_width=True)
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="JPEG", quality=100)   # HIGH QUALITY JPEG
            st.download_button(
                label="⬇️ Download",
                data=img_bytes.getvalue(),
                file_name=name.replace(".png", ".jpg"),
                mime="image/jpeg"
            )

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for name, img in results:
                img_bytes = io.BytesIO()
                img.save(img_bytes, format="JPEG", quality=100)  # HIGH QUALITY JPEG
                zipf.writestr(name.replace(".png", ".jpg"), img_bytes.getvalue())
        zip_buffer.seek(0)
        st.download_button(
            label="📦 Download All as ZIP",
            data=zip_buffer,
            file_name="Edited_Images.zip",
            mime="application/zip"
        )
else:
    st.info("Upload images and set your options to begin.")
