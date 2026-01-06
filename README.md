# QR Code Generator CLI

A command-line tool for generating QR codes with strict validation and global history tracking.

## Features

- Generate QR codes for URLs, text, WiFi credentials, vCards, email, and SMS
- Strict input validation with clear error messages
- PNG and SVG output formats
- Global history tracking with command recall
- Clean installation via pipx

## Installation

### Prerequisites

- Python 3.10 or higher
- pipx (recommended) or pip

### Install with pipx (Recommended)

```bash
# Install pipx if you haven't already
brew install pipx  # macOS
# or
pip install pipx

# Ensure pipx binaries are in PATH
pipx ensurepath

# Install qr-generator
cd /path/to/qr-generator
pipx install .
```

### Install with pip

```bash
pip install .
```

## Usage

All commands require `--output` to specify the output file. The format (PNG/SVG) is inferred from the file extension.

### URL

```bash
qr url "https://example.com" --output ~/codes/example.png
qr url "https://github.com" --output github.svg
```

### Plain Text

```bash
qr text "Hello World" --output message.png
qr text "Secret Message" --output secret.svg
```

### WiFi Credentials

```bash
qr wifi --ssid "MyNetwork" --password "secret123" --output wifi.png
qr wifi --ssid "GuestWifi" --password "guest" --security WPA2 --output guest.png
qr wifi --ssid "OpenNetwork" --password "" --security nopass --output open.png
```

### Contact Card (vCard)

```bash
qr vcard --name "John Doe" --phone "555-123-4567" --email "john@example.com" --output contact.png
qr vcard --name "Jane Smith" --phone "+1-555-987-6543" --org "Acme Inc" --title "CEO" --output jane.png
```

### Email

```bash
qr email "contact@example.com" --output email.png
qr email "support@example.com" --subject "Help Request" --body "I need assistance with..." --output support.png
```

### SMS

```bash
qr sms "555-123-4567" --output sms.png
qr sms "+1-555-987-6543" --message "Hi there!" --output greeting.png
```

### Format Override

By default, the format is inferred from the file extension. Use `--format` to override:

```bash
# Save as SVG even though the filename says .png
qr url "https://example.com" --output code.png --format svg
```

## History

View your QR code generation history:

```bash
# Show all history
qr history

# Show last 5 entries
qr history --limit 5

# Clear all history
qr history clear
```

History shows the exact command used, making it easy to regenerate or modify previous QR codes:

```
[1] 2026-01-04 12:30:00 - url
    qr url "https://example.com" --output ~/codes/example.png

[2] 2026-01-04 12:35:00 - wifi
    qr wifi --ssid "MyNetwork" --password **** --security WPA --output wifi.png
```

## Validation Rules

The tool performs strict validation on all inputs:

| Type | Requirements |
|------|--------------|
| URL | Must be valid http:// or https:// URL |
| Email | Must be valid email format |
| Phone | 7-15 digits, optional + prefix |
| WiFi | SSID required; password required unless security is "nopass" |
| vCard | Name required |
| Output | Must be .png or .svg; directory must exist and be writable |

## Error Handling

Invalid inputs produce clear error messages and exit with code 1:

```bash
$ qr url "not-a-url" --output test.png
Error: Invalid URL format: 'https://not-a-url'. URL must be a valid http:// or https:// address.

$ qr wifi --ssid "Test" --password "" --security WPA --output test.png
Error: Password is required for WPA security. Use --security nopass for open networks.
```

## Global History Location

History is stored at `~/.qr-generator/history.json`.

## License

MIT

