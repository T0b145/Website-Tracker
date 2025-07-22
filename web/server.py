import json
import os
import uuid
from flask import Flask, jsonify, request, render_template, abort

app = Flask(__name__, template_folder='templates', static_folder='static')

# Determine the absolute path to the project's root directory
# This allows the script to be run from anywhere, not just the project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRACKED_SITES_FILE = os.path.join(project_root, 'tracked_sites.json')
HISTORY_FILE = os.path.join(project_root, 'change_history.json')

def read_json_file(file_path):
    """Read a JSON file and return its content."""
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error reading {file_path}: {e}")
        return []

def write_json_file(file_path, data):
    """Write data to a JSON file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"Error writing to {file_path}: {e}")

@app.route('/')
def index():
    """Serve the main HTML page."""
    return render_template('index.html')

@app.route('/api/sites', methods=['GET'])
def get_sites():
    """Get all tracked sites."""
    sites = read_json_file(TRACKED_SITES_FILE)
    return jsonify(sites)

@app.route('/api/sites', methods=['POST'])
def add_site():
    """Add a new tracked site."""
    if not request.json:
        abort(400, description="Invalid JSON")

    new_site = {
        'id': str(uuid.uuid4()),
        'name': request.json.get('name', ''),
        'url': request.json.get('url', ''),
        'selector': request.json.get('selector', ''),
        'receivers': request.json.get('receivers', []),
        'use_playwright': request.json.get('use_playwright', False)
    }

    if not new_site['name'] or not new_site['url']:
        abort(400, description="Name and URL are required.")

    sites = read_json_file(TRACKED_SITES_FILE)
    sites.append(new_site)
    write_json_file(TRACKED_SITES_FILE, sites)
    return jsonify(new_site), 201

@app.route('/api/sites/<site_id>', methods=['PUT'])
def update_site(site_id):
    """Update an existing site."""
    if not request.json:
        abort(400, description="Invalid JSON")

    sites = read_json_file(TRACKED_SITES_FILE)
    site_to_update = next((s for s in sites if s.get('id') == site_id), None)

    if not site_to_update:
        abort(404, description="Site not found")

    # Update fields from the request
    site_to_update['name'] = request.json.get('name', site_to_update['name'])
    site_to_update['url'] = request.json.get('url', site_to_update['url'])
    site_to_update['selector'] = request.json.get('selector', site_to_update['selector'])
    site_to_update['receivers'] = request.json.get('receivers', site_to_update['receivers'])
    site_to_update['use_playwright'] = request.json.get('use_playwright', site_to_update['use_playwright'])

    write_json_file(TRACKED_SITES_FILE, sites)
    return jsonify(site_to_update)

@app.route('/api/sites/<site_id>', methods=['DELETE'])
def delete_site(site_id):
    """Delete a tracked site."""
    sites = read_json_file(TRACKED_SITES_FILE)
    sites_after_delete = [s for s in sites if s.get('id') != site_id]

    if len(sites) == len(sites_after_delete):
        abort(404, description="Site not found")

    write_json_file(TRACKED_SITES_FILE, sites_after_delete)
    return '', 204

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get the change history, optionally filtered by URL."""
    history = read_json_file(HISTORY_FILE)
    url_to_filter = request.args.get('url')

    if url_to_filter:
        history = [entry for entry in history if entry.get('url') == url_to_filter]

    # Sort history by timestamp in descending order
    sorted_history = sorted(history, key=lambda x: x.get('timestamp', ''), reverse=True)
    return jsonify(sorted_history)

if __name__ == '__main__':
    app.run(debug=True, port=5000) 