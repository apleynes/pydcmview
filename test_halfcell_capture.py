#!/usr/bin/env python3
"""Test HalfcellImage rendering and capture what it produces."""

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Static
from textual_image.widget import HalfcellImage
from PIL import Image as PILImage
import sys
import os

# Add src to path
sys.path.insert(0, '/Users/apleynes/dev/pydcmview/src')


class CaptureHalfcellApp(App):
    """Test app that renders HalfcellImage and exits quickly."""

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

    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path
        self.captured = False

    def compose(self) -> ComposeResult:
        """Create the interface."""
        yield Container(HalfcellImage("", id="image_display"), id="image_container")
        yield Container(Static("", id="status"), id="status_bar")

    def on_mount(self):
        """Initialize and load image."""
        try:
            # Load the image
            pil_image = PILImage.open(self.image_path)
            print(f"Loaded image: {pil_image.size}, mode: {pil_image.mode}")

            # Update the widget
            image_widget = self.query_one("#image_display")
            image_widget.image = pil_image

            status_text = f"HalfcellImage loaded: {pil_image.size}\nPress 'q' to quit"
            self.query_one("#status", Static).update(status_text)

            print("Image set on HalfcellImage widget")
            print("You should see the gradient displayed in the terminal")

        except Exception as e:
            import traceback
            error_msg = f"Error: {e}\n{traceback.format_exc()}"
            print(error_msg)
            self.query_one("#status", Static).update(error_msg)

    def action_quit(self):
        """Quit the application."""
        self.exit()

    BINDINGS = [("q", "quit", "Quit")]


def main():
    """Run the test application."""
    print("=" * 60)
    print("HALFCELLIMAGE CAPTURE TEST")
    print("=" * 60)
    print()

    print("Environment:")
    print(f"  TERM: {os.environ.get('TERM', 'not set')}")
    print(f"  TERM_PROGRAM: {os.environ.get('TERM_PROGRAM', 'not set')}")
    print(f"  sys.__stdout__.isatty(): {sys.__stdout__.isatty() if sys.__stdout__ else 'N/A'}")
    print()

    # Use the rendered output
    image_path = "render_output.png"
    if not os.path.exists(image_path):
        print(f"Error: {image_path} not found")
        print("Run: python test_capture_render.py")
        return

    print(f"Loading rendered image: {image_path}")
    print("This will display it using HalfcellImage widget")
    print()
    print("Expected: You should see a diagonal gradient")
    print("          If you see nothing or black blocks, there's a rendering issue")
    print()

    app = CaptureHalfcellApp(image_path)
    app.run()


if __name__ == "__main__":
    main()
