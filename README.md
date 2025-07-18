# Website Tracker

A Python script that monitors websites for changes and sends notifications via Signal.

## Features

- 🔍 **Website Monitoring**: Track changes on any website or specific content areas
- 📱 **Signal Notifications**: Get instant notifications when changes are detected
- 🎯 **CSS Selectors**: Monitor specific parts of websites using CSS selectors
- 📝 **Comprehensive Logging**: Detailed logs for debugging and monitoring
- 🔒 **Secure Configuration**: Sensitive data kept separate from code
- ⚡ **Fast & Efficient**: Optimized for performance with timeout handling

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

5. **Run the tracker:**
   ```bash
   python tracker.py
   ```

## Configuration

The `config.json` and `tracked_sites.json` files contain sensitive information and are excluded from version control. Copy the example files and modify them with your settings.

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
- `site_data.json`: Stored site data (auto-generated)
- `tracker.log`: Log file (auto-generated)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 