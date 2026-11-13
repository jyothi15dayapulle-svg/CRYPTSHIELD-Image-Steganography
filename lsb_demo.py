
from PIL import Image

# Step 1: Open the original image
img = Image.open("sample.png").convert("RGB")

# Step 2: Secret message
message = "HELLO"

# Step 3: Convert message into binary
binary_message = ""

for byte in message.encode():
    binary_message += format(byte, '08b')

# Step 4: Hide the binary message in RGB values
pixels = list(img.get_flattened_data())

bit_index = 0

for i in range(len(pixels)):
    if bit_index >= len(binary_message):
        break

    red, green, blue = pixels[i]
    channels = [red, green, blue]

    for j in range(3):
        if bit_index < len(binary_message):
            bit = int(binary_message[bit_index])
            channels[j] = (channels[j] & 254) | bit
            bit_index += 1

    pixels[i] = tuple(channels)

# Step 5: Save modified image
img.putdata(pixels)
img.save("hello_hidden.png")

print("Original message:", message)
print("Total bits hidden:", bit_index)
print("Modified image saved successfully!")
