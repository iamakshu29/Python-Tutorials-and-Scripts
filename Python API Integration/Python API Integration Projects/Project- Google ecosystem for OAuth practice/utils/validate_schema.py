import re

def validate_row(row, expected_columns=5):
    """Ensure row has correct number of fields and email is valid."""
    if len(row) < expected_columns:
        return False
    # Check email format
    if not re.match(r'^[^@]+@[^@]+\.[^@]+$', row[1]):
        return False
    return True