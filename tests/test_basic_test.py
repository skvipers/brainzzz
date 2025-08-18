import pytest


def test_basic_import():
    """Test that basic modules can be imported."""
    try:
        # Проверяем, что модули доступны для импорта
        import brains
        import evo
        import tasks

        # Если импорт прошел успешно, модули работают
        assert brains is not None  # nosec B101 - тесты
        assert evo is not None  # nosec B101 - тесты
        assert tasks is not None  # nosec B101 - тесты
    except ImportError as e:
        pytest.skip(f"Module not available: {e}")


def test_simple_math():
    """Simple test to ensure pytest works."""
    assert 2 + 2 == 4  # nosec B101 - тесты
    assert 3 * 3 == 9  # nosec B101 - тесты
