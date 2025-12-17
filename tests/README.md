# Bongo Cat Tests

This directory contains unit tests for the Bongo Cat application.

## Running Tests

### Using unittest (no additional dependencies)

```bash
# Run all tests
python -m unittest discover tests

# Run specific test file
python -m unittest tests.test_config

# Run specific test class
python -m unittest tests.test_config.TestConfigDefaults

# Run specific test method
python -m unittest tests.test_config.TestConfigDefaults.test_default_config_values
```

### Using pytest (recommended)

```bash
# Install pytest
pip install pytest

# Run all tests
pytest tests/

# Run with verbose output
pytest -v tests/

# Run specific test file
pytest tests/test_config.py

# Run with coverage
pip install pytest-cov
pytest --cov=bongo_cat tests/
```

## Test Structure

- `test_utils.py` - Tests for utility functions (resource_path, logging)
- `test_config.py` - Tests for configuration management
- `test_platform.py` - Tests for platform-specific functionality

## Writing New Tests

When adding new tests:

1. Create a new file with the prefix `test_`
2. Import unittest and any necessary modules
3. Create test classes that inherit from `unittest.TestCase`
4. Name test methods with the prefix `test_`
5. Use descriptive docstrings

Example:

```python
import unittest

class TestMyFeature(unittest.TestCase):
    """Test my new feature."""

    def test_basic_functionality(self):
        """Test that basic functionality works."""
        result = my_function()
        self.assertEqual(result, expected_value)
```

## Coverage Goals

- Configuration management: 100%
- Utility functions: 100%
- Platform-specific code: 100%
- Core UI logic: 70%+
- Animation logic: 50%+
