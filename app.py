# good_vibes_studio_app.py

import streamlit as st
from PIL import Image
import io

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="🌟 GOOD VIBES STUDIO™",
    page_icon="🧿",
    layout="centered"
)

# ==================== HEADER ====================
st.markdown(
    """
    <div style='background: linear-gradient(to right, #6a11cb, #2575fc); padding: 20px; border-radius: 12px; text-align: center;'>
        <h1 style='color: #fff; font-size: 50px; margin: 0;'>GOOD VIBES STUDIO™</h1>
        <h4 style='color: #ddd; margin-top: 10px;'>Your All-in-One PicksArt-Style Bulk Photo Editor</h4>
        <p style='color: #ccc;'>Designed with ❤️ by Shivam Bind</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# ==================== SIDEBAR ====================
st.sidebar.title("📌 Upload Your Assets")

uploaded_images = st.sidebar.file_uploader(
    "🖼️ Upload Multiple Photos", 
    type=["jpg", "jpeg", "png"], 
    accept_multiple_files=True
)

uploaded_fonts = st.sidebar.file_uploader(
    "🔤 Upload Custom Fonts (.ttf/.otf)", 
    type=["ttf", "otf"], 
    accept_multiple_files=True
)

uploaded_stickers = st.sidebar.file_uploader(
    "🌟 Upload Stickers / Logos (PNG recommended)", 
    type=["png"], 
    accept_multiple_files=True
)

st.sidebar.markdown("---")
st.sidebar.success("✅ All files securely loaded in memory.")

# ==================== MAIN SECTION ====================
st.subheader("🖼️ Your Uploaded Photos")

if uploaded_images:
    cols = st.columns(3)
    for idx, img_file in enumerate(uploaded_images):
        with cols[idx % 3]:
            img = Image.open(img_file)
            st.image(img, caption=img_file.name, use_column_width=True)
else:
    st.info("👉 Upload photos in the sidebar to see them here.")

st.markdown("---")
st.subheader("🗂️ Uploaded Fonts")
if uploaded_fonts:
    st.success(f"✅ {len(uploaded_fonts)} fonts ready to use!")
else:
    st.warning("⚠️ No fonts uploaded yet.")

st.markdown("---")
st.subheader("🎨 Uploaded Stickers / Logos")
if uploaded_stickers:
    st.success(f"✅ {len(uploaded_stickers)} stickers/logos ready to use!")
else:
    st.warning("⚠️ No stickers uploaded yet.")

