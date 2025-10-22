#!/usr/bin/env python3
"""
Version Bumping Script for PyDCMView

Automatically updates version in pyproject.toml and src/pydcmview/__init__.py
Supports semantic versioning: major.minor.patch

Usage:
    python scripts/bump_version.py          # Bumps patch version (default)
    python scripts/bump_version.py patch    # Bumps patch version
    python scripts/bump_version.py minor    # Bumps minor version
    python scripts/bump_version.py major    # Bumps major version
    python scripts/bump_version.py 1.2.3    # Sets specific version
"""

import re
import sys
from pathlib import Path


def get_current_version():
    """Read current version from pyproject.toml"""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    content = pyproject_path.read_text()

    match = re.search(r'^version\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
    if not match:
        raise ValueError("Could not find version in pyproject.toml")

    return match.group(1)


def parse_version(version_str):
    """Parse version string into (major, minor, patch)"""
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)$', version_str)
    if not match:
        raise ValueError(f"Invalid version format: {version_str}")

    return tuple(map(int, match.groups()))


def bump_version(current_version, bump_type):
    """Bump version based on type (major, minor, patch)"""
    major, minor, patch = parse_version(current_version)

    if bump_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif bump_type == 'minor':
        minor += 1
        patch = 0
    elif bump_type == 'patch':
        patch += 1
    else:
        # Assume it's a specific version string
        try:
            parse_version(bump_type)  # Validate format
            return bump_type
        except ValueError:
            raise ValueError(f"Invalid bump type or version: {bump_type}")

    return f"{major}.{minor}.{patch}"


def update_pyproject_toml(new_version):
    """Update version in pyproject.toml"""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    content = pyproject_path.read_text()

    new_content = re.sub(
        r'^version\s*=\s*["\'][^"\']+["\']',
        f'version = "{new_version}"',
        content,
        flags=re.MULTILINE
    )

    pyproject_path.write_text(new_content)
    print(f"✓ Updated pyproject.toml to version {new_version}")


def update_init_py(new_version):
    """Update version in src/pydcmview/__init__.py"""
    init_path = Path(__file__).parent.parent / "src" / "pydcmview" / "__init__.py"
    content = init_path.read_text()

    new_content = re.sub(
        r'^__version__\s*=\s*["\'][^"\']+["\']',
        f'__version__ = "{new_version}"',
        content,
        flags=re.MULTILINE
    )

    init_path.write_text(new_content)
    print(f"✓ Updated __init__.py to version {new_version}")


def main():
    try:
        # Get current version
        current_version = get_current_version()
        print(f"Current version: {current_version}")

        # Determine bump type (default to patch)
        bump_type = sys.argv[1] if len(sys.argv) > 1 else 'patch'

        # Calculate new version
        new_version = bump_version(current_version, bump_type)

        if new_version == current_version:
            print(f"Version is already {current_version}")
            return 0

        print(f"New version: {new_version}")

        # Update both files
        update_pyproject_toml(new_version)
        update_init_py(new_version)

        print(f"\n✓ Version bumped from {current_version} to {new_version}")
        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
