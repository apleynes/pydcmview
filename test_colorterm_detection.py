#!/usr/bin/env python3
"""Test to understand COLORTERM and terminal detection better."""

import os
import sys

print("=" * 60)
print("COLORTERM DETECTION TEST")
print("=" * 60)
print()

print("Current environment:")
print(f"  TERM: {os.environ.get('TERM', 'not set')}")
print(f"  TERM_PROGRAM: {os.environ.get('TERM_PROGRAM', 'not set')}")
print(f"  COLORTERM: {os.environ.get('COLORTERM', 'not set')}")
print(f"  KITTY_WINDOW_ID: {os.environ.get('KITTY_WINDOW_ID', 'not set')}")
print()

# Check what the original logic would have done
colorterm = os.environ.get("COLORTERM", "").lower()
would_use_fallback = colorterm not in ["truecolor", "24bit"]

print(f"Original logic would use unicode fallback: {would_use_fallback}")
print()

# Check terminal program
term_program = os.environ.get("TERM_PROGRAM", "").lower()
term = os.environ.get("TERM", "").lower()

print("Terminal identification:")
if "kitty" in term or os.environ.get("KITTY_WINDOW_ID"):
    print("  Detected: Kitty")
    print("  Should use: TGP (auto-detection)")
elif "iterm" in term_program:
    print("  Detected: iTerm2")
    print("  Should try: Sixel, fallback to HalfcellImage")
elif "wezterm" in os.environ.get("WEZTERM_EXECUTABLE", "").lower():
    print("  Detected: WezTerm")
    print("  Should try: Sixel, fallback to HalfcellImage")
elif "apple" in term_program or term_program == "apple_terminal":
    print("  Detected: Apple Terminal")
    print("  Should use: HalfcellImage (no Sixel/TGP support)")
else:
    print(f"  Detected: Unknown terminal ({term_program})")
    print("  Should use: HalfcellImage for safety")

print()
print("=" * 60)
