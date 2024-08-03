import curses
import random
import requests
import re
from collections import Counter

# Generate a random IP address within the 192.168.x.x range
def generate_random_ip():
    return f"192.168.{random.randint(0, 255)}.{random.randint(0, 255)}"

# Check if the IP address is valid within the 192.168.x.x range
def is_valid_ip(ip):
    return bool(re.match(r'^192\.168\.\d{1,3}\.\d{1,3}$', ip))

# Generate a list of random IP addresses
def generate_ip_addresses(count):
    return [generate_random_ip() for _ in range(count)]

# Find the most common IP address in the list
def most_common_ip(ip_list):
    if not ip_list:
        return None
    ip_counter = Counter(ip_list)
    return ip_counter.most_common(1)[0][0]

# Save IP addresses to a text file with validity status
def save_to_file(ip_list):
    file_name = "ip.txt"
    with open(file_name, "w") as file:
        for ip in ip_list:
            file.write(f"{ip} {'valid' if is_valid_ip(ip) else 'invalid'}\n")
    return file_name

# Send the file to the specified webhook URL
def send_to_webhook(file_name, webhook_url):
    with open(file_name, "rb") as file:
        response = requests.post(
            webhook_url,
            files={"file": ("ip.txt", file)},
            data={"content": "Here are your generated IP addresses:"}
        )
    return response

# Display a message to the user
def display_message(stdscr, message):
    stdscr.clear()
    stdscr.addstr(0, 0, message)
    stdscr.refresh()
    stdscr.getch()

# Handle the process of sending IPs to a webhook
def handle_webhook(stdscr):
    curses.curs_set(1)
    stdscr.clear()
    stdscr.addstr(0, 0, "Enter the Discord Webhook URL:")
    curses.echo()
    webhook_url = stdscr.getstr().decode('utf-8').strip()
    
    stdscr.addstr(1, 0, "Enter the number of IPs to generate (1-1000000):")
    count = int(stdscr.getstr().decode('utf-8').strip())
    
    ips = generate_ip_addresses(count)
    file_name = save_to_file(ips)
    response = send_to_webhook(file_name, webhook_url)
    
    if response.status_code == 204:
        display_message(stdscr, "IPs have been sent to the webhook successfully.")
    else:
        display_message(stdscr, "Failed to send IPs to the webhook.")
    
    curses.curs_set(0)

# Handle the process of generating and displaying IPs locally
def handle_local_generation(stdscr):
    curses.curs_set(1)
    stdscr.clear()
    stdscr.addstr(0, 0, "Enter the number of IPs to generate (1-1000000):")
    curses.echo()
    count = int(stdscr.getstr().decode('utf-8').strip())
    
    ips = generate_ip_addresses(count)
    most_common = most_common_ip(ips)
    
    stdscr.clear()
    stdscr.addstr(0, 0, f"Most Common IP: {most_common}")
    
    y = 1
    for i, ip in enumerate(ips):
        stdscr.addstr(y, 0, f"{i + 1}: {ip} {'valid' if is_valid_ip(ip) else 'invalid'}")
        y += 1
        if y >= curses.LINES - 2:
            stdscr.addstr(y, 0, "Scroll down to see more...")
            break
    
    stdscr.addstr(y + 1, 0, "Generation finished ✔️")
    stdscr.refresh()
    stdscr.getch()
    curses.curs_set(0)

# Main function to handle the menu and user input
def main(stdscr):
    curses.curs_set(0)
    stdscr.clear()
    stdscr.addstr(0, 0, "1. Send IPs to Webhook")
    stdscr.addstr(1, 0, "2. Generate IPs Here")
    stdscr.addstr(2, 0, "Select an option (1 or 2):")
    stdscr.refresh()
    
    choice = stdscr.getch()
    
    if choice == ord('1'):
        handle_webhook(stdscr)
    elif choice == ord('2'):
        handle_local_generation(stdscr)
    else:
        display_message(stdscr, "Invalid choice. Please restart the application.")

# Entry point of the script
if __name__ == "__main__":
    curses.wrapper(main)
