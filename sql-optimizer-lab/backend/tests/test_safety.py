import pytest
from app.engine.safety import validate_read_only

def test_select_allowed(): validate_read_only("SELECT 1")
def test_write_blocked():
    with pytest.raises(ValueError): validate_read_only("DELETE FROM users")
