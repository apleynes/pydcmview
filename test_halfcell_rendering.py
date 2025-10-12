#!/usr/bin/env python3
"""Test HalfcellImage rendering directly."""

import numpy as np
from PIL import Image as PILImage
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Static
from textual_image.widget import HalfcellImage, UnicodeImage
import sys


class TestHalfcellApp(App):
    """Test app to verify HalfcellImage rendering."""

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
        yield Container(HalfcellImage("", id="image_display"), id="image_container")
        yield Container(Static("", id="status"), id="status_bar")

    def on_mount(self):
        """Initialize the application."""
        try:
            # Create a simple test gradient - red to blue
            width, height = 100, 100
            test_array = np.zeros((height, width, 3), dtype=np.uint8)

            for y in range(height):
                for x in range(width):
                    test_array[y, x, 0] = int((x / width) * 255)  # Red gradient left to right
                    test_array[y, x, 2] = int((y / height) * 255)  # Blue gradient top to bottom

            test_image = PILImage.fromarray(test_array, mode='RGB')

            # Update the image widget
            image_widget = self.query_one("#image_display")
            image_widget.image = test_image

            status_text = (
                f"HalfcellImage Test | Image size: {width}x{height}\n"
                f"You should see a gradient from red (left) to blue (bottom)\n"
                f"Press 'q' to quit"
            )
            self.query_one("#status", Static).update(status_text)

        except Exception as e:
            import traceback
            self.query_one("#status", Static).update(f"Error: {e}\n{traceback.format_exc()}")

    def action_quit(self):
        """Quit the application."""
        self.exit()

    BINDINGS = [("q", "quit", "Quit")]


def main():
    """Run the test application."""
    print("=" * 60)
    print("HALFCELLIMAGE RENDERING TEST")
    print("=" * 60)
    print()
    print("This will display a simple gradient using HalfcellImage.")
    print("Expected: Colored gradient from red (left) to blue (bottom)")
    print()
    print(f"sys.__stdout__.isatty(): {sys.__stdout__.isatty() if sys.__stdout__ else 'N/A'}")
    print()
    print("Starting app...")
    print()

    app = TestHalfcellApp()
    app.run()


if __name__ == "__main__":
    main()
