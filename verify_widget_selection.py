#!/usr/bin/env python3
"""Verify that the widget selection logic works correctly."""

import os
import sys

# Add src to path so we can import the viewer
sys.path.insert(0, '/Users/apleynes/dev/pydcmview/src')

from textual_image.widget import Image, HalfcellImage
from pydcmview.viewer import ImageViewer
from pathlib import Path

print("=" * 60)
print("WIDGET SELECTION VERIFICATION")
print("=" * 60)
print()

# Test with current environment
print("Current environment:")
print(f"  TERM: {os.environ.get('TERM', 'not set')}")
print(f"  TERM_PROGRAM: {os.environ.get('TERM_PROGRAM', 'not set')}")
print(f"  COLORTERM: {os.environ.get('COLORTERM', 'not set')}")
print(f"  KITTY_WINDOW_ID: {os.environ.get('KITTY_WINDOW_ID', 'not set')}")
print()

# Create a dummy viewer instance to test the selection logic
test_path = Path("/tmp/dummy.nrrd")  # Doesn't need to exist for this test
viewer = ImageViewer(test_path)

# Test the widget selection
selected_widget = viewer._select_image_widget()
print(f"Selected widget type: {selected_widget.__name__}")

if selected_widget == HalfcellImage:
    print("✓ Correctly selected HalfcellImage for broad compatibility")
elif selected_widget == Image:
    print("✓ Selected Image (auto-detection) for advanced protocol support")
else:
    print(f"⚠️  Selected unknown widget: {selected_widget}")

print()

# Test different scenarios
print("Testing different environment scenarios:")
print()

scenarios = [
    {
        "name": "Apple Terminal (default)",
        "env": {"TERM": "xterm-256color", "TERM_PROGRAM": "Apple_Terminal"},
        "expected": HalfcellImage
    },
    {
        "name": "Kitty Terminal",
        "env": {"TERM": "xterm-kitty", "KITTY_WINDOW_ID": "1"},
        "expected": Image
    },
    {
        "name": "Terminal with COLORTERM=truecolor",
        "env": {"TERM": "xterm-256color", "COLORTERM": "truecolor"},
        "expected": Image
    },
    {
        "name": "iTerm2 without COLORTERM",
        "env": {"TERM": "xterm-256color", "TERM_PROGRAM": "iTerm.app"},
        "expected": HalfcellImage
    },
]

for scenario in scenarios:
    # Save current env
    saved_env = {}
    for key in ["TERM", "TERM_PROGRAM", "COLORTERM", "KITTY_WINDOW_ID"]:
        saved_env[key] = os.environ.get(key)
        if key in os.environ:
            del os.environ[key]

    # Set test env
    for key, value in scenario["env"].items():
        os.environ[key] = value

    # Test selection
    viewer_test = ImageViewer(test_path)
    selected = viewer_test._select_image_widget()

    # Check result
    if selected == scenario["expected"]:
        print(f"✓ {scenario['name']}: {selected.__name__}")
    else:
        print(f"✗ {scenario['name']}: got {selected.__name__}, expected {scenario['expected'].__name__}")

    # Restore env
    for key, value in saved_env.items():
        if value is not None:
            os.environ[key] = value
        elif key in os.environ:
            del os.environ[key]

print()
print("=" * 60)
