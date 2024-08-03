import tkinter as tk
from tkinter import simpledialog, messagebox
import random
import requests
from collections import Counter
import re
import time

# Helper functions for IP generation
def generate_random_ip():
    return f"192.168.{random.randint(0, 255)}.{random.randint(0, 255)}"

def is_valid_ip(ip):
    # Example validation: IP address should be in the range 192.168.x.y
    return bool(re.match(r'^192\.168\.\d{1,3}\.\d{1,3}$', ip))

def generate_ip_addresses(count):
    return [generate_random_ip() for _ in range(count)]

def most_common_ip(ip_list):
    if not ip_list:
        return None
    ip_counter = Counter(ip_list)
    return ip_counter.most_common(1)[0][0]

def save_to_file(ip_list):
    file_name = "ip.txt"
    with open(file_name, "w") as file:
        for ip in ip_list:
            file.write(f"{ip} {'valid' if is_valid_ip(ip) else 'invalid'}\n")
    return file_name

def send_to_webhook(file_name, webhook_url):
    with open(file_name, "rb") as file:
        requests.post(
            webhook_url,
            files={"file": ("ip.txt", file)},
            data={"content": "Here are your generated IP addresses:"}
        )

# GUI for IP generation
def generate_ip_gui(webhook_url=None):
    def on_generate():
        try:
            count = int(count_entry.get())
            if count < 1 or count > 1000000:
                raise ValueError("Invalid count")
            
            ips = []
            for i in range(0, count, 1000):
                ips.extend(generate_ip_addresses(min(1000, count - i)))
                root.update_idletasks()
                time.sleep(0.001)  # To simulate progress and avoid freezing

            most_common = most_common_ip(ips)
            
            if webhook_url:
                file_name = save_to_file(ips)
                send_to_webhook(file_name, webhook_url)
                messagebox.showinfo("Info", "IPs have been sent to the webhook.")
            else:
                results = [f"{i+1}: gen {ip} {'valid' if is_valid_ip(ip) else 'invalid'}" for i, ip in enumerate(ips)]
                result_window = tk.Toplevel(root)
                result_window.title("Generated IP Addresses")
                result_window.geometry("600x400")
                result_window.config(bg="#f0f0f0")
                
                text_area = tk.Text(result_window, wrap=tk.WORD, bg="#ffffff", fg="#000000", font=("Arial", 12))
                text_area.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
                text_area.insert(tk.END, f"Most Common IP: {most_common}\n\n")
                text_area.insert(tk.END, "\n".join(results))
                text_area.config(state=tk.DISABLED)
                messagebox.showinfo("Info", "IPs have been generated and displayed.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
    
    root = tk.Tk()
    root.title("IP Generator")
    root.geometry("400x300")
    root.config(bg="#e0e0e0")
    
    tk.Label(root, text="Number of IPs to generate (1-1000000):", bg="#e0e0e0", fg="#333333", font=("Arial", 12)).pack(pady=10)
    count_entry = tk.Entry(root, font=("Arial", 12))
    count_entry.pack(pady=10)
    
    tk.Button(root, text="Generate IPs", command=on_generate, bg="#4CAF50", fg="#ffffff", font=("Arial", 12)).pack(pady=20)
    
    root.mainloop()

# GUI for the initial choice
def show_initial_gui():
    def on_send_ip():
        webhook_url = simpledialog.askstring("Webhook URL", "Please enter the Discord Webhook URL:")
        if webhook_url:
            root.destroy()
            generate_ip_gui(webhook_url)

    def on_generate_ip():
        root.destroy()
        generate_ip_gui()

    root = tk.Tk()
    root.title("IP Generator")
    root.geometry("400x200")
    root.config(bg="#e0e0e0")
    
    tk.Label(root, text="Select an option:", bg="#e0e0e0", fg="#333333", font=("Arial", 14)).pack(pady=20)
    tk.Button(root, text="Send IPs to Webhook", command=on_send_ip, bg="#2196F3", fg="#ffffff", font=("Arial", 12)).pack(pady=10)
    tk.Button(root, text="Generate IPs Here", command=on_generate_ip, bg="#FFC107", fg="#000000", font=("Arial", 12)).pack(pady=10)

    root.mainloop()

# Start the program
show_initial_gui()
