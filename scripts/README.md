# PyDCMView - Publishing Scripts

This directory contains automation scripts for building and publishing PyDCMView to PyPI.

## Quick Start

### One-Line Publishing

The simplest way to publish a new version:

```bash
./scripts/publish.sh
```

This will:
1. Show current version
2. Prompt for version bump type (patch/minor/major)
3. Update version in all necessary files
4. Clean and build distribution
5. Run quality checks
6. Upload to PyPI
7. Create and push git tag

### Step-by-Step Publishing

If you prefer more control:

```bash
# 1. Bump version (patch by default)
python scripts/bump_version.py

# Or specify bump type
python scripts/bump_version.py minor
python scripts/bump_version.py major
python scripts/bump_version.py 1.0.0  # specific version

# 2. Build and publish
make build
make check
make publish
```

## Scripts Overview

### `bump_version.py`

Automatic version management script that updates version in both:
- `pyproject.toml` (source of truth)
- `src/pydcmview/__init__.py` (kept in sync)

**Usage:**
```bash
python scripts/bump_version.py           # Bumps patch (0.1.5 → 0.1.6)
python scripts/bump_version.py patch     # Bumps patch (0.1.5 → 0.1.6)
python scripts/bump_version.py minor     # Bumps minor (0.1.5 → 0.2.0)
python scripts/bump_version.py major     # Bumps major (0.1.5 → 1.0.0)
python scripts/bump_version.py 2.0.0     # Sets specific version
```

### `publish.sh`

Interactive publishing script that handles the complete workflow.

**Features:**
- Interactive version bump selection
- Safety confirmations at each step
- Automatic git tagging
- Color-coded output
- Error handling

**Usage:**
```bash
./scripts/publish.sh
```

## Makefile Targets

Convenient shortcuts for common tasks:

```bash
make help          # Show all available targets
make version       # Display current version
make clean         # Remove build artifacts
make build         # Build distribution packages
make check         # Check distribution with twine
make publish       # Publish to PyPI (production)
make publish-test  # Publish to TestPyPI (testing)
make install-dev   # Install build dependencies
```

## Prerequisites

### 1. Install Build Tools

```bash
make install-dev
# or
pip install --upgrade build twine
```

### 2. Configure PyPI Credentials

Create `~/.pypirc` with your API tokens:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR_PRODUCTION_TOKEN_HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TESTPYPI_TOKEN_HERE
```

**Get API tokens:**
- PyPI: https://pypi.org/manage/account/token/
- TestPyPI: https://test.pypi.org/manage/account/token/

## Publishing Workflows

### First-Time Setup

```bash
# 1. Install dependencies
make install-dev

# 2. Configure ~/.pypirc with API tokens

# 3. Test with TestPyPI (optional)
make publish-test
```

### Regular Release

```bash
# Option A: One-line (recommended)
./scripts/publish.sh

# Option B: Using Make
python scripts/bump_version.py patch
make publish

# Option C: Manual control
python scripts/bump_version.py
make clean
make build
make check
twine upload dist/*
git tag v0.1.6
git push origin v0.1.6
```

### Emergency/Manual Version

```bash
# Set specific version
python scripts/bump_version.py 0.1.7

# Build and publish
make publish
```

## Version Bumping Strategy

The project follows [Semantic Versioning](https://semver.org/):

- **MAJOR** (1.0.0 → 2.0.0): Breaking changes, incompatible API changes
- **MINOR** (0.1.0 → 0.2.0): New features, backwards-compatible
- **PATCH** (0.1.5 → 0.1.6): Bug fixes, small improvements (default)

### When to Bump

- **Patch**: Bug fixes, documentation, small improvements
- **Minor**: New features, new functionality
- **Major**: Breaking changes, major rewrite

## Testing Before Publishing

Always test manually before publishing:

```bash
# 1. Bump version
python scripts/bump_version.py

# 2. Install locally
pip install -e .

# 3. Test functionality
pydcmview --help
pydcmview /path/to/test/dicom

# 4. Build and check
make build
make check

# 5. Publish
make publish
```

## Troubleshooting

### Build Fails

```bash
# Clean everything and rebuild
make clean
make build
```

### Upload Fails

1. Check `~/.pypirc` credentials
2. Verify API token has upload permissions
3. Ensure version doesn't already exist on PyPI

### Git Tag Issues

```bash
# List existing tags
git tag

# Delete local tag
git tag -d v0.1.6

# Delete remote tag (if pushed)
git push origin --delete v0.1.6
```

### Version Mismatch

If versions get out of sync:

```bash
# Manually edit pyproject.toml
# Then sync __init__.py
python scripts/bump_version.py 0.1.6
```

## CI/CD Integration (Future)

These scripts are designed for manual publishing from a local machine with API keys.

For GitHub Actions automation, consider:
- Using `PYPI_API_TOKEN` secret
- Trigger on git tags
- Run tests before publish
- Auto-generate changelog

## Security Notes

- **Never commit** `~/.pypirc` or API tokens
- API tokens are account-wide or project-scoped
- Regenerate tokens if compromised
- Use TestPyPI for testing

## Support

For issues or questions:
- GitHub Issues: https://github.com/apleynes/pydcmview/issues
- Email: andrew.leynes@example.com
