import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import random
import io

# App Title
st.set_page_config(page_title="EDIT photo in one click")
st.title("EDIT photo in one click")

# Upload images
uploaded_images = st.file_uploader(
    "Upload one or more photos", accept_multiple_files=True, type=["jpg", "jpeg", "png"]
)

# Main text
main_text = st.text_input("Main Text", "Good Morning")
sub_text = st.text_input("Sub Text", "Have a Nice Day")

# Coverage slider (new scaling)
coverage_percent = st.slider("Main Text Coverage (%)", 5, 25, 10)

# Font selection
font_choice = st.selectbox("Choose Font", ["Default (Roboto)", "Upload Your Own Font"])
if font_choice == "Default (Roboto)":
    font_path = "Roboto-Regular.ttf"  # Make sure this .ttf is in same folder
else:
    uploaded_font = st.file_uploader("Upload a .ttf Font", type=["ttf"], key="font")
    if uploaded_font:
        font_bytes = uploaded_font.read()
        font_path = io.BytesIO(font_bytes)
    else:
        font_path = None

# Texture option
apply_texture = st.checkbox("Apply Text Texture")
if apply_texture:
    texture_image = st.file_uploader("Upload Texture Image (PNG recommended)", type=["png"], key="texture")

# Add date option
add_date = st.checkbox("Add Today's Date on Photo")

# Helper function: random high-contrast color
def get_random_high_contrast_color():
    base = random.choice([(200, 50), (50, 200)])
    r = random.randint(base[0], 255)
    g = random.randint(0, 50)
    b = random.randint(base[1], 255)
    return (r, g, b)

# Process button
if st.button("Generate Images"):
    if not uploaded_images:
        st.warning("Please upload at least one photo.")
    elif font_path is None:
        st.warning("Please select or upload a font.")
    else:
        for img_file in uploaded_images:
            img = Image.open(img_file).convert("RGBA")
            W, H = img.size

            # Create overlay for text
            overlay = Image.new('RGBA', img.size, (255,255,255,0))
            draw = ImageDraw.Draw(overlay)

            # Calculate font size with new scaling
            main_font_size = int((coverage_percent / 4) * H / 100)
            sub_font_size = int(main_font_size * 0.5)
            date_font_size = int(H * 0.04)

            main_color = get_random_high_contrast_color()
            sub_color = get_random_high_contrast_color()
            while sub_color == main_color:
                sub_color = get_random_high_contrast_color()

            try:
                main_font = ImageFont.truetype(font_path, main_font_size)
                sub_font = ImageFont.truetype(font_path, sub_font_size)
                date_font = ImageFont.truetype(font_path, date_font_size)
            except:
                st.error("Invalid font file. Please use a valid .ttf.")
                break

            # Random safe position
            margin = 50
            x_pos = random.randint(margin, W - margin - main_font_size*len(main_text)//2)
            y_pos = random.randint(margin, H - margin - main_font_size)

            # Draw Main Text
            draw.text((x_pos, y_pos), main_text, font=main_font, fill=main_color)

            # Draw Sub Text below Main Text
            sub_y_pos = y_pos + main_font_size + 10
            if sub_y_pos + sub_font_size < H - margin:
                draw.text((x_pos, sub_y_pos), sub_text, font=sub_font, fill=sub_color)

            # Apply texture if chosen
            if apply_texture and texture_image:
                texture = Image.open(texture_image).resize((W, H)).convert("RGBA")
                overlay = Image.composite(texture, overlay, overlay)

            # Add Date if chosen
            if add_date:
                today = datetime.now().strftime("%-d %B %Y")
                date_x = random.randint(margin, W - margin - 200)
                date_y = random.randint(H - 100, H - margin)
                draw.text((date_x, date_y), today, font=date_font, fill=get_random_high_contrast_color())

            # Merge overlay with image
            final_image = Image.alpha_composite(img, overlay).convert("RGB")

            # Display and download
            st.image(final_image, caption=f"Edited - {img_file.name}", use_column_width=True)

            buf = io.BytesIO()
            final_image.save(buf, format="JPEG")
            byte_im = buf.getvalue()
            st.download_button(
                label=f"Download {img_file.name}",
                data=byte_im,
                file_name=f"edited_{img_file.name}",
                mime="image/jpeg"
            )

