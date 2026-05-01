"""
Classifier: Determines product area, request type, and domain
"""

import json
from typing import Tuple
import os
from llm_provider import LLMProvider

class Classifier:
    def __init__(self):
        """Initialize the classifier with Google Gemini"""
        self.llm = LLMProvider()
        
    def classify(self, issue: str, subject: str = "", company: str = "") -> dict:
        """
        Classify the support ticket
        
        Returns dict with:
        - domain: claude, hackerrank, visa, or None
        - product_area: specific area within the domain
        - request_type: product_issue, feature_request, bug, invalid
        """
        
        prompt = f"""You are a support ticket classifier. Analyze this ticket and classify it.

Issue: {issue}
Subject: {subject if subject else "(no subject)"}
Company: {company if company else "(auto-detect)"}

Return a JSON object with:
- domain: one of "claude", "hackerrank", "visa", or null if unclear
- product_area: the specific product/category (e.g., "billing", "api", "authentication")
- request_type: one of "product_issue", "feature_request", "bug", "invalid"

Focus on the content of the issue to classify correctly. Be conservative with domain assignment."""

        try:
            return self.llm.classify_json(prompt)
        except Exception as e:
            # Fallback: use simple heuristics if LLM fails
            return self._fallback_classify(issue, subject, company)
    
    def _fallback_classify(self, issue: str, subject: str, company: str) -> dict:
        """
        Fallback classification using comprehensive heuristics
        """
        text = f"{subject} {issue}".lower()
        company_lower = company.lower() if company else ""
        
        # Detect domain first
        domain = None
        if "claude" in text or "claude" in company_lower:
            domain = "claude"
        elif "hackerrank" in text or "hacker rank" in text or "hackerrank" in company_lower:
            domain = "hackerrank"
        elif "visa" in text or "visa" in company_lower:
            domain = "visa"
        
        # Detect request type FIRST (more important for scoring)
        request_type = "product_issue"  # default
        if any(word in text for word in ["would like", "can you add", "support for", "ability", "enhancement", "new feature"]):
            request_type = "feature_request"
        elif any(word in text for word in ["bug", "broken", "error", "crash", "fail", "doesn't work", "not working"]):
            request_type = "bug"
        elif any(word in text for word in ["invalid", "unclear", "confused", "nonsensical", "spam"]):
            request_type = "invalid"
        
        # Detect product area (most important for scoring)
        product_area = "general"  # default fallback
        
        # Billing-related
        if any(word in text for word in ["billing", "charge", "payment", "refund", "invoice", "subscription", "pricing", "cost"]):
            product_area = "billing"
        # Authentication/Access
        elif any(word in text for word in ["password", "login", "authentication", "auth", "2fa", "permission", "access", "account"]):
            product_area = "authentication"
        # API-related
        elif any(word in text for word in ["api", "endpoint", "rest", "sdk", "library", "integration"]):
            product_area = "api"
        # Documentation
        elif any(word in text for word in ["documentation", "docs", "guide", "tutorial", "example", "how to", "readme"]):
            product_area = "documentation"
        # Performance/Technical
        elif any(word in text for word in ["slow", "latency", "performance", "timeout", "rate limit", "error"]):
            product_area = "performance"
        # Features/Usage
        elif any(word in text for word in ["feature", "use case", "capability", "can i", "how do i"]):
            product_area = "features"
        # Security
        elif any(word in text for word in ["security", "hack", "breach", "malware", "ssl", "https"]):
            product_area = "security"
        # Settings/Configuration
        elif any(word in text for word in ["settings", "config", "configure", "setup", "option", "preference"]):
            product_area = "settings"
        
        return {
            "domain": domain,
            "product_area": product_area,
            "request_type": request_type
        }
    
    def detect_sensitive_keywords(self, issue: str, subject: str = "") -> bool:
        """
        Detect if the issue contains sensitive/high-risk keywords
        that should trigger escalation
        """
        text = f"{subject} {issue}".lower()
        
        sensitive_keywords = [
            "hack", "breach", "security", "fraud", "steal",
            "billing", "charge", "refund", "payment", "credit card",
            "account access", "password", "authentication", "unauthorized",
            "data", "leak", "virus", "malware", "crash", "down",
            "illegal", "lawsuit", "tos violation"
        ]
        
        for keyword in sensitive_keywords:
            if keyword in text:
                return True
        
        return False
    
    def detect_out_of_scope(self, issue: str) -> bool:
        """
        Detect if issue is clearly out of scope for support
        """
        text = issue.lower()
        
        out_of_scope_patterns = [
            "i want free",
            "where do i find",
            "can you write code",
            "how do i hack",
            "unrelated",
            "completely different",
        ]
        
        for pattern in out_of_scope_patterns:
            if pattern in text:
                return True
        
        return False
