import os
import time
import tkinter as tk
from tkinter import messagebox
from cryptography.fernet import Fernet
from pynput.mouse import Listener
from PIL import Image, ImageTk
import random

# Globals
mouse_position = (0, 0)
mouse_speed = 0
key = Fernet.generate_key()  # Symmetric encryption key
fernet = Fernet(key)
SPEED_THRESHOLD = 200  # Threshold for mouse speed
encrypted_files = []

# Paths
user_documents = os.path.expanduser("~/Documents")
encrypt_dir = os.path.join(user_documents, "EncryptMe")
monkey_pics_dir = os.path.join(user_documents, "monkey pics")

# Ensure directories exist
os.makedirs(encrypt_dir, exist_ok=True)
os.makedirs(monkey_pics_dir, exist_ok=True)

# Encryption and Decryption
def encrypt_files():
    """Encrypt files in the target directory."""
    global encrypted_files
    for file_name in os.listdir(encrypt_dir):
        file_path = os.path.join(encrypt_dir, file_name)
        if os.path.isfile(file_path):
            try:
                with open(file_path, "rb") as file:
                    data = file.read()
                encrypted_data = fernet.encrypt(data)
                with open(file_path, "wb") as file:
                    file.write(encrypted_data)
                encrypted_files.append(file_path)
            except Exception as e:
                print(f"Error encrypting {file_name}: {e}")

def decrypt_files():
    """Decrypt previously encrypted files."""
    for file_path in encrypted_files:
        if os.path.isfile(file_path):
            try:
                with open(file_path, "rb") as file:
                    encrypted_data = file.read()
                decrypted_data = fernet.decrypt(encrypted_data)
                with open(file_path, "wb") as file:
                    file.write(decrypted_data)
            except Exception as e:
                print(f"Error decrypting {file_path}: {e}")
    messagebox.showinfo("Decryption", "All files have been decrypted!")

# Monkey Behavior
def update_monkey_expression(state):
    """Update the monkey's expression."""
    canvas.itemconfig(monkey_image_on_canvas, image=monkey_images[state])

def delete_random_file():
    """Delete a random file from the monkey pics directory."""
    files = os.listdir(monkey_pics_dir)
    if files:
        file_to_delete = random.choice(files)
        file_path = os.path.join(monkey_pics_dir, file_to_delete)
        os.remove(file_path)
        print(f"Deleted file: {file_to_delete}")

def monitor_mouse_speed():
    """Monitor the mouse speed and make the monkey angry if it moves too fast."""
    global mouse_position
    last_position = mouse_position
    while True:
        time.sleep(0.1)
        current_position = mouse_position
        x_diff = current_position[0] - last_position[0]
        y_diff = current_position[1] - last_position[1]
        speed = (x_diff**2 + y_diff**2) ** 0.5 / 0.1  # Speed = distance / time
        if speed > SPEED_THRESHOLD:
            update_monkey_expression("angry")
            delete_random_file()
        else:
            update_monkey_expression("happy")
        last_position = current_position

def on_mouse_move(x, y):
    """Update the mouse position."""
    global mouse_position
    mouse_position = (x, y)

# GUI Setup
root = tk.Tk()
root.title("Monkey File Protector")
root.geometry("400x400")
root.resizable(False, False)

# Load monkey images
happy_monkey_img = Image.open("happy_monkey.png").resize((150, 150), Image.ANTIALIAS)
angry_monkey_img = Image.open("angry_monkey.png").resize((150, 150), Image.ANTIALIAS)
happy_monkey = ImageTk.PhotoImage(happy_monkey_img)
angry_monkey = ImageTk.PhotoImage(angry_monkey_img)
monkey_images = {"happy": happy_monkey, "angry": angry_monkey}

# Canvas to display monkey
canvas = tk.Canvas(root, width=400, height=400)
canvas.pack()
monkey_image_on_canvas = canvas.create_image(200, 200, image=happy_monkey)

# Buttons
encrypt_button = tk.Button(root, text="Encrypt Files", command=encrypt_files)
encrypt_button.pack(pady=10)
decrypt_button = tk.Button(root, text="Decrypt Files", command=decrypt_files)
decrypt_button.pack(pady=10)

# Start a thread for mouse speed monitoring
import threading
threading.Thread(target=monitor_mouse_speed, daemon=True).start()

# Start mouse listener
listener = Listener(on_move=on_mouse_move)
listener.start()

# Run the GUI
root.mainloop()

