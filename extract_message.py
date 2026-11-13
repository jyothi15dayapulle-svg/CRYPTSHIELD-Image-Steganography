
from PIL import Image

# Open the image
img = Image.open("hello_hidden.png").convert("RGB")

width, height = img.size

# We need only 40 bits for HELLO
extracted_bits = []

for i in range(40):
    pixel_index = i // 3
    channel_index = i % 3

    x = pixel_index % width
    y = pixel_index // width

    pixel = img.getpixel((x, y))

    bit = pixel[channel_index] & 1
    extracted_bits.append(str(bit))

# Combine the extracted bits
binary_message = "".join(extracted_bits)

print("Extracted binary message:")
print(binary_message)

# Convert binary into text
message_bytes = bytearray()

for i in range(0, len(binary_message), 8):
    byte = binary_message[i:i+8]
    message_bytes.append(int(byte, 2))

original_message = message_bytes.decode()

print("Recovered message:", original_message)
