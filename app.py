import os, zipfile, shutil, subprocess, sys
import streamlit as st

# Agar gdown library nahi hai toh install kar do
try:
    import gdown
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "gdown"])
    import gdown

ASSETS_DIR = "assets"
ZIP_FILE = "assets.zip"

# GOOGLE DRIVE FILE ID
FILE_ID = "18qGAPUO3aCFKx7tfDxD2kOPzFXLUo66U"
ZIP_URL = f"https://drive.google.com/uc?export=download&id={FILE_ID}"

# Agar assets folder nahi hai, toh download aur extract karo
if not os.path.exists(ASSETS_DIR):
    st.info("Downloading assets from Google Drive... ⏳")
    gdown.download(ZIP_URL, ZIP_FILE, quiet=False)

    with zipfile.ZipFile(ZIP_FILE, 'r') as zip_ref:
        zip_ref.extractall("temp_assets_extract")

    # Move content correctly
    top = os.listdir("temp_assets_extract")
    if len(top) == 1 and os.path.isdir(os.path.join("temp_assets_extract", top[0])):
        shutil.move(os.path.join("temp_assets_extract", top[0]), ASSETS_DIR)
    else:
        os.makedirs(ASSETS_DIR, exist_ok=True)
        for item in top:
            shutil.move(os.path.join("temp_assets_extract", item), ASSETS_DIR)

# Yahan se tumhara original code shuru hota hai
st.title("Mera Cool Tool")

# Example: agar assets me koi image hai to dikhao
for fname in os.listdir(ASSETS_DIR):
    st.write("Asset file:", fname)
