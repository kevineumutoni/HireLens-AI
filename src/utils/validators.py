"""
Validation utilities for AI outputs and data integrity.
"""
from typing import Any


def validate_ai_match_response(response: dict) -> tuple[bool, str]:
    """Validate that an AI match response has required fields and valid types."""
    required_fields = ["matchScore", "strengths", "gaps", "recommendation"]
    
    for field in required_fields:
        if field not in response:
            return False, f"Missing required field: {field}"
    
    score = response["matchScore"]
    if not isinstance(score, (int, float)) or not (0 <= score <= 100):
        return False, f"matchScore must be number 0-100, got: {score}"
    
    for field_name in ["strengths", "gaps"]:
        if not isinstance(response[field_name], list):
            return False, f"{field_name} must be a list"
        if not all(isinstance(item, str) for item in response[field_name]):
            return False, f"All items in {field_name} must be strings"
    
    if not isinstance(response["recommendation"], str) or not response["recommendation"].strip():
        return False, "recommendation must be a non-empty string"
    
    return True, ""