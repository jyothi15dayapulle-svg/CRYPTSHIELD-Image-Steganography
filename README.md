# 🔐 CRYPTSHIELD – Image Steganography with AES Encryption

**CRYPTSHIELD** is a Python-based application that combines AES encryption and image steganography to securely hide confidential messages inside digital images.

It provides two main operations: sending a secret message by embedding encrypted data into an image, and receiving the message by extracting and decrypting the hidden data.

## ✨ Features

- **AES-128-GCM Encryption:** Encrypts secret messages and provides authentication to detect tampering.
- **LSB Image Steganography:** Hides encrypted data inside image pixels using the Least Significant Bit technique.
- **Message Extraction:** Extracts hidden encrypted data from the stego image.
- **Secure Decryption:** Decrypts the extracted message using the correct AES key.
- **Graphical User Interface:** User-friendly interface built using CustomTkinter.
- **Key Generation:** Generates a random AES key for encryption.

## ⚙️ Technologies Used

- Python
- CustomTkinter
- PyCryptodome
- Pillow (PIL)
- AES-128-GCM
- Least Significant Bit (LSB) Steganography

## 🔄 Working Process

1. The sender enters a secret message.
2. The application encrypts the message using AES-128-GCM.
3. The encrypted data is embedded into an image using LSB steganography.
4. The modified image is saved and shared with the receiver.
5. The receiver selects the image and provides the correct AES key.
6. The application extracts the encrypted data and decrypts it.
7. The original secret message is displayed.

## 🛠️ Installation and Execution

### 1. Clone the repository

```bash
git clone https://github.com/jyothi15dayapulle-svg/CRYPTSHIELD-Image-Steganography.git
```

### 2. Open the project folder

```bash
cd CRYPTSHIELD-Image-Steganography
```

### 3. Create a virtual environment (optional)

```bash
python -m venv .venv
```

### 4. Activate the virtual environment (Windows)

```bash
.venv\Scripts\activate
```

### 5. Install the required libraries

```bash
pip install -r requirements.txt
```

### 6. Run the application

```bash
python main.py
```

## 🔒 Security Notes

- AES-GCM provides message confidentiality and authentication.
- The AES key must be shared securely with the intended receiver.
- The key is not stored inside the image.
- Use PNG images to preserve the hidden LSB data. JPEG compression may damage the embedded information.
- If the wrong key is provided, authentication fails and the original message cannot be recovered.

## 📁 Project Structure

```text
CRYPTSHIELD-Image-Steganography/
│
├── main.py
├── aes_demo.py
├── aes_encrypt_demo.py
├── cipher_to_binary.py
├── extract_aes_from_image.py
├── extract_message.py
├── hide_aes_in_image.py
├── image_demo.py
├── lsb_demo.py
├── modify_pixel.py
├── sample.png
├── requirements.txt
└── .gitignore
```

## 🎯 Project Objective

The objective of CRYPTSHIELD is to demonstrate how cryptographic encryption and image steganography can be combined to provide an additional layer of security for confidential communication.

**Developed as an academic project for Cryptography and Network Security.**