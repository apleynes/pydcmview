"""Main image viewer application using Textual."""

import numpy as np
from pathlib import Path
from typing import Tuple

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Static
from textual.binding import Binding
from textual.screen import Screen
from textual_image.widget import Image
from rich.text import Text

from .image_loader import ImageLoader


class DimensionSelectionScreen(Screen):
    """Screen for selecting display dimensions."""
    
    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "confirm", "Confirm"),
        Binding("up,k", "cursor_up", "Up"),
        Binding("down,j", "cursor_down", "Down"),
        Binding("x", "set_x", "Set X"),
        Binding("y", "set_y", "Set Y"),
    ]
    
    def __init__(self, shape: Tuple[int, ...], current_x: int, current_y: int):
        super().__init__()
        self.shape = shape
        self.current_x = current_x
        self.current_y = current_y
        self.selected_dim = 0
        self.new_x = current_x
        self.new_y = current_y
    
    def compose(self) -> ComposeResult:
        """Create the dimension selection interface."""
        yield Container(
            Static("Select Display Dimensions", id="title"),
            Static(self._get_dimension_text(), id="dimensions"),
            Static("Use ↑↓/jk to navigate, x/y to assign, Enter to confirm, Esc to cancel", id="help"),
            id="dim_container"
        )
    
    def _get_dimension_text(self) -> Text:
        """Generate the dimension selection text."""
        text = Text()
        for i, size in enumerate(self.shape):
            prefix = "→ " if i == self.selected_dim else "  "
            x_marker = " [X]" if i == self.new_x else ""
            y_marker = " [Y]" if i == self.new_y else ""
            
            line = f"{prefix}Dim {i}: size {size}{x_marker}{y_marker}\n"
            if i == self.selected_dim:
                text.append(line, style="bold yellow")
            else:
                text.append(line)
        return text
    
    def action_cursor_up(self):
        """Move cursor up."""
        self.selected_dim = max(0, self.selected_dim - 1)
        self.query_one("#dimensions", Static).update(self._get_dimension_text())
    
    def action_cursor_down(self):
        """Move cursor down."""
        self.selected_dim = min(len(self.shape) - 1, self.selected_dim + 1)
        self.query_one("#dimensions", Static).update(self._get_dimension_text())
    
    def action_set_x(self):
        """Set selected dimension as X axis."""
        if self.selected_dim == self.new_y:
            # If selected dim is already Y, swap X and Y
            self.new_x, self.new_y = self.new_y, self.new_x
        else:
            self.new_x = self.selected_dim
        self.query_one("#dimensions", Static).update(self._get_dimension_text())
    
    def action_set_y(self):
        """Set selected dimension as Y axis."""
        if self.selected_dim == self.new_x:
            # If selected dim is already X, swap X and Y
            self.new_x, self.new_y = self.new_y, self.new_x
        else:
            self.new_y = self.selected_dim
        self.query_one("#dimensions", Static).update(self._get_dimension_text())
    
    def action_confirm(self):
        """Confirm selection."""
        self.dismiss((self.new_x, self.new_y))
    
    def action_cancel(self):
        """Cancel selection."""
        self.dismiss(None)


class ImageViewer(App):
    """Main image viewer application."""
    
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
    
    #dim_container {
        align: center middle;
        width: 60;
        height: auto;
        background: $surface;
        border: solid $primary;
    }
    
    #dim_overlay {
        layer: overlay;
        dock: top;
        height: 100%;
        background: rgba(0, 0, 0, 0.7);
    }
    
    #dim_panel {
        align: center middle;
        width: 60;
        height: auto;
        background: $surface;
        border: solid $primary;
        padding: 1;
    }
    
    .hidden {
        display: none;
    }
    
    #title {
        text-align: center;
        margin: 1;
    }
    
    #dimensions {
        margin: 1;
    }
    
    #help {
        text-align: center;
        margin: 1;
        color: $text-muted;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("up,k", "slice_up", "Previous slice"),
        Binding("down,j", "slice_down", "Next slice"),
        Binding("t", "toggle_dimensions", "Toggle dimensions"),
        Binding("c", "crosshair_mode", "Crosshair mode"),
        Binding("w", "window_level_mode", "Window/Level mode"),
        Binding("plus", "zoom_in", "Zoom in"),
        Binding("minus", "zoom_out", "Zoom out"),
    ]
    
    def __init__(self, image_path: Path):
        super().__init__()
        self.image_path = image_path
        self.loader = None
        self.array = None
        self.shape = None
        self.current_slice = 0
        self.display_x = 0
        self.display_y = 1
        self.slice_axis = None
        self.window_center = None
        self.window_width = None
        self.mode = "normal"  # normal, crosshair, window_level, dimension_select
        self.crosshair_x = 0
        self.crosshair_y = 0
        self.crosshair_opacity = 0.5
        self.zoom_level = 1.0
        # Dimension selection state
        self.dim_selected = 0
        self.dim_new_x = None
        self.dim_new_y = None
        self.dim_flipped = set()  # Set of flipped dimensions
        
    def compose(self) -> ComposeResult:
        """Create the main interface."""
        yield Container(
            Image("", id="image_display"),
            id="image_container"
        )
        yield Container(
            Static("Loading...", id="status"),
            id="status_bar"
        )
        # Dimension selection overlay (initially hidden)
        yield Container(
            Container(
                Static("Select Display Dimensions", id="dim_title"),
                Static("", id="dim_list"),
                Static("Use ↑↓/jk to navigate, x/y to assign, f to flip, Enter to confirm, Esc to cancel", id="dim_help"),
                id="dim_panel"
            ),
            id="dim_overlay",
            classes="hidden"
        )
    
    def on_mount(self):
        """Initialize the application."""
        try:
            self.loader = ImageLoader(self.image_path)
            self.array, self.shape = self.loader.load()
            
            # Set default display axes (two largest dimensions)
            self.display_x, self.display_y = self.loader.get_default_display_axes()
            
            # Determine slice axis (the remaining axis for 3D data)
            if len(self.shape) >= 3:
                all_axes = set(range(len(self.shape)))
                display_axes = {self.display_x, self.display_y}
                remaining_axes = list(all_axes - display_axes)
                self.slice_axis = remaining_axes[0] if remaining_axes else None
            
            self.window_center = self.loader.window_center
            self.window_width = self.loader.window_width
            
            # Initialize crosshair to center
            if len(self.shape) >= 2:
                self.crosshair_x = self.shape[self.display_x] // 2
                self.crosshair_y = self.shape[self.display_y] // 2
            
            self._update_display()
            
        except Exception as e:
            self.query_one("#status", Static).update(f"Error: {e}")
    
    def _get_current_slice(self) -> np.ndarray:
        """Get the current 2D slice for display."""
        if len(self.shape) == 2:
            # 2D image
            slice_2d = self.array
        elif len(self.shape) >= 3 and self.slice_axis is not None:
            # Multi-dimensional image - extract 2D slice
            slice_indices = [slice(None)] * len(self.shape)
            slice_indices[self.slice_axis] = self.current_slice
            slice_nd = self.array[tuple(slice_indices)]
            
            # Transpose to get display axes in correct order
            axes_order = list(range(len(self.shape)))
            if self.slice_axis in axes_order:
                axes_order.remove(self.slice_axis)
            
            # Find positions of display axes in remaining dimensions
            remaining_axes = [ax if ax < self.slice_axis else ax - 1 for ax in [self.display_x, self.display_y] if ax != self.slice_axis]
            
            if len(remaining_axes) >= 2:
                slice_2d = np.transpose(slice_nd, remaining_axes)
            else:
                slice_2d = slice_nd
        else:
            slice_2d = self.array
        
        return slice_2d
    
    def _get_dimension_text(self):
        """Generate the dimension selection text with flipping support."""
        text = Text()
        for i, size in enumerate(self.shape):
            prefix = "→ " if i == self.dim_selected else "  "
            x_marker = " [X]" if i == self.dim_new_x else ""
            y_marker = " [Y]" if i == self.dim_new_y else ""
            flip_marker = " *" if i in self.dim_flipped else ""
            
            line = f"{prefix}Dim {i}: size {size}{x_marker}{y_marker}{flip_marker}\n"
            if i == self.dim_selected:
                text.append(line, style="bold yellow")
            else:
                text.append(line)
        return text
    
    def _show_dimension_overlay(self):
        """Show the dimension selection overlay."""
        self.mode = "dimension_select"
        self.dim_selected = 0
        self.dim_new_x = self.display_x
        self.dim_new_y = self.display_y
        
        # Show overlay
        overlay = self.query_one("#dim_overlay")
        overlay.remove_class("hidden")
        
        # Update dimension list
        self.query_one("#dim_list", Static).update(self._get_dimension_text())
        self._update_status()
    
    def _hide_dimension_overlay(self):
        """Hide the dimension selection overlay."""
        overlay = self.query_one("#dim_overlay")
        overlay.add_class("hidden")
        self.mode = "normal"
        self._update_status()
    
    def _add_crosshair_overlay(self, pil_image):
        """Add red crosshair overlay to the PIL image."""
        from PIL import Image as PILImage, ImageDraw
        
        # Convert to RGBA for transparency support
        if pil_image.mode != 'RGBA':
            pil_image = pil_image.convert('RGBA')
        
        # Create a transparent overlay
        overlay = PILImage.new('RGBA', pil_image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Calculate crosshair position (PIL uses (x, y) coordinates)
        # Account for zoom level
        width, height = pil_image.size
        x = int(self.crosshair_x * self.zoom_level)
        y = int(self.crosshair_y * self.zoom_level)
        
        # Ensure crosshair is within bounds
        if 0 <= x < width and 0 <= y < height:
            # Calculate alpha value (0-255)
            alpha = int(self.crosshair_opacity * 255)
            
            # Draw horizontal line
            draw.line([(0, y), (width - 1, y)], fill=(255, 0, 0, alpha), width=1)
            
            # Draw vertical line  
            draw.line([(x, 0), (x, height - 1)], fill=(255, 0, 0, alpha), width=1)
        
        # Composite the overlay onto the original image
        result = PILImage.alpha_composite(pil_image, overlay)
        return result
    
    def _update_display(self):
        """Update the image display."""
        try:
            slice_2d = self._get_current_slice()
            
            # Apply window/level
            display_array = self.loader.apply_window_level(
                slice_2d, self.window_center, self.window_width
            )
            
            # Convert to PIL Image
            from PIL import Image as PILImage
            pil_image = PILImage.fromarray(display_array, mode='L')  # 'L' for grayscale
            
            # Apply zoom if not 1.0
            if self.zoom_level != 1.0:
                width, height = pil_image.size
                new_width = int(width * self.zoom_level)
                new_height = int(height * self.zoom_level)
                pil_image = pil_image.resize((new_width, new_height), PILImage.Resampling.NEAREST)
            
            # Add crosshair overlay if in crosshair mode
            if self.mode == "crosshair":
                pil_image = self._add_crosshair_overlay(pil_image)
            
            # Update textual-image widget
            image_widget = self.query_one("#image_display", Image)
            image_widget.image = pil_image
            
            self._update_status()
            
        except Exception as e:
            self.query_one("#status", Static).update(f"Display error: {e}")
    
    def _update_status(self):
        """Update the status bar."""
        status_parts = []
        
        # File info
        status_parts.append(f"File: {self.image_path.name}")
        
        # Dimensions
        status_parts.append(f"Shape: {self.shape}")
        
        # Current slice info
        if self.slice_axis is not None and len(self.shape) > 2:
            status_parts.append(f"Slice: {self.current_slice + 1}/{self.shape[self.slice_axis]}")
        
        # Display axes
        status_parts.append(f"Display: X=dim{self.display_x}, Y=dim{self.display_y}")
        
        # Window/Level
        status_parts.append(f"W/L: {self.window_width:.1f}/{self.window_center:.1f}")
        
        # Zoom level
        status_parts.append(f"Zoom: {self.zoom_level:.1f}x")
        
        # Mode-specific info
        if self.mode == "crosshair":
            status_parts.append(f"Crosshair: ({self.crosshair_x}, {self.crosshair_y})")
            status_parts.append(f"Opacity: {self.crosshair_opacity:.1f}")
            # Get intensity value at crosshair
            slice_2d = self._get_current_slice()
            if 0 <= self.crosshair_y < slice_2d.shape[0] and 0 <= self.crosshair_x < slice_2d.shape[1]:
                intensity = slice_2d[self.crosshair_y, self.crosshair_x]
                status_parts.append(f"Intensity: {intensity:.2f}")
        
        # Key bindings based on mode
        if self.mode == "normal":
            keys = "q:Quit | ↑↓/jk:Slice | t:Dims | c:Crosshair | w:W/L | +/- :Zoom"
        elif self.mode == "crosshair":
            keys = "ESC:Exit | ↑↓←→/hjkl:Move crosshair | Shift+↑↓/jk:Opacity"
        elif self.mode == "window_level":
            keys = "ESC:Exit | ↑↓/jk:Window | ←→/hl:Level"
        elif self.mode == "dimension_select":
            keys = "ESC:Exit | ↑↓/jk:Navigate | x/y:Assign | f:Flip | Enter:Confirm"
        else:
            keys = ""
        
        status_text = " | ".join(status_parts) + "\n" + keys
        self.query_one("#status", Static).update(status_text)
    
    def action_slice_up(self):
        """Move to previous slice."""
        if self.mode == "normal" and self.slice_axis is not None:
            self.current_slice = max(0, self.current_slice - 1)
            self._update_display()
        elif self.mode == "crosshair":
            self.crosshair_y = max(0, self.crosshair_y - 1)
            self._update_display()
        elif self.mode == "window_level":
            self.window_width = max(1, self.window_width + 10)
            self._update_display()
    
    def action_slice_down(self):
        """Move to next slice."""
        if self.mode == "normal" and self.slice_axis is not None:
            max_slice = self.shape[self.slice_axis] - 1
            self.current_slice = min(max_slice, self.current_slice + 1)
            self._update_display()
        elif self.mode == "crosshair":
            slice_2d = self._get_current_slice()
            self.crosshair_y = min(slice_2d.shape[0] - 1, self.crosshair_y + 1)
            self._update_display()
        elif self.mode == "window_level":
            self.window_width = max(1, self.window_width - 10)
            self._update_display()
    
    def action_toggle_dimensions(self):
        """Toggle dimension selection overlay."""
        if self.mode == "normal":
            self._show_dimension_overlay()
        elif self.mode == "dimension_select":
            self._hide_dimension_overlay()
    
    def action_crosshair_mode(self):
        """Toggle crosshair mode."""
        if self.mode == "normal":
            self.mode = "crosshair"
            self._update_display()
    
    def action_window_level_mode(self):
        """Toggle window/level mode."""
        if self.mode == "normal":
            self.mode = "window_level"
            self._update_display()
    
    def action_zoom_in(self):
        """Zoom in the image."""
        if self.mode == "normal":
            self.zoom_level = min(5.0, self.zoom_level * 1.2)
            self._update_display()
    
    def action_zoom_out(self):
        """Zoom out the image."""
        if self.mode == "normal":
            self.zoom_level = max(0.1, self.zoom_level / 1.2)
            self._update_display()
    
    def on_key(self, event):
        """Handle additional key events."""
        if event.key == "escape":
            if self.mode in ["crosshair", "window_level"]:
                self.mode = "normal"
                self._update_display()
            elif self.mode == "dimension_select":
                self._hide_dimension_overlay()
        elif self.mode == "dimension_select":
            if event.key in ["up", "k"]:
                self.dim_selected = max(0, self.dim_selected - 1)
                self.query_one("#dim_list", Static).update(self._get_dimension_text())
            elif event.key in ["down", "j"]:
                self.dim_selected = min(len(self.shape) - 1, self.dim_selected + 1)
                self.query_one("#dim_list", Static).update(self._get_dimension_text())
            elif event.key == "x":
                if self.dim_selected == self.dim_new_y:
                    # Swap X and Y if selected dim is already Y
                    self.dim_new_x, self.dim_new_y = self.dim_new_y, self.dim_new_x
                else:
                    self.dim_new_x = self.dim_selected
                self.query_one("#dim_list", Static).update(self._get_dimension_text())
            elif event.key == "y":
                if self.dim_selected == self.dim_new_x:
                    # Swap X and Y if selected dim is already X
                    self.dim_new_x, self.dim_new_y = self.dim_new_y, self.dim_new_x
                else:
                    self.dim_new_y = self.dim_selected
                self.query_one("#dim_list", Static).update(self._get_dimension_text())
            elif event.key == "f":
                # Toggle flip for selected dimension
                if self.dim_selected in self.dim_flipped:
                    self.dim_flipped.remove(self.dim_selected)
                else:
                    self.dim_flipped.add(self.dim_selected)
                self.query_one("#dim_list", Static).update(self._get_dimension_text())
            elif event.key == "enter":
                # Apply changes
                self.display_x, self.display_y = self.dim_new_x, self.dim_new_y
                
                # Update slice axis
                if len(self.shape) >= 3:
                    all_axes = set(range(len(self.shape)))
                    display_axes = {self.display_x, self.display_y}
                    remaining_axes = list(all_axes - display_axes)
                    self.slice_axis = remaining_axes[0] if remaining_axes else None
                    self.current_slice = 0  # Reset to first slice
                
                self._hide_dimension_overlay()
                self._update_display()
        elif self.mode == "crosshair":
            if event.key in ["left", "h"]:
                self.crosshair_x = max(0, self.crosshair_x - 1)
                self._update_display()
            elif event.key in ["right", "l"]:
                slice_2d = self._get_current_slice()
                self.crosshair_x = min(slice_2d.shape[1] - 1, self.crosshair_x + 1)
                self._update_display()
            elif event.key in ["shift+up", "shift+k"]:
                self.crosshair_opacity = min(1.0, self.crosshair_opacity + 0.1)
                self._update_display()
            elif event.key in ["shift+down", "shift+j"]:
                self.crosshair_opacity = max(0.1, self.crosshair_opacity - 0.1)
                self._update_display()
        elif self.mode == "window_level":
            if event.key in ["left", "h"]:
                self.window_center -= 10
                self._update_display()
            elif event.key in ["right", "l"]:
                self.window_center += 10
                self._update_display()