"""Data formatters for QR code content types.

These formatters convert structured data into standard QR code formats
that can be recognized by QR code scanners.
"""

from typing import Optional
from urllib.parse import quote, urlencode


def format_wifi(ssid: str, password: str, security: str, hidden: bool = False) -> str:
    """Format WiFi credentials for QR code.
    
    Uses the standard WIFI: format recognized by most QR scanners.
    
    Args:
        ssid: The network SSID.
        password: The network password.
        security: The security type (WPA, WPA2, WPA3, WEP, NOPASS).
        hidden: Whether the network is hidden.
        
    Returns:
        Formatted WiFi string.
    """
    # Escape special characters in SSID and password
    def escape(s: str) -> str:
        return s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace('"', '\\"').replace(":", "\\:")
    
    parts = [
        f"T:{security}",
        f"S:{escape(ssid)}",
    ]
    
    if password and security != "NOPASS":
        parts.append(f"P:{escape(password)}")
    
    if hidden:
        parts.append("H:true")
    
    return f"WIFI:{';'.join(parts)};;"


def format_vcard(
    name: str,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    organization: Optional[str] = None,
    title: Optional[str] = None,
    url: Optional[str] = None,
    address: Optional[str] = None,
    note: Optional[str] = None,
) -> str:
    """Format contact information as vCard 3.0.
    
    Args:
        name: Full name of the contact.
        phone: Phone number.
        email: Email address.
        organization: Company/organization name.
        title: Job title.
        url: Website URL.
        address: Physical address.
        note: Additional notes.
        
    Returns:
        vCard 3.0 formatted string.
    """
    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
    ]
    
    # Parse name into structured format if possible
    name_parts = name.strip().split()
    if len(name_parts) >= 2:
        # Assume last word is surname
        surname = name_parts[-1]
        given = " ".join(name_parts[:-1])
        lines.append(f"N:{surname};{given};;;")
    else:
        lines.append(f"N:{name};;;;")
    
    lines.append(f"FN:{name}")
    
    if organization:
        lines.append(f"ORG:{organization}")
    
    if title:
        lines.append(f"TITLE:{title}")
    
    if phone:
        lines.append(f"TEL;TYPE=CELL:{phone}")
    
    if email:
        lines.append(f"EMAIL:{email}")
    
    if url:
        lines.append(f"URL:{url}")
    
    if address:
        # Simple address format
        lines.append(f"ADR:;;{address};;;;")
    
    if note:
        lines.append(f"NOTE:{note}")
    
    lines.append("END:VCARD")
    
    return "\n".join(lines)


def format_email(
    address: str,
    subject: Optional[str] = None,
    body: Optional[str] = None,
    cc: Optional[str] = None,
    bcc: Optional[str] = None,
) -> str:
    """Format email as mailto: URI.
    
    Args:
        address: The recipient email address.
        subject: Optional email subject.
        body: Optional email body.
        cc: Optional CC recipients.
        bcc: Optional BCC recipients.
        
    Returns:
        mailto: URI string.
    """
    params = {}
    
    if subject:
        params["subject"] = subject
    
    if body:
        params["body"] = body
    
    if cc:
        params["cc"] = cc
    
    if bcc:
        params["bcc"] = bcc
    
    if params:
        query = urlencode(params, quote_via=quote)
        return f"mailto:{address}?{query}"
    
    return f"mailto:{address}"


def format_sms(phone: str, message: Optional[str] = None) -> str:
    """Format SMS as sms: URI.
    
    Args:
        phone: The recipient phone number.
        message: Optional pre-filled message.
        
    Returns:
        sms: URI string.
    """
    if message:
        encoded_message = quote(message)
        return f"sms:{phone}?body={encoded_message}"
    
    return f"sms:{phone}"


def format_phone(phone: str) -> str:
    """Format phone number as tel: URI.
    
    Args:
        phone: The phone number.
        
    Returns:
        tel: URI string.
    """
    return f"tel:{phone}"


def format_geo(latitude: float, longitude: float, query: Optional[str] = None) -> str:
    """Format geographic coordinates as geo: URI.
    
    Args:
        latitude: Latitude coordinate.
        longitude: Longitude coordinate.
        query: Optional location query/name.
        
    Returns:
        geo: URI string.
    """
    if query:
        encoded_query = quote(query)
        return f"geo:{latitude},{longitude}?q={encoded_query}"
    
    return f"geo:{latitude},{longitude}"

