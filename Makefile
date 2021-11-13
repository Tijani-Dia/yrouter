default: format

format:
	isort src/yrouter tests
	black src/yrouter tests
	flake8 src/yrouter tests

clean:
	find . -name '*.pyc' -exec rm -rf {} +
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '*.egg-info' -exec rm -rf {} +
	rm -rf dist/ build/ .pytest_cache/
