#!/usr/bin/env python3
"""QR Code Generator CLI - Compact version with full functionality."""
import json, re, sys, click, qrcode, validators
from datetime import datetime
from pathlib import Path
from urllib.parse import quote, urlencode

HISTORY_FILE = Path.home() / ".qr-generator" / "history.json"

class ValidationError(Exception): pass

def validate_output(path):
    p = Path(path).expanduser().resolve()
    if p.suffix.lower() not in (".png", ".svg"):
        raise ValidationError("Output must be .png or .svg")
    if not p.parent.exists():
        raise ValidationError(f"Directory does not exist: {p.parent}")
    return p

def validate_url(url):
    if not url.startswith(("http://", "https://")): url = f"https://{url}"
    if not validators.url(url): raise ValidationError(f"Invalid URL: {url}")
    return url

def validate_email(email):
    if not validators.email(email): raise ValidationError(f"Invalid email: {email}")
    return email

def validate_phone(phone):
    normalized = re.sub(r"[\s\-\.\(\)]", "", phone)
    if not re.match(r"^\+?\d{7,15}$", normalized): raise ValidationError(f"Invalid phone: {phone}")
    return normalized

def generate(data, output, fmt=None):
    p = validate_output(output)
    fmt = fmt or p.suffix.lower().lstrip(".")
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    if fmt == "svg":
        from qrcode.image.svg import SvgPathImage
        qr.make_image(image_factory=SvgPathImage).save(str(p.with_suffix(".svg")))
    else:
        qr.make_image(fill_color="black", back_color="white").save(str(p.with_suffix(".png")))
    return p

def save_history(qr_type, cmd, output):
    HISTORY_FILE.parent.mkdir(exist_ok=True)
    data = json.loads(HISTORY_FILE.read_text()) if HISTORY_FILE.exists() else {"entries": []}
    data["entries"].append({"type": qr_type, "command": cmd, "output": str(output), "time": datetime.now().isoformat()})
    HISTORY_FILE.write_text(json.dumps(data, indent=2))

def error(msg):
    click.secho(f"Error: {msg}", fg="red", err=True)
    sys.exit(1)

@click.group()
@click.version_option("1.0.0")
def cli(): """QR Code Generator - All commands require --output (-o)."""

@cli.command()
@click.argument("url")
@click.option("-o", "--output", required=True)
@click.option("-f", "--format", "fmt", type=click.Choice(["png", "svg"]))
def url(url, output, fmt):
    """Generate QR for a URL."""
    try:
        url = validate_url(url)
        p = generate(url, output, fmt)
        save_history("url", f'qr url "{url}" -o {output}', p)
        click.secho(f"✓ {p}", fg="green")
    except (ValidationError, Exception) as e: error(e)

@cli.command()
@click.argument("text")
@click.option("-o", "--output", required=True)
@click.option("-f", "--format", "fmt", type=click.Choice(["png", "svg"]))
def text(text, output, fmt):
    """Generate QR for plain text."""
    try:
        if not text: raise ValidationError("Text cannot be empty")
        p = generate(text, output, fmt)
        save_history("text", f'qr text "{text[:50]}" -o {output}', p)
        click.secho(f"✓ {p}", fg="green")
    except (ValidationError, Exception) as e: error(e)

@cli.command()
@click.option("-s", "--ssid", required=True)
@click.option("-p", "--password", required=True)
@click.option("-t", "--security", default="WPA")
@click.option("-o", "--output", required=True)
@click.option("-f", "--format", "fmt", type=click.Choice(["png", "svg"]))
def wifi(ssid, password, security, output, fmt):
    """Generate QR for WiFi credentials."""
    try:
        sec = security.upper()
        if sec not in ("WPA", "WPA2", "WPA3", "WEP", "NOPASS"): raise ValidationError(f"Invalid security: {security}")
        if sec != "NOPASS" and not password: raise ValidationError("Password required for secured networks")
        esc = lambda s: s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace(":", "\\:")
        data = f"WIFI:T:{sec};S:{esc(ssid)};P:{esc(password)};;"
        p = generate(data, output, fmt)
        save_history("wifi", f'qr wifi -s "{ssid}" -p **** -t {sec} -o {output}', p)
        click.secho(f"✓ {p}", fg="green")
    except (ValidationError, Exception) as e: error(e)

@cli.command()
@click.option("-n", "--name", required=True)
@click.option("-p", "--phone")
@click.option("-e", "--email")
@click.option("--org")
@click.option("-o", "--output", required=True)
@click.option("-f", "--format", "fmt", type=click.Choice(["png", "svg"]))
def vcard(name, phone, email, org, output, fmt):
    """Generate QR for a contact card."""
    try:
        lines = ["BEGIN:VCARD", "VERSION:3.0", f"FN:{name}"]
        if phone: lines.append(f"TEL:{validate_phone(phone)}")
        if email: lines.append(f"EMAIL:{validate_email(email)}")
        if org: lines.append(f"ORG:{org}")
        lines.append("END:VCARD")
        p = generate("\n".join(lines), output, fmt)
        save_history("vcard", f'qr vcard -n "{name}" -o {output}', p)
        click.secho(f"✓ {p}", fg="green")
    except (ValidationError, Exception) as e: error(e)

@cli.command()
@click.argument("address")
@click.option("-s", "--subject")
@click.option("-b", "--body")
@click.option("-o", "--output", required=True)
@click.option("-f", "--format", "fmt", type=click.Choice(["png", "svg"]))
def email(address, subject, body, output, fmt):
    """Generate QR for an email address."""
    try:
        address = validate_email(address)
        params = {k: v for k, v in [("subject", subject), ("body", body)] if v}
        data = f"mailto:{address}?{urlencode(params, quote_via=quote)}" if params else f"mailto:{address}"
        p = generate(data, output, fmt)
        save_history("email", f'qr email "{address}" -o {output}', p)
        click.secho(f"✓ {p}", fg="green")
    except (ValidationError, Exception) as e: error(e)

@cli.command()
@click.argument("phone")
@click.option("-m", "--message")
@click.option("-o", "--output", required=True)
@click.option("-f", "--format", "fmt", type=click.Choice(["png", "svg"]))
def sms(phone, message, output, fmt):
    """Generate QR for SMS."""
    try:
        phone = validate_phone(phone)
        data = f"sms:{phone}?body={quote(message)}" if message else f"sms:{phone}"
        p = generate(data, output, fmt)
        save_history("sms", f'qr sms "{phone}" -o {output}', p)
        click.secho(f"✓ {p}", fg="green")
    except (ValidationError, Exception) as e: error(e)

@cli.command("history")
@click.option("-l", "--limit", type=int)
@click.option("--clear", is_flag=True)
def history_cmd(limit, clear):
    """View or clear generation history."""
    if clear:
        if HISTORY_FILE.exists(): HISTORY_FILE.unlink()
        click.secho("✓ History cleared", fg="green")
        return
    if not HISTORY_FILE.exists():
        click.echo("No history found.")
        return
    entries = json.loads(HISTORY_FILE.read_text()).get("entries", [])[-limit if limit else len(entries):]
    for i, e in enumerate(reversed(entries), 1):
        click.echo(f"[{i}] {e.get('time', '')[:19]} - {e.get('type')}\n    {e.get('command')}\n")

if __name__ == "__main__": cli()
