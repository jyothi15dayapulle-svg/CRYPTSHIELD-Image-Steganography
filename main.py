
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk

from PIL import Image
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes


# --------------------------------------------------
# APPLICATION SETTINGS
# --------------------------------------------------

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("CRYPTSHIELD - Image Steganography")
root.geometry("1100x750")
root.minsize(900, 650)

BG = "#0B1120"
SIDEBAR = "#111C30"
CARD = "#17243A"
BLUE = "#3B82F6"
GREEN = "#22C55E"
TEXT = "#F8FAFC"
MUTED = "#94A3B8"


# --------------------------------------------------
# GLOBAL VARIABLES
# --------------------------------------------------

sender_image_path = None
receiver_image_path = None

sender_preview_image = None
receiver_preview_image = None


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def bytes_to_binary(data):
    """Convert bytes into a binary string."""
    return ''.join(format(byte, '08b') for byte in data)


def read_bits(bits):
    """Convert a binary string back into bytes."""
    return bytes(
        int(bits[i:i + 8], 2)
        for i in range(0, len(bits), 8)
    )


def embed_data(image, data):
    """Hide binary data inside the RGB LSBs of an image."""

    binary_data = bytes_to_binary(data)

    # Store payload length in the first 32 bits.
    length_header = format(len(data), '032b')
    complete_data = length_header + binary_data

    pixels = list(image.get_flattened_data())

    capacity = len(pixels) * 3

    if len(complete_data) > capacity:
        raise ValueError(
            "Image is too small to store this message. "
            "Please select a larger image."
        )

    bit_index = 0

    for i in range(len(pixels)):

        if bit_index >= len(complete_data):
            break

        red, green, blue = pixels[i]
        channels = [red, green, blue]

        for j in range(3):

            if bit_index < len(complete_data):

                bit = int(complete_data[bit_index])

                channels[j] = (
                    channels[j] & 254
                ) | bit

                bit_index += 1

        pixels[i] = tuple(channels)

    image.putdata(pixels)

    return image


def extract_data(image):
    """Extract hidden bytes from an image."""

    pixels = list(image.get_flattened_data())

    # Read the first 32 bits to get payload length.
    header_bits = ""

    for pixel in pixels:
        for channel in pixel:
            header_bits += str(channel & 1)

            if len(header_bits) == 32:
                break

        if len(header_bits) == 32:
            break

    if len(header_bits) != 32:
        raise ValueError("Unable to read image data.")

    data_length = int(header_bits, 2)

    total_bits = 32 + (data_length * 8)

    if total_bits > len(pixels) * 3:
        raise ValueError("Invalid or incomplete hidden data.")

    # Read the complete header and payload.
    extracted_bits = ""

    for pixel in pixels:
        for channel in pixel:
            extracted_bits += str(channel & 1)

            if len(extracted_bits) == total_bits:
                break

        if len(extracted_bits) == total_bits:
            break

    payload_bits = extracted_bits[32:]

    return read_bits(payload_bits)


# --------------------------------------------------
# SENDER FUNCTIONS
# --------------------------------------------------

def select_sender_image():

    global sender_image_path, sender_preview_image

    path = filedialog.askopenfilename(
        filetypes=[
            ("Image files", "*.png *.jpg *.jpeg *.bmp")
        ]
    )

    if path:

        try:
            preview = Image.open(path).convert("RGB")

            sender_image_path = path

            sender_file_label.configure(
                text=path.split("/")[-1],
                text_color=TEXT
            )

            sender_preview_image = ctk.CTkImage(
                light_image=preview,
                dark_image=preview,
                size=(200, 130)
            )

            sender_preview_label.configure(
                image=sender_preview_image,
                text=""
            )

            sender_status.configure(
                text="Cover image selected successfully.",
                text_color=GREEN
            )

        except Exception as error:

            messagebox.showerror(
                "Image Error",
                str(error)
            )


def encrypt_and_hide():

    global sender_image_path

    message = sender_message_box.get("1.0", "end").strip()

    if not message:
        messagebox.showwarning(
            "Missing Message",
            "Please enter a secret message."
        )
        return

    if not sender_image_path:
        messagebox.showwarning(
            "Missing Image",
            "Please select a cover image."
        )
        return

    sender_progress.stop()
    sender_progress.set(0)

    try:

        sender_status.configure(
            text="Encrypting and hiding message...",
            text_color=BLUE
        )

        sender_progress.start()
        root.update_idletasks()

        # Step 1: Generate a 128-bit AES key.
        key = get_random_bytes(16)

        # Step 2: Encrypt the message using AES-GCM.
        cipher = AES.new(key, AES.MODE_GCM)

        ciphertext, tag = cipher.encrypt_and_digest(
            message.encode("utf-8")
        )

        nonce = cipher.nonce

        # Step 3: Combine nonce, tag and ciphertext.
        payload = nonce + tag + ciphertext

        # Step 4: Load the selected image.
        image = Image.open(sender_image_path).convert("RGB")

        # Step 5: Hide encrypted data inside the image.
        image = embed_data(image, payload)

        # Step 6: Ask where to save the output.
        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png")],
            initialfile="encrypted_hidden.png"
        )

        if not save_path:
            sender_progress.stop()
            sender_progress.set(0)
            sender_status.configure(
                text="Save cancelled.",
                text_color=MUTED
            )
            return

        # Step 7: Save the modified image.
        image.save(save_path, format="PNG")

        # Step 8: Display the AES key.
        sender_key_entry.configure(state="normal")
        sender_key_entry.delete(0, "end")
        sender_key_entry.insert(0, key.hex())
        sender_key_entry.configure(state="readonly")

        sender_progress.stop()
        sender_progress.set(1)

        sender_status.configure(
            text="Message encrypted and hidden successfully!",
            text_color=GREEN
        )

        messagebox.showinfo(
            "Success",
            "Your secret message has been encrypted "
            "and hidden inside the image!\n\n"
            f"Saved image:\n{save_path}\n\n"
            "Share the AES key separately with the receiver."
        )

    except Exception as error:

        sender_progress.stop()
        sender_progress.set(0)

        sender_status.configure(
            text="Encryption failed.",
            text_color="#EF4444"
        )

        messagebox.showerror(
            "Encryption Error",
            str(error)
        )


def copy_key():

    key = sender_key_entry.get()

    if key:

        root.clipboard_clear()
        root.clipboard_append(key)

        messagebox.showinfo(
            "Copied",
            "AES key copied to clipboard."
        )

    else:

        messagebox.showwarning(
            "No Key",
            "Generate an AES key first."
        )


# --------------------------------------------------
# RECEIVER FUNCTIONS
# --------------------------------------------------

def select_receiver_image():

    global receiver_image_path, receiver_preview_image

    path = filedialog.askopenfilename(
        filetypes=[
            ("PNG images", "*.png")
        ]
    )

    if path:

        try:

            preview = Image.open(path).convert("RGB")

            receiver_image_path = path

            receiver_file_label.configure(
                text=path.split("/")[-1],
                text_color=TEXT
            )

            receiver_preview_image = ctk.CTkImage(
                light_image=preview,
                dark_image=preview,
                size=(200, 130)
            )

            receiver_preview_label.configure(
                image=receiver_preview_image,
                text=""
            )

            receiver_status.configure(
                text="Encrypted image selected successfully.",
                text_color=GREEN
            )

        except Exception as error:

            messagebox.showerror(
                "Image Error",
                str(error)
            )


def extract_and_decrypt():

    if not receiver_image_path:

        messagebox.showwarning(
            "Missing Image",
            "Please select an encrypted image."
        )
        return

    key_text = receiver_key_entry.get().strip()

    try:

        key = bytes.fromhex(key_text)

        if len(key) not in (16, 24, 32):
            raise ValueError(
                "AES key must be 16, 24 or 32 bytes."
            )

    except ValueError:

        messagebox.showerror(
            "Invalid Key",
            "Please enter a valid AES key in hexadecimal format."
        )
        return

    receiver_progress.stop()
    receiver_progress.set(0)

    try:

        receiver_status.configure(
            text="Extracting and decrypting message...",
            text_color=GREEN
        )

        receiver_progress.start()
        root.update_idletasks()

        # Step 1: Open the encrypted image.
        image = Image.open(receiver_image_path).convert("RGB")

        # Step 2: Extract hidden encrypted data.
        payload = extract_data(image)

        # Step 3: Separate nonce, tag and ciphertext.
        if len(payload) < 32:
            raise ValueError("Hidden data is incomplete.")

        nonce = payload[:16]
        tag = payload[16:32]
        ciphertext = payload[32:]

        # Step 4: Decrypt and verify using AES-GCM.
        cipher = AES.new(
            key,
            AES.MODE_GCM,
            nonce=nonce
        )

        plaintext = cipher.decrypt_and_verify(
            ciphertext,
            tag
        )

        recovered_message = plaintext.decode("utf-8")

        # Step 5: Display recovered message.
        receiver_result_box.delete("1.0", "end")
        receiver_result_box.insert(
            "1.0",
            recovered_message
        )

        receiver_progress.stop()
        receiver_progress.set(1)

        receiver_status.configure(
            text="Message extracted and verified successfully!",
            text_color=GREEN
        )

    except Exception as error:

        receiver_progress.stop()
        receiver_progress.set(0)

        receiver_status.configure(
            text="Extraction or decryption failed.",
            text_color="#EF4444"
        )

        receiver_result_box.delete("1.0", "end")

        messagebox.showerror(
            "Decryption Error",
            "Unable to recover the message.\n\n"
            "Check that you selected the correct image "
            "and entered the correct AES key.\n\n"
            f"Details: {error}"
        )


# --------------------------------------------------
# MAIN APPLICATION LAYOUT
# --------------------------------------------------

main_frame = ctk.CTkFrame(
    root,
    fg_color=BG,
    corner_radius=0
)

main_frame.pack(fill="both", expand=True)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

sidebar = ctk.CTkFrame(
    main_frame,
    width=230,
    fg_color=SIDEBAR,
    corner_radius=0
)

sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)


logo = ctk.CTkLabel(
    sidebar,
    text="🔐 CRYPTSHIELD",
    font=("Arial", 23, "bold"),
    text_color=TEXT
)

logo.pack(pady=(35, 8), padx=15)


logo_subtitle = ctk.CTkLabel(
    sidebar,
    text="SECURE IMAGE COMMUNICATION",
    font=("Arial", 9),
    text_color=MUTED
)

logo_subtitle.pack(pady=(0, 45))


def show_sender():

    receiver_page.pack_forget()
    sender_page.pack(fill="both", expand=True, padx=30, pady=25)

    sender_nav.configure(
        fg_color=BLUE,
        text_color="white"
    )

    receiver_nav.configure(
        fg_color="transparent",
        text_color=MUTED
    )


def show_receiver():

    sender_page.pack_forget()
    receiver_page.pack(fill="both", expand=True, padx=30, pady=25)

    receiver_nav.configure(
        fg_color=GREEN,
        text_color="white"
    )

    sender_nav.configure(
        fg_color="transparent",
        text_color=MUTED
    )


sender_nav = ctk.CTkButton(
    sidebar,
    text="✉   Sender",
    height=48,
    corner_radius=10,
    anchor="w",
    font=("Arial", 15, "bold"),
    fg_color=BLUE,
    command=show_sender
)

sender_nav.pack(fill="x", padx=18, pady=8)


receiver_nav = ctk.CTkButton(
    sidebar,
    text="🔓   Receiver",
    height=48,
    corner_radius=10,
    anchor="w",
    font=("Arial", 15, "bold"),
    fg_color="transparent",
    text_color=MUTED,
    hover_color=CARD,
    command=show_receiver
)

receiver_nav.pack(fill="x", padx=18, pady=8)


sidebar_footer = ctk.CTkLabel(
    sidebar,
    text="AES-128-GCM\nLSB STEGANOGRAPHY\n\nCNS MINI PROJECT",
    font=("Arial", 10),
    text_color=MUTED,
    justify="left"
)

sidebar_footer.pack(side="bottom", pady=30, padx=18)


# --------------------------------------------------
# MAIN CONTENT AREA
# --------------------------------------------------

content = ctk.CTkFrame(
    main_frame,
    fg_color=BG,
    corner_radius=0
)

content.pack(side="left", fill="both", expand=True)


# --------------------------------------------------
# SENDER PAGE
# --------------------------------------------------

sender_page = ctk.CTkScrollableFrame(
    content,
    fg_color="transparent",
    corner_radius=0
)


sender_title = ctk.CTkLabel(
    sender_page,
    text="Sender Workspace",
    font=("Arial", 28, "bold"),
    text_color=TEXT
)

sender_title.pack(anchor="w", pady=(5, 5))


sender_subtitle = ctk.CTkLabel(
    sender_page,
    text="Encrypt your secret message and hide it inside an image.",
    font=("Arial", 13),
    text_color=MUTED
)

sender_subtitle.pack(anchor="w", pady=(0, 25))


# Message card
message_card = ctk.CTkFrame(
    sender_page,
    fg_color=CARD,
    corner_radius=15
)

message_card.pack(fill="x", pady=10)


ctk.CTkLabel(
    message_card,
    text="01  |  SECRET MESSAGE",
    font=("Arial", 14, "bold"),
    text_color=TEXT
).pack(anchor="w", padx=20, pady=(20, 10))


sender_message_box = ctk.CTkTextbox(
    message_card,
    height=110,
    corner_radius=10,
    font=("Arial", 14),
    border_width=1,
    border_color="#334155"
)

sender_message_box.pack(
    fill="x",
    padx=20,
    pady=(0, 20)
)


# Image card
image_card = ctk.CTkFrame(
    sender_page,
    fg_color=CARD,
    corner_radius=15
)

image_card.pack(fill="x", pady=10)


ctk.CTkLabel(
    image_card,
    text="02  |  COVER IMAGE",
    font=("Arial", 14, "bold"),
    text_color=TEXT
).pack(anchor="w", padx=20, pady=(20, 10))


ctk.CTkButton(
    image_card,
    text="Select Cover Image",
    height=38,
    fg_color="#263B59",
    hover_color="#345477",
    command=select_sender_image
).pack(anchor="w", padx=20, pady=5)


sender_file_label = ctk.CTkLabel(
    image_card,
    text="No image selected",
    text_color=MUTED,
    font=("Arial", 12)
)

sender_file_label.pack(anchor="w", padx=20, pady=5)


sender_preview_label = ctk.CTkLabel(
    image_card,
    text="Image preview will appear here",
    text_color=MUTED
)

sender_preview_label.pack(
    anchor="w",
    padx=20,
    pady=(5, 15)
)


# Encrypt button
ctk.CTkButton(
    sender_page,
    text="🔒  ENCRYPT & HIDE MESSAGE",
    height=48,
    corner_radius=10,
    font=("Arial", 15, "bold"),
    fg_color=BLUE,
    hover_color="#2563EB",
    command=encrypt_and_hide
).pack(fill="x", pady=(15, 10))


sender_progress = ctk.CTkProgressBar(
    sender_page,
    height=8,
    progress_color=BLUE
)

sender_progress.pack(fill="x", pady=8)
sender_progress.set(0)


sender_status = ctk.CTkLabel(
    sender_page,
    text="Ready to encrypt.",
    font=("Arial", 12),
    text_color=MUTED
)

sender_status.pack(anchor="w", pady=8)


# AES key card
key_card = ctk.CTkFrame(
    sender_page,
    fg_color=CARD,
    corner_radius=15
)

key_card.pack(fill="x", pady=10)


ctk.CTkLabel(
    key_card,
    text="03  |  GENERATED AES KEY",
    font=("Arial", 14, "bold"),
    text_color=TEXT
).pack(anchor="w", padx=20, pady=(20, 10))


sender_key_entry = ctk.CTkEntry(
    key_card,
    height=40,
    font=("Consolas", 12),
    show="*",
    placeholder_text="AES key will appear here"
)

sender_key_entry.pack(
    fill="x",
    padx=20,
    pady=5
)

sender_key_entry.configure(state="readonly")


ctk.CTkButton(
    key_card,
    text="Copy AES Key",
    height=35,
    fg_color="#263B59",
    hover_color="#345477",
    command=copy_key
).pack(anchor="w", padx=20, pady=(5, 20))


# --------------------------------------------------
# RECEIVER PAGE
# --------------------------------------------------

receiver_page = ctk.CTkScrollableFrame(
    content,
    fg_color="transparent",
    corner_radius=0
)


receiver_title = ctk.CTkLabel(
    receiver_page,
    text="Receiver Workspace",
    font=("Arial", 28, "bold"),
    text_color=TEXT
)

receiver_title.pack(anchor="w", pady=(5, 5))


receiver_subtitle = ctk.CTkLabel(
    receiver_page,
    text="Extract the hidden message and decrypt it using the AES key.",
    font=("Arial", 13),
    text_color=MUTED
)

receiver_subtitle.pack(anchor="w", pady=(0, 25))


# Encrypted image card
receive_card = ctk.CTkFrame(
    receiver_page,
    fg_color=CARD,
    corner_radius=15
)

receive_card.pack(fill="x", pady=10)


ctk.CTkLabel(
    receive_card,
    text="01  |  ENCRYPTED IMAGE",
    font=("Arial", 14, "bold"),
    text_color=TEXT
).pack(anchor="w", padx=20, pady=(20, 10))


ctk.CTkButton(
    receive_card,
    text="Select Encrypted Image",
    height=38,
    fg_color="#263B59",
    hover_color="#345477",
    command=select_receiver_image
).pack(anchor="w", padx=20, pady=5)


receiver_file_label = ctk.CTkLabel(
    receive_card,
    text="No image selected",
    text_color=MUTED,
    font=("Arial", 12)
)

receiver_file_label.pack(anchor="w", padx=20, pady=5)


receiver_preview_label = ctk.CTkLabel(
    receive_card,
    text="Image preview will appear here",
    text_color=MUTED
)

receiver_preview_label.pack(
    anchor="w",
    padx=20,
    pady=(5, 15)
)


# AES key card
receiver_key_card = ctk.CTkFrame(
    receiver_page,
    fg_color=CARD,
    corner_radius=15
)

receiver_key_card.pack(fill="x", pady=10)


ctk.CTkLabel(
    receiver_key_card,
    text="02  |  AES DECRYPTION KEY",
    font=("Arial", 14, "bold"),
    text_color=TEXT
).pack(anchor="w", padx=20, pady=(20, 10))


receiver_key_entry = ctk.CTkEntry(
    receiver_key_card,
    height=42,
    font=("Consolas", 12),
    placeholder_text="Enter the AES key received from sender"
)

receiver_key_entry.pack(
    fill="x",
    padx=20,
    pady=(0, 20)
)


# Decrypt button
ctk.CTkButton(
    receiver_page,
    text="🔓  EXTRACT & DECRYPT MESSAGE",
    height=48,
    corner_radius=10,
    font=("Arial", 15, "bold"),
    fg_color=GREEN,
    hover_color="#16A34A",
    command=extract_and_decrypt
).pack(fill="x", pady=(15, 10))


receiver_progress = ctk.CTkProgressBar(
    receiver_page,
    height=8,
    progress_color=GREEN
)

receiver_progress.pack(fill="x", pady=8)
receiver_progress.set(0)


receiver_status = ctk.CTkLabel(
    receiver_page,
    text="Ready to receive.",
    font=("Arial", 12),
    text_color=MUTED
)

receiver_status.pack(anchor="w", pady=8)


# Recovered message card
result_card = ctk.CTkFrame(
    receiver_page,
    fg_color=CARD,
    corner_radius=15
)

result_card.pack(fill="x", pady=10)


ctk.CTkLabel(
    result_card,
    text="03  |  RECOVERED SECRET MESSAGE",
    font=("Arial", 14, "bold"),
    text_color=TEXT
).pack(anchor="w", padx=20, pady=(20, 10))


receiver_result_box = ctk.CTkTextbox(
    result_card,
    height=120,
    corner_radius=10,
    font=("Arial", 14),
    border_width=1,
    border_color="#334155"
)

receiver_result_box.pack(
    fill="x",
    padx=20,
    pady=(0, 20)
)


# --------------------------------------------------
# START APPLICATION
# --------------------------------------------------

show_sender()

root.mainloop()
