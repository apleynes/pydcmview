# PyDCMView - PyPI Publishing Guide

This document outlines the steps to publish PyDCMView to PyPI.

## Prerequisites

1. **PyPI Account**: Create accounts on both:
   - [TestPyPI](https://test.pypi.org/account/register/) (for testing)
   - [PyPI](https://pypi.org/account/register/) (for production)

2. **API Tokens**: Generate API tokens for authentication:
   - TestPyPI: https://test.pypi.org/manage/account/token/
   - PyPI: https://pypi.org/manage/account/token/

3. **Build Tools**: Install required packages
   ```bash
   pip install build twine
   ```

## Pre-Publication Checklist

### Version Management
- [ ] Update version in `pyproject.toml`
- [ ] Update version in `src/pydcmview/__init__.py`
- [ ] Update CHANGELOG.md (if exists)

### Dependencies
- [ ] Verify all dependencies are correctly listed in `pyproject.toml`
- [ ] Ensure `textual-image>=0.3.0` (not rich-pixels)
- [ ] Test installation in clean environment

### Documentation
- [ ] Update README.md with latest features
- [ ] Verify all key bindings are documented
- [ ] Update terminal compatibility section

### Code Quality
- [ ] Run syntax checks: `python -m py_compile src/pydcmview/*.py`
- [ ] Verify imports work: `python -c "import pydcmview; print(pydcmview.__version__)"`
- [ ] Test entry point: `python -m pydcmview --help`

## Publishing Steps

### 1. Clean Previous Builds
```bash
rm -rf dist/ build/ src/*.egg-info/
```

### 2. Build Distribution
```bash
python -m build
```

This creates:
- `dist/pydcmview-X.Y.Z-py3-none-any.whl` (wheel)
- `dist/pydcmview-X.Y.Z.tar.gz` (source distribution)

### 3. Check Distribution
```bash
twine check dist/*
```

### 4. Test Upload (TestPyPI)
```bash
twine upload --repository testpypi dist/*
```

### 5. Test Installation from TestPyPI
```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ pydcmview
```

### 6. Production Upload (PyPI)
```bash
twine upload dist/*
```

## Authentication Setup

### Option 1: API Token (Recommended)
Create `~/.pypirc`:
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR_API_TOKEN_HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TESTPYPI_TOKEN_HERE
```

### Option 2: Interactive Authentication
Twine will prompt for credentials if `~/.pypirc` is not configured.

## Post-Publication

### Verification
1. **Check PyPI page**: https://pypi.org/project/pydcmview/
2. **Test installation**: `pip install pydcmview`
3. **Verify functionality**: `pydcmview --help`

### GitHub Release
1. Create a git tag: `git tag v0.1.0`
2. Push tags: `git push origin --tags`
3. Create GitHub release with changelog

## Current Package Status

### Built Files
- ✅ `dist/pydcmview-0.1.0-py3-none-any.whl`
- ✅ `dist/pydcmview-0.1.0.tar.gz`
- ✅ Both files pass `twine check`

### Package Structure
```
pydcmview/
├── pyproject.toml          # ✅ Modern build configuration
├── README.md               # ✅ Comprehensive documentation
├── LICENSE                 # ✅ MIT License
├── MANIFEST.in            # ✅ Package data inclusion
├── requirements.txt        # ✅ Updated dependencies
└── src/pydcmview/
    ├── __init__.py        # ✅ Package metadata
    ├── main.py            # ✅ Entry point
    ├── viewer.py          # ✅ Main application
    └── image_loader.py    # ✅ Image handling
```

### Dependencies
- textual>=0.70.0 (UI framework)
- textual-image>=0.3.0 (high-quality image rendering)
- SimpleITK>=2.3.0 (medical image I/O)
- numpy>=1.21.0 (array operations)
- pydicom>=2.3.0 (DICOM support)
- Pillow>=8.0.0 (image processing)

### Key Features Ready for PyPI
- ✅ High-quality terminal graphics with Sixel/Kitty protocols
- ✅ Zoom functionality (+/- keys)
- ✅ Dimension flipping with visual indicators
- ✅ Overlay-based dimension selection
- ✅ Interactive crosshair with adjustable opacity
- ✅ Multi-format support (DICOM, NRRD, Nifti)

## Troubleshooting

### Common Issues
1. **Build fails**: Check `pyproject.toml` syntax
2. **Import errors**: Verify all dependencies in requirements
3. **Upload fails**: Check API token permissions
4. **Installation fails**: Test in clean virtual environment

### Support
- GitHub Issues: https://github.com/aleynes/pydcmview/issues
- Email: andrew.leynes@example.com

---

**Ready for publication!** The package is properly configured and tested for PyPI distribution.