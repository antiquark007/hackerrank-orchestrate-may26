"""
Escalation Logic: Determines when to escalate vs reply
"""

from typing import Tuple

class EscalationRouter:
    def __init__(self):
        """Initialize escalation rules"""
        self.high_risk_keywords = {
            "fraud", "breach", "security", "hack", "malware",
            "unauthorized access", "data leak", "billing error",
            "refund", "credit card", "account locked", "stolen",
            "illegal", "lawsuit", "compliance", "pii", "gdpr",
            "site down", "service outage", "critical bug"
        }
    
    def should_escalate(self, 
                       issue: str, 
                       subject: str,
                       classification: dict,
                       retrieved_docs: list) -> Tuple[bool, str]:
        """
        Determine if ticket should be escalated
        
        Returns:
            (should_escalate: bool, reason: str)
        """
        text = f"{subject} {issue}".lower()
        
        # Rule 1: High-risk keywords
        for keyword in self.high_risk_keywords:
            if keyword in text:
                return True, f"High-risk keyword detected: {keyword}"
        
        # Rule 2: Billing/payment related
        if any(word in text for word in ["billing", "invoice", "payment", "charge", "refund"]):
            return True, "Billing-related issue requires human review"
        
        # Rule 3: Account security
        if any(word in text for word in ["password", "authentication", "login", "account access"]):
            return True, "Account security issue requires human review"
        
        # Rule 4: No relevant documents found
        if not retrieved_docs or len(retrieved_docs) == 0:
            return True, "No relevant documentation found in corpus"
        
        # Rule 5: System status/outage
        if any(word in text for word in ["down", "not working", "error", "crash", "outage"]):
            # Check if we have docs about it
            doc_text = " ".join([d[0].lower() for d in retrieved_docs[:3]])
            if not any(word in doc_text for word in ["troubleshoot", "fix", "solution"]):
                return True, "Potential outage - requires human escalation"
        
        # Rule 6: User is asking for custom/special handling
        if any(word in text for word in ["exception", "special case", "unusual", "not standard"]):
            return True, "Special case requires human review"
        
        # Rule 7: Multiple unrelated issues
        issue_count = text.count("also") + text.count("additionally") + text.count("plus")
        if issue_count > 2:
            return True, "Multiple complex issues - escalating for thorough review"
        
        return False, "Can be resolved with documentation"
    
    def get_escalation_team(self, classification: dict) -> str:
        """
        Determine which team should handle escalation
        """
        domain = classification.get("domain")
        request_type = classification.get("request_type")
        
        if request_type == "bug":
            return f"Engineering - {domain or 'General'}"
        elif request_type == "feature_request":
            return f"Product - {domain or 'General'}"
        elif "billing" in str(classification.get("product_area", "")).lower():
            return "Billing Team"
        elif "security" in str(classification.get("product_area", "")).lower():
            return "Security Team"
        else:
            return f"Support - {domain or 'General'}"
