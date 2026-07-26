"""Data loading and formatting utilities for the Phishing Email Triage Agent labs."""

import json
import os
from typing import Optional

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def load_emails(small: bool = False) -> list[dict]:
    """Load the email dataset.

    Args:
        small: If True, load the 5-email subset (Lab 1). Otherwise load full 50-email set.

    Returns:
        List of email dictionaries.
    """
    filename = "emails_small.json" if small else "emails.json"
    with open(os.path.join(_DATA_DIR, filename)) as f:
        return json.load(f)


def load_threat_intel() -> dict:
    """Load the threat intelligence database.

    Returns:
        Dictionary with malicious_domains, safe_domains, known_phishing_senders, url_reputation.
    """
    with open(os.path.join(_DATA_DIR, "threat_intel_db.json")) as f:
        return json.load(f)


def format_email_for_analysis(email: dict) -> str:
    """Format a single email dict into a human-readable string for LLM analysis.

    Args:
        email: Email dictionary from the dataset.

    Returns:
        Formatted multi-line string.
    """
    lines = [
        f"Email ID: {email['id']}",
        f"Timestamp: {email['timestamp']}",
        f"From: {email['from_display_name']} <{email['from_address']}>",
        f"To: {email['to_address']}",
        f"Subject: {email['subject']}",
        "",
        "--- Body ---",
        email["body"],
        "--- End Body ---",
        "",
    ]

    if email.get("urls"):
        lines.append(f"URLs in email: {', '.join(email['urls'])}")
    else:
        lines.append("URLs in email: None")

    if email.get("attachments"):
        att_strs = [f"{a['filename']} ({a['type']})" for a in email["attachments"]]
        lines.append(f"Attachments: {', '.join(att_strs)}")
    else:
        lines.append("Attachments: None")

    headers = email.get("headers", {})
    lines.append(
        f"Authentication: SPF={headers.get('spf', 'unknown')}, "
        f"DKIM={headers.get('dkim', 'unknown')}, "
        f"DMARC={headers.get('dmarc', 'unknown')}"
    )

    return "\n".join(lines)


def get_email_by_id(email_id: str, emails: Optional[list[dict]] = None) -> Optional[dict]:
    """Look up a single email by its ID.

    Args:
        email_id: The email ID (e.g., "EMAIL-001").
        emails: Optional pre-loaded email list. If None, loads the full dataset.

    Returns:
        The email dict, or None if not found.
    """
    if emails is None:
        emails = load_emails(small=False)
    for email in emails:
        if email["id"] == email_id:
            return email
    return None
