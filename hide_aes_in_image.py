
from PIL import Image

# AES data from our previous encryption
nonce_hex = "5e0c6d3e57c5e39483ac94386af80188"
tag_hex = "18810480deb602e7f617a4dedbcbb9cf"
ciphertext_hex = "5f5f6ad3d6"

# Convert hexadecimal into bytes
nonce = bytes.fromhex(nonce_hex)
tag = bytes.fromhex(tag_hex)
ciphertext = bytes.fromhex(ciphertext_hex)

# Combine AES data
payload = nonce + tag + ciphertext

# Convert payload into binary
binary_payload = ""

for byte in payload:
    binary_payload += format(byte, '08b')

# Create a 32-bit header containing payload length
length_header = format(len(binary_payload), '032b')

# Combine header and payload
final_bits = length_header + binary_payload

# Open the original image
img = Image.open("sample.png").convert("RGB")

width, height = img.size

# Check image capacity
if len(final_bits) > width * height * 3:
    print("Image is too small!")
else:
    pixels = list(img.getdata())
    bit_index = 0

    # Hide bits in RGB channels
    for i in range(len(pixels)):
        if bit_index >= len(final_bits):
            break

        red, green, blue = pixels[i]
        channels = [red, green, blue]

        for j in range(3):
            if bit_index < len(final_bits):
                bit = int(final_bits[bit_index])
                channels[j] = (channels[j] & 254) | bit
                bit_index += 1

        pixels[i] = tuple(channels)

    # Save the new image
    img.putdata(pixels)
    img.save("encrypted_hidden.png")

    print("AES data hidden successfully!")
    print("Total bits hidden:", bit_index)
    print("Output image: encrypted_hidden.png")
