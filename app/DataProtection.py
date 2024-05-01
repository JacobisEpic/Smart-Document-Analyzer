# DataProtection.py
import re
from html import escape

def sanitize_input(data):
    """
    Sanitizes input data to prevent common security threats like XSS and SQL injection.
    Args:
    data (str): Input data from the user.
    
    Returns:
    str: Sanitized data.
    """
    # HTML escape to prevent XSS attacks
    data = escape(data)
    
    # Strip out unwanted scripts or SQL injections patterns
    data = re.sub(r'[^\w.@+-]', '', data)
    
    return data

def validate_username(username):
    """
    Validates the username to meet certain conditions.
    Args:
    username (str): Username to validate.
    
    Returns:
    bool, str: Validation success, and message.
    """
    if len(username) < 3:
        return False, "Username must be at least 3 characters long."
    if len(username) > 20:
        return False, "Username cannot be more than 20 characters long."
    if not re.match(r'^\w+$', username):
        return False, "Username can only contain alphanumeric characters and underscores."
    return True, "Username is valid."

def validate_password(password):
    """
    Validates the password to ensure it meets security requirements.
    Args:
    password (str): Password to validate.
    
    Returns:
    bool, str: Validation success, and message.
    """
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
    if not re.search(r'[A-Za-z]', password) or not re.search(r'[0-9]', password):
        return False, "Password must include both letters and numbers."
    return True, "Password is valid."
