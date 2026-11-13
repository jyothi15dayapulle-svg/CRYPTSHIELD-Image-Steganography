from PIL import Image

img = Image.open("sample.png")

# Read the pixel at position (0, 0)
pixel = img.getpixel((0, 0))

# Display RGB values
red = pixel[0]
green = pixel[1]
blue = pixel[2]

print("Red value:", red)
print("Green value:", green)
print("Blue value:", blue)

# Display binary values
print("Red in binary:", format(red, '08b'))
print("Green in binary:", format(green, '08b'))
print("Blue in binary:", format(blue, '08b'))