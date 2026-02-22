import re

# Simple regex for demo purposes (Real CDSS needs dedicated NER for PHI)
PHI_PATTERNS = [r"\b\d{3}-\d{2}-\d{4}\b", r"\b[A-Z]{2}\d{7}\b"]

RISK_WORDS = ["suicide", "harm", "killing"]

def check_input_safety(text: str):
    for pattern in PHI_PATTERNS:
        if re.search(pattern, text):
            return False, "Potential PHI (SSN/ID) detected. Input rejected"
        
    for risk in RISK_WORDS:
        if risk in text.lower():
            return False, "Crisis detected. Please contact emergency services"
        
    return True, "OK"

def check_output_safety(text: str):
    """Ensure disclaimer is present."""
    disclaimer = "Consult a qualified healthcare provider."
    if disclaimer not in text:
        text += f"\n\n[SYSTEM DISCLAIMER]: {disclaimer}"
    return text