"""
LLM Provider: Abstraction for different LLM backends
"""

import json
import os
from typing import Dict, Any

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except:
    GEMINI_AVAILABLE = False

class LLMProvider:
    def __init__(self):
        """Initialize LLM provider with Google Gemini"""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not set in .env")
        
        if GEMINI_AVAILABLE:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            self.use_library = True
        else:
            self.api_key = api_key
            self.use_library = False
    
    def call(self, prompt: str, max_tokens: int = 1000, json_mode: bool = False) -> str:
        """
        Call the LLM
        
        Args:
            prompt: Input prompt
            max_tokens: Max output tokens
            json_mode: If True, request JSON output
        
        Returns:
            Model response text
        """
        
        if json_mode:
            prompt += "\n\nReturn ONLY valid JSON, no markdown or extra text."
        
        if self.use_library:
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=max_tokens,
                        temperature=0.7,
                    )
                )
                return response.text.strip()
            except Exception as e:
                # If API fails, return escalation message
                raise Exception(f"LLM generation failed: {str(e)}")
        else:
            raise Exception("Google Generative AI library not available")
    
    def classify_json(self, prompt: str) -> Dict[str, Any]:
        """
        Call LLM and parse JSON response
        """
        response_text = self.call(prompt, json_mode=True)
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            # If JSON parsing fails, try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    raise Exception(f"Could not parse JSON from LLM response: {response_text}")
            raise Exception(f"No valid JSON in LLM response: {response_text}")
