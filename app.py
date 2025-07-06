def apply_filter(img, selected):
    if selected == "None":
        return img
    elif selected == "Black & White":
        return img.convert("L").convert("RGB")
    elif selected == "Sepia":
        sepia_img = img.convert("RGB")
        pixels = sepia_img.load()
        for y in range(sepia_img.height):
            for x in range(sepia_img.width):
                r, g, b = pixels[x, y]
                tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                pixels[x, y] = (min(tr, 255), min(tg, 255), min(tb, 255))
        return sepia_img
    elif selected == "Brighten":
        enhancer = ImageEnhance.Brightness(img)
        return enhancer.enhance(1.3)
    elif selected == "Contrast Boost":
        enhancer = ImageEnhance.Contrast(img)
        return enhancer.enhance(1.5)
    elif selected == "Cool Blue":
        r, g, b = img.split()
        b = b.point(lambda i: min(255, int(i * 1.2)))
        return Image.merge("RGB", (r, g, b))
    elif selected == "Warm":
        r, g, b = img.split()
        r = r.point(lambda i: min(255, int(i * 1.2)))
        return Image.merge("RGB", (r, g, b))
    else:
        return img

