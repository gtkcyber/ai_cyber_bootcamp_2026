"""Mock security tools for the Phishing Email Triage Agent labs.

These tools simulate real security lookups (URL reputation, sender reputation,
email authentication checks) using the local threat_intel_db.json file so
students don't need paid API keys.

Used in Labs 2-5 where the LLM calls tools via LangGraph.
"""

import json
import os
from typing import Optional

from langchain_core.tools import tool

# Load threat intel DB once at import time
_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
with open(os.path.join(_DATA_DIR, "threat_intel_db.json")) as f:
    _THREAT_DB = json.load(f)


@tool
def check_url_reputation(url: str) -> str:
    """Check a URL against the threat intelligence database.

    Args:
        url: The URL to check for malicious activity.

    Returns:
        A summary of the URL reputation check results.
    """
    # Check for exact or prefix match in URL reputation database
    for entry in _THREAT_DB["url_reputation"]:
        if url.startswith(entry["url"]) or entry["url"].startswith(url.split("?")[0]):
            verdict = entry["verdict"]
            confidence = entry["confidence"]
            threat = entry.get("threat_type") or "none"
            return (
                f"URL: {url}\n"
                f"Verdict: {verdict.upper()}\n"
                f"Threat Type: {threat}\n"
                f"Confidence: {confidence:.0%}"
            )

    # Check if the domain is in malicious domains list
    from urllib.parse import urlparse
    try:
        domain = urlparse(url).netloc
    except Exception:
        domain = url

    for entry in _THREAT_DB["malicious_domains"]:
        if entry["domain"] in domain:
            return (
                f"URL: {url}\n"
                f"Verdict: MALICIOUS\n"
                f"Threat Type: {entry['category']}\n"
                f"Confidence: {entry['confidence']:.0%}\n"
                f"Note: Domain {entry['domain']} flagged since {entry['first_seen']}"
            )

    # Check safe domains
    for entry in _THREAT_DB["safe_domains"]:
        if entry["domain"] in domain:
            return (
                f"URL: {url}\n"
                f"Verdict: CLEAN\n"
                f"Threat Type: none\n"
                f"Confidence: 95%\n"
                f"Note: Domain {entry['domain']} is a verified {entry['category']} domain"
            )

    return (
        f"URL: {url}\n"
        f"Verdict: UNKNOWN\n"
        f"Threat Type: unknown\n"
        f"Confidence: N/A\n"
        f"Note: URL not found in threat intelligence database"
    )


@tool
def check_sender_reputation(email_address: str) -> str:
    """Check a sender's email address against known phishing sender databases and domain reputation.

    Args:
        email_address: The sender's email address to check.

    Returns:
        A summary of the sender reputation check results.
    """
    # Check known phishing senders
    for entry in _THREAT_DB["known_phishing_senders"]:
        if entry["email"] == email_address:
            return (
                f"Sender: {email_address}\n"
                f"Verdict: KNOWN PHISHING SENDER\n"
                f"Reports: {entry['reported_count']} reports since {entry['first_reported']}\n"
                f"Recommendation: BLOCK"
            )

    # Extract domain and check
    domain = email_address.split("@")[-1] if "@" in email_address else email_address

    # Check malicious domains
    for entry in _THREAT_DB["malicious_domains"]:
        if entry["domain"] == domain:
            return (
                f"Sender: {email_address}\n"
                f"Verdict: SUSPICIOUS DOMAIN\n"
                f"Domain Category: {entry['category']}\n"
                f"Domain First Seen: {entry['first_seen']}\n"
                f"Confidence: {entry['confidence']:.0%}\n"
                f"Recommendation: INVESTIGATE"
            )

    # Check safe domains
    for entry in _THREAT_DB["safe_domains"]:
        if entry["domain"] == domain:
            return (
                f"Sender: {email_address}\n"
                f"Verdict: TRUSTED SENDER\n"
                f"Domain Category: {entry['category']}\n"
                f"Domain Verified: {entry['verified']}\n"
                f"Recommendation: ALLOW"
            )

    return (
        f"Sender: {email_address}\n"
        f"Verdict: UNKNOWN\n"
        f"Note: Sender not found in reputation databases\n"
        f"Recommendation: PROCEED WITH CAUTION"
    )


@tool
def check_email_authentication(
    from_address: str,
    spf: str,
    dkim: str,
    dmarc: str,
) -> str:
    """Analyze email authentication headers (SPF, DKIM, DMARC) to assess legitimacy.

    Args:
        from_address: The sender's email address.
        spf: SPF check result (pass, fail, softfail, neutral, none).
        dkim: DKIM check result (pass, fail, none).
        dmarc: DMARC check result (pass, fail, none).

    Returns:
        A summary of the email authentication analysis.
    """
    results = []
    score = 0

    # Evaluate SPF
    spf_lower = spf.lower()
    if spf_lower == "pass":
        results.append("SPF: PASS - Sender IP is authorized to send for this domain")
        score += 1
    elif spf_lower == "softfail":
        results.append("SPF: SOFTFAIL - Sender IP is NOT explicitly authorized (possible misconfiguration or spoofing)")
        score += 0.5
    elif spf_lower == "neutral":
        results.append("SPF: NEUTRAL - Domain makes no assertion about this sender")
        score += 0.25
    else:
        results.append("SPF: FAIL - Sender IP is NOT authorized to send for this domain (likely spoofed)")

    # Evaluate DKIM
    dkim_lower = dkim.lower()
    if dkim_lower == "pass":
        results.append("DKIM: PASS - Email signature is valid and verified")
        score += 1
    else:
        results.append("DKIM: FAIL - Email signature is invalid or missing (message may be tampered)")

    # Evaluate DMARC
    dmarc_lower = dmarc.lower()
    if dmarc_lower == "pass":
        results.append("DMARC: PASS - Email passes domain alignment checks")
        score += 1
    else:
        results.append("DMARC: FAIL - Email fails domain alignment (high risk of spoofing)")

    # Overall assessment
    if score >= 2.5:
        overall = "LEGITIMATE - Authentication checks pass"
        risk = "LOW"
    elif score >= 1.5:
        overall = "INCONCLUSIVE - Some authentication checks fail"
        risk = "MEDIUM"
    else:
        overall = "SUSPICIOUS - Most authentication checks fail"
        risk = "HIGH"

    return (
        f"Email Authentication Analysis for {from_address}\n"
        f"{'=' * 50}\n"
        + "\n".join(results)
        + f"\n{'=' * 50}\n"
        f"Overall: {overall}\n"
        f"Risk Level: {risk}\n"
        f"Auth Score: {score}/3"
    )


# Convenience list for binding to LLMs
SECURITY_TOOLS = [check_url_reputation, check_sender_reputation, check_email_authentication]
