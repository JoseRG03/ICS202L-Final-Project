import os
import tkinter as tk
from tkinter import messagebox
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from PIL import Image, ImageTk
import random
from pathlib import Path

key = os.urandom(32)  # AES-256 key (32 bytes)
iv = os.urandom(16)   # Initialization Vector (16 bytes)
encrypted_files = []

user_documents = os.path.expanduser("~/Documents")
encrypt_dir = os.path.join(user_documents, "EncryptMe")
os.makedirs(encrypt_dir, exist_ok=True)

assets_dir = Path(__file__).parent / "assets"

# Encryption and Decryption
def encrypt_files():
    """Encrypt files in the target directory and its subdirectories using AES-CTR while maintaining original size."""
    global encrypted_files

    for root_dir, _, files in os.walk(encrypt_dir):
        for file_name in files:
            file_path = os.path.join(root_dir, file_name)
            if os.path.isfile(file_path):
                try:
                    # Read file data
                    with open(file_path, "rb") as file:
                        data = file.read()

                    # Encrypt data using AES-CTR
                    cipher = Cipher(algorithms.AES(key), modes.CTR(iv), backend=default_backend())
                    encryptor = cipher.encryptor()
                    encrypted_data = encryptor.update(data) + encryptor.finalize()

                    # Write encrypted data to the file
                    with open(file_path, "wb") as file:
                        file.write(encrypted_data)

                    encrypted_files.append(file_path)
                    print(f"Encrypted: {file_path}")
                except Exception as e:
                    print(f"Error encrypting {file_path}: {e}")

def decrypt_files():
    """Decrypt previously encrypted files using AES-CTR while maintaining original size."""
    for file_path in encrypted_files:
        if os.path.isfile(file_path):
            try:
                # Read encrypted file data
                with open(file_path, "rb") as file:
                    encrypted_data = file.read()

                # Decrypt data using AES-CTR
                cipher = Cipher(algorithms.AES(key), modes.CTR(iv), backend=default_backend())
                decryptor = cipher.decryptor()
                decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()

                # Write decrypted data back to the file
                with open(file_path, "wb") as file:
                    file.write(decrypted_data)

                print(f"Decrypted: {os.path.basename(file_path)}")
            except Exception as e:
                print(f"Error decrypting {file_path}: {e}")
    messagebox.showinfo("Decryption", "All files have been decrypted!")

# Monkey Behavior
def update_monkey_expression(state):
    """Update the monkey's expression."""
    canvas.itemconfig(monkey_image_on_canvas, image=monkey_images[state])

def delete_random_file():
    """Delete a random file from the EncryptMe directory."""
    files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(encrypt_dir) for f in filenames]
    if files:
        file_to_delete = random.choice(files)
        os.remove(file_to_delete)
        print(f"Deleted file: {file_to_delete}")
    else:
        print("No files left to delete in EncryptMe!")

# GUI Setup
root = tk.Tk()
root.title("Monkey File Protector")
root.geometry("400x500")  # Increased height to accommodate buttons
root.resizable(False, False)

encrypt_files()

# Load monkey images
happy_monkey_img = Image.open(assets_dir / "happy_monkey.png").resize((150, 150), Image.Resampling.LANCZOS)
angry_monkey_img = Image.open(assets_dir / "angry_monkey.png").resize((150, 150), Image.Resampling.LANCZOS)
happy_monkey = ImageTk.PhotoImage(happy_monkey_img)
angry_monkey = ImageTk.PhotoImage(angry_monkey_img)
monkey_images = {"happy": happy_monkey, "angry": angry_monkey}

# Create a frame for the monkey display
monkey_frame = tk.Frame(root, width=400, height=300)
monkey_frame.pack_propagate(False)  # Prevent frame from resizing
monkey_frame.pack(pady=10)

# Canvas to display monkey
canvas = tk.Canvas(monkey_frame, width=400, height=300)
canvas.pack()
monkey_image_on_canvas = canvas.create_image(200, 150, image=happy_monkey)

# Create a frame for the buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=20)

# Buttons
decrypt_button = tk.Button(button_frame, text="Decrypt Files", command=decrypt_files, width=20)
decrypt_button.grid(row=1, column=0, padx=10, pady=5)

# Run the GUI
root.mainloop()

