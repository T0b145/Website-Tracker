# Website Tracker

A Python script that monitors websites for changes and sends notifications via Signal.

## Features

- 🔍 **Website Monitoring**: Track changes on any website or specific content areas
- 📱 **Signal Notifications**: Get instant notifications when changes are detected
- 🎯 **CSS Selectors**: Monitor specific parts of websites using CSS selectors
- 📝 **Comprehensive Logging**: Detailed logs for debugging and monitoring
- 🔒 **Secure Configuration**: Sensitive data kept separate from code
- ⚡ **Fast & Efficient**: Optimized for performance with timeout handling
- 📊 **Change History**: Track all changes with timestamps and diff summaries

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Signal CLI:**
   - Install and set up Signal CLI
   - Register your device

3. **Create configuration:**
   ```bash
   cp config.example.json config.json
   ```
   Then edit `config.json` with your settings:
   - `signal_recipient`: Your phone number for receiving notifications
   - `tracked_sites_file`: Path to your tracked sites configuration
   - `site_data_file`: Path to store site data
   - `history_file`: Path to store change history
   - `signal_api`: Signal API configuration
     - `base_url`: Your Signal API server URL
     - `sender`: Your registered Signal phone number
     - `auth`: Basic authentication credentials
       - `username`: Your API username
       - `password`: Your API password

4. **Configure tracked sites:**
   ```bash
   cp tracked_sites.example.json tracked_sites.json
   ```
   Then edit `tracked_sites.json` to add the websites you want to monitor:
   ```json
   [
     {
       "url": "https://example.com",
       "selector": ".content-area"
     },
     {
       "url": "https://another-example.com"
     }
   ]
   ```
   - `url`: The website URL to monitor
   - `selector`: (Optional) CSS selector to monitor specific content

## Quick Setup (Recommended)

1. **Run the install script:**
   ```bash
   bash install.sh
   ```
   This will:
   - Create a virtual environment (`venv`)
   - Activate it
   - Install all requirements
   - Install Playwright browser binaries

2. **Activate the virtual environment in every new terminal session:**
   ```bash
   source venv/bin/activate
   ```
   > **Note:** You must activate the venv each time you open a new terminal before running the tracker.

3. **Run the tracker:**
   ```bash
   python tracker.py
   ```

## Configuration

The `config.json`, `tracked_sites.json`, `site_data.json`, and `change_history.json` files contain sensitive information and are excluded from version control. Copy the example files and modify them with your settings.

### Signal API Configuration

The Signal API configuration includes:
- **base_url**: The URL of your Signal API server
- **sender**: Your registered Signal phone number (used to send messages)
- **auth**: Basic authentication credentials for the API

### Tracked Sites Configuration

Each tracked site can have:
- **url**: The website URL to monitor (required)
- **selector**: CSS selector to monitor specific content (optional)
  - If no selector is provided, the entire page content is monitored
  - Examples: `.content`, `main`, `#specific-id`

## Change History

The tracker automatically maintains a history of all changes detected:

### History File Structure
```json
[
  {
    "timestamp": "2024-01-15T10:30:45.123456",
    "url": "https://example.com",
    "selector": ".content",
    "old_content_length": 1500,
    "new_content_length": 1550,
    "diff_lines": ["- old line", "+ new line"],
    "diff_summary": {
      "added_lines": 5,
      "removed_lines": 3,
      "total_diff_lines": 8
    }
  }
]
```

### History Features
- **Timestamps**: ISO format timestamps for each change
- **Content Lengths**: Track how content size changes over time
- **Diff Summaries**: Quick statistics about what changed
- **Automatic Trimming**: Keeps only the last 1000 changes to prevent large files
- **Diff Storage**: Stores the first 50 diff lines for each change

## Logging

The tracker creates detailed logs in `tracker.log` with timestamps and different log levels:
- **INFO**: Normal operation messages
- **WARNING**: Non-critical issues (e.g., selector not found)
- **ERROR**: Critical errors that prevent operation

## Files

- `tracker.py`: Main tracking script
- `signal_notify.py`: Signal notification module
- `config.json`: Configuration (not in version control)
- `config.example.json`: Example configuration
- `tracked_sites.json`: List of websites to monitor (not in version control)
- `tracked_sites.example.json`: Example tracked sites configuration
- `site_data.json`: Stored site data (auto-generated, not in version control)
- `change_history.json`: Change history (auto-generated, not in version control)
- `tracker.log`: Log file (auto-generated)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 