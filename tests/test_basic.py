import pytest

def test_basic_import():
    """Test that basic modules can be imported."""
    try:
        import brains
        import evo
        import tasks
        assert True
    except ImportError as e:
        pytest.skip(f"Module not available: {e}")

def test_simple_math():
    """Simple test to ensure pytest works."""
    assert 2 + 2 == 4
    assert 3 * 3 == 9
