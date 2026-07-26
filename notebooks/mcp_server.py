"""
Worksheet 12.1 — a small MCP server exposing security investigation tools.

This is the SERVER your agent will connect to in the lab. It is complete and
given to you; you do not need to edit it. Read it to see how an MCP server is
built with FastMCP, then switch to the notebook to connect an agent to it.

The tools return SIMULATED results (the same idea as the mock tools from
Module 12). In a real deployment these would call out to threat-intelligence
services, DNS, and mail-authentication checks.

Run it directly to smoke-test that it imports and starts:
    python mcp_server.py
(It will wait for a client on stdin — press Ctrl-C to stop.)
"""

from mcp.server.fastmcp import FastMCP

# The server's name. A host uses this to identify the server it connected to.
mcp = FastMCP("security-tools")

# A tiny simulated reputation database. Any domain not listed is treated as
# unknown / low signal.
_BAD_DOMAINS = {
    "paypa1-secure.com": "malicious (credential phishing kit observed)",
    "account-verify.net": "malicious (bulk phishing infrastructure)",
    "cheap-meds-now.ru": "malicious (spam / malware distribution)",
}
_GOOD_DOMAINS = {
    "paypal.com": "trusted (verified brand domain)",
    "github.com": "trusted (verified brand domain)",
    "irs.gov": "trusted (verified government domain)",
}


@mcp.tool()
def check_url_reputation(url: str) -> str:
    """Look up the reputation of a URL or domain and return a risk summary.

    Use this whenever an email contains a link and you need to know whether the
    destination is known-malicious, trusted, or unknown.

    Args:
        url: The URL or bare domain to check, for example "http://paypa1-secure.com/login".

    Returns:
        A short reputation summary for the domain.
    """
    domain = url.split("//")[-1].split("/")[0].lower()
    if domain in _BAD_DOMAINS:
        return f"{domain}: {_BAD_DOMAINS[domain]}  [risk score 90/100]"
    if domain in _GOOD_DOMAINS:
        return f"{domain}: {_GOOD_DOMAINS[domain]}  [risk score 5/100]"
    return f"{domain}: no reputation data found  [risk score 40/100, treat with caution]"


@mcp.tool()
def check_sender_reputation(from_address: str) -> str:
    """Assess the reputation of an email sender address.

    Use this to judge whether the sender domain is a known brand, a look-alike,
    or an unknown sender.

    Args:
        from_address: The full sender address, for example "billing@paypa1-secure.com".

    Returns:
        A short reputation summary for the sender.
    """
    domain = from_address.split("@")[-1].lower().strip()
    if domain in _BAD_DOMAINS:
        return f"sender {from_address}: domain flagged as {_BAD_DOMAINS[domain]}"
    if domain in _GOOD_DOMAINS:
        return f"sender {from_address}: domain is {_GOOD_DOMAINS[domain]}"
    return f"sender {from_address}: unknown sender domain, no established reputation"


@mcp.tool()
def check_email_authentication(from_address: str, spf: str, dkim: str, dmarc: str) -> str:
    """Analyze SPF, DKIM, and DMARC results to assess whether an email is spoofed.

    Use this when you have the authentication header results and want to know
    whether the message genuinely came from the domain it claims.

    Args:
        from_address: The sender address the email claims to be from.
        spf: SPF result (pass, fail, softfail, neutral, none).
        dkim: DKIM result (pass, fail, none).
        dmarc: DMARC result (pass, fail, none).

    Returns:
        A summary of the authentication analysis.
    """
    failures = [name for name, val in
                (("SPF", spf), ("DKIM", dkim), ("DMARC", dmarc))
                if val.lower() in ("fail", "softfail", "none")]
    if not failures:
        return f"{from_address}: SPF/DKIM/DMARC all pass — authentication looks legitimate."
    return (f"{from_address}: authentication problems on {', '.join(failures)} "
            f"— the message may be spoofed.")


if __name__ == "__main__":
    # stdio transport by default: the host launches this file as a subprocess
    # and talks to it over standard input/output.
    mcp.run()
