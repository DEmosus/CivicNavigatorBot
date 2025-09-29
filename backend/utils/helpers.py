import random, string

def generate_public_id(length: int = 8) -> str:
    """Generate a random alphanumeric public ID."""
    if length < 0:
        raise ValueError("length must be non-negative")
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))

