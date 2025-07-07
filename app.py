import os
import tempfile
from PIL import Image, ImageFont
import streamlit as st

# ------------------------
# CONSTANTS
# ------------------------
DEFAULT_FONT_PATH = "roboto.ttf"

# ------------------------
# FONT SELECTION
# ------------------------
st.subheader("Font Options")

font_choice = st.selectbox(
    "Choose Font", 
    ["Default (Roboto)", "Upload Your Own Font"]
)

if font_choice == "Default (Roboto)":
    font_path = DEFAULT_FONT_PATH
    st.success(f"✅ Using default font: {DEFAULT_FONT_PATH}")
else:
    uploaded_font_file = st.file_uploader("Upload a .ttf font", type=["ttf"])
    if uploaded_font_file is not None:
        temp_font_path = os.path.join(tempfile.gettempdir(), uploaded_font_file.name)
        with open(temp_font_path, "wb") as f:
            f.write(uploaded_font_file.getbuffer())
        font_path = temp_font_path
        st.success(f"✅ Uploaded font: {uploaded_font_file.name}")

        # Font preview message
        st.markdown(f"**Font file saved at:** `{temp_font_path}`")
    else:
        st.warning("⚠️ Please upload a valid .ttf font to continue.")
        st.stop()

# ------------------------
# LOAD THE FONT (SAFE)
# ------------------------
try:
    main_font = ImageFont.truetype(font_path, 80)
    st.success("✅ Font loaded successfully!")
except Exception as e:
    st.error(f"❌ Font load failed: {e}")
    st.stop()

# ------------------------
# WATERMARK PNG UPLOAD
# ------------------------
st.subheader("Watermark Logo Upload")

uploaded_watermark_file = st.file_uploader("Upload PNG watermark", type=["png"])
if uploaded_watermark_file is not None:
    try:
        watermark_image = Image.open(uploaded_watermark_file).convert("RGBA")
        st.image(watermark_image, caption="Uploaded Watermark Preview", use_column_width=True)
        st.success("✅ Watermark PNG loaded successfully!")
    except Exception as e:
        st.error(f"❌ Failed to load PNG: {e}")
else:
    st.info("ℹ️ No watermark PNG uploaded yet.")
