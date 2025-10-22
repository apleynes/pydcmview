# PyDCMView - PyPI Publishing Automation

**Quick Reference: One-line publishing to PyPI**

This document describes the automated publishing system for PyDCMView.

## TL;DR - Quick Publish

```bash
./scripts/publish.sh
```

That's it! The script will guide you through the rest.

---

## What's Been Automated

### 1. Version Management
- **Single source of truth**: Version is defined in `pyproject.toml`
- **Auto-sync**: `__init__.py` is automatically updated to match
- **Semantic versioning**: Support for major.minor.patch bumps
- **Script**: `scripts/bump_version.py`

### 2. Build & Publish Workflow
- **One command**: `./scripts/publish.sh` handles everything
- **Safety checks**: Multiple confirmations before uploading
- **Git integration**: Automatically creates and pushes version tags
- **Color-coded**: Clear visual feedback during the process

### 3. Make Targets
- **Quick access**: Common tasks via `make` commands
- **Consistent**: Standard targets across environments
- **Helpful**: `make help` shows all options

---

## Publishing Workflow

### The Automated Way (Recommended)

```bash
./scripts/publish.sh
```

**What it does:**
1. Shows current version (0.1.6)
2. Asks for version bump type (patch/minor/major/manual)
3. Updates version in both files
4. Cleans previous builds
5. Builds distribution packages
6. Runs `twine check` for validation
7. Asks for confirmation before uploading
8. Uploads to PyPI
9. Creates git tag (e.g., `v0.1.6`)
10. Pushes tag to remote

**Interactive prompts:**
- Version bump selection (defaults to patch)
- Confirmation before build
- Confirmation before upload
- All with clear, color-coded output

### The Manual Way

```bash
# 1. Update version
python scripts/bump_version.py patch    # or minor, major, or specific version

# 2. Build
make build

# 3. Check
make check

# 4. Publish
make publish

# 5. Tag and push
git tag v0.1.6
git push origin v0.1.6
```

---

## Version Bumping

### Default Behavior
Running `python scripts/bump_version.py` without arguments **bumps the patch version**:
- 0.1.6 → 0.1.7

### Explicit Bumps

```bash
# Patch bump (0.1.6 → 0.1.7)
python scripts/bump_version.py patch

# Minor bump (0.1.6 → 0.2.0)
python scripts/bump_version.py minor

# Major bump (0.1.6 → 1.0.0)
python scripts/bump_version.py major

# Specific version
python scripts/bump_version.py 2.0.0
```

### When to Use Each

- **Patch**: Bug fixes, documentation updates, small improvements (most common)
- **Minor**: New features, significant improvements, backwards-compatible changes
- **Major**: Breaking changes, major rewrites, incompatible API changes

---

## Makefile Commands

```bash
make help          # Show all available commands
make version       # Display current version (0.1.6)
make clean         # Remove build artifacts (dist/, build/, *.egg-info/)
make build         # Clean + build distribution packages
make check         # Run twine check on built packages
make publish       # build + check + upload to PyPI
make publish-test  # build + check + upload to TestPyPI
make install-dev   # Install build dependencies (build, twine)
```

---

## Prerequisites

### 1. Install Build Dependencies

```bash
make install-dev
```

Or manually:
```bash
pip install --upgrade build twine
```

### 2. Configure PyPI Credentials

Create `~/.pypirc` in your home directory:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-AgENdGVzdC5weXBpLm9yZwIkZjNm...  # Your actual token

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-AgENdGVzdC5weXBpLm9yZwIkZjNm...  # Your actual token
```

**Get API tokens:**
- Production PyPI: https://pypi.org/manage/account/token/
- Test PyPI: https://test.pypi.org/manage/account/token/

**Security:**
- Never commit `~/.pypirc` to git
- Use project-scoped tokens when possible
- Regenerate immediately if compromised

---

## File Structure

```
pydcmview/
├── Makefile                    # NEW: Build/publish shortcuts
├── AUTOMATION.md              # NEW: This file
├── scripts/
│   ├── README.md              # NEW: Detailed script documentation
│   ├── bump_version.py        # NEW: Version management
│   └── publish.sh             # NEW: One-line publish script
├── pyproject.toml             # UPDATED: Version 0.1.6
└── src/pydcmview/
    └── __init__.py            # UPDATED: Version 0.1.6
```

---

## Example Publishing Session

```bash
$ ./scripts/publish.sh

═══════════════════════════════════════════════
     PyDCMView - PyPI Publishing Script
═══════════════════════════════════════════════

Current version: 0.1.6

Version bump options:
  1) patch  (0.1.6 → 0.1.7)
  2) minor  (0.1.6 → 0.2.0)
  3) major  (0.1.6 → 1.0.0)
  4) manual (enter specific version)

Select version bump [1-4, default=1]: 1

Bumping version (patch)...
✓ Updated pyproject.toml to version 0.1.7
✓ Updated __init__.py to version 0.1.7

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Ready to publish version 0.1.7 to PyPI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This will:
  1. Clean previous builds
  2. Build distribution packages
  3. Run twine check
  4. Upload to PyPI
  5. Create and push git tag v0.1.7

Continue? [y/N]: y

Cleaning previous builds...
✓ Clean complete

Building distribution packages...
[build output]
✓ Build complete

Checking distribution with twine...
Checking dist/pydcmview-0.1.7-py3-none-any.whl: PASSED
Checking dist/pydcmview-0.1.7.tar.gz: PASSED
✓ Check complete

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Final confirmation: Upload to PyPI?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

-rw-r--r-- 1 user user 16558 Oct 22 06:55 dist/pydcmview-0.1.7-py3-none-any.whl
-rw-r--r-- 1 user user 18976 Oct 22 06:55 dist/pydcmview-0.1.7.tar.gz

Upload to PyPI now? [y/N]: y

Uploading to PyPI...
Uploading pydcmview-0.1.7-py3-none-any.whl
Uploading pydcmview-0.1.7.tar.gz
✓ Upload complete

Creating git tag v0.1.7...
✓ Tag created

Pushing git tag...
✓ Tag pushed

═══════════════════════════════════════════════
        ✓ Successfully Published!
═══════════════════════════════════════════════

Version 0.1.7 published to PyPI

Next steps:
  • Verify on PyPI: https://pypi.org/project/pydcmview/0.1.7/
  • Test install: pip install --upgrade pydcmview
  • Check functionality: pydcmview --help

Don't forget to commit the version changes!
  git add pyproject.toml src/pydcmview/__init__.py
  git commit -m 'Bump version to 0.1.7'
  git push
```

---

## Testing Before Publishing

**Always test manually before publishing!**

```bash
# 1. Update version
python scripts/bump_version.py patch

# 2. Install locally in editable mode
pip install -e .

# 3. Test the application
pydcmview --help
pydcmview /path/to/test/dicom

# 4. Run any tests
python test_scroll.py  # if applicable

# 5. When satisfied, publish
./scripts/publish.sh
# Select "manual" and enter the same version you already set
```

---

## Troubleshooting

### "Version already exists on PyPI"

You cannot re-upload the same version. Bump to a new version:

```bash
python scripts/bump_version.py patch
make publish
```

### "Authentication failed"

Check your `~/.pypirc` file:
- Correct API token format
- Token not expired
- Token has upload permissions

### "Twine check failed"

Usually indicates issues with package metadata. Check:
- `pyproject.toml` syntax
- README.md formatting
- All required files present

### Build artifacts not cleaned

```bash
make clean
# or manually:
rm -rf dist/ build/ src/*.egg-info/
```

### Git tag already exists

```bash
# Delete local tag
git tag -d v0.1.6

# Delete remote tag (careful!)
git push origin --delete v0.1.6
```

---

## Advanced Usage

### Test on TestPyPI First

```bash
# Option 1: Using make
make publish-test

# Option 2: Manual
twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ pydcmview
```

### Skip Tag Creation

Edit `scripts/publish.sh` and comment out the git tag section, or manually:

```bash
python scripts/bump_version.py patch
make publish
# Skip: git tag v0.1.7
# Skip: git push origin v0.1.7
```

### Publish Without Version Bump

If you already have the correct version set:

```bash
# Just build and publish
make clean
make build
make check
make publish
```

---

## Current Status

- **Repository**: Ready for automated publishing
- **Current version**: 0.1.6
- **Last published**: 0.1.5 (on PyPI)
- **Next version**: 0.1.6 (ready to publish)
- **Automation**: ✓ Complete

---

## Quick Reference Card

| Task | Command |
|------|---------|
| One-line publish | `./scripts/publish.sh` |
| Bump patch | `python scripts/bump_version.py` |
| Bump minor | `python scripts/bump_version.py minor` |
| Bump major | `python scripts/bump_version.py major` |
| Show version | `make version` |
| Clean build | `make clean` |
| Build only | `make build` |
| Check build | `make check` |
| Publish | `make publish` |
| Test publish | `make publish-test` |
| Install deps | `make install-dev` |
| Show help | `make help` |

---

## Notes

- Python version requirement: **>=3.8** (as configured in `pyproject.toml`)
- Default bump type: **patch** (0.1.6 → 0.1.7)
- Git tags format: **v{version}** (e.g., v0.1.6)
- Build system: **setuptools** with modern pyproject.toml
- Distribution format: **wheel + source tarball**

---

**Ready to publish!** Run `./scripts/publish.sh` when ready.
