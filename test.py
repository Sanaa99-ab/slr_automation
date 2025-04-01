from PIL import Image, ImageDraw, ImageFont

# Create a new 16x16 image with a blue background
size = (16, 16)
image = Image.new("RGB", size, "#1E90FF")  # Blue background
draw = ImageDraw.Draw(image)

# Draw an "S" (using a basic font; adjust if you have a custom font)
try:
    font = ImageFont.truetype("arial.ttf", 12)  # Use Arial, size 12
except:
    font = ImageFont.load_default()  # Fallback to default if Arial isn’t available
draw.text((4, 2), "S", font=font, fill="white")  # Center the "S"

# Save as favicon.ico
image.save("favicon.ico", format="ICO")

print("favicon.ico generated successfully!")