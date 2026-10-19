from PIL import Image, ImageDraw, ImageFont
f = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 26)
img = Image.new("RGB", (64, 64), (0, 0, 0))
d = ImageDraw.Draw(img)
d.ellipse([2, 2, 61, 61], fill=(53, 199, 216))
d.text((32, 33), "Y", font=f, fill=(8, 10, 14), anchor="mm")
img.save("favicon.png")
print("favicon.png")
