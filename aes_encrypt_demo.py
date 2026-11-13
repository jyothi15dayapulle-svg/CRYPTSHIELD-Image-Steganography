
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# Step 1: Original message
message = "HELLO"

# Step 2: Generate AES key
key = get_random_bytes(16)

# Step 3: Create AES cipher
cipher = AES.new(key, AES.MODE_GCM)

# Step 4: Encrypt the message
ciphertext, tag = cipher.encrypt_and_digest(message.encode())

# Step 5: Display the results
print("Original message:", message)
print("AES key:", key.hex())
print("Encrypted message:", ciphertext.hex())
print("Nonce:", cipher.nonce.hex())
print("Authentication tag:", tag.hex())
