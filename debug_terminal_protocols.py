#!/usr/bin/env python3
"""Debug script to test terminal graphics protocol detection."""

import os
import sys
from textual_image.widget import Image, HalfcellImage, UnicodeImage

def print_env_info():
    """Print relevant environment variables."""
    print("=" * 60)
    print("ENVIRONMENT VARIABLES")
    print("=" * 60)

    env_vars = [
        "TERM",
        "TERM_PROGRAM",
        "TERM_PROGRAM_VERSION",
        "COLORTERM",
        "KITTY_WINDOW_ID",
        "ITERM_SESSION_ID",
        "WEZTERM_EXECUTABLE",
        "TMUX",
        "SSH_CONNECTION",
        "SSH_CLIENT",
        "SSH_TTY",
    ]

    for var in env_vars:
        value = os.environ.get(var, "<not set>")
        print(f"{var:25s}: {value}")

    print()

def check_textual_image_protocols():
    """Check which protocols textual-image can detect."""
    print("=" * 60)
    print("TEXTUAL-IMAGE PROTOCOL DETECTION")
    print("=" * 60)

    try:
        # Try to inspect the Image widget to see what protocols it supports
        from textual_image import TerminalImageProtocol

        print(f"Available protocols: {dir(TerminalImageProtocol)}")
        print()

        # Try to get the auto-detected protocol
        try:
            protocol = TerminalImageProtocol.auto()
            print(f"Auto-detected protocol: {protocol}")
        except Exception as e:
            print(f"Error auto-detecting protocol: {e}")

    except ImportError as e:
        print(f"Could not import TerminalImageProtocol: {e}")

    print()

def test_image_widget():
    """Test creating Image widgets with different configurations."""
    print("=" * 60)
    print("IMAGE WIDGET CREATION TEST")
    print("=" * 60)

    try:
        from PIL import Image as PILImage
        import numpy as np

        # Create a simple test image
        test_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        test_image = PILImage.fromarray(test_array, mode='RGB')

        print("Creating Image widget (graphics mode)...")
        try:
            img_widget = Image("")
            img_widget.image = test_image
            print("  ✓ Image widget created successfully")
        except Exception as e:
            print(f"  ✗ Error creating Image widget: {e}")

        print("\nCreating HalfcellImage widget (Unicode blocks)...")
        try:
            halfcell_widget = HalfcellImage("")
            halfcell_widget.image = test_image
            print("  ✓ HalfcellImage widget created successfully")
        except Exception as e:
            print(f"  ✗ Error creating HalfcellImage widget: {e}")

    except Exception as e:
        print(f"Error in test: {e}")

    print()

def check_terminal_capabilities():
    """Check terminal capabilities."""
    print("=" * 60)
    print("TERMINAL CAPABILITIES")
    print("=" * 60)

    # Check if stdout is a TTY
    print(f"stdout is TTY: {sys.stdout.isatty()}")

    # Check terminal size
    try:
        import shutil
        cols, rows = shutil.get_terminal_size()
        print(f"Terminal size: {cols}x{rows}")
    except Exception as e:
        print(f"Could not get terminal size: {e}")

    # Check color support
    term = os.environ.get("TERM", "")
    print(f"TERM value: {term}")
    print(f"256 color support: {'256color' in term or 'xterm' in term}")
    print(f"Truecolor support: {os.environ.get('COLORTERM') in ['truecolor', '24bit']}")

    print()

def main():
    """Run all diagnostic tests."""
    print("\n" + "=" * 60)
    print("TERMINAL GRAPHICS PROTOCOL DIAGNOSTIC TOOL")
    print("=" * 60)
    print()

    print_env_info()
    check_terminal_capabilities()
    check_textual_image_protocols()
    test_image_widget()

    print("=" * 60)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
