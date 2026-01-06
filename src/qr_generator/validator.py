"""Strict input validation for QR code data types."""

import os
import re
from pathlib import Path
from typing import Optional

import validators


class ValidationError(Exception):
    """Raised when input validation fails."""

    pass


def validate_url(url: str) -> str:
    """Validate URL format.
    
    Args:
        url: The URL to validate.
        
    Returns:
        The validated URL.
        
    Raises:
        ValidationError: If the URL is invalid.
    """
    if not url:
        raise ValidationError("URL cannot be empty")
    
    # Check if it has a scheme, add https if not
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"
    
    if not validators.url(url):
        raise ValidationError(
            f"Invalid URL format: '{url}'. "
            "URL must be a valid http:// or https:// address."
        )
    
    return url


def validate_email(email: str) -> str:
    """Validate email address format.
    
    Args:
        email: The email address to validate.
        
    Returns:
        The validated email.
        
    Raises:
        ValidationError: If the email is invalid.
    """
    if not email:
        raise ValidationError("Email address cannot be empty")
    
    if not validators.email(email):
        raise ValidationError(
            f"Invalid email format: '{email}'. "
            "Please provide a valid email address (e.g., user@example.com)."
        )
    
    return email


def validate_phone(phone: str) -> str:
    """Validate phone number format.
    
    Args:
        phone: The phone number to validate.
        
    Returns:
        The validated and normalized phone number.
        
    Raises:
        ValidationError: If the phone number is invalid.
    """
    if not phone:
        raise ValidationError("Phone number cannot be empty")
    
    # Remove common formatting characters
    normalized = re.sub(r"[\s\-\.\(\)]", "", phone)
    
    # Allow optional + prefix and digits
    if not re.match(r"^\+?\d{7,15}$", normalized):
        raise ValidationError(
            f"Invalid phone number format: '{phone}'. "
            "Phone number should contain 7-15 digits, optionally starting with +."
        )
    
    return normalized


def validate_wifi_security(security: str) -> str:
    """Validate WiFi security type.
    
    Args:
        security: The security type to validate.
        
    Returns:
        The validated security type (uppercase).
        
    Raises:
        ValidationError: If the security type is invalid.
    """
    valid_types = {"WPA", "WPA2", "WPA3", "WEP", "NOPASS"}
    security_upper = security.upper()
    
    # Handle common aliases
    if security_upper in ("NONE", "OPEN"):
        security_upper = "NOPASS"
    
    if security_upper not in valid_types:
        raise ValidationError(
            f"Invalid WiFi security type: '{security}'. "
            f"Must be one of: {', '.join(sorted(valid_types))}."
        )
    
    return security_upper


def validate_wifi(
    ssid: str,
    password: Optional[str],
    security: str,
) -> tuple[str, str, str]:
    """Validate WiFi credentials.
    
    Args:
        ssid: The network SSID.
        password: The network password.
        security: The security type.
        
    Returns:
        Tuple of (ssid, password, security).
        
    Raises:
        ValidationError: If any field is invalid.
    """
    if not ssid:
        raise ValidationError("WiFi SSID cannot be empty")
    
    if len(ssid) > 32:
        raise ValidationError(
            f"WiFi SSID too long ({len(ssid)} chars). Maximum is 32 characters."
        )
    
    security = validate_wifi_security(security)
    
    if security != "NOPASS" and not password:
        raise ValidationError(
            f"Password is required for {security} security. "
            "Use --security nopass for open networks."
        )
    
    if security == "NOPASS":
        password = ""
    
    return ssid, password or "", security


def validate_vcard(
    name: str,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    organization: Optional[str] = None,
    title: Optional[str] = None,
    url: Optional[str] = None,
) -> dict:
    """Validate vCard fields.
    
    Args:
        name: The contact name (required).
        phone: Optional phone number.
        email: Optional email address.
        organization: Optional organization name.
        title: Optional job title.
        url: Optional website URL.
        
    Returns:
        Dictionary of validated vCard fields.
        
    Raises:
        ValidationError: If required fields are missing or invalid.
    """
    if not name:
        raise ValidationError(
            "Name is required for vCard. Use --name to specify the contact name."
        )
    
    result = {"name": name.strip()}
    
    if phone:
        result["phone"] = validate_phone(phone)
    
    if email:
        result["email"] = validate_email(email)
    
    if organization:
        result["organization"] = organization.strip()
    
    if title:
        result["title"] = title.strip()
    
    if url:
        result["url"] = validate_url(url)
    
    return result


def validate_output_path(output: str) -> Path:
    """Validate output file path.
    
    Args:
        output: The output file path.
        
    Returns:
        The validated Path object.
        
    Raises:
        ValidationError: If the path is invalid or not writable.
    """
    if not output:
        raise ValidationError(
            "Output path is required. Use --output to specify the file path."
        )
    
    path = Path(output).expanduser().resolve()
    
    # Check extension
    suffix = path.suffix.lower()
    if suffix not in (".png", ".svg"):
        raise ValidationError(
            f"Invalid output format: '{suffix}'. "
            "Output file must have .png or .svg extension."
        )
    
    # Check if parent directory exists and is writable
    parent = path.parent
    if not parent.exists():
        raise ValidationError(
            f"Output directory does not exist: '{parent}'. "
            "Please create the directory first or choose a different path."
        )
    
    if not os.access(parent, os.W_OK):
        raise ValidationError(
            f"Output directory is not writable: '{parent}'. "
            "Please check permissions or choose a different path."
        )
    
    return path


def validate_text(text: str) -> str:
    """Validate plain text input.
    
    Args:
        text: The text to validate.
        
    Returns:
        The validated text.
        
    Raises:
        ValidationError: If the text is empty or too long.
    """
    if not text:
        raise ValidationError("Text cannot be empty")
    
    # QR codes have practical limits based on error correction
    # Version 40 with L error correction can hold ~4296 alphanumeric chars
    if len(text) > 4000:
        raise ValidationError(
            f"Text too long ({len(text)} chars). "
            "Maximum recommended length is 4000 characters for reliable scanning."
        )
    
    return text

