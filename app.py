import zipfile

# Function to create a ZIP file containing all the images
def create_zip(images, zip_filename):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zip_file:
        for img_bytes, file_name in images:
            zip_file.writestr(file_name, img_bytes.getvalue())
    zip_buffer.seek(0)
    return zip_buffer

# BUTTON
if st.button("✅ Generate Edited Images"):
    if uploaded_images:
        with st.spinner("Processing..."):
            logo = None
            if logo_path:
                logo = Image.open(logo_path).convert("RGBA")
                logo.thumbnail((150, 150))

            font_bytes = None
            if uploaded_font:
                font_bytes = io.BytesIO(uploaded_font.read())
            elif selected_font:
                font_bytes = os.path.join("assets/fonts", selected_font)
            else:
                font_bytes = "assets/fonts/roboto.ttf"

            def generate_single_variant(img, seed=None):
                random.seed(seed)
                img = crop_to_3_4(img)
                img_w, img_h = img.size
                main_text_area = (coverage_percent / 100) * img_w * img_h
                main_font_size = max(30, int((main_text_area) ** 0.5 * 0.6))
                sub_font_size = int(main_font_size * 0.5)
                date_font_size = int(main_font_size * date_size_factor / 100)

                try:
                    if isinstance(font_bytes, str):
                        main_font = ImageFont.truetype(font_bytes, size=main_font_size)
                        sub_font = ImageFont.truetype(font_bytes, size=sub_font_size)
                        date_font = ImageFont.truetype(font_bytes, size=date_font_size)
                    else:
                        main_font = ImageFont.truetype(font_bytes, size=main_font_size)
                        sub_font = ImageFont.truetype(font_bytes, size=sub_font_size)
                        date_font = ImageFont.truetype(font_bytes, size=date_font_size)
                except:
                    main_font = ImageFont.load_default()
                    sub_font = ImageFont.load_default()
                    date_font = ImageFont.load_default()

                draw = ImageDraw.Draw(img)
                safe_margin = 30

                # Colors
                strong_colors = [(255, 255, 0), (255, 0, 0), (255, 255, 255), (255, 192, 203), (0, 255, 0)]
                text_color = random.choice(strong_colors + [tuple(random.randint(100, 255) for _ in range(3))])

                # Main Text
                x = random.randint(safe_margin, max(safe_margin, img_w - main_font_size * len(greeting_type)//2 - safe_margin))
                y = random.randint(safe_margin, max(safe_margin, img_h - main_font_size - safe_margin))
                shadow_color = "black"
                for dx in [-2, 2]:
                    for dy in [-2, 2]:
                        draw.text((x+dx, y+dy), greeting_type, font=main_font, fill=shadow_color)
                draw.text((x, y), greeting_type, font=main_font, fill=text_color)

                # Subtext
                sub_x = x + random.randint(-20, 20)
                sub_y = y + main_font_size + 10
                draw.text((sub_x, sub_y), user_subtext, font=sub_font, fill=text_color)

                # Date
                if show_date:
                    today_str = datetime.datetime.now().strftime("%d %B %Y")
                    date_x = random.randint(safe_margin, max(safe_margin, img_w - date_font_size * 10 - safe_margin))
                    date_y = random.randint(safe_margin, max(safe_margin, img_h - date_font_size - safe_margin))
                    for dx in [-2, 2]:
                        for dy in [-2, 2]:
                            draw.text((date_x+dx, date_y+dy), today_str, font=date_font, fill=shadow_color)
                    draw.text((date_x, date_y), today_str, font=date_font, fill=text_color)

                # Logo
                if logo:
                    img.paste(logo, (img_w - logo.width - 10, img_h - logo.height - 10), mask=logo)

                return img

            all_results = []
            for img_file in uploaded_images:
                image = Image.open(img_file).convert("RGB")
                variants = []
                random_font = random.choice(available_fonts)  # Randomly select a font for each image
                font_bytes = os.path.join("assets/fonts", random_font) if font_source == "Available Fonts" else io.BytesIO(uploaded_font.read()) 

                if generate_variations:
                    for i in range(4):
                        variant = generate_single_variant(image.copy(), seed=random.randint(0, 99999))
                        variants.append(variant)
                else:
                    variants = [generate_single_variant(image)]

                all_results.append((img_file.name, variants))

        st.success("✅ All images processed successfully!")

        # Preview and Download
        images_for_zip = []
        for name, variants in all_results:
            if generate_variations:
                st.write(f"**{name} - Variations**")
                for variant in variants:
                    st.image(variant, use_column_width=True)
            else:
                st.image(variants[0], caption=name, use_column_width=True)

            for i, img in enumerate(variants):
                img_bytes = io.BytesIO()
                img.save(img_bytes, format="JPEG", quality=95)
                timestamp = datetime.datetime.now().strftime("%y-%m-%d_%H-%M-%S-%f")
                file_name = f"Picsart_{timestamp}.jpg"
                st.download_button(f"⬇️ Download {file_name}", data=img_bytes.getvalue(), file_name=file_name, mime="image/jpeg")
                
                # Store images in the list for zipping
                images_for_zip.append((img_bytes, file_name))

        # Add a "Download All" button to download all images as a ZIP file
        if images_for_zip:
            zip_buffer = create_zip(images_for_zip, "all_images.zip")
            st.download_button(
                label="⬇️ Download All Images",
                data=zip_buffer,
                file_name="all_images.zip",
                mime="application/zip"
            )

    else:
        st.warning("⚠️ Please upload images before clicking Generate.")
