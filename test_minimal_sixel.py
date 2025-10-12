#!/usr/bin/env python3
"""Minimal test that exactly matches textual-image demo structure."""

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Static
from textual_image.widget import SixelImage, HalfcellImage
import os

TEST_IMAGE = "render_output.png"


class MinimalSixelApp(App):
    """Minimal app to test Sixel rendering."""

    CSS = """
    Container {
        align: center middle;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose the UI."""
        # Check terminal
        term_program = os.environ.get("TERM_PROGRAM", "unknown")

        # Try SixelImage for iTerm2
        if "iterm" in term_program.lower():
            print(f"Detected iTerm2, using SixelImage")
            with Container():
                yield SixelImage(TEST_IMAGE)
        else:
            print(f"Using HalfcellImage for {term_program}")
            with Container():
                yield HalfcellImage(TEST_IMAGE)

        yield Static(f"Terminal: {term_program}", id="status")


def main():
    """Run the test."""
    print("=" * 60)
    print("MINIMAL SIXEL TEST")
    print("=" * 60)
    print()
    print(f"TERM_PROGRAM: {os.environ.get('TERM_PROGRAM', 'not set')}")
    print(f"TERM: {os.environ.get('TERM', 'not set')}")
    print()

    if not os.path.exists(TEST_IMAGE):
        print(f"ERROR: {TEST_IMAGE} not found")
        print("Run: python test_capture_render.py")
        return

    print("Starting app...")
    print()

    app = MinimalSixelApp()
    app.run()


if __name__ == "__main__":
    main()
