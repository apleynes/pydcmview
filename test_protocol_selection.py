#!/usr/bin/env python3
"""Test to see what protocol textual-image actually selects."""

import sys
import os

print("=" * 60)
print("PROTOCOL SELECTION TEST")
print("=" * 60)
print()

# Check environment
print("Environment:")
print(f"  TERM: {os.environ.get('TERM', 'not set')}")
print(f"  TERM_PROGRAM: {os.environ.get('TERM_PROGRAM', 'not set')}")
print(f"  COLORTERM: {os.environ.get('COLORTERM', 'not set')}")
print(f"  KITTY_WINDOW_ID: {os.environ.get('KITTY_WINDOW_ID', 'not set')}")
print(f"  sys.__stdout__.isatty(): {sys.__stdout__.isatty() if sys.__stdout__ else 'N/A'}")
print()

# Import and check what gets selected
print("Importing textual_image...")
from textual_image import renderable
from textual_image.widget import Image

print(f"  renderable.Image class: {renderable.Image}")
print(f"  widget.Image class: {Image}")
print()

# Check protocol query functions
print("Protocol support queries:")
try:
    from textual_image.renderable import sixel, tgp
    sixel_support = sixel.query_terminal_support()
    print(f"  Sixel support: {sixel_support}")
except Exception as e:
    print(f"  Sixel support check error: {e}")

try:
    from textual_image.renderable import tgp
    tgp_support = tgp.query_terminal_support()
    print(f"  TGP support: {tgp_support}")
except Exception as e:
    print(f"  TGP support check error: {e}")

print()
print("Selected protocol:")
print(f"  {renderable.Image.__module__}.{renderable.Image.__name__}")
print()

# Try to understand why
if renderable.Image.__name__ == "UnicodeImage":
    print("⚠️  WARNING: UnicodeImage was selected!")
    print("This suggests the terminal is not detected as a TTY or protocol queries failed.")
elif renderable.Image.__name__ == "HalfcellImage":
    print("✓ HalfcellImage selected - this is the expected fallback for most terminals")
elif renderable.Image.__name__ == "SixelImage":
    print("✓ SixelImage selected - excellent quality!")
elif renderable.Image.__name__ == "TGPImage":
    print("✓ TGPImage selected - Kitty graphics protocol!")

print()
print("=" * 60)
