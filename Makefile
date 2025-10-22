.PHONY: help clean build check publish publish-test install-dev version

help:
	@echo "PyDCMView - Build and Publish Automation"
	@echo ""
	@echo "Available targets:"
	@echo "  make clean         - Remove build artifacts"
	@echo "  make build         - Build distribution packages"
	@echo "  make check         - Check distribution with twine"
	@echo "  make publish       - Publish to PyPI"
	@echo "  make publish-test  - Publish to TestPyPI"
	@echo "  make install-dev   - Install build dependencies"
	@echo "  make version       - Show current version"
	@echo ""
	@echo "Quick publish workflow:"
	@echo "  ./scripts/publish.sh    - One-line publish (bumps patch by default)"

clean:
	@echo "Cleaning build artifacts..."
	rm -rf dist/ build/ src/*.egg-info/ *.egg-info/
	@echo "✓ Clean complete"

build: clean
	@echo "Building distribution packages..."
	python -m build
	@echo "✓ Build complete"

check:
	@echo "Checking distribution with twine..."
	twine check dist/*
	@echo "✓ Check complete"

publish: build check
	@echo "Publishing to PyPI..."
	twine upload dist/*
	@echo "✓ Published to PyPI"

publish-test: build check
	@echo "Publishing to TestPyPI..."
	twine upload --repository testpypi dist/*
	@echo "✓ Published to TestPyPI"

install-dev:
	@echo "Installing development dependencies..."
	pip install --upgrade build twine
	@echo "✓ Dependencies installed"

version:
	@python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])" 2>/dev/null || \
	python -c "import re; print(re.search(r'version\s*=\s*\"([^\"]+)\"', open('pyproject.toml').read()).group(1))"
