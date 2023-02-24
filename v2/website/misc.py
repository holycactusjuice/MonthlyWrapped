import re
import string
import secrets


def is_valid_email(email):
    """
    Check if email is valid
    ** note that this function does not check if the email actually exists **

    Args:
        email (str): email address to check
    Returns:
        bool: True if email is valid, False otherwise
    """

    # Define the regular expression pattern to match a valid email address
    pattern = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

    # Use the pattern to check if the email matches the regular expression
    if pattern.match(email):
        return True
    return False


def build_state():
    state = ''.join(
        secrets.choice(string.ascii_uppercase + string.digits) for _ in range(16)
    )

    return state
