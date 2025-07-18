import requests
from requests.auth import HTTPBasicAuth
import json

def load_config():
    """Load configuration from config.json file"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: config.json not found. Please create it with your configuration.")
        exit(1)
    except json.JSONDecodeError:
        print("Error: Invalid JSON in config.json")
        exit(1)

def get_signal_config():
    """Get Signal API configuration from config file"""
    config = load_config()
    signal_config = config.get('signal_api', {})
    
    if not signal_config:
        print("Error: signal_api configuration not found in config.json")
        exit(1)
    
    base_url = signal_config.get('base_url')
    sender = signal_config.get('sender')
    auth_config = signal_config.get('auth', {})
    username = auth_config.get('username')
    password = auth_config.get('password')
    
    if not all([base_url, sender, username, password]):
        print("Error: Missing required signal_api configuration in config.json")
        exit(1)
    
    return base_url, sender, HTTPBasicAuth(username, password)

def parse_json_response(res):
    if res.status_code not in (200, 201):
        print(f"Error: Received status code {res.status_code}. Response: {res.text}")
        return None
    try:
        return res.json()
    except ValueError:
        print(f"Non-JSON response received (status {res.status_code}):", res.text)
        return None

def send_text(receiver: str, message: str):
    base_url, sender, auth = get_signal_config()
    url = f"{base_url}/v2/send"
    payload = {
        "message": message,
        "number": sender,
        "recipients": [receiver]
    }
    res = requests.post(url, json=payload, auth=auth)
    return parse_json_response(res)

def send_text_with_image(receiver: str, message: str, image_path: str):
    base_url, sender, auth = get_signal_config()
    url = f"{base_url}/v2/send"
    with open(image_path, 'rb') as img:
        files = {'attachments': img}
        data = {
            "message": message,
            "number": sender,
            "recipients": [receiver]
        }
        res = requests.post(url, data=data, files=files, auth=auth)
    return parse_json_response(res)

def send_group_message(group_id: str, message: str):
    base_url, sender, auth = get_signal_config()
    url = f"{base_url}/v2/send"
    payload = {
        "message": message,
        "number": sender,
        "groupId": group_id
    }
    res = requests.post(url, json=payload, auth=auth)
    return parse_json_response(res)

def receive_messages():
    base_url, sender, auth = get_signal_config()
    url = f"{base_url}/v1/receive/{sender}"
    res = requests.get(url, auth=auth)
    return parse_json_response(res)


if __name__ == "__main__":
    # Example usage
    config = load_config()
    signal_recipient = config.get('signal_recipient')
    
    if signal_recipient:
        send_text(signal_recipient, "Hi from Signal API behind Nginx Proxy Manager!💪")
    
    msgs = receive_messages()
    print("Incoming messages:", json.dumps(msgs, indent=4))

    