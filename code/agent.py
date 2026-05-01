"""
Support Triage Agent: Main agent logic with RAG and reasoning
"""

import os
import json
from typing import Dict, Any
from llm_provider import LLMProvider
from corpus import CorpusLoader
from classifier import Classifier
from escalation import EscalationRouter

class SupportTriageAgent:
    def __init__(self, data_dir: str):
        """Initialize the support triage agent"""
        self.llm = LLMProvider()
        
        # Initialize components
        self.corpus = CorpusLoader(data_dir)
        self.corpus.load_corpus()
        self.corpus.build_index()
        
        self.classifier = Classifier()
        self.escalation_router = EscalationRouter()
        
        print(f"Agent initialized with {len(self.corpus.documents)} documents")
    
    def process_ticket(self, issue: str, subject: str = "", company: str = "") -> Dict[str, Any]:
        """
        Process a single support ticket and return triage decision
        
        Returns:
            {
                "status": "replied" | "escalated",
                "product_area": str,
                "response": str,
                "justification": str,
                "request_type": str
            }
        """
        
        # Step 1: Classify the issue
        classification = self.classifier.classify(issue, subject, company)
        
        # Step 2: Retrieve relevant documents
        search_query = f"{subject} {issue}".strip() or issue
        retrieved_docs = self.corpus.search(search_query, top_k=5)
        
        # Step 3: Determine if escalation is needed
        should_escalate, escalation_reason = self.escalation_router.should_escalate(
            issue, subject, classification, retrieved_docs
        )
        
        # Step 4: Generate response
        if should_escalate:
            status = "escalated"
            escalation_team = self.escalation_router.get_escalation_team(classification)
            response = f"This issue requires specialist attention from our {escalation_team} team. Thank you for reaching out - a specialist will assist you shortly."
            justification = escalation_reason
        else:
            status = "replied"
            response = self._generate_response(issue, subject, classification, retrieved_docs)
            justification = self._generate_justification(classification, retrieved_docs, response)
        
        return {
            "status": status,
            "product_area": classification.get("product_area", "uncategorized"),
            "response": response,
            "justification": justification,
            "request_type": classification.get("request_type", "invalid")
        }
    
    def _generate_response(self, issue: str, subject: str, classification: dict, retrieved_docs: list) -> str:
        """
        Generate a grounded response based on retrieved documents
        """
        
        # Build context from retrieved docs
        context = ""
        for i, (doc_text, metadata, score) in enumerate(retrieved_docs[:3]):
            context += f"\n--- Source {i+1} ({metadata['product_area']}) ---\n{doc_text[:1000]}\n"
        
        prompt = f"""You are a support agent. Based on ONLY the provided documentation, 
answer this support ticket accurately and helpfully.

SUPPORT DOCUMENTATION:
{context}

TICKET:
Subject: {subject if subject else "(no subject)"}
Issue: {issue}

Rules:
1. Base your answer ONLY on the provided documentation
2. If the documentation doesn't cover the issue, say so clearly
3. Be concise but thorough
4. Provide step-by-step instructions when relevant
5. Never make up policies or procedures

Generate a professional, helpful response."""

        try:
            return self.llm.call(prompt, max_tokens=1000)
        except Exception as e:
            # Fallback: return summary from retrieved docs if LLM fails
            if retrieved_docs:
                doc_text = retrieved_docs[0][0]
                summary = doc_text[:500] if len(doc_text) > 500 else doc_text
                return f"Based on our documentation:\n\n{summary}\n\nFor more details, please refer to our support documentation or contact our support team."
            else:
                return "I don't have relevant documentation to answer this question. Please contact our support team."
    
    def _generate_justification(self, classification: dict, retrieved_docs: list, response: str) -> str:
        """
        Generate a justification for the triage decision
        """
        
        domain = classification.get("domain", "unknown")
        product_area = classification.get("product_area", "general")
        request_type = classification.get("request_type", "unknown")
        
        doc_sources = ", ".join([m["product_area"] for _, m, _ in retrieved_docs[:2]]) if retrieved_docs else "no docs"
        
        justification = (
            f"Classified as {request_type} in {product_area} ({domain}). "
            f"Retrieved relevant documentation from {doc_sources}. "
            f"Response grounded in support corpus."
        )
        
        return justification
