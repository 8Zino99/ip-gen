import urwid
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

def generate_ips_without_webhook(count):
    ips = generate_ip_addresses(count)
    most_common = most_common_ip(ips)
    results = [f"{i+1}: gen {ip} {'valid' if is_valid_ip(ip) else 'invalid'}" for i, ip in enumerate(ips)]
    results.append(f"Most Common IP: {most_common}")
    return "\n".join(results)

def main_menu(button):
    choice = button.get_label()
    if choice == 'Send IPs to Webhook':
        urwid.connect_signal(header, 'click', lambda button: send_ip_to_webhook())
    elif choice == 'Generate IPs Here':
        urwid.connect_signal(header, 'click', lambda button: generate_ips_here())

def send_ip_to_webhook():
    def on_ask_webhook_url(button):
        urwid.disconnect_signal(edit, 'change', on_ask_webhook_url)
        webhook_url = edit.get_edit_text()
        urwid.connect_signal(header, 'click', lambda button: ask_ip_count(webhook_url))

    def ask_ip_count(webhook_url):
        urwid.connect_signal(edit, 'change', lambda button: generate_and_send_to_webhook(edit.get_edit_text(), webhook_url))

        pile.contents[1] = (urwid.Text("Enter the number of IPs to generate (1-1000000):"), pile.options())
        urwid.connect_signal(edit, 'change', on_ask_webhook_url)
    
    footer = urwid.Text('Enter the Discord Webhook URL:')
    edit = urwid.Edit()
    urwid.connect_signal(edit, 'change', lambda edit: urwid.emit_signal(edit, 'change'))
    pile = urwid.Pile([header, footer, edit])
    urwid.MainLoop(urwid.LineBox(pile)).run()

def generate_and_send_to_webhook(count, webhook_url):
    try:
        count = int(count)
        if count < 1 or count > 1000000:
            raise ValueError("Invalid count")
        
        ips = generate_ip_addresses(count)
        file_name = save_to_file(ips)
        send_to_webhook(file_name, webhook_url)
        body = urwid.Text("IPs have been sent to the webhook.")
        urwid.MainLoop(urwid.LineBox(body)).run()
    except ValueError as e:
        body = urwid.Text(f"Error: {e}")
        urwid.MainLoop(urwid.LineBox(body)).run()

def generate_ips_here():
    def on_ask_ip_count(button):
        urwid.disconnect_signal(edit, 'change', on_ask_ip_count)
        count = edit.get_edit_text()
        urwid.connect_signal(header, 'click', lambda button: generate_and_display_ips(count))

    def generate_and_display_ips(count):
        try:
            count = int(count)
            if count < 1 or count > 1000000:
                raise ValueError("Invalid count")
            
            results = generate_ips_without_webhook(count)
            body = urwid.Text(results)
            urwid.MainLoop(urwid.LineBox(body)).run()
        except ValueError as e:
            body = urwid.Text(f"Error: {e}")
            urwid.MainLoop(urwid.LineBox(body)).run()

    footer = urwid.Text('Enter the number of IPs to generate (1-1000000):')
    edit = urwid.Edit()
    urwid.connect_signal(edit, 'change', lambda edit: urwid.emit_signal(edit, 'change'))
    pile = urwid.Pile([header, footer, edit])
    urwid.MainLoop(urwid.LineBox(pile)).run()

header = urwid.Text('Select an option:')
button_send = urwid.Button('Send IPs to Webhook')
button_gen = urwid.Button('Generate IPs Here')
urwid.connect_signal(button_send, 'click', main_menu)
urwid.connect_signal(button_gen, 'click', main_menu)

pile = urwid.Pile([header, urwid.AttrMap(button_send, None, focus_map='reversed'), urwid.AttrMap(button_gen, None, focus_map='reversed')])
top = urwid.LineBox(pile)

urwid.MainLoop(top).run()
