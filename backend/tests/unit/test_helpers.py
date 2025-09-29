import pytest
import string

from backend.utils.helpers import generate_public_id


# -------------------------
# Basic functionality
# -------------------------
def test_generate_public_id_default_length():
    """Ensure default length is 8 and only contains uppercase letters + digits."""
    public_id = generate_public_id()
    assert len(public_id) == 8
    assert all(ch in string.ascii_uppercase + string.digits for ch in public_id)


def test_generate_public_id_custom_length():
    """Ensure custom length works correctly."""
    public_id = generate_public_id(12)
    assert len(public_id) == 12
    assert all(ch in string.ascii_uppercase + string.digits for ch in public_id)


# -------------------------
# Randomness / uniqueness
# -------------------------
def test_generate_public_id_uniqueness():
    """Generate many IDs and ensure they are unique enough."""
    ids = {generate_public_id() for _ in range(1000)}
    # With 36^8 possibilities, collisions are extremely unlikely
    assert len(ids) == 1000


# -------------------------
# Edge cases
# -------------------------
def test_generate_public_id_zero_length():
    """Length 0 should return an empty string."""
    assert generate_public_id(0) == ""


def test_generate_public_id_negative_length():
    """Negative length should raise a ValueError from random.choices."""
    with pytest.raises(ValueError):
        generate_public_id(-5)
