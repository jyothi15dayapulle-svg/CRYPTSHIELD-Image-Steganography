
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# Step 1: Original message
message = "Hello Friend! This is my secret message."

# Step 2: Generate a secret key
key = get_random_bytes(16)

# Step 3: Create AES cipher
cipher = AES.new(key, AES.MODE_GCM)

# Step 4: Encrypt the message
ciphertext, tag = cipher.encrypt_and_digest(message.encode())

print("Original Message:", message)
print("Encrypted Message:", ciphertext.hex())

# Step 5: Decrypt the message
decrypt_cipher = AES.new(
    key,
    AES.MODE_GCM,
    nonce=cipher.nonce
)

decrypted_message = decrypt_cipher.decrypt_and_verify(
    ciphertext, tag
)

print("Decrypted Message:", decrypted_message.decode())
