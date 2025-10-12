#!/usr/bin/env python3
"""Check what protocol the textual-image demo actually uses."""

import os
import sys

print("=" * 60)
print("CHECK TEXTUAL-IMAGE DEMO PROTOCOL")
print("=" * 60)
print()

print("Environment:")
print(f"  TERM_PROGRAM: {os.environ.get('TERM_PROGRAM', 'not set')}")
print(f"  TERM: {os.environ.get('TERM', 'not set')}")
print(f"  sys.__stdout__.isatty(): {sys.__stdout__.isatty() if sys.__stdout__ else 'N/A'}")
print()

# Import and check
from textual_image.widget import Image as AutoImage
from textual_image import renderable

print("textual_image.renderable.Image class:")
print(f"  {renderable.Image}")
print(f"  Module: {renderable.Image.__module__}")
print(f"  Name: {renderable.Image.__name__}")
print()

print("textual_image.widget.Image (AutoImage):")
print(f"  {AutoImage}")
print()

# Check what the demo's RENDERING_METHODS uses
try:
    from textual_image.demo.widget import RENDERING_METHODS
    print("Demo RENDERING_METHODS:")
    for key, widget_class in RENDERING_METHODS.items():
        print(f"  {key}: {widget_class.__name__}")
    print()

    auto_widget = RENDERING_METHODS['auto']
    print(f"Demo 'auto' selection: {auto_widget.__name__}")
except Exception as e:
    print(f"Could not import demo: {e}")

print()
print("=" * 60)
