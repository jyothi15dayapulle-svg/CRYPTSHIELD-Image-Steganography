
from PIL import Image
from Crypto.Cipher import AES


# Open the image containing hidden AES data
img = Image.open("encrypted_hidden.png").convert("RGB")

width, height = img.size


# -----------------------------------
# STEP 1: EXTRACT THE 32-BIT HEADER
# -----------------------------------

header_bits = ""

for i in range(32):

    pixel_index = i // 3
    channel_index = i % 3

    x = pixel_index % width
    y = pixel_index // width

    pixel = img.getpixel((x, y))

    bit = pixel[channel_index] & 1

    header_bits += str(bit)


# Convert header into an integer
payload_length = int(header_bits, 2)

print("Extracted header:", header_bits)
print("Payload length:", payload_length, "bits")


# -----------------------------------
# STEP 2: EXTRACT THE AES PAYLOAD
# -----------------------------------

if payload_length % 8 != 0:
    raise ValueError("Invalid payload length.")

if 32 + payload_length > width * height * 3:
    raise ValueError("Image does not contain the complete payload.")

extracted_bits = ""

for i in range(32, 32 + payload_length):

    pixel_index = i // 3
    channel_index = i % 3

    x = pixel_index % width
    y = pixel_index // width

    pixel = img.getpixel((x, y))

    bit = pixel[channel_index] & 1

    extracted_bits += str(bit)


print("Total extracted bits:", len(extracted_bits))


# -----------------------------------
# STEP 3: CONVERT BINARY INTO BYTES
# -----------------------------------

extracted_bytes = bytearray()

for i in range(0, len(extracted_bits), 8):

    byte = extracted_bits[i:i + 8]

    extracted_bytes.append(int(byte, 2))


print("Total extracted bytes:", len(extracted_bytes))


# -----------------------------------
# STEP 4: SEPARATE AES COMPONENTS
# -----------------------------------

if len(extracted_bytes) < 32:
    raise ValueError("Incomplete AES payload.")

nonce = bytes(extracted_bytes[:16])

tag = bytes(extracted_bytes[16:32])

ciphertext = bytes(extracted_bytes[32:])


print("Recovered nonce:", nonce.hex())
print("Recovered tag:", tag.hex())
print("Recovered ciphertext:", ciphertext.hex())


# -----------------------------------
# STEP 5: GET AES KEY FROM USER
# -----------------------------------

key_hex = input("Enter your AES key: ").strip()


# -----------------------------------
# STEP 6: DECRYPT THE MESSAGE
# -----------------------------------

try:

    key = bytes.fromhex(key_hex)

    if len(key) not in (16, 24, 32):
        raise ValueError("Invalid AES key length.")

    decrypt_cipher = AES.new(
        key,
        AES.MODE_GCM,
        nonce=nonce
    )

    decrypted_message = decrypt_cipher.decrypt_and_verify(
        ciphertext,
        tag
    )

    original_message = decrypted_message.decode("utf-8")

    print("\nDecrypted message:", original_message)

except (ValueError, UnicodeDecodeError) as error:

    print("\nDecryption failed:", error)
