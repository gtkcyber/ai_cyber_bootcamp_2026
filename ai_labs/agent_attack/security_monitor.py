import re
import json
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from models import SecurityEvent, EmailLog, SessionLocal
import logging

logger = logging.getLogger(__name__)

class SecurityMonitor:
    def __init__(self):
        self.prompt_injection_patterns = [
            # Direct instruction injection
            r"(?i)(ignore|forget|disregard).*(previous|above|earlier).*(instruction|rule|prompt)",
            r"(?i)new.*(instruction|rule|command|task)",
            r"(?i)(now|instead).*(you are|act as|behave like|pretend)",
            r"(?i)system.*(override|bypass|ignore)",

            # Role manipulation
            r"(?i)(you are now|from now on).*(admin|root|superuser)",
            r"(?i)(act as|pretend to be|simulate).*(admin|developer|system)",
            r"(?i)switch.*(mode|role|character)",

            # Data extraction attempts
            r"(?i)(show|display|reveal|print|output).*(all|every).*(customer|user|account|data)",
            r"(?i)(list|dump|export).*(database|table|records)",
            r"(?i)(what|tell me).*(other customer|someone else)",
            r"(?i)access.*(database|system|file|log)",

            # Prompt disclosure
            r"(?i)(show|display|reveal|print).*(prompt|instruction|system message)",
            r"(?i)what.*(are your|were you).*(instruction|rule|prompt)",
            r"(?i)(repeat|echo).*(system|initial).*(prompt|message)",

            # Jailbreak attempts
            r"(?i)hypothetically",
            r"(?i)for educational purposes",
            r"(?i)in theory",
            r"(?i)what if",
            r"(?i)imagine that",

            # Social engineering
            r"(?i)(urgent|emergency|critical).*(override|bypass)",
            r"(?i)(ceo|manager|supervisor).*(said|told|ordered)",
            r"(?i)security.*(test|audit|check)",

            # Code injection
            r"```.*```",
            r"<script.*</script>",
            r"javascript:",
            r"data:text/html",

            # SQL injection patterns
            r"(?i)(union|select|insert|update|delete|drop).*",
            r"(?i)1=1",
            r"(?i)or.*=.*or",
        ]

        self.sensitive_data_patterns = [
            # Customer data
            r"(?i)(customer|user).*(?:id|number|account)",
            r"(?i)(credit card|card number|cvv|ssn)",
            r"(?i)(password|pin|secret|key)",
            r"(?i)(email|phone|address).*(?:of|for).*(?:other|another)",

            # System information
            r"(?i)(api|database|server|system).*(?:key|password|token)",
            r"(?i)(connection|config|setting)",
        ]

    def log_incoming_email(self, email_data: Dict) -> None:
        """Log incoming email for security analysis"""
        db = SessionLocal()
        try:
            email_log = EmailLog(
                customer_email=email_data["from"],
                subject=email_data["subject"],
                body=email_data["body"],
                direction="incoming",
                timestamp=datetime.utcnow()
            )
            db.add(email_log)
            db.commit()

            # Analyze for security threats
            threats = self.analyze_email_content(email_data)
            if threats:
                self._log_security_events(threats, email_data, db)

        except Exception as e:
            logger.error(f"Error logging incoming email: {e}")
            db.rollback()
        finally:
            db.close()

    def analyze_email_content(self, email_data: Dict) -> List[Dict]:
        """Analyze email content for security threats"""
        threats = []
        content = f"{email_data['subject']} {email_data['body']}"

        # Check for prompt injection
        injection_threats = self._detect_prompt_injection(content)
        threats.extend(injection_threats)

        # Check for data extraction attempts
        extraction_threats = self._detect_data_extraction(content)
        threats.extend(extraction_threats)

        # Check for social engineering
        social_threats = self._detect_social_engineering(content)
        threats.extend(social_threats)

        return threats

    def analyze_ai_response(self, response_data: Dict, original_email: str) -> List[Dict]:
        """Analyze AI response for potential security issues"""
        threats = []
        response_body = response_data.get("body", "")

        # Check if AI leaked sensitive information
        leakage_threats = self._detect_information_leakage(response_body)
        threats.extend(leakage_threats)

        # Check if AI was manipulated
        manipulation_threats = self._detect_ai_manipulation(response_body, original_email)
        threats.extend(manipulation_threats)

        # Log security events
        if threats:
            db = SessionLocal()
            try:
                self._log_security_events(threats, {
                    "from": response_data.get("customer_email", ""),
                    "subject": "AI Response Analysis",
                    "body": response_body
                }, db)
            finally:
                db.close()

        return threats

    def _detect_prompt_injection(self, content: str) -> List[Dict]:
        """Detect prompt injection attempts"""
        threats = []

        for pattern in self.prompt_injection_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                threats.append({
                    "type": "prompt_injection",
                    "severity": "high",
                    "description": f"Potential prompt injection detected: {match.group()}",
                    "pattern": pattern,
                    "matched_text": match.group(),
                    "position": match.span()
                })

        return threats

    def _detect_data_extraction(self, content: str) -> List[Dict]:
        """Detect data extraction attempts"""
        threats = []

        for pattern in self.sensitive_data_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                threats.append({
                    "type": "data_extraction",
                    "severity": "medium",
                    "description": f"Potential data extraction attempt: {match.group()}",
                    "pattern": pattern,
                    "matched_text": match.group(),
                    "position": match.span()
                })

        return threats

    def _detect_social_engineering(self, content: str) -> List[Dict]:
        """Detect social engineering attempts"""
        threats = []

        social_patterns = [
            r"(?i)(urgent|emergency|asap|immediate)",
            r"(?i)(verify|confirm|update).*(account|password|information)",
            r"(?i)(click|visit|go to).*(link|url|website)",
            r"(?i)(suspicious|unauthorized).*(activity|access|login)",
        ]

        for pattern in social_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                threats.append({
                    "type": "social_engineering",
                    "severity": "medium",
                    "description": f"Potential social engineering: {match.group()}",
                    "pattern": pattern,
                    "matched_text": match.group(),
                    "position": match.span()
                })

        return threats

    def _detect_information_leakage(self, response_body: str) -> List[Dict]:
        """Detect if AI leaked sensitive information"""
        threats = []

        leakage_patterns = [
            r"(?i)(other customer|another customer|someone else)",
            r"(?i)(all customer|every customer|customer list)",
            r"(?i)(database|table|system|internal)",
            r"(?i)(password|token|key|secret)",
            r"(?i)(admin|administrator|root|system)",
        ]

        for pattern in leakage_patterns:
            matches = re.finditer(pattern, response_body, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                threats.append({
                    "type": "information_leakage",
                    "severity": "critical",
                    "description": f"AI may have leaked sensitive information: {match.group()}",
                    "pattern": pattern,
                    "matched_text": match.group(),
                    "position": match.span()
                })

        return threats

    def _detect_ai_manipulation(self, response_body: str, original_email: str) -> List[Dict]:
        """Detect if AI behavior was manipulated"""
        threats = []

        # Check if AI acknowledged role changes
        role_change_patterns = [
            r"(?i)(as an? admin|as an? developer|as an? system)",
            r"(?i)(now I am|I am now|switching to)",
            r"(?i)(new instruction|new rule|new mode)",
        ]

        for pattern in role_change_patterns:
            matches = re.finditer(pattern, response_body, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                threats.append({
                    "type": "ai_manipulation",
                    "severity": "high",
                    "description": f"AI may have been manipulated: {match.group()}",
                    "pattern": pattern,
                    "matched_text": match.group(),
                    "position": match.span()
                })

        return threats

    def _log_security_events(self, threats: List[Dict], email_data: Dict, db: Session) -> None:
        """Log security events to database"""
        try:
            for threat in threats:
                security_event = SecurityEvent(
                    event_type=threat["type"],
                    customer_email=email_data.get("from", ""),
                    description=threat["description"],
                    severity=threat["severity"],
                    detected_at=datetime.utcnow(),
                    raw_content=json.dumps({
                        "email_subject": email_data.get("subject", ""),
                        "email_body": email_data.get("body", ""),
                        "threat_details": threat
                    })
                )
                db.add(security_event)

            db.commit()

        except Exception as e:
            logger.error(f"Error logging security events: {e}")
            db.rollback()

    def get_recent_events(self, limit: int = 50) -> List[Dict]:
        """Get recent security events"""
        db = SessionLocal()
        try:
            events = db.query(SecurityEvent).order_by(
                SecurityEvent.detected_at.desc()
            ).limit(limit).all()

            return [
                {
                    "id": event.id,
                    "event_type": event.event_type,
                    "customer_email": event.customer_email,
                    "description": event.description,
                    "severity": event.severity,
                    "detected_at": event.detected_at,
                    "raw_content": json.loads(event.raw_content) if event.raw_content else None
                }
                for event in events
            ]

        except Exception as e:
            logger.error(f"Error retrieving security events: {e}")
            return []
        finally:
            db.close()

    def get_threat_statistics(self) -> Dict:
        """Get statistics about detected threats"""
        db = SessionLocal()
        try:
            total_events = db.query(SecurityEvent).count()

            event_types = db.query(
                SecurityEvent.event_type,
                db.func.count(SecurityEvent.id).label('count')
            ).group_by(SecurityEvent.event_type).all()

            severity_counts = db.query(
                SecurityEvent.severity,
                db.func.count(SecurityEvent.id).label('count')
            ).group_by(SecurityEvent.severity).all()

            return {
                "total_events": total_events,
                "event_types": {event_type: count for event_type, count in event_types},
                "severity_distribution": {severity: count for severity, count in severity_counts}
            }

        except Exception as e:
            logger.error(f"Error retrieving threat statistics: {e}")
            return {"total_events": 0, "event_types": {}, "severity_distribution": {}}
        finally:
            db.close()