# ✨ Updated portion only shown for brevity ✨

# ========== SIDEBAR ==========
st.sidebar.header("🛠️ Tool Settings")
greeting_type = st.sidebar.selectbox("Greeting Type", ["Good Morning", "Good Night"])
use_overlay_mode = st.sidebar.checkbox("🖼️ Use PNG Overlay Wishes Instead of Text")  # NEW
if use_overlay_mode:
    st.sidebar.markdown("<span style='color:yellow; font-weight:bold;'>✔ Pre-made PNG overlay mode ON</span>", unsafe_allow_html=True)

default_wish = random.choice(MORNING_WISHES if greeting_type == "Good Morning" else NIGHT_WISHES)
custom_wish = st.sidebar.text_input("Wishes Text (optional)", value="")
show_wish_text = st.sidebar.checkbox("Show Wishes Text", value=True)
coverage_percent = st.sidebar.slider("Main Text Coverage (%)", 5, 20, 8)
show_date = st.sidebar.checkbox("Add Today's Date", value=False)
date_size_factor = st.sidebar.slider("Date Text Size (%)", 30, 120, 70)

available_fonts = list_files("assets/fonts", [".ttf", ".otf"])
font_file = st.sidebar.selectbox("Choose Font", available_fonts)

available_logos = list_files("assets/logos", [".png"])
logo_file = st.sidebar.selectbox("Choose Watermark Logo", available_logos)

uploaded_images = st.file_uploader("📁 Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# ✨ Helper function to apply random PNG overlays
def apply_png_wishes(image, folder_path):
    if not os.path.exists(folder_path) or not os.listdir(folder_path):
        return image, False
    files = [f for f in os.listdir(folder_path) if f.lower().endswith(".png")]
    if not files:
        return image, False

    w, h = image.size
    for _ in range(random.randint(1, 3)):
        file = random.choice(files)
        overlay = Image.open(os.path.join(folder_path, file)).convert("RGBA")
        overlay.thumbnail((int(w * 0.3), int(h * 0.15)))
        x = safe_randint(0, w - overlay.width)
        y = safe_randint(0, h - overlay.height)
        image.paste(overlay, (x, y), overlay)

    return image, True

# ========== MAIN PROCESS ==========
if st.button("✅ Generate Edited Images"):
    if uploaded_images:
        with st.spinner("🌀 Processing images... Please wait."):
            status_text = st.empty()
            logo_path = os.path.join("assets/logos", logo_file)
            font_path = os.path.join("assets/fonts", font_file)

            for idx, image_file in enumerate(uploaded_images, start=1):
                try:
                    status_text.markdown(f"🔧 Processing **{image_file.name}** ({idx}/{len(uploaded_images)})...")
                    time.sleep(0.3)

                    image = Image.open(image_file).convert("RGBA")
                    image = crop_to_3_4(image)
                    w, h = image.size

                    main_text_area = (coverage_percent / 100) * w * h
                    main_font_size = max(30, int(main_text_area ** 0.5 * 0.6))
                    sub_font_size = int(main_font_size * 0.5)
                    date_font_size = int(main_font_size * date_size_factor / 100)

                    main_font = ImageFont.truetype(font_path, main_font_size)
                    sub_font = ImageFont.truetype(font_path, sub_font_size)
                    date_font = ImageFont.truetype(font_path, date_font_size)

                    draw = ImageDraw.Draw(image)
                    text_color = random.choice(COLORS)
                    wish_text = custom_wish if custom_wish.strip() else default_wish

                    if use_overlay_mode:
                        overlay_folder = f"assets/overlays/{greeting_type.lower().split()[1]}"
                        image, overlay_success = apply_png_wishes(image, overlay_folder)
                        if not overlay_success:
                            overlay_text(draw, (50, 50), "⚠ PNG Wishes Coming Soon!", main_font, (255, 255, 0), shadow=True)
                    else:
                        x_range = max(30, w - main_font_size * len(greeting_type) // 2 - 30)
                        y_range = max(30, h - main_font_size - 30)
                        x = safe_randint(30, x_range)
                        y = safe_randint(30, y_range)

                        overlay_text(draw, (x, y), greeting_type, main_font, text_color,
                                     shadow=random.choice([True, False]),
                                     outline=random.choice([True, False]))

                        if show_wish_text:
                            wish_x = x + random.randint(-15, 15)
                            wish_y = y + main_font_size + 10
                            overlay_text(draw, (wish_x, wish_y), wish_text, sub_font, text_color,
                                         shadow=random.choice([True, False]))

                    if show_date:
                        today = datetime.datetime.now().strftime("%d %B %Y")
                        dx = safe_randint(30, max(30, w - 200))
                        dy = safe_randint(30, max(30, h - 50))
                        overlay_text(draw, (dx, dy), today, date_font, random.choice(COLORS),
                                     shadow=random.choice([True, False]))

                    logo = Image.open(logo_path).convert("RGBA")
                    logo.thumbnail((int(w * 0.25), int(h * 0.25)))
                    image = place_logo_random(image, logo)

                    final_image = image.convert("RGB")
                    results.append((image_file.name, final_image))

                except Exception as e:
                    st.error(f"❌ Error Occurred: {str(e)}")

            status_text.success("✅ All images processed successfully!")

# 🔚 Remainder of code stays same — ZIP download & per-image download
