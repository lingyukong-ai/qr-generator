"""QR code generation with PNG and SVG output support."""

from pathlib import Path
from typing import Literal, Optional

import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.svg import SvgPathImage


def generate_qr(
    data: str,
    output_path: Path,
    format_override: Optional[Literal["png", "svg"]] = None,
    error_correction: Literal["L", "M", "Q", "H"] = "M",
    box_size: int = 10,
    border: int = 4,
) -> Path:
    """Generate a QR code and save to file.
    
    Args:
        data: The data to encode in the QR code.
        output_path: The path to save the QR code image.
        format_override: Override the output format (inferred from extension if None).
        error_correction: Error correction level (L=7%, M=15%, Q=25%, H=30%).
        box_size: Size of each box in pixels (for PNG).
        border: Border size in boxes.
        
    Returns:
        The path to the generated QR code file.
    """
    # Determine output format
    if format_override:
        output_format = format_override.lower()
    else:
        output_format = output_path.suffix.lower().lstrip(".")
    
    # Map error correction level
    ec_map = {
        "L": qrcode.constants.ERROR_CORRECT_L,
        "M": qrcode.constants.ERROR_CORRECT_M,
        "Q": qrcode.constants.ERROR_CORRECT_Q,
        "H": qrcode.constants.ERROR_CORRECT_H,
    }
    error_level = ec_map.get(error_correction.upper(), qrcode.constants.ERROR_CORRECT_M)
    
    # Create QR code
    qr = qrcode.QRCode(
        version=None,  # Auto-determine version
        error_correction=error_level,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    # Generate image based on format
    if output_format == "svg":
        img = qr.make_image(image_factory=SvgPathImage)
        # Ensure output path has .svg extension
        if output_path.suffix.lower() != ".svg":
            output_path = output_path.with_suffix(".svg")
    else:
        # PNG output
        img = qr.make_image(image_factory=StyledPilImage, fill_color="black", back_color="white")
        # Ensure output path has .png extension
        if output_path.suffix.lower() != ".png":
            output_path = output_path.with_suffix(".png")
    
    # Save the image
    img.save(str(output_path))
    
    return output_path


def get_qr_info(data: str) -> dict:
    """Get information about a QR code without generating it.
    
    Args:
        data: The data to analyze.
        
    Returns:
        Dictionary with QR code information.
    """
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    return {
        "version": qr.version,
        "data_length": len(data),
        "modules": qr.modules_count,
        "error_correction": "M",
    }

