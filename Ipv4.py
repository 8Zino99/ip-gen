import curses
import random
import requests
import re
import io
from collections import Counter

def generate_random_ip():
    return f"192.168.{random.randint(0, 255)}.{random.randint(0, 255)}"

def is_valid_ip(ip):
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

def generate_ips_without_webhook(count, stdscr):
    ips = generate_ip_addresses(count)
    most_common = most_common_ip(ips)
    stdscr.addstr(0, 0, f"Most Common IP: {most_common}")
    for i, ip in enumerate(ips, 1):
        stdscr.addstr(i, 0, f"{i}: gen {ip} {'valid' if is_valid_ip(ip) else 'invalid'}")
    stdscr.addstr(count + 1, 0, "Generation finished ✔️")
    stdscr.refresh()
    stdscr.getch()

def main(stdscr):
    curses.curs_set(0)
    stdscr.clear()
    stdscr.addstr(0, 0, "1. Send IPs to Webhook")
    stdscr.addstr(1, 0, "2. Generate IPs Here")
    stdscr.addstr(2, 0, "Select an option (1 or 2):")
    stdscr.refresh()
    
    choice = stdscr.getch()
    
    if choice == ord('1'):
        stdscr.clear()
        stdscr.addstr(0, 0, "Enter the Discord Webhook URL:")
        curses.echo()
        webhook_url = stdscr.getstr().decode('utf-8')
        
        stdscr.addstr(1, 0, "Enter the number of IPs to generate (1-1000000):")
        count = int(stdscr.getstr().decode('utf-8'))
        
        ips = generate_ip_addresses(count)
        file_name = save_to_file(ips)
        send_to_webhook(file_name, webhook_url)
        
        stdscr.addstr(2, 0, "IPs have been sent to the webhook.")
        stdscr.refresh()
        stdscr.getch()
    
    elif choice == ord('2'):
        stdscr.clear()
        stdscr.addstr(0, 0, "Enter the number of IPs to generate (1-1000000):")
        curses.echo()
        count = int(stdscr.getstr().decode('utf-8'))
        
        generate_ips_without_webhook(count, stdscr)

curses.wrapper(main)
