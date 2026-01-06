"""Command-line interface for QR code generator."""

import sys
from typing import Optional

import click

from . import formatters, generator, history, validator
from .validator import ValidationError


def _build_command(ctx: click.Context) -> str:
    """Reconstruct the command string from context.
    
    Args:
        ctx: Click context object.
        
    Returns:
        The reconstructed command string.
    """
    parts = ["qr", ctx.info_name]
    
    # Get parent command if exists (for subcommands like 'history clear')
    if ctx.parent and ctx.parent.info_name not in ("cli", "qr"):
        parts = ["qr", ctx.parent.info_name, ctx.info_name]
    
    # Add arguments and options
    for param in ctx.command.params:
        value = ctx.params.get(param.name)
        if value is None:
            continue
        
        if isinstance(param, click.Argument):
            if isinstance(value, str):
                parts.append(f'"{value}"')
            else:
                parts.append(str(value))
        elif isinstance(param, click.Option):
            if isinstance(value, bool):
                if value:
                    parts.append(f"--{param.name.replace('_', '-')}")
            elif value:
                if isinstance(value, str) and " " in value:
                    parts.append(f'--{param.name.replace("_", "-")} "{value}"')
                else:
                    parts.append(f"--{param.name.replace('_', '-')} {value}")
    
    return " ".join(parts)


def _handle_error(error: Exception) -> None:
    """Handle errors consistently.
    
    Args:
        error: The exception to handle.
    """
    click.secho(f"Error: {error}", fg="red", err=True)
    sys.exit(1)


@click.group()
@click.version_option(package_name="qr-generator")
def cli():
    """QR Code Generator - Generate QR codes from the command line.
    
    All commands require --output to specify the output file path.
    Output format is inferred from the file extension (.png or .svg).
    """
    pass


@cli.command()
@click.argument("url")
@click.option("--output", "-o", required=True, help="Output file path (.png or .svg)")
@click.option("--format", "-f", "format_override", type=click.Choice(["png", "svg"]), help="Override output format")
@click.pass_context
def url(ctx: click.Context, url: str, output: str, format_override: Optional[str]):
    """Generate QR code for a URL.
    
    URL: The URL to encode (http:// or https://)
    """
    try:
        validated_url = validator.validate_url(url)
        output_path = validator.validate_output_path(output)
        
        result_path = generator.generate_qr(
            data=validated_url,
            output_path=output_path,
            format_override=format_override,
        )
        
        # Record in history
        command = _build_command(ctx)
        history.add_entry(
            qr_type="url",
            command=command,
            output_path=str(result_path),
            data={"url": validated_url},
        )
        
        click.secho(f"✓ QR code saved to: {result_path}", fg="green")
        
    except ValidationError as e:
        _handle_error(e)


@cli.command()
@click.argument("text")
@click.option("--output", "-o", required=True, help="Output file path (.png or .svg)")
@click.option("--format", "-f", "format_override", type=click.Choice(["png", "svg"]), help="Override output format")
@click.pass_context
def text(ctx: click.Context, text: str, output: str, format_override: Optional[str]):
    """Generate QR code for plain text.
    
    TEXT: The text to encode
    """
    try:
        validated_text = validator.validate_text(text)
        output_path = validator.validate_output_path(output)
        
        result_path = generator.generate_qr(
            data=validated_text,
            output_path=output_path,
            format_override=format_override,
        )
        
        # Record in history
        command = _build_command(ctx)
        history.add_entry(
            qr_type="text",
            command=command,
            output_path=str(result_path),
            data={"text": validated_text[:100] + "..." if len(validated_text) > 100 else validated_text},
        )
        
        click.secho(f"✓ QR code saved to: {result_path}", fg="green")
        
    except ValidationError as e:
        _handle_error(e)


@cli.command()
@click.option("--ssid", "-s", required=True, help="WiFi network name (SSID)")
@click.option("--password", "-p", required=True, help="WiFi password")
@click.option("--security", "-t", default="WPA", help="Security type (WPA/WPA2/WPA3/WEP/nopass)")
@click.option("--hidden", is_flag=True, help="Network is hidden")
@click.option("--output", "-o", required=True, help="Output file path (.png or .svg)")
@click.option("--format", "-f", "format_override", type=click.Choice(["png", "svg"]), help="Override output format")
@click.pass_context
def wifi(
    ctx: click.Context,
    ssid: str,
    password: str,
    security: str,
    hidden: bool,
    output: str,
    format_override: Optional[str],
):
    """Generate QR code for WiFi credentials.
    
    Creates a QR code that can be scanned to connect to a WiFi network.
    """
    try:
        ssid, password, security = validator.validate_wifi(ssid, password, security)
        output_path = validator.validate_output_path(output)
        
        wifi_data = formatters.format_wifi(ssid, password, security, hidden)
        
        result_path = generator.generate_qr(
            data=wifi_data,
            output_path=output_path,
            format_override=format_override,
        )
        
        # Record in history
        command = _build_command(ctx)
        history.add_entry(
            qr_type="wifi",
            command=command,
            output_path=str(result_path),
            data={"ssid": ssid, "security": security, "hidden": hidden},
        )
        
        click.secho(f"✓ QR code saved to: {result_path}", fg="green")
        
    except ValidationError as e:
        _handle_error(e)


@cli.command()
@click.option("--name", "-n", required=True, help="Contact name")
@click.option("--phone", "-p", help="Phone number")
@click.option("--email", "-e", help="Email address")
@click.option("--organization", "--org", help="Organization/company name")
@click.option("--title", "-t", help="Job title")
@click.option("--url", "-u", help="Website URL")
@click.option("--output", "-o", required=True, help="Output file path (.png or .svg)")
@click.option("--format", "-f", "format_override", type=click.Choice(["png", "svg"]), help="Override output format")
@click.pass_context
def vcard(
    ctx: click.Context,
    name: str,
    phone: Optional[str],
    email: Optional[str],
    organization: Optional[str],
    title: Optional[str],
    url: Optional[str],
    output: str,
    format_override: Optional[str],
):
    """Generate QR code for a contact card (vCard).
    
    Creates a QR code that can be scanned to add a contact.
    """
    try:
        vcard_data = validator.validate_vcard(
            name=name,
            phone=phone,
            email=email,
            organization=organization,
            title=title,
            url=url,
        )
        output_path = validator.validate_output_path(output)
        
        formatted = formatters.format_vcard(**vcard_data)
        
        result_path = generator.generate_qr(
            data=formatted,
            output_path=output_path,
            format_override=format_override,
        )
        
        # Record in history
        command = _build_command(ctx)
        history.add_entry(
            qr_type="vcard",
            command=command,
            output_path=str(result_path),
            data={"name": name, "phone": phone, "email": email},
        )
        
        click.secho(f"✓ QR code saved to: {result_path}", fg="green")
        
    except ValidationError as e:
        _handle_error(e)


@cli.command()
@click.argument("address")
@click.option("--subject", "-s", help="Email subject")
@click.option("--body", "-b", help="Email body")
@click.option("--cc", help="CC recipients")
@click.option("--bcc", help="BCC recipients")
@click.option("--output", "-o", required=True, help="Output file path (.png or .svg)")
@click.option("--format", "-f", "format_override", type=click.Choice(["png", "svg"]), help="Override output format")
@click.pass_context
def email(
    ctx: click.Context,
    address: str,
    subject: Optional[str],
    body: Optional[str],
    cc: Optional[str],
    bcc: Optional[str],
    output: str,
    format_override: Optional[str],
):
    """Generate QR code for an email address.
    
    ADDRESS: The recipient email address
    """
    try:
        validated_email = validator.validate_email(address)
        output_path = validator.validate_output_path(output)
        
        email_data = formatters.format_email(
            address=validated_email,
            subject=subject,
            body=body,
            cc=cc,
            bcc=bcc,
        )
        
        result_path = generator.generate_qr(
            data=email_data,
            output_path=output_path,
            format_override=format_override,
        )
        
        # Record in history
        command = _build_command(ctx)
        history.add_entry(
            qr_type="email",
            command=command,
            output_path=str(result_path),
            data={"email": validated_email, "subject": subject},
        )
        
        click.secho(f"✓ QR code saved to: {result_path}", fg="green")
        
    except ValidationError as e:
        _handle_error(e)


@cli.command()
@click.argument("phone")
@click.option("--message", "-m", help="Pre-filled message text")
@click.option("--output", "-o", required=True, help="Output file path (.png or .svg)")
@click.option("--format", "-f", "format_override", type=click.Choice(["png", "svg"]), help="Override output format")
@click.pass_context
def sms(
    ctx: click.Context,
    phone: str,
    message: Optional[str],
    output: str,
    format_override: Optional[str],
):
    """Generate QR code for SMS.
    
    PHONE: The recipient phone number
    """
    try:
        validated_phone = validator.validate_phone(phone)
        output_path = validator.validate_output_path(output)
        
        sms_data = formatters.format_sms(validated_phone, message)
        
        result_path = generator.generate_qr(
            data=sms_data,
            output_path=output_path,
            format_override=format_override,
        )
        
        # Record in history
        command = _build_command(ctx)
        history.add_entry(
            qr_type="sms",
            command=command,
            output_path=str(result_path),
            data={"phone": validated_phone, "message": message},
        )
        
        click.secho(f"✓ QR code saved to: {result_path}", fg="green")
        
    except ValidationError as e:
        _handle_error(e)


@cli.group(invoke_without_command=True)
@click.option("--limit", "-l", type=int, help="Limit number of entries shown")
@click.pass_context
def history_cmd(ctx: click.Context, limit: Optional[int]):
    """View or manage QR code generation history.
    
    Shows recent QR codes with the command used to generate them.
    """
    if ctx.invoked_subcommand is None:
        entries = history.get_entries(limit=limit)
        
        if not entries:
            click.echo("No history entries found.")
            return
        
        click.echo(f"\nQR Code Generation History ({len(entries)} entries):\n")
        
        for i, entry in enumerate(entries, 1):
            formatted = history.format_entry_for_display(entry, i)
            click.echo(formatted)
            click.echo()


# Rename the group to 'history' for CLI
history_cmd.name = "history"


@history_cmd.command("clear")
@click.confirmation_option(prompt="Are you sure you want to clear all history?")
def history_clear():
    """Clear all history entries."""
    count = history.clear_history()
    click.secho(f"✓ Cleared {count} history entries.", fg="green")


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()

