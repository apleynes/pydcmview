#!/usr/bin/env python3
"""
Test script to verify terminal graphics protocol detection works correctly.

This script creates a simple test image and displays it using textual-image's
automatic protocol detection to verify that the fix for terminal compatibility
is working correctly.
"""

import numpy as np
from PIL import Image as PILImage
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Static
from textual_image.widget import Image
import sys
import os


class TestImageApp(App):
    """Simple test app to display an image."""

    CSS = """
    #image_container {
        dock: top;
        height: 1fr;
    }

    #status_bar {
        dock: bottom;
        height: 3;
        background: $surface;
    }
    """

    def compose(self) -> ComposeResult:
        """Create the interface."""
        yield Container(Image("", id="image_display"), id="image_container")
        yield Container(Static("", id="status"), id="status_bar")

    def on_mount(self):
        """Initialize the application."""
        try:
            # Create a simple gradient test image
            width, height = 200, 200
            test_array = np.zeros((height, width, 3), dtype=np.uint8)

            # Create a colorful gradient pattern
            for y in range(height):
                for x in range(width):
                    test_array[y, x, 0] = int((x / width) * 255)  # Red gradient
                    test_array[y, x, 1] = int((y / height) * 255)  # Green gradient
                    test_array[y, x, 2] = 128  # Fixed blue

            test_image = PILImage.fromarray(test_array, mode='RGB')

            # Update the image widget
            image_widget = self.query_one("#image_display")
            image_widget.image = test_image

            # Get environment info
            term = os.environ.get("TERM", "unknown")
            term_program = os.environ.get("TERM_PROGRAM", "unknown")
            colorterm = os.environ.get("COLORTERM", "not set")

            # Determine what protocol textual-image would use
            protocol_info = self._detect_protocol()

            status_text = (
                f"Terminal Graphics Protocol Test\n"
                f"TERM: {term} | TERM_PROGRAM: {term_program} | COLORTERM: {colorterm}\n"
                f"Protocol: {protocol_info} | Press 'q' to quit"
            )

            self.query_one("#status", Static).update(status_text)

        except Exception as e:
            self.query_one("#status", Static).update(f"Error: {e}")

    def _detect_protocol(self) -> str:
        """Detect which protocol textual-image is using."""
        try:
            # Check if stdout is a TTY
            is_tty = sys.__stdout__ and sys.__stdout__.isatty()

            if not is_tty:
                return "UnicodeImage (not a TTY)"

            # Try to determine protocol by checking the renderable module
            from textual_image import renderable
            from textual_image.renderable import sixel, tgp

            # This mirrors the logic in textual_image/renderable/__init__.py
            if sixel.query_terminal_support():
                return "SixelImage (best quality)"
            elif tgp.query_terminal_support():
                return "TGP/Kitty Graphics Protocol (best quality)"
            else:
                return "HalfcellImage (Unicode blocks, good compatibility)"

        except Exception as e:
            return f"Unknown (error: {e})"

    def action_quit(self):
        """Quit the application."""
        self.exit()

    BINDINGS = [("q", "quit", "Quit")]


def main():
    """Run the test application."""
    print("=" * 60)
    print("TERMINAL GRAPHICS PROTOCOL TEST")
    print("=" * 60)
    print()
    print("This test will display a gradient image using textual-image's")
    print("automatic protocol detection.")
    print()
    print("Expected behavior by terminal:")
    print("  • Kitty: TGP (Terminal Graphics Protocol)")
    print("  • iTerm2: Sixel (if enabled) or HalfcellImage")
    print("  • WezTerm: Sixel or HalfcellImage")
    print("  • Alacritty, foot: Sixel (if compiled with support)")
    print("  • Others: HalfcellImage (Unicode colored blocks)")
    print()
    print("Press Enter to start the test, or Ctrl+C to cancel...")
    input()

    app = TestImageApp()
    app.run()


if __name__ == "__main__":
    main()
