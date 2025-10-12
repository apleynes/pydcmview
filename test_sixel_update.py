#!/usr/bin/env python3
"""Test if SixelImage can be updated after creation."""

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Static
from textual_image.widget import SixelImage
import os

TEST_IMAGE = "render_output.png"


class SixelUpdateApp(App):
    """Test updating SixelImage after creation."""

    CSS = """
    Container {
        align: center middle;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose UI - create EMPTY widget like our main app does."""
        with Container():
            # Create empty widget - this is what our main app does
            yield SixelImage("", id="test_image")
        yield Static("Image should appear after mount", id="status")

    def on_mount(self):
        """Update the image after mount - like our main app."""
        print("on_mount: updating image...")
        try:
            # Get the widget and update it
            image_widget = self.query_one("#test_image")
            image_widget.image = TEST_IMAGE
            print(f"on_mount: set image to {TEST_IMAGE}")

            self.query_one("#status", Static).update(
                f"Image updated to {TEST_IMAGE}. Press q to quit."
            )
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            self.query_one("#status", Static).update(f"Error: {e}")


def main():
    """Run the test."""
    print("=" * 60)
    print("SIXEL UPDATE TEST")
    print("=" * 60)
    print()
    print("This test creates an EMPTY SixelImage widget,")
    print("then updates it in on_mount() - exactly like our main app.")
    print()
    print(f"TERM_PROGRAM: {os.environ.get('TERM_PROGRAM', 'not set')}")
    print()

    if not os.path.exists(TEST_IMAGE):
        print(f"ERROR: {TEST_IMAGE} not found")
        print("Run: python test_capture_render.py")
        return

    print("Starting app...")
    print("If you see the gradient image, SixelImage.image setter works.")
    print("If you see nothing, that's the bug.")
    print()

    app = SixelUpdateApp()
    app.run()


if __name__ == "__main__":
    main()
