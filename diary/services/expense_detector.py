import re
from decimal import Decimal

EXPENSE_PATTERNS = [
    r'₹\s*\d+',
    r'Rs\.?\s*\d+',
    r'INR\s*\d+',
    r'spent\s*₹?\s*\d+',
    r'paid\s*₹?\s*\d+',
    r'cost\s*₹?\s*\d+',
]

def extract_expenses(text):
    """
    Extract expense amounts from text using regex patterns.
    Returns a list of tuples: (amount, context)
    """
    results = []
    for pattern in EXPENSE_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            amount_match = re.search(r'\d+', match)
            if amount_match:
                amount = Decimal(amount_match.group())
                results.append((amount, match))
    return results
