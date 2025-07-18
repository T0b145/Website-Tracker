import difflib
import json
import os
import logging
from datetime import datetime

from bs4 import BeautifulSoup
import requests

from signal_notify import send_text

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tracker.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_config():
    """Load configuration from config.json file"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("config.json not found. Please create it with your configuration.")
        exit(1)
    except json.JSONDecodeError:
        logger.error("Invalid JSON in config.json")
        exit(1)

def load_tracked_sites(tracked_sites_file):
    try:
        with open(tracked_sites_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Tracked sites file '{tracked_sites_file}' not found.")
        exit(1)
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in '{tracked_sites_file}'")
        exit(1)

def load_site_data(site_data_file):
    if not os.path.exists(site_data_file):
        return {}
    try:
        with open(site_data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        logger.warning(f"Invalid JSON in '{site_data_file}', starting with empty data.")
        return {}

def save_site_data(site_data_file, data):
    try:
        with open(site_data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Site data saved to {site_data_file}")
    except Exception as e:
        logger.error(f"Failed to save site data: {e}")

def load_change_history(history_file):
    """Load change history from file"""
    if not os.path.exists(history_file):
        return []
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        logger.warning(f"Invalid JSON in '{history_file}', starting with empty history.")
        return []

def save_change_history(history_file, history):
    """Save change history to file"""
    try:
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        logger.info(f"Change history saved to {history_file}")
    except Exception as e:
        logger.error(f"Failed to save change history: {e}")

def add_change_to_history(history, url, selector, old_content, new_content, diff_lines):
    """Add a change to the history"""
    change_entry = {
        "timestamp": datetime.now().isoformat(),
        "url": url,
        "selector": selector,
        "old_content_length": len(old_content),
        "new_content_length": len(new_content),
        "diff_lines": diff_lines,
        "diff_summary": {
            "added_lines": len([line for line in diff_lines if line.startswith('+') and not line.startswith('+++')]),
            "removed_lines": len([line for line in diff_lines if line.startswith('-') and not line.startswith('---')]),
            "total_diff_lines": len(diff_lines)
        }
    }
    history.append(change_entry)
    
    # Keep only last 1000 changes to prevent file from growing too large
    if len(history) > 1000:
        history = history[-1000:]
        logger.info("Trimmed history to last 1000 changes")
    
    return history

def fetch_content(url, selector=None):
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        if selector:
            el = soup.select_one(selector)
            if not el:
                logger.warning(f"Selector '{selector}' not found on {url}")
                return ''
            return el.get_text(separator='\n', strip=True)
        else:
            return soup.get_text(separator='\n', strip=True)
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch {url}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching {url}: {e}")
        raise

def show_diff(old, new):
    old_lines = old.splitlines()
    new_lines = new.splitlines()
    diff = list(difflib.unified_diff(old_lines, new_lines, lineterm='', fromfile='previous', tofile='current'))
    print('\n'.join(diff))
    return diff

def main():
    logger.info("Starting website tracker...")
    
    # Load configuration
    config = load_config()
    tracked_sites_file = config.get('tracked_sites_file', 'tracked_sites.json')
    site_data_file = config.get('site_data_file', 'site_data.json')
    history_file = config.get('history_file', 'change_history.json')
    signal_recipient = config.get('signal_recipient')
    
    if not signal_recipient:
        logger.error("signal_recipient not found in config.json")
        exit(1)
    
    tracked_sites = load_tracked_sites(tracked_sites_file)
    site_data = load_site_data(site_data_file)
    change_history = load_change_history(history_file)
    changed = False
    
    logger.info(f"Checking {len(tracked_sites)} tracked sites...")
    
    for entry in tracked_sites:
        url = entry['url']
        selector = entry.get('selector')
        logger.info(f'Checking {url} (selector: {selector})...')
        
        try:
            content = fetch_content(url, selector)
        except Exception as e:
            logger.error(f'  Error fetching: {e}')
            continue
            
        key = f"{url}::{selector if selector else 'FULL'}"
        prev_content = site_data.get(key, '')
        
        if prev_content != content:
            logger.info('  Change detected! Showing diff:')
            diff_lines = show_diff(prev_content, content)
            site_data[key] = content
            changed = True
            
            # Add to change history
            change_history = add_change_to_history(change_history, url, selector, prev_content, content, diff_lines)
            
            # Prepare diff for Signal message
            max_lines = 30
            diff_text = '\n'.join(diff_lines[:max_lines])
            if len(diff_lines) > max_lines:
                diff_text += '\n...diff truncated...'
                
            # Send Signal notification
            msg = f"Website changed: {url}\nSelector: {selector}\nDiff:\n{diff_text}"
            try:
                #send_text(signal_recipient, msg)
                logger.info(f"Signal notification sent to {signal_recipient}")
            except Exception as e:
                logger.error(f"Failed to send Signal notification: {e}")
        else:
            logger.info('  No change.')
    
    if changed:
        save_site_data(site_data_file, site_data)
        save_change_history(history_file, change_history)
        logger.info('Site data and change history updated.')
    else:
        logger.info('No changes detected. Site data not updated.')
    
    logger.info("Website tracker finished.")

if __name__ == '__main__':
    main() 
