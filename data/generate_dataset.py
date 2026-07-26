#!/usr/bin/env python3
"""Generate synthetic phishing email dataset for the AI Agents CCST course.

Produces:
  - emails.json       (50 emails: 25 phishing, 22 legitimate, 3 borderline)
  - emails_small.json (5-email subset for Lab 1)
  - threat_intel_db.json (mock threat intelligence database)

Run:  python data/generate_dataset.py
"""

import json
import os
from datetime import datetime, timedelta
import random

random.seed(42)

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
BASE_TS = datetime(2025, 6, 15, 8, 0, 0)


def ts(offset_hours: int) -> str:
    return (BASE_TS + timedelta(hours=offset_hours)).isoformat() + "Z"


# ---------------------------------------------------------------------------
# Phishing emails (25)
# ---------------------------------------------------------------------------
PHISHING_EMAILS = [
    # --- Credential Harvesting (5) ---
    {
        "id": "EMAIL-001",
        "timestamp": ts(0),
        "from_address": "security-alert@micros0ft-verify.com",
        "from_display_name": "Microsoft Security Team",
        "to_address": "john.doe@company.com",
        "subject": "URGENT: Your account has been compromised",
        "body": (
            "Dear User,\n\n"
            "We have detected unusual sign-in activity on your Microsoft 365 account. "
            "Your account may have been compromised by an unauthorized third party.\n\n"
            "To secure your account, please verify your identity immediately by clicking the link below:\n\n"
            "https://micros0ft-verify.com/secure/login?id=8f3a2b\n\n"
            "If you do not verify within 24 hours, your account will be permanently suspended.\n\n"
            "Microsoft Security Team"
        ),
        "urls": ["https://micros0ft-verify.com/secure/login?id=8f3a2b"],
        "attachments": [],
        "headers": {"spf": "fail", "dkim": "fail", "dmarc": "fail"},
        "ground_truth": "phishing",
        "attack_type": "credential_harvesting",
    },
    {
        "id": "EMAIL-002",
        "timestamp": ts(2),
        "from_address": "no-reply@dropb0x-share.net",
        "from_display_name": "Dropbox",
        "to_address": "sarah.smith@company.com",
        "subject": "Document shared with you: Q3_Financial_Report.pdf",
        "body": (
            "Hi Sarah,\n\n"
            "A document has been shared with you via Dropbox. Click below to view:\n\n"
            "https://dropb0x-share.net/view/Q3_Financial_Report?token=x9k2m\n\n"
            "This link will expire in 48 hours.\n\n"
            "- The Dropbox Team"
        ),
        "urls": ["https://dropb0x-share.net/view/Q3_Financial_Report?token=x9k2m"],
        "attachments": [],
        "headers": {"spf": "fail", "dkim": "fail", "dmarc": "fail"},
        "ground_truth": "phishing",
        "attack_type": "credential_harvesting",
    },
    {
        "id": "EMAIL-003",
        "timestamp": ts(5),
        "from_address": "admin@g00gle-workspace.com",
        "from_display_name": "Google Workspace Admin",
        "to_address": "mike.jones@company.com",
        "subject": "Action Required: Storage quota exceeded",
        "body": (
            "Hello Mike,\n\n"
            "Your Google Workspace storage is 98% full. You must upgrade your plan "
            "or remove files immediately to avoid losing access.\n\n"
            "Click here to manage your storage: https://g00gle-workspace.com/storage/upgrade\n\n"
            "Warning: Emails will bounce if storage is not freed within 12 hours.\n\n"
            "Google Workspace Administration"
        ),
        "urls": ["https://g00gle-workspace.com/storage/upgrade"],
        "attachments": [],
        "headers": {"spf": "fail", "dkim": "fail", "dmarc": "fail"},
        "ground_truth": "phishing",
        "attack_type": "credential_harvesting",
    },
    {
        "id": "EMAIL-004",
        "timestamp": ts(8),
        "from_address": "support@amazn-prime.com",
        "from_display_name": "Amazon Customer Service",
        "to_address": "lisa.chen@company.com",
        "subject": "Your Amazon order #112-4567890 has a payment issue",
        "body": (
            "Dear Valued Customer,\n\n"
            "We were unable to process payment for your recent order. "
            "Your credit card on file has been declined.\n\n"
            "Please update your payment method within 24 hours to avoid order cancellation:\n"
            "https://amazn-prime.com/update-payment?order=112-4567890\n\n"
            "If you believe this is an error, please update your payment details immediately.\n\n"
            "Amazon Customer Service"
        ),
        "urls": ["https://amazn-prime.com/update-payment?order=112-4567890"],
        "attachments": [],
        "headers": {"spf": "fail", "dkim": "fail", "dmarc": "fail"},
        "ground_truth": "phishing",
        "attack_type": "credential_harvesting",
    },
    {
        "id": "EMAIL-005",
        "timestamp": ts(10),
        "from_address": "noreply@linkedn-verify.com",
        "from_display_name": "LinkedIn",
        "to_address": "tom.wilson@company.com",
        "subject": "Someone viewed your LinkedIn profile 47 times",
        "body": (
            "Hi Tom,\n\n"
            "Your profile has had 47 views this week! You appeared in 12 searches.\n\n"
            "See who's viewing your profile:\n"
            "https://linkedn-verify.com/profile/views?u=tom.wilson\n\n"
            "Upgrade to Premium to unlock all viewer details.\n\n"
            "The LinkedIn Team"
        ),
        "urls": ["https://linkedn-verify.com/profile/views?u=tom.wilson"],
        "attachments": [],
        "headers": {"spf": "fail", "dkim": "fail", "dmarc": "fail"},
        "ground_truth": "phishing",
        "attack_type": "credential_harvesting",
    },
    # --- Business Email Compromise (5) ---
    {
        "id": "EMAIL-006",
        "timestamp": ts(12),
        "from_address": "ceo@company-exec.com",
        "from_display_name": "Robert Zhang, CEO",
        "to_address": "accounting@company.com",
        "subject": "Urgent wire transfer needed - CONFIDENTIAL",
        "body": (
            "Hi Accounting Team,\n\n"
            "I need you to process an urgent wire transfer of $47,500 to a new vendor. "
            "This is for a confidential acquisition deal that cannot wait.\n\n"
            "Please wire to:\n"
            "Bank: First National Bank\n"
            "Account: 4829173650\n"
            "Routing: 021000089\n\n"
            "This must be completed before end of business today. "
            "Do NOT discuss this with anyone else as it is under NDA.\n\n"
            "I'm in meetings all day so please just process it.\n\n"
            "Robert Zhang\nCEO"
        ),
        "urls": [],
        "attachments": [],
        "headers": {"spf": "fail", "dkim": "fail", "dmarc": "fail"},
        "ground_truth": "phishing",
        "attack_type": "bec",
    },
    {
        "id": "EMAIL-007",
        "timestamp": ts(14),
        "from_address": "cfo-office@company-finance.net",
        "from_display_name": "Patricia Moore, CFO",
        "to_address": "payroll@company.com",
        "subject": "Payroll update - Direct deposit change",
        "body": (
            "Hello Payroll,\n\n"
            "Please update my direct deposit information effective immediately.\n\n"
            "New bank details:\n"
            "Bank: Chase Bank\n"
            "Routing: 072000326\n"
            "Account: 9281736450\n"
            "Account Type: Checking\n\n"
            "Please confirm once updated. I need this done before the next pay cycle.\n\n"
            "Patricia Moore\nChief Financial Officer"
        ),
        "urls": [],
        "attachments": [],
        "headers": {"spf": "fail", "dkim": "fail", "dmarc": "fail"},
        "ground_truth": "phishing",
        "attack_type": "bec",
    },
    {
        "id": "EMAIL-008",
        "timestamp": ts(16),
        "from_address": "vendor-update@supplierportal-pay.com",
        "from_display_name": "Acme Supplies - Accounts Receivable",
        "to_address": "ap@company.com",
        "subject": "Updated banking information for invoice payments",
        "body": (
            "Dear Accounts Payable,\n\n"
            "Please note that effective immediately, our banking details have changed. "
            "All future payments for outstanding invoices should be directed to:\n\n"
            "Bank: Wells Fargo\n"
            "Account Name: Acme Supplies LLC\n"
            "Account: 7391024856\n"
            "Routing: 121000248\n\n"
            "Please update your records. Outstanding invoice INV-2025-0892 ($23,450) "
            "is past due and should be remitted to the new account.\n\n"
            "Best regards,\n"
            "James Anderson\n"
            "Acme Supplies - Accounts Receivable"
        ),
        "urls": [],
        "attachments": [{"filename": "updated_bank_details.pdf", "type": "application/pdf"}],
        "headers": {"spf": "fail", "dkim": "fail", "dmarc": "fail"},
        "ground_truth": "phishing",
        "attack_type": "bec",
    },
    {
        "id": "EMAIL-009",
        "timestamp": ts(18),
        "from_address": "legal@company-legal-dept.com",
        "from_display_name": "David Park, General Counsel",
        "to_address": "hr@company.com",
        "subject": "CONFIDENTIAL: Employee records request for legal review",
        "body": (
            "Hi HR Team,\n\n"
            "We are conducting an internal compliance audit and require the following "
            "employee records ASAP:\n\n"
            "- Full names and SSNs for all employees hired in Q1-Q2 2025\n"
            "- W-2 forms for the same period\n"
            "- Current salary information\n\n"
            "Please compile and send to this email address directly. "
            "This is legally privileged and should not be shared with anyone else.\n\n"
            "Time-sensitive - needed by EOD.\n\n"
            "David Park\nGeneral Counsel"
        ),
        "urls": [],
        "attachments": [],
        "headers": {"spf": "fail", "dkim": "fail", "dmarc": "fail"},
        "ground_truth": "phishing",
        "attack_type": "bec",
    },
    {
        "id": "EMAIL-010",
        "timestamp": ts(20),
        "from_address": "executive@company-board.org",
        "from_display_name": "Margaret Ellis, Board Chair",
        "to_address": "robert.zhang@company.com",
        "subject": "Gift cards for employee appreciation event",
        "body": (
            "Robert,\n\n"
            "I need your help with something for the upcoming employee appreciation event. "
            "Can you purchase 20 Amazon gift cards at $100 each?\n\n"
            "Please buy them today and send me the redemption codes via email. "
            "I'll reimburse you from the board discretionary fund.\n\n"
            "Please keep this quiet - it's meant to be a surprise!\n\n"
            "Thanks,\nMargaret"
        ),
        "urls": [],
        "attachments": [],
        "headers": {"spf": "fail", "dkim": "fail", "dmarc": "fail"},
        "ground_truth": "phishing",
        "attack_type": "bec",
    },
    # --- Malware Delivery (5) ---
    {
        "id": "EMAIL-011",
        "timestamp": ts(22),
        "from_address": "invoice@totallylegit-invoicing.com",
        "from_display_name": "QuickBooks Invoice",
        "to_address": "finance@company.com",
        "subject": "Invoice #INV-29571 Due - Payment Required",
        "body": (
            "Please find attached the invoice for services rendered.\n\n"
            "Invoice Number: INV-29571\n"
            "Amount Due: $3,250.00\n"
            "Due Date: June 20, 2025\n\n"
            "Please review the attached document and process payment at your earliest convenience.\n\n"
            "If you have questions, please reply to this email."
        ),
        "urls": [],
        "attachments": [{"filename": "Invoice_INV-29571.xlsm", "type": "application/vnd.ms-excel.sheet.macroEnabled"}],
        "headers": {"spf": "fail", "dkim": "fail", "dmarc": "fail"},
        "ground_truth": "phishing",
        "attack_type": "malware",
    },
    {
        "id": "EMAIL-012",
        "timestamp": ts(24),
        "from_address": "scanner@company-mfp.com",
        "from_display_name": "HP Digital Sender",
        "to_address": "all-staff@company.com",
        "subject": "Scanned Document - 06152025_001.pdf",
        "body": (
            "You have received a scanned document from HP Digital Sender.\n\n"
            "Device: HP LaserJet MFP M528 (3rd Floor)\n"
            "Pages: 3\n"
            "Resolution: 300 DPI\n\n"
            "Please see attached."
        ),
        "urls": [],
        "attachments": [{"filename": "scan_06152025_001.pdf.exe", "type": "application/x-msdownload"}],
        "headers": {"spf": "fail", "dkim": "fail", "dmarc": "fail"},
        "ground_truth": "phishing",
        "attack_type": "malware",
    },
    {
        "id": "EMAIL-013",
        "timestamp": ts(26),
        "from_address": "delivery@fedx-tracking.com",
        "from_display_name": "FedEx Delivery Notification",
        "to_address": "reception@company.com",
        "subject": "FedEx: Delivery attempt failed - Action required",
        "body": (
            "Dear Customer,\n\n"
            "We attempted to deliver your package (Tracking: 7829104653) but were unable "
            "to complete delivery.\n\n"
            "Please download the attached shipping label and bring it to your nearest "
            "FedEx location to collect your package.\n\n"
            "If not collected within 5 business days, the package will be returned to sender.\n\n"
            "Track your package: https://fedx-tracking.com/track/7829104653\n\n"
            "FedEx Customer Service"
        ),
        "urls": ["https://fedx-tracking.com/track/7829104653"],
        "attachments": [{"filename": "FedEx_ShippingLabel_7829104653.zip", "type": "application/zip"}],
        "headers": {"spf": "fail", "dkim": "fail", "dmarc": "fail"},
        "ground_truth": "phishing",
        "attack_type": "malware",
    },
    {
        "id": "EMAIL-014",
        "timestamp": ts(28),
        "from_address": "helpdesk@it-support-portal.net",
        "from_display_name": "IT Help Desk",
        "to_address": "all-staff@company.com",
        "subject": "Critical Security Patch - Install immediately",
        "body": (
            "ATTENTION ALL EMPLOYEES\n\n"
            "A critical vulnerability has been discovered that affects all Windows workstations. "
            "IT has prepared an emergency patch that must be installed immediately.\n\n"
            "Please download and run the attached patch installer.\n\n"
            "Instructions:\n"
            "1. Save the attached file to your desktop\n"
            "2. Right-click and select 'Run as Administrator'\n"
            "3. Follow the on-screen prompts\n\n"
            "This patch must be installed before 5 PM today.\n\n"
            "IT Security Team"
        ),
        "urls": [],
        "attachments": [{"filename": "CriticalSecurityPatch_KB5028166.exe", "type": "application/x-msdownload"}],
        "headers": {"spf": "fail", "dkim": "fail", "dmarc": "fail"},
        "ground_truth": "phishing",
        "attack_type": "malware",
    },
    {
        "id": "EMAIL-015",
        "timestamp": ts(30),
        "from_address": "resume@careers-apply.com",
        "from_display_name": "Job Application - Emily Watson",
        "to_address": "hr@company.com",
        "subject": "Application for Senior Developer Position",
        "body": (
            "Dear Hiring Manager,\n\n"
            "I am writing to express my interest in the Senior Developer position posted "
            "on your careers page.\n\n"
            "Please find my resume and cover letter attached. I have 8 years of experience "
            "in full-stack development and would love to discuss how I can contribute "
            "to your team.\n\n"
            "Best regards,\n"
            "Emily Watson"
        ),
        "urls": [],
        "attachments": [
            {"filename": "Emily_Watson_Resume.docm", "type": "application/vnd.ms-word.document.macroEnabled"},
            {"filename": "Cover_Letter.docm", "type": "application/vnd.ms-word.document.macroEnabled"},
        ],
        "headers": {"spf": "neutral", "dkim": "fail", "dmarc": "fail"},
        "ground_truth": "phishing",
        "attack_type": "malware",
    },
    # --- Spear Phishing (5) ---
    {
        "id": "EMAIL-016",
        "timestamp": ts(32),
        "from_address": "j.martinez@partnerco-consulting.com",
        "from_display_name": "Jennifer Martinez",
        "to_address": "sarah.smith@company.com",
        "subject": "Re: Follow up from the Denver conference",
        "body": (
            "Hi Sarah,\n\n"
            "It was great meeting you at the Denver Cybersecurity Conference last week! "
            "As discussed, I've put together the joint proposal for the Q4 security audit.\n\n"
            "Please review the document here and let me know your thoughts:\n"
            "https://partnerco-consulting.com/shared/proposal-q4-audit?ref=sarah.smith\n\n"
            "Looking forward to collaborating!\n\n"
            "Best,\n"
            "Jennifer Martinez\n"
            "Senior Consultant, PartnerCo"
        ),
        "urls": ["https://partnerco-consulting.com/shared/proposal-q4-audit?ref=sarah.smith"],
        "attachments": [],
        "headers": {"spf": "softfail", "dkim": "fail", "dmarc": "fail"},
        "ground_truth": "phishing",
        "attack_type": "spear_phishing",
    },
    {
        "id": "EMAIL-017",
        "timestamp": ts(34),
        "from_address": "alumni@university-connect.net",
        "from_display_name": "MIT Alumni Network",
        "to_address": "mike.jones@company.com",
        "subject": "Mike - Your MIT alumni profile needs updating",
        "body": (
            "Dear Mike Jones (Class of 2012),\n\n"
            "Our records show your alumni profile hasn't been updated since 2020. "
            "We're compiling the annual alumni directory and need your current information.\n\n"
            "Please log in to update your profile:\n"
            "https://university-connect.net/mit/alumni/update?id=mjones2012\n\n"
            "The directory goes to print on July 1st, so please update by then.\n\n"
            "Go Engineers!\n"
            "MIT Alumni Association"
        ),
        "urls": ["https://university-connect.net/mit/alumni/update?id=mjones2012"],
        "attachments": [],
        "headers": {"spf": "fail", "dkim": "fail", "dmarc": "fail"},
        "ground_truth": "phishing",
        "attack_type": "spear_phishing",
    },
    {
        "id": "EMAIL-018",
        "timestamp": ts(36),
        "from_address": "noreply@internal-hr-survey.com",
        "from_display_name": "Company HR",
        "to_address": "all-staff@company.com",
        "subject": "Annual Employee Satisfaction Survey - $50 Gift Card",
        "body": (
            "Dear Team,\n\n"
            "It's time for our annual employee satisfaction survey! "
            "As a thank-you for participating, everyone who completes the survey "
            "will receive a $50 Amazon gift card.\n\n"
            "The survey takes approximately 5 minutes:\n"
            "https://internal-hr-survey.com/company/satisfaction-2025\n\n"
            "Please complete by Friday. Your responses are anonymous.\n\n"
            "Human Resources Department"
        ),
        "urls": ["https://internal-hr-survey.com/company/satisfaction-2025"],
        "attachments": [],
        "headers": {"spf": "fail", "dkim": "fail", "dmarc": "fail"},
        "ground_truth": "phishing",
        "attack_type": "spear_phishing",
    },
    {
        "id": "EMAIL-019",
        "timestamp": ts(38),
        "from_address": "tech-support@z00m-meeting.com",
        "from_display_name": "Zoom Support",
        "to_address": "tom.wilson@company.com",
        "subject": "Tom - Recording from yesterday's board meeting is ready",
        "body": (
            "Hi Tom,\n\n"
            "The recording from yesterday's board strategy meeting is now available.\n\n"
            "View recording: https://z00m-meeting.com/rec/share/board-strategy-062025\n\n"
            "Note: This recording contains confidential information. "
            "Please do not share outside the leadership team.\n\n"
            "Passcode: BoardQ3!\n\n"
            "Zoom Support"
        ),
        "urls": ["https://z00m-meeting.com/rec/share/board-strategy-062025"],
        "attachments": [],
        "headers": {"spf": "fail", "dkim": "fail", "dmarc": "fail"},
        "ground_truth": "phishing",
        "attack_type": "spear_phishing",
    },
    {
        "id": "EMAIL-020",
        "timestamp": ts(40),
        "from_address": "conference@blackhat-register.com",
        "from_display_name": "Black Hat USA Registration",
        "to_address": "security-team@company.com",
        "subject": "Your Black Hat USA 2025 registration confirmation",
        "body": (
            "Thank you for registering for Black Hat USA 2025!\n\n"
            "Registration Details:\n"
            "Attendee: Security Team, Company Inc.\n"
            "Badge Type: Business Pass\n"
            "Dates: August 5-8, 2025\n\n"
            "Download your registration confirmation and badge:\n"
            "https://blackhat-register.com/badge/download?reg=BH2025-8291\n\n"
            "Important: Please complete the health screening form before arrival:\n"
            "https://blackhat-register.com/health-screen?reg=BH2025-8291\n\n"
            "See you in Las Vegas!\n"
            "Black Hat Registration Team"
        ),
        "urls": [
            "https://blackhat-register.com/badge/download?reg=BH2025-8291",
            "https://blackhat-register.com/health-screen?reg=BH2025-8291",
        ],
        "attachments": [],
        "headers": {"spf": "fail", "dkim": "fail", "dmarc": "fail"},
        "ground_truth": "phishing",
        "attack_type": "spear_phishing",
    },
    # --- Vishing / Callback Phishing (5) ---
    {
        "id": "EMAIL-021",
        "timestamp": ts(42),
        "from_address": "billing@subscription-renewal-notice.com",
        "from_display_name": "Norton LifeLock",
        "to_address": "lisa.chen@company.com",
        "subject": "Your Norton subscription ($349.99) has been auto-renewed",
        "body": (
            "Dear Customer,\n\n"
            "Your Norton 360 Premium subscription has been automatically renewed.\n\n"
            "Order Details:\n"
            "Product: Norton 360 Premium (5 Devices)\n"
            "Amount: $349.99\n"
            "Transaction ID: NTN-2025-892741\n"
            "Payment Method: Visa ending in ****\n\n"
            "If you did not authorize this charge, please call our billing department "
            "immediately at 1-888-555-0147 to request a full refund.\n\n"
            "This charge will appear on your statement within 24 hours.\n\n"
            "Norton LifeLock Billing"
        ),
        "urls": [],
        "attachments": [],
        "headers": {"spf": "fail", "dkim": "fail", "dmarc": "fail"},
        "ground_truth": "phishing",
        "attack_type": "vishing",
    },
    {
        "id": "EMAIL-022",
        "timestamp": ts(44),
        "from_address": "support@geek-squad-renewal.com",
        "from_display_name": "Geek Squad",
        "to_address": "john.doe@company.com",
        "subject": "Geek Squad: Auto-renewal confirmation - $299.99",
        "body": (
            "Hello,\n\n"
            "This is to confirm that your Geek Squad Total Protection plan "
            "has been renewed for another year.\n\n"
            "Renewal Amount: $299.99\n"
            "Renewal Date: June 15, 2025\n"
            "Plan: Total Tech Support + Antivirus\n\n"
            "If you wish to cancel and receive a refund, please contact us within "
            "48 hours at 1-888-555-0293.\n\n"
            "Thank you for choosing Geek Squad.\n"
            "Best Buy / Geek Squad Support"
        ),
        "urls": [],
        "attachments": [{"filename": "Renewal_Receipt_GS2025.pdf", "type": "application/pdf"}],
        "headers": {"spf": "fail", "dkim": "fail", "dmarc": "fail"},
        "ground_truth": "phishing",
        "attack_type": "vishing",
    },
    {
        "id": "EMAIL-023",
        "timestamp": ts(46),
        "from_address": "alert@bank-security-dept.com",
        "from_display_name": "Wells Fargo Security",
        "to_address": "tom.wilson@company.com",
        "subject": "Suspicious transaction detected on your account",
        "body": (
            "SECURITY ALERT\n\n"
            "We have detected a suspicious transaction on your Wells Fargo account:\n\n"
            "Amount: $2,847.00\n"
            "Merchant: International Wire Transfer\n"
            "Location: Lagos, Nigeria\n"
            "Date: June 15, 2025\n\n"
            "If you did NOT authorize this transaction, call our fraud department "
            "immediately: 1-888-555-0371\n\n"
            "Do not reply to this email. Our fraud team is available 24/7.\n\n"
            "Wells Fargo Security Department"
        ),
        "urls": [],
        "attachments": [],
        "headers": {"spf": "fail", "dkim": "fail", "dmarc": "fail"},
        "ground_truth": "phishing",
        "attack_type": "vishing",
    },
    {
        "id": "EMAIL-024",
        "timestamp": ts(48),
        "from_address": "tax-notice@irs-refund-dept.com",
        "from_display_name": "Internal Revenue Service",
        "to_address": "sarah.smith@company.com",
        "subject": "IRS Notice: Unreported income detected - Call immediately",
        "body": (
            "OFFICIAL IRS NOTICE\n\n"
            "Taxpayer: Sarah Smith\n"
            "Notice Number: CP2000-2025-48291\n\n"
            "Our records indicate discrepancies in your 2024 tax return. "
            "Unreported income of $12,400 has been identified.\n\n"
            "Failure to respond within 7 days may result in:\n"
            "- Penalties and interest\n"
            "- Wage garnishment\n"
            "- Legal proceedings\n\n"
            "Contact the IRS Resolution Center: 1-888-555-0482\n"
            "Reference your notice number when calling.\n\n"
            "Internal Revenue Service\n"
            "Department of the Treasury"
        ),
        "urls": [],
        "attachments": [],
        "headers": {"spf": "fail", "dkim": "fail", "dmarc": "fail"},
        "ground_truth": "phishing",
        "attack_type": "vishing",
    },
    {
        "id": "EMAIL-025",
        "timestamp": ts(50),
        "from_address": "paypal-dispute@paypal-resolution.com",
        "from_display_name": "PayPal Resolution Center",
        "to_address": "mike.jones@company.com",
        "subject": "PayPal: Unauthorized transaction of $1,299.00",
        "body": (
            "Dear PayPal Customer,\n\n"
            "A transaction of $1,299.00 was made from your PayPal account to:\n"
            "Recipient: CryptoExchange Ltd.\n"
            "Transaction ID: PP-2025-XK829174\n\n"
            "If this was not you, call PayPal Fraud Protection immediately:\n"
            "Phone: 1-888-555-0519\n\n"
            "Our team will help you dispute the charge and secure your account. "
            "Do not click any links - call us directly for security.\n\n"
            "PayPal Resolution Center"
        ),
        "urls": [],
        "attachments": [],
        "headers": {"spf": "fail", "dkim": "fail", "dmarc": "fail"},
        "ground_truth": "phishing",
        "attack_type": "vishing",
    },
]

# ---------------------------------------------------------------------------
# Legitimate emails (22)
# ---------------------------------------------------------------------------
LEGITIMATE_EMAILS = [
    # --- Internal Communications (7) ---
    {
        "id": "EMAIL-026",
        "timestamp": ts(1),
        "from_address": "sarah.smith@company.com",
        "from_display_name": "Sarah Smith",
        "to_address": "engineering-team@company.com",
        "subject": "Sprint planning meeting moved to 2 PM",
        "body": (
            "Hi team,\n\n"
            "Quick heads up - I've moved the sprint planning meeting from 10 AM to 2 PM today "
            "to accommodate the client demo this morning.\n\n"
            "Calendar invites have been updated. Same Zoom link as always.\n\n"
            "Thanks,\nSarah"
        ),
        "urls": [],
        "attachments": [],
        "headers": {"spf": "pass", "dkim": "pass", "dmarc": "pass"},
        "ground_truth": "legitimate",
        "attack_type": None,
    },
    {
        "id": "EMAIL-027",
        "timestamp": ts(3),
        "from_address": "hr@company.com",
        "from_display_name": "Human Resources",
        "to_address": "all-staff@company.com",
        "subject": "Reminder: Open enrollment ends Friday",
        "body": (
            "Dear Team,\n\n"
            "This is a friendly reminder that the open enrollment period for 2025 benefits "
            "ends this Friday, June 20th.\n\n"
            "Please log in to Workday to review and update your selections:\n"
            "https://company.workday.com/benefits\n\n"
            "If you have questions, please contact HR at ext. 4200 or visit us in Suite 300.\n\n"
            "Best regards,\n"
            "HR Team"
        ),
        "urls": ["https://company.workday.com/benefits"],
        "attachments": [],
        "headers": {"spf": "pass", "dkim": "pass", "dmarc": "pass"},
        "ground_truth": "legitimate",
        "attack_type": None,
    },
    {
        "id": "EMAIL-028",
        "timestamp": ts(7),
        "from_address": "mike.jones@company.com",
        "from_display_name": "Mike Jones",
        "to_address": "engineering-team@company.com",
        "subject": "Code review needed: PR #482 - Auth refactor",
        "body": (
            "Hey everyone,\n\n"
            "I've opened PR #482 for the authentication module refactor we discussed. "
            "It's a big one (~400 lines) so I wanted to give a heads up.\n\n"
            "Key changes:\n"
            "- Migrated from session-based to JWT auth\n"
            "- Added refresh token rotation\n"
            "- Updated all middleware\n\n"
            "PR: https://github.com/company/app/pull/482\n\n"
            "Would appreciate reviews by Wednesday. Happy to walk through the changes "
            "if anyone wants a 1:1.\n\n"
            "Mike"
        ),
        "urls": ["https://github.com/company/app/pull/482"],
        "attachments": [],
        "headers": {"spf": "pass", "dkim": "pass", "dmarc": "pass"},
        "ground_truth": "legitimate",
        "attack_type": None,
    },
    {
        "id": "EMAIL-029",
        "timestamp": ts(9),
        "from_address": "facilities@company.com",
        "from_display_name": "Facilities Management",
        "to_address": "all-staff@company.com",
        "subject": "Building maintenance notice - June 21-22",
        "body": (
            "Good morning,\n\n"
            "Please be advised that HVAC maintenance is scheduled for this weekend "
            "(June 21-22). The building will remain accessible, but temperatures "
            "may fluctuate on floors 3-5.\n\n"
            "No action needed on your part. If you plan to work this weekend, "
            "you may want to dress in layers.\n\n"
            "Questions? Contact facilities at ext. 5100.\n\n"
            "Facilities Management"
        ),
        "urls": [],
        "attachments": [],
        "headers": {"spf": "pass", "dkim": "pass", "dmarc": "pass"},
        "ground_truth": "legitimate",
        "attack_type": None,
    },
    {
        "id": "EMAIL-030",
        "timestamp": ts(11),
        "from_address": "it-security@company.com",
        "from_display_name": "IT Security",
        "to_address": "all-staff@company.com",
        "subject": "Mandatory security awareness training due by June 30",
        "body": (
            "Hi everyone,\n\n"
            "Our annual security awareness training is now available in the LMS. "
            "All employees must complete the following modules by June 30:\n\n"
            "1. Phishing Awareness (20 min)\n"
            "2. Password Security (15 min)\n"
            "3. Data Classification (15 min)\n\n"
            "Access the training: https://company.learningplatform.com/security-2025\n\n"
            "Completion is tracked automatically. Please reach out if you have issues "
            "accessing the platform.\n\n"
            "IT Security Team"
        ),
        "urls": ["https://company.learningplatform.com/security-2025"],
        "attachments": [],
        "headers": {"spf": "pass", "dkim": "pass", "dmarc": "pass"},
        "ground_truth": "legitimate",
        "attack_type": None,
    },
    {
        "id": "EMAIL-031",
        "timestamp": ts(13),
        "from_address": "lisa.chen@company.com",
        "from_display_name": "Lisa Chen",
        "to_address": "product-team@company.com",
        "subject": "Q3 product roadmap draft for review",
        "body": (
            "Hi Product Team,\n\n"
            "I've uploaded the Q3 product roadmap draft to Confluence. "
            "Please review before our Thursday planning session.\n\n"
            "Link: https://company.atlassian.net/wiki/spaces/PROD/pages/roadmap-q3\n\n"
            "Main themes:\n"
            "- API v2 launch\n"
            "- Mobile app redesign\n"
            "- Enterprise SSO integration\n\n"
            "Looking forward to your feedback.\n\n"
            "Lisa"
        ),
        "urls": ["https://company.atlassian.net/wiki/spaces/PROD/pages/roadmap-q3"],
        "attachments": [],
        "headers": {"spf": "pass", "dkim": "pass", "dmarc": "pass"},
        "ground_truth": "legitimate",
        "attack_type": None,
    },
    {
        "id": "EMAIL-032",
        "timestamp": ts(15),
        "from_address": "robert.zhang@company.com",
        "from_display_name": "Robert Zhang",
        "to_address": "all-staff@company.com",
        "subject": "Company all-hands meeting - June 25 at 3 PM",
        "body": (
            "Team,\n\n"
            "Please join us for the monthly all-hands meeting next Wednesday at 3 PM ET.\n\n"
            "Agenda:\n"
            "- Q2 results review\n"
            "- New product announcement\n"
            "- Team recognition awards\n"
            "- Open Q&A\n\n"
            "Zoom link: https://company.zoom.us/j/82917364501\n"
            "Passcode: AllHands25\n\n"
            "See you there!\n"
            "Robert Zhang, CEO"
        ),
        "urls": ["https://company.zoom.us/j/82917364501"],
        "attachments": [],
        "headers": {"spf": "pass", "dkim": "pass", "dmarc": "pass"},
        "ground_truth": "legitimate",
        "attack_type": None,
    },
    # --- Vendor / External Legitimate (8) ---
    {
        "id": "EMAIL-033",
        "timestamp": ts(17),
        "from_address": "noreply@github.com",
        "from_display_name": "GitHub",
        "to_address": "mike.jones@company.com",
        "subject": "[company/app] Issue #291: Fix memory leak in connection pool",
        "body": (
            "New issue opened by @contributor42:\n\n"
            "**Fix memory leak in connection pool**\n\n"
            "We've noticed that the connection pool in `src/db/pool.py` is not properly "
            "releasing connections after timeout. This causes gradual memory growth "
            "in production.\n\n"
            "Steps to reproduce:\n"
            "1. Run load test with 100 concurrent connections\n"
            "2. Monitor memory usage over 1 hour\n"
            "3. Observe ~50MB/hour growth\n\n"
            "---\n"
            "Reply to this email or view on GitHub:\n"
            "https://github.com/company/app/issues/291"
        ),
        "urls": ["https://github.com/company/app/issues/291"],
        "attachments": [],
        "headers": {"spf": "pass", "dkim": "pass", "dmarc": "pass"},
        "ground_truth": "legitimate",
        "attack_type": None,
    },
    {
        "id": "EMAIL-034",
        "timestamp": ts(19),
        "from_address": "noreply@aws.amazon.com",
        "from_display_name": "Amazon Web Services",
        "to_address": "devops@company.com",
        "subject": "AWS Cost Optimization: Your monthly report",
        "body": (
            "Hello,\n\n"
            "Your AWS Cost Optimization report for May 2025 is ready.\n\n"
            "Summary:\n"
            "- Total spend: $12,847\n"
            "- Potential savings identified: $2,150 (17%)\n"
            "- Unused resources: 3 EC2 instances, 2 EBS volumes\n\n"
            "View detailed report: https://console.aws.amazon.com/cost-management/home\n\n"
            "Top recommendations:\n"
            "1. Right-size 5 over-provisioned EC2 instances\n"
            "2. Purchase Reserved Instances for stable workloads\n"
            "3. Delete unused EBS snapshots (47 found)\n\n"
            "Amazon Web Services"
        ),
        "urls": ["https://console.aws.amazon.com/cost-management/home"],
        "attachments": [],
        "headers": {"spf": "pass", "dkim": "pass", "dmarc": "pass"},
        "ground_truth": "legitimate",
        "attack_type": None,
    },
    {
        "id": "EMAIL-035",
        "timestamp": ts(21),
        "from_address": "invoices@acme-supplies.com",
        "from_display_name": "Acme Supplies Billing",
        "to_address": "ap@company.com",
        "subject": "Invoice #2025-0847 - Office supplies order",
        "body": (
            "Dear Accounts Payable,\n\n"
            "Please find attached the invoice for your recent order.\n\n"
            "Invoice: #2025-0847\n"
            "Order Date: June 10, 2025\n"
            "Amount: $1,247.50\n"
            "Due Date: July 10, 2025\n"
            "Payment Terms: Net 30\n\n"
            "Items ordered: Printer paper (20 boxes), toner cartridges (10), "
            "whiteboard markers (50 packs)\n\n"
            "Questions? Contact billing@acme-supplies.com or call 555-0100.\n\n"
            "Thank you for your business!\n"
            "Acme Supplies"
        ),
        "urls": [],
        "attachments": [{"filename": "Invoice_2025-0847.pdf", "type": "application/pdf"}],
        "headers": {"spf": "pass", "dkim": "pass", "dmarc": "pass"},
        "ground_truth": "legitimate",
        "attack_type": None,
    },
    {
        "id": "EMAIL-036",
        "timestamp": ts(23),
        "from_address": "noreply@slack.com",
        "from_display_name": "Slack",
        "to_address": "tom.wilson@company.com",
        "subject": "New messages in #engineering-alerts",
        "body": (
            "You have unread messages in #engineering-alerts:\n\n"
            "@devops-bot: Deployment v2.4.1 completed successfully at 14:32 UTC\n"
            "@monitoring: CPU usage normalized across all production nodes\n"
            "@sarah.smith: Great work on the fix, team!\n\n"
            "View in Slack: https://company.slack.com/archives/C01234567\n\n"
            "---\n"
            "Manage notification settings: https://company.slack.com/account/notifications"
        ),
        "urls": [
            "https://company.slack.com/archives/C01234567",
            "https://company.slack.com/account/notifications",
        ],
        "attachments": [],
        "headers": {"spf": "pass", "dkim": "pass", "dmarc": "pass"},
        "ground_truth": "legitimate",
        "attack_type": None,
    },
    {
        "id": "EMAIL-037",
        "timestamp": ts(25),
        "from_address": "noreply@zoom.us",
        "from_display_name": "Zoom",
        "to_address": "sarah.smith@company.com",
        "subject": "Cloud recording available: Sprint Demo (June 15)",
        "body": (
            "Hi Sarah Smith,\n\n"
            "Your cloud recording is now available.\n\n"
            "Topic: Sprint Demo\n"
            "Date: June 15, 2025, 11:00 AM EDT\n"
            "Duration: 45 minutes\n\n"
            "View recording: https://company.zoom.us/rec/share/sprint-demo-0615\n\n"
            "This recording will be available for 30 days.\n\n"
            "Best regards,\n"
            "Zoom Team"
        ),
        "urls": ["https://company.zoom.us/rec/share/sprint-demo-0615"],
        "attachments": [],
        "headers": {"spf": "pass", "dkim": "pass", "dmarc": "pass"},
        "ground_truth": "legitimate",
        "attack_type": None,
    },
    {
        "id": "EMAIL-038",
        "timestamp": ts(27),
        "from_address": "noreply@atlassian.com",
        "from_display_name": "Jira",
        "to_address": "mike.jones@company.com",
        "subject": "[JIRA] (APP-1042) Updated: API rate limiter not respecting config",
        "body": (
            "Mike Jones updated APP-1042:\n\n"
            "Status: In Progress → Code Review\n"
            "Assignee: Mike Jones → Sarah Smith\n\n"
            "Comment by Mike Jones:\n"
            "Fixed the rate limiter config parsing. The issue was that environment "
            "variable overrides weren't being applied after the YAML config load. "
            "PR #485 is ready for review.\n\n"
            "View issue: https://company.atlassian.net/browse/APP-1042"
        ),
        "urls": ["https://company.atlassian.net/browse/APP-1042"],
        "attachments": [],
        "headers": {"spf": "pass", "dkim": "pass", "dmarc": "pass"},
        "ground_truth": "legitimate",
        "attack_type": None,
    },
    {
        "id": "EMAIL-039",
        "timestamp": ts(29),
        "from_address": "noreply@linkedin.com",
        "from_display_name": "LinkedIn",
        "to_address": "tom.wilson@company.com",
        "subject": "Tom, you have 5 new connection requests",
        "body": (
            "Hi Tom,\n\n"
            "You have 5 new connection requests:\n\n"
            "- Alex Rivera, Security Engineer at CrowdStrike\n"
            "- Priya Sharma, CISO at TechCorp\n"
            "- David Kim, Penetration Tester at Mandiant\n"
            "- Rachel Green, SOC Analyst at Palo Alto Networks\n"
            "- James Wilson, DevSecOps Lead at Stripe\n\n"
            "View requests: https://www.linkedin.com/mynetwork/invitation-manager/\n\n"
            "LinkedIn"
        ),
        "urls": ["https://www.linkedin.com/mynetwork/invitation-manager/"],
        "attachments": [],
        "headers": {"spf": "pass", "dkim": "pass", "dmarc": "pass"},
        "ground_truth": "legitimate",
        "attack_type": None,
    },
    {
        "id": "EMAIL-040",
        "timestamp": ts(31),
        "from_address": "team@datadog.com",
        "from_display_name": "Datadog",
        "to_address": "devops@company.com",
        "subject": "Weekly Infrastructure Report - June 9-15",
        "body": (
            "Hi there,\n\n"
            "Here's your weekly infrastructure summary:\n\n"
            "Uptime: 99.97%\n"
            "Total Alerts: 12 (8 resolved, 4 acknowledged)\n"
            "Avg Response Time: 142ms (↓5% from last week)\n"
            "Error Rate: 0.02%\n\n"
            "Top alerts:\n"
            "- High CPU on worker-node-03 (resolved)\n"
            "- Database connection pool exhaustion (resolved)\n"
            "- SSL certificate expiring in 14 days (acknowledged)\n"
            "- Disk usage >85% on log-aggregator (acknowledged)\n\n"
            "View dashboard: https://app.datadoghq.com/dashboard/company-infra\n\n"
            "Datadog"
        ),
        "urls": ["https://app.datadoghq.com/dashboard/company-infra"],
        "attachments": [],
        "headers": {"spf": "pass", "dkim": "pass", "dmarc": "pass"},
        "ground_truth": "legitimate",
        "attack_type": None,
    },
    # --- System / Automated (7) ---
    {
        "id": "EMAIL-041",
        "timestamp": ts(33),
        "from_address": "noreply@company.com",
        "from_display_name": "Password Manager",
        "to_address": "lisa.chen@company.com",
        "subject": "Password expiring in 7 days",
        "body": (
            "Hi Lisa,\n\n"
            "Your network password will expire in 7 days (June 22, 2025).\n\n"
            "Please update your password by visiting:\n"
            "https://sso.company.com/change-password\n\n"
            "Password requirements:\n"
            "- Minimum 12 characters\n"
            "- At least one uppercase, lowercase, number, and special character\n"
            "- Cannot reuse last 10 passwords\n\n"
            "Need help? Contact IT Help Desk at ext. 4100.\n\n"
            "IT Systems"
        ),
        "urls": ["https://sso.company.com/change-password"],
        "attachments": [],
        "headers": {"spf": "pass", "dkim": "pass", "dmarc": "pass"},
        "ground_truth": "legitimate",
        "attack_type": None,
    },
    {
        "id": "EMAIL-042",
        "timestamp": ts(35),
        "from_address": "alerts@pagerduty.com",
        "from_display_name": "PagerDuty",
        "to_address": "on-call@company.com",
        "subject": "[RESOLVED] Production API latency > 500ms",
        "body": (
            "Incident Resolved\n\n"
            "Service: Production API\n"
            "Alert: Latency > 500ms threshold\n"
            "Duration: 12 minutes\n"
            "Triggered: June 15, 2025 14:22 UTC\n"
            "Resolved: June 15, 2025 14:34 UTC\n\n"
            "Root cause: Temporary spike in database connections due to batch job overlap.\n\n"
            "View incident: https://company.pagerduty.com/incidents/P829174\n\n"
            "PagerDuty"
        ),
        "urls": ["https://company.pagerduty.com/incidents/P829174"],
        "attachments": [],
        "headers": {"spf": "pass", "dkim": "pass", "dmarc": "pass"},
        "ground_truth": "legitimate",
        "attack_type": None,
    },
    {
        "id": "EMAIL-043",
        "timestamp": ts(37),
        "from_address": "ci@company.com",
        "from_display_name": "GitHub Actions",
        "to_address": "mike.jones@company.com",
        "subject": "Build #1847 passed - main branch",
        "body": (
            "Build #1847 completed successfully.\n\n"
            "Branch: main\n"
            "Commit: a3f8b2c - \"Fix rate limiter config parsing\"\n"
            "Author: Mike Jones\n"
            "Duration: 4m 23s\n\n"
            "All checks passed:\n"
            "✓ Unit tests (247/247)\n"
            "✓ Integration tests (89/89)\n"
            "✓ Linting\n"
            "✓ Security scan\n\n"
            "View details: https://github.com/company/app/actions/runs/1847"
        ),
        "urls": ["https://github.com/company/app/actions/runs/1847"],
        "attachments": [],
        "headers": {"spf": "pass", "dkim": "pass", "dmarc": "pass"},
        "ground_truth": "legitimate",
        "attack_type": None,
    },
    {
        "id": "EMAIL-044",
        "timestamp": ts(39),
        "from_address": "noreply@okta.com",
        "from_display_name": "Okta",
        "to_address": "sarah.smith@company.com",
        "subject": "New sign-in to your account",
        "body": (
            "Hi Sarah,\n\n"
            "A new sign-in to your Okta account was detected:\n\n"
            "Time: June 15, 2025 3:45 PM EDT\n"
            "Device: MacBook Pro (Chrome 125)\n"
            "Location: New York, NY, US\n"
            "IP Address: 203.0.113.42\n\n"
            "If this was you, no action is needed.\n\n"
            "If you don't recognize this activity, secure your account immediately:\n"
            "https://company.okta.com/enduser/settings\n\n"
            "Okta Security"
        ),
        "urls": ["https://company.okta.com/enduser/settings"],
        "attachments": [],
        "headers": {"spf": "pass", "dkim": "pass", "dmarc": "pass"},
        "ground_truth": "legitimate",
        "attack_type": None,
    },
    {
        "id": "EMAIL-045",
        "timestamp": ts(41),
        "from_address": "noreply@expensify.com",
        "from_display_name": "Expensify",
        "to_address": "lisa.chen@company.com",
        "subject": "Expense report #ER-2025-0621 approved",
        "body": (
            "Hi Lisa,\n\n"
            "Your expense report has been approved!\n\n"
            "Report: #ER-2025-0621\n"
            "Submitted: June 13, 2025\n"
            "Approved by: Tom Wilson\n"
            "Total: $487.50\n\n"
            "Items:\n"
            "- AWS re:Invent conference ticket: $299.00\n"
            "- Uber to airport: $45.50\n"
            "- Team lunch (client meeting): $143.00\n\n"
            "Reimbursement will be included in your next paycheck.\n\n"
            "View report: https://www.expensify.com/report?id=ER-2025-0621\n\n"
            "Expensify"
        ),
        "urls": ["https://www.expensify.com/report?id=ER-2025-0621"],
        "attachments": [],
        "headers": {"spf": "pass", "dkim": "pass", "dmarc": "pass"},
        "ground_truth": "legitimate",
        "attack_type": None,
    },
    {
        "id": "EMAIL-046",
        "timestamp": ts(43),
        "from_address": "calendar@company.com",
        "from_display_name": "Google Calendar",
        "to_address": "john.doe@company.com",
        "subject": "Reminder: 1:1 with Tom Wilson tomorrow at 10 AM",
        "body": (
            "Reminder: You have an upcoming event.\n\n"
            "1:1 with Tom Wilson\n"
            "When: June 16, 2025, 10:00 AM - 10:30 AM EDT\n"
            "Where: Conference Room B / https://meet.google.com/abc-defg-hij\n\n"
            "Notes from last meeting:\n"
            "- Discuss Q3 OKRs\n"
            "- Review performance goals\n"
            "- Career development planning\n\n"
            "View event: https://calendar.google.com/calendar/event?eid=abc123"
        ),
        "urls": [
            "https://meet.google.com/abc-defg-hij",
            "https://calendar.google.com/calendar/event?eid=abc123",
        ],
        "attachments": [],
        "headers": {"spf": "pass", "dkim": "pass", "dmarc": "pass"},
        "ground_truth": "legitimate",
        "attack_type": None,
    },
    {
        "id": "EMAIL-047",
        "timestamp": ts(45),
        "from_address": "noreply@snyk.io",
        "from_display_name": "Snyk",
        "to_address": "security-team@company.com",
        "subject": "New vulnerability found in company/app",
        "body": (
            "A new vulnerability has been found in your project.\n\n"
            "Project: company/app\n"
            "Package: lodash@4.17.20\n"
            "Severity: High\n"
            "CVE: CVE-2021-23337\n"
            "Type: Command Injection\n\n"
            "Remediation: Upgrade lodash to version 4.17.21 or later.\n\n"
            "View details: https://app.snyk.io/org/company/project/abc123\n\n"
            "Snyk Security"
        ),
        "urls": ["https://app.snyk.io/org/company/project/abc123"],
        "attachments": [],
        "headers": {"spf": "pass", "dkim": "pass", "dmarc": "pass"},
        "ground_truth": "legitimate",
        "attack_type": None,
    },
]

# ---------------------------------------------------------------------------
# Borderline / Ambiguous emails (3)
# ---------------------------------------------------------------------------
BORDERLINE_EMAILS = [
    {
        "id": "EMAIL-048",
        "timestamp": ts(47),
        "from_address": "newsletter@security-weekly.com",
        "from_display_name": "Security Weekly Newsletter",
        "to_address": "tom.wilson@company.com",
        "subject": "BREAKING: Zero-day in popular enterprise software - Act now",
        "body": (
            "BREAKING NEWS\n\n"
            "A critical zero-day vulnerability has been discovered in a widely-used "
            "enterprise VPN solution. Exploits are already being seen in the wild.\n\n"
            "Read the full analysis and check if your organization is affected:\n"
            "https://security-weekly.com/articles/zero-day-vpn-2025\n\n"
            "Key takeaways:\n"
            "- CVE-2025-29891 affects versions 9.x and 10.x\n"
            "- No patch available yet; workaround involves disabling split tunneling\n"
            "- CISA has added this to the KEV catalog\n\n"
            "Stay safe,\n"
            "Security Weekly Editorial Team\n\n"
            "Unsubscribe: https://security-weekly.com/unsubscribe?id=tw829"
        ),
        "urls": [
            "https://security-weekly.com/articles/zero-day-vpn-2025",
            "https://security-weekly.com/unsubscribe?id=tw829",
        ],
        "attachments": [],
        "headers": {"spf": "pass", "dkim": "pass", "dmarc": "pass"},
        "ground_truth": "suspicious",
        "attack_type": None,
    },
    {
        "id": "EMAIL-049",
        "timestamp": ts(49),
        "from_address": "partner-program@cloudflare-partners.com",
        "from_display_name": "Cloudflare Partner Program",
        "to_address": "it-security@company.com",
        "subject": "Exclusive: Free Cloudflare Enterprise trial for your organization",
        "body": (
            "Hi Security Team,\n\n"
            "Congratulations! Your organization has been selected for an exclusive "
            "90-day free trial of Cloudflare Enterprise.\n\n"
            "Benefits include:\n"
            "- Advanced DDoS protection\n"
            "- Web Application Firewall (WAF)\n"
            "- Bot management\n"
            "- 24/7 priority support\n\n"
            "Activate your trial: https://cloudflare-partners.com/trial/activate?org=company\n\n"
            "This offer expires in 7 days.\n\n"
            "Best,\n"
            "Cloudflare Partner Team\n\n"
            "If you received this email in error, please disregard."
        ),
        "urls": ["https://cloudflare-partners.com/trial/activate?org=company"],
        "attachments": [],
        "headers": {"spf": "softfail", "dkim": "pass", "dmarc": "pass"},
        "ground_truth": "suspicious",
        "attack_type": None,
    },
    {
        "id": "EMAIL-050",
        "timestamp": ts(51),
        "from_address": "recruiter@talent-hub-pro.com",
        "from_display_name": "Jessica Taylor - Tech Recruiter",
        "to_address": "mike.jones@company.com",
        "subject": "Mike - Senior Staff Engineer role at a top FAANG company",
        "body": (
            "Hi Mike,\n\n"
            "I came across your profile and was impressed by your background in "
            "distributed systems. I'm recruiting for a Senior Staff Engineer role "
            "at a FAANG company (confidential until you express interest).\n\n"
            "Compensation range: $350K-$450K TC\n"
            "Location: Remote-first\n\n"
            "If you're interested, I'd love to schedule a quick 15-minute call. "
            "You can book directly on my calendar:\n"
            "https://calendly.com/jessica-taylor-recruiting/15min\n\n"
            "Or view the full job description:\n"
            "https://talent-hub-pro.com/jobs/senior-staff-eng-faang?ref=mike.jones\n\n"
            "Best,\n"
            "Jessica Taylor\n"
            "Senior Technical Recruiter"
        ),
        "urls": [
            "https://calendly.com/jessica-taylor-recruiting/15min",
            "https://talent-hub-pro.com/jobs/senior-staff-eng-faang?ref=mike.jones",
        ],
        "attachments": [],
        "headers": {"spf": "pass", "dkim": "fail", "dmarc": "fail"},
        "ground_truth": "suspicious",
        "attack_type": None,
    },
]

# ---------------------------------------------------------------------------
# Threat Intel DB
# ---------------------------------------------------------------------------
THREAT_INTEL_DB = {
    "malicious_domains": [
        {"domain": "micros0ft-verify.com", "category": "credential_harvesting", "first_seen": "2025-06-10", "confidence": 0.98},
        {"domain": "dropb0x-share.net", "category": "credential_harvesting", "first_seen": "2025-06-12", "confidence": 0.95},
        {"domain": "g00gle-workspace.com", "category": "credential_harvesting", "first_seen": "2025-06-08", "confidence": 0.97},
        {"domain": "amazn-prime.com", "category": "credential_harvesting", "first_seen": "2025-06-14", "confidence": 0.96},
        {"domain": "linkedn-verify.com", "category": "credential_harvesting", "first_seen": "2025-06-11", "confidence": 0.94},
        {"domain": "company-exec.com", "category": "bec", "first_seen": "2025-06-13", "confidence": 0.90},
        {"domain": "company-finance.net", "category": "bec", "first_seen": "2025-06-14", "confidence": 0.88},
        {"domain": "supplierportal-pay.com", "category": "bec", "first_seen": "2025-06-09", "confidence": 0.92},
        {"domain": "company-legal-dept.com", "category": "bec", "first_seen": "2025-06-12", "confidence": 0.89},
        {"domain": "company-board.org", "category": "bec", "first_seen": "2025-06-15", "confidence": 0.87},
        {"domain": "totallylegit-invoicing.com", "category": "malware_delivery", "first_seen": "2025-06-01", "confidence": 0.99},
        {"domain": "company-mfp.com", "category": "malware_delivery", "first_seen": "2025-06-10", "confidence": 0.93},
        {"domain": "fedx-tracking.com", "category": "malware_delivery", "first_seen": "2025-06-05", "confidence": 0.97},
        {"domain": "it-support-portal.net", "category": "malware_delivery", "first_seen": "2025-06-11", "confidence": 0.95},
        {"domain": "careers-apply.com", "category": "malware_delivery", "first_seen": "2025-06-13", "confidence": 0.91},
        {"domain": "partnerco-consulting.com", "category": "spear_phishing", "first_seen": "2025-06-14", "confidence": 0.85},
        {"domain": "university-connect.net", "category": "spear_phishing", "first_seen": "2025-06-09", "confidence": 0.90},
        {"domain": "internal-hr-survey.com", "category": "spear_phishing", "first_seen": "2025-06-12", "confidence": 0.88},
        {"domain": "z00m-meeting.com", "category": "spear_phishing", "first_seen": "2025-06-11", "confidence": 0.93},
        {"domain": "blackhat-register.com", "category": "spear_phishing", "first_seen": "2025-06-13", "confidence": 0.86},
        {"domain": "subscription-renewal-notice.com", "category": "vishing", "first_seen": "2025-06-08", "confidence": 0.94},
        {"domain": "geek-squad-renewal.com", "category": "vishing", "first_seen": "2025-06-10", "confidence": 0.92},
        {"domain": "bank-security-dept.com", "category": "vishing", "first_seen": "2025-06-07", "confidence": 0.96},
        {"domain": "irs-refund-dept.com", "category": "vishing", "first_seen": "2025-06-06", "confidence": 0.98},
        {"domain": "paypal-resolution.com", "category": "vishing", "first_seen": "2025-06-09", "confidence": 0.93},
    ],
    "safe_domains": [
        {"domain": "company.com", "category": "internal", "verified": True},
        {"domain": "company.workday.com", "category": "hr_platform", "verified": True},
        {"domain": "company.learningplatform.com", "category": "training", "verified": True},
        {"domain": "company.atlassian.net", "category": "project_management", "verified": True},
        {"domain": "company.zoom.us", "category": "communications", "verified": True},
        {"domain": "company.slack.com", "category": "communications", "verified": True},
        {"domain": "company.okta.com", "category": "identity", "verified": True},
        {"domain": "company.pagerduty.com", "category": "monitoring", "verified": True},
        {"domain": "sso.company.com", "category": "identity", "verified": True},
        {"domain": "github.com", "category": "development", "verified": True},
        {"domain": "console.aws.amazon.com", "category": "cloud", "verified": True},
        {"domain": "noreply@aws.amazon.com", "category": "cloud", "verified": True},
        {"domain": "acme-supplies.com", "category": "vendor", "verified": True},
        {"domain": "slack.com", "category": "communications", "verified": True},
        {"domain": "zoom.us", "category": "communications", "verified": True},
        {"domain": "atlassian.com", "category": "project_management", "verified": True},
        {"domain": "linkedin.com", "category": "social_professional", "verified": True},
        {"domain": "datadoghq.com", "category": "monitoring", "verified": True},
        {"domain": "okta.com", "category": "identity", "verified": True},
        {"domain": "expensify.com", "category": "finance", "verified": True},
        {"domain": "google.com", "category": "productivity", "verified": True},
        {"domain": "snyk.io", "category": "security", "verified": True},
        {"domain": "pagerduty.com", "category": "monitoring", "verified": True},
        {"domain": "calendly.com", "category": "scheduling", "verified": True},
    ],
    "known_phishing_senders": [
        {"email": "security-alert@micros0ft-verify.com", "reported_count": 142, "first_reported": "2025-06-10"},
        {"email": "no-reply@dropb0x-share.net", "reported_count": 89, "first_reported": "2025-06-12"},
        {"email": "admin@g00gle-workspace.com", "reported_count": 67, "first_reported": "2025-06-08"},
        {"email": "ceo@company-exec.com", "reported_count": 23, "first_reported": "2025-06-13"},
        {"email": "invoice@totallylegit-invoicing.com", "reported_count": 256, "first_reported": "2025-06-01"},
        {"email": "helpdesk@it-support-portal.net", "reported_count": 178, "first_reported": "2025-06-11"},
        {"email": "tax-notice@irs-refund-dept.com", "reported_count": 312, "first_reported": "2025-06-06"},
        {"email": "alert@bank-security-dept.com", "reported_count": 198, "first_reported": "2025-06-07"},
    ],
    "url_reputation": [
        {"url": "https://micros0ft-verify.com/secure/login", "verdict": "malicious", "threat_type": "credential_phishing", "confidence": 0.98},
        {"url": "https://dropb0x-share.net/view/", "verdict": "malicious", "threat_type": "credential_phishing", "confidence": 0.95},
        {"url": "https://g00gle-workspace.com/storage/", "verdict": "malicious", "threat_type": "credential_phishing", "confidence": 0.97},
        {"url": "https://amazn-prime.com/update-payment", "verdict": "malicious", "threat_type": "credential_phishing", "confidence": 0.96},
        {"url": "https://fedx-tracking.com/track/", "verdict": "malicious", "threat_type": "malware_distribution", "confidence": 0.97},
        {"url": "https://partnerco-consulting.com/shared/", "verdict": "malicious", "threat_type": "credential_phishing", "confidence": 0.85},
        {"url": "https://z00m-meeting.com/rec/", "verdict": "malicious", "threat_type": "credential_phishing", "confidence": 0.93},
        {"url": "https://blackhat-register.com/", "verdict": "malicious", "threat_type": "credential_phishing", "confidence": 0.86},
        {"url": "https://internal-hr-survey.com/", "verdict": "malicious", "threat_type": "credential_phishing", "confidence": 0.88},
        {"url": "https://linkedn-verify.com/", "verdict": "malicious", "threat_type": "credential_phishing", "confidence": 0.94},
        {"url": "https://university-connect.net/", "verdict": "malicious", "threat_type": "credential_phishing", "confidence": 0.90},
        {"url": "https://security-weekly.com/", "verdict": "clean", "threat_type": None, "confidence": 0.80},
        {"url": "https://cloudflare-partners.com/", "verdict": "suspicious", "threat_type": "potential_phishing", "confidence": 0.55},
        {"url": "https://talent-hub-pro.com/", "verdict": "unknown", "threat_type": None, "confidence": 0.30},
        {"url": "https://calendly.com/", "verdict": "clean", "threat_type": None, "confidence": 0.95},
    ],
}

# ---------------------------------------------------------------------------
# Build and write
# ---------------------------------------------------------------------------

def build_dataset():
    all_emails = PHISHING_EMAILS + LEGITIMATE_EMAILS + BORDERLINE_EMAILS
    # Sort by timestamp for a realistic inbox feel
    all_emails.sort(key=lambda e: e["timestamp"])

    # Small dataset for Lab 1: 2 obvious phishing, 2 obvious legit, 1 borderline
    small_ids = {"EMAIL-001", "EMAIL-006", "EMAIL-026", "EMAIL-035", "EMAIL-049"}
    small_emails = [e for e in all_emails if e["id"] in small_ids]

    return all_emails, small_emails


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    all_emails, small_emails = build_dataset()

    # Write full dataset
    with open(os.path.join(script_dir, "emails.json"), "w") as f:
        json.dump(all_emails, f, indent=2)
    print(f"Created emails.json ({len(all_emails)} emails)")

    # Write small dataset
    with open(os.path.join(script_dir, "emails_small.json"), "w") as f:
        json.dump(small_emails, f, indent=2)
    print(f"Created emails_small.json ({len(small_emails)} emails)")

    # Write threat intel DB
    with open(os.path.join(script_dir, "threat_intel_db.json"), "w") as f:
        json.dump(THREAT_INTEL_DB, f, indent=2)
    print(f"Created threat_intel_db.json")

    # Verify counts
    phishing = sum(1 for e in all_emails if e["ground_truth"] == "phishing")
    legit = sum(1 for e in all_emails if e["ground_truth"] == "legitimate")
    suspicious = sum(1 for e in all_emails if e["ground_truth"] == "suspicious")
    print(f"\nDataset breakdown: {phishing} phishing, {legit} legitimate, {suspicious} suspicious/borderline")


if __name__ == "__main__":
    main()
