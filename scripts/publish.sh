#!/bin/bash
set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}     PyDCMView - PyPI Publishing Script      ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

# Get current version
CURRENT_VERSION=$(python scripts/bump_version.py | grep "Current version:" | awk '{print $3}')
echo -e "${YELLOW}Current version: $CURRENT_VERSION${NC}"
echo ""

# Ask for version bump type (default to patch)
echo -e "${BLUE}Version bump options:${NC}"
echo "  1) patch  (${CURRENT_VERSION} → $(python -c "v='$CURRENT_VERSION'.split('.'); v[2]=str(int(v[2])+1); print('.'.join(v))"))"
echo "  2) minor  (${CURRENT_VERSION} → $(python -c "v='$CURRENT_VERSION'.split('.'); v[1]=str(int(v[1])+1); v[2]='0'; print('.'.join(v))"))"
echo "  3) major  (${CURRENT_VERSION} → $(python -c "v='$CURRENT_VERSION'.split('.'); v[0]=str(int(v[0])+1); v[1]='0'; v[2]='0'; print('.'.join(v))"))"
echo "  4) manual (enter specific version)"
echo ""
read -p "Select version bump [1-4, default=1]: " BUMP_CHOICE

case $BUMP_CHOICE in
    2)
        BUMP_TYPE="minor"
        ;;
    3)
        BUMP_TYPE="major"
        ;;
    4)
        read -p "Enter version (e.g., 1.0.0): " BUMP_TYPE
        ;;
    *)
        BUMP_TYPE="patch"
        ;;
esac

# Bump version
echo ""
echo -e "${GREEN}Bumping version ($BUMP_TYPE)...${NC}"
python scripts/bump_version.py $BUMP_TYPE

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Version bump failed${NC}"
    exit 1
fi

# Get new version
NEW_VERSION=$(grep -oP 'version\s*=\s*"\K[^"]+' pyproject.toml)
echo ""

# Confirm before proceeding
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Ready to publish version ${NEW_VERSION} to PyPI${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "This will:"
echo "  1. Clean previous builds"
echo "  2. Build distribution packages"
echo "  3. Run twine check"
echo "  4. Upload to PyPI"
echo "  5. Create and push git tag v${NEW_VERSION}"
echo ""
read -p "Continue? [y/N]: " CONFIRM

if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
    echo -e "${RED}Aborted${NC}"
    exit 1
fi

# Clean previous builds
echo ""
echo -e "${GREEN}Cleaning previous builds...${NC}"
make clean

# Build
echo ""
echo -e "${GREEN}Building distribution packages...${NC}"
python -m build

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Build failed${NC}"
    exit 1
fi

# Check with twine
echo ""
echo -e "${GREEN}Checking distribution with twine...${NC}"
twine check dist/*

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Twine check failed${NC}"
    exit 1
fi

# Final confirmation before upload
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Final confirmation: Upload to PyPI?${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
ls -lh dist/
echo ""
read -p "Upload to PyPI now? [y/N]: " UPLOAD_CONFIRM

if [[ ! $UPLOAD_CONFIRM =~ ^[Yy]$ ]]; then
    echo -e "${RED}Upload cancelled${NC}"
    echo -e "${YELLOW}Build artifacts are ready in dist/ directory${NC}"
    exit 1
fi

# Upload to PyPI
echo ""
echo -e "${GREEN}Uploading to PyPI...${NC}"
twine upload dist/*

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Upload failed${NC}"
    exit 1
fi

# Create and push git tag
echo ""
echo -e "${GREEN}Creating git tag v${NEW_VERSION}...${NC}"
git tag -a "v${NEW_VERSION}" -m "Release version ${NEW_VERSION}"

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Git tag creation failed${NC}"
    echo -e "${YELLOW}Package was uploaded to PyPI successfully${NC}"
    exit 1
fi

echo -e "${GREEN}Pushing git tag...${NC}"
git push -u origin "v${NEW_VERSION}"

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Git push failed${NC}"
    echo -e "${YELLOW}Package was uploaded to PyPI successfully${NC}"
    echo -e "${YELLOW}Tag v${NEW_VERSION} created locally but not pushed${NC}"
    exit 1
fi

# Success!
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}        ✓ Successfully Published!              ${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}Version ${NEW_VERSION} published to PyPI${NC}"
echo ""
echo "Next steps:"
echo "  • Verify on PyPI: https://pypi.org/project/pydcmview/${NEW_VERSION}/"
echo "  • Test install: pip install --upgrade pydcmview"
echo "  • Check functionality: pydcmview --help"
echo ""
echo -e "${YELLOW}Don't forget to commit the version changes!${NC}"
echo "  git add pyproject.toml src/pydcmview/__init__.py"
echo "  git commit -m 'Bump version to ${NEW_VERSION}'"
echo "  git push"
echo ""
