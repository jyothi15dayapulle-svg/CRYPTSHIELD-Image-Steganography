
# AES values from our previous encryption output
nonce_hex = "5e0c6d3e57c5e39483ac94386af80188"

tag_hex = "18810480deb602e7f617a4dedbcbb9cf"

ciphertext_hex = "5f5f6ad3d6"

# Convert hexadecimal values into bytes
nonce = bytes.fromhex(nonce_hex)
tag = bytes.fromhex(tag_hex)
ciphertext = bytes.fromhex(ciphertext_hex)

# Combine all AES data
payload = nonce + tag + ciphertext

# Convert payload into binary
binary_message = ""

for byte in payload:
    binary_message += format(byte, '08b')

print("Nonce size:", len(nonce), "bytes")
print("Tag size:", len(tag), "bytes")
print("Ciphertext size:", len(ciphertext), "bytes")

print("Total payload size:", len(payload), "bytes")
print("Total binary bits:", len(binary_message))
