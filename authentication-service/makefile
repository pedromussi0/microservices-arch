.PHONY: test test-integration test-unit test-auth lint clean

# Default target
test: test-integration test-unit

# Run all integration tests
test-integration:
	pytest tests/integration -v

# Run all unit tests
test-unit:
	pytest tests/unit -v

# Run specific integration test file for authentication
test-auth:
	pytest tests/integration/test_auth.py -v

# Run linting checks
lint:
	flake8 . --exclude=venv
	black --check . --exclude=venv
	isort --check-only . --skip=venv

format:
	black . --exclude=venv
	isort . --skip=venv

# Clean up any test cache or temporary files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov