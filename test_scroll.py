#!/usr/bin/env python3
"""Test script to understand textual-image scrolling capabilities."""

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Static
from textual_image.widget import Image
from PIL import Image as PILImage, ImageDraw
import numpy as np

class ScrollTestApp(App):
    """Test app for textual-image scrolling."""
    
    CSS = """
    #image_container {
        width: 40;
        height: 20;
        border: solid red;
    }
    
    #image_display {
        width: 100%;
        height: 100%;
    }
    
    #info {
        dock: bottom;
        height: 5;
    }
    """
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("up", "scroll_up", "Scroll up"),
        ("down", "scroll_down", "Scroll down"),
        ("left", "scroll_left", "Scroll left"),
        ("right", "scroll_right", "Scroll right"),
        ("c", "center", "Center"),
        ("h", "home", "Home"),
        ("i", "info", "Info"),
    ]
    
    def compose(self) -> ComposeResult:
        # Create a large test image (larger than container)
        img = PILImage.new('RGB', (200, 100), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw a grid pattern
        for x in range(0, 200, 20):
            draw.line([(x, 0), (x, 100)], fill='black', width=1)
        for y in range(0, 100, 10):
            draw.line([(0, y), (200, y)], fill='black', width=1)
            
        # Draw some text
        draw.text((10, 10), "Top Left", fill='red')
        draw.text((150, 10), "Top Right", fill='blue')
        draw.text((10, 80), "Bottom Left", fill='green')
        draw.text((130, 80), "Bottom Right", fill='purple')
        draw.text((80, 45), "CENTER", fill='orange')
        
        image_widget = Image(img, id="image_display")
        
        yield Container(image_widget, id="image_container")
        yield Static("Controls: q=quit, arrows=scroll, c=center, h=home, i=info", id="info")
    
    def on_mount(self):
        self.update_info()
    
    def update_info(self):
        """Update info display with current scroll position."""
        image_widget = self.query_one("#image_display", Image)
        info_text = (
            f"Scroll: ({image_widget.scroll_x:.1f}, {image_widget.scroll_y:.1f}) "
            f"Max: ({image_widget.max_scroll_x}, {image_widget.max_scroll_y}) "
            f"Size: {image_widget.size} "
            f"Content: {image_widget.content_size} "
            f"Scrollable: {image_widget.scrollable_size}"
        )
        self.query_one("#info", Static).update(info_text)
    
    def action_scroll_up(self):
        image_widget = self.query_one("#image_display", Image)
        image_widget.scroll_relative(y=-5, animate=False)
        self.update_info()
    
    def action_scroll_down(self):
        image_widget = self.query_one("#image_display", Image)
        image_widget.scroll_relative(y=5, animate=False)
        self.update_info()
    
    def action_scroll_left(self):
        image_widget = self.query_one("#image_display", Image)
        image_widget.scroll_relative(x=-5, animate=False)
        self.update_info()
    
    def action_scroll_right(self):
        image_widget = self.query_one("#image_display", Image)
        image_widget.scroll_relative(x=5, animate=False)
        self.update_info()
    
    def action_center(self):
        """Center the image."""
        image_widget = self.query_one("#image_display", Image)
        # Calculate center position
        center_x = image_widget.max_scroll_x / 2
        center_y = image_widget.max_scroll_y / 2
        image_widget.scroll_to(x=center_x, y=center_y, animate=False)
        self.update_info()
    
    def action_home(self):
        """Go to home position (0,0)."""
        image_widget = self.query_one("#image_display", Image)
        image_widget.scroll_to(x=0, y=0, animate=False)
        self.update_info()
    
    def action_info(self):
        """Print detailed info."""
        image_widget = self.query_one("#image_display", Image)
        print(f"Image size: {image_widget._image_width}x{image_widget._image_height}")
        print(f"Widget size: {image_widget.size}")
        print(f"Content size: {image_widget.content_size}")
        print(f"Scrollable size: {image_widget.scrollable_size}")
        print(f"Current scroll: {image_widget.scroll_offset}")
        print(f"Max scroll: ({image_widget.max_scroll_x}, {image_widget.max_scroll_y})")
        print(f"Scroll bounds: x=[0, {image_widget.max_scroll_x}], y=[0, {image_widget.max_scroll_y}]")
        self.update_info()

if __name__ == "__main__":
    app = ScrollTestApp()
    app.run()