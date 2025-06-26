"""Main image viewer application using Textual."""

import numpy as np
from pathlib import Path
from typing import Tuple

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Static
from textual.binding import Binding
from textual.screen import ModalScreen
from textual_image.widget import Image, HalfcellImage, UnicodeImage
from rich.text import Text
import os

from .image_loader import ImageLoader
from .colormap import ColorMapManager


class DimensionSelectionScreen(ModalScreen[dict]):
    """Modal screen for dimension selection."""

    CSS = """
    DimensionSelectionScreen {
        align: center middle;
    }
    
    #dim_dialog {
        width: 60;
        height: auto;
        background: $surface;
        border: solid $primary;
        padding: 1;
    }
    
    #dim_title {
        text-align: center;
        margin: 1;
        color: $text;
    }
    
    #dim_list {
        margin: 1;
        min-height: 10;
    }
    
    #dim_help {
        text-align: center;
        margin: 1;
        color: $text-muted;
    }
    """

    BINDINGS = [
        Binding("escape", "dismiss", "Cancel"),
        Binding("up,k", "move_up", "Move up"),
        Binding("down,j", "move_down", "Move down"),
        Binding("x", "assign_x", "Assign X"),
        Binding("y", "assign_y", "Assign Y"),
        Binding("f", "flip_dimension", "Flip"),
        Binding("enter", "confirm", "Confirm"),
    ]

    def __init__(self, shape, current_x, current_y, flipped_dims=None):
        super().__init__()
        self.shape = shape
        self.selected = 0
        self.new_x = current_x
        self.new_y = current_y
        self.flipped = flipped_dims or set()

    def compose(self) -> ComposeResult:
        yield Container(
            Static("Select Display Dimensions", id="dim_title"),
            Static("", id="dim_list"),
            Static(
                "Use ↑↓/jk to navigate, x/y to assign, f to flip, Enter to confirm, Esc to cancel",
                id="dim_help",
            ),
            id="dim_dialog",
        )

    def on_mount(self):
        self._update_dimension_list()

    def _update_dimension_list(self):
        """Update the dimension list display."""
        text = Text()
        for i, size in enumerate(self.shape):
            prefix = "→ " if i == self.selected else "  "
            x_marker = " [X]" if i == self.new_x else ""
            y_marker = " [Y]" if i == self.new_y else ""
            flip_marker = " *" if i in self.flipped else ""

            line = f"{prefix}Dim {i}: size {size}{x_marker}{y_marker}{flip_marker}\n"
            if i == self.selected:
                text.append(line, style="bold yellow")
            else:
                text.append(line)

        self.query_one("#dim_list", Static).update(text)

    def action_move_up(self):
        self.selected = max(0, self.selected - 1)
        self._update_dimension_list()

    def action_move_down(self):
        self.selected = min(len(self.shape) - 1, self.selected + 1)
        self._update_dimension_list()

    def action_assign_x(self):
        if self.selected == self.new_y:
            # Swap if currently assigned to Y
            self.new_x, self.new_y = self.new_y, self.new_x
        else:
            self.new_x = self.selected
        self._update_dimension_list()

    def action_assign_y(self):
        if self.selected == self.new_x:
            # Swap if currently assigned to X
            self.new_x, self.new_y = self.new_y, self.new_x
        else:
            self.new_y = self.selected
        self._update_dimension_list()

    def action_flip_dimension(self):
        if self.selected in self.flipped:
            self.flipped.remove(self.selected)
        else:
            self.flipped.add(self.selected)
        self._update_dimension_list()

    def action_confirm(self):
        """Confirm selection and return results."""
        result = {"x": self.new_x, "y": self.new_y, "flipped": self.flipped}
        self.dismiss(result)

    def action_dismiss(self):
        """Cancel without changes."""
        self.dismiss(None)


class ColormapSelectionScreen(ModalScreen[str]):
    """Modal screen for colormap selection."""

    CSS = """
    ColormapSelectionScreen {
        align: center middle;
    }
    
    #colormap_dialog {
        width: 80;
        height: auto;
        background: $surface;
        border: solid $primary;
        padding: 1;
    }
    
    #colormap_title {
        text-align: center;
        margin: 1;
        color: $text;
    }
    
    #colormap_list {
        margin: 1;
        min-height: 15;
    }
    
    #colormap_help {
        text-align: center;
        margin: 1;
        color: $text-muted;
    }
    """

    BINDINGS = [
        Binding("escape", "dismiss", "Cancel"),
        Binding("up,k", "move_up", "Move up"),
        Binding("down,j", "move_down", "Move down"),
        Binding("enter", "confirm", "Confirm"),
    ]

    def __init__(self, current_colormap: str):
        super().__init__()
        self.colormap_manager = ColorMapManager()
        self.colormap_names = self.colormap_manager.get_names()
        self.selected = 0
        self.current_colormap = current_colormap

        # Set selected to current colormap
        if current_colormap in self.colormap_names:
            self.selected = self.colormap_names.index(current_colormap)

    def compose(self) -> ComposeResult:
        yield Container(
            Static("Select Colormap", id="colormap_title"),
            Static("", id="colormap_list"),
            Static(
                "Use ↑↓/jk to navigate, Enter to confirm, Esc to cancel",
                id="colormap_help",
            ),
            id="colormap_dialog",
        )

    def on_mount(self):
        self._update_colormap_list()

    def _update_colormap_list(self):
        """Update the colormap list display with previews."""
        from textual_image.widget import Image as TextualImage

        text = Text()
        for i, name in enumerate(self.colormap_names):
            prefix = "→ " if i == self.selected else "  "
            current_marker = " [CURRENT]" if name == self.current_colormap else ""

            # Create a simple text representation of the colormap
            # We'll show the colormap name with a visual indicator
            line = f"{prefix}{name}{current_marker}\n"

            if i == self.selected:
                text.append(line, style="bold yellow")
            else:
                text.append(line)

            # Add a colored preview using text characters
            if i < len(self.colormap_names):
                colormap = self.colormap_manager.get_colormap(name)
                # Create a colored gradient preview using block characters
                preview_text = Text("  ")
                for j in range(16):  # 16 character gradient
                    intensity = int(j * 255 / 15)
                    rgb = colormap._lut[intensity]
                    # Convert RGB values to hex color for Rich styling
                    hex_color = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
                    preview_text.append("█", style=hex_color)

                preview_text.append("\n")
                text.append(preview_text)

        self.query_one("#colormap_list", Static).update(text)

    def action_move_up(self):
        self.selected = max(0, self.selected - 1)
        self._update_colormap_list()

    def action_move_down(self):
        self.selected = min(len(self.colormap_names) - 1, self.selected + 1)
        self._update_colormap_list()

    def action_confirm(self):
        """Confirm selection and return selected colormap name."""
        selected_name = self.colormap_names[self.selected]
        self.dismiss(selected_name)

    def action_dismiss(self):
        """Cancel without changes."""
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
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("up,k", "slice_up", "Previous slice"),
        Binding("down,j", "slice_down", "Next slice"),
        Binding("w", "scroll_up", "Scroll up"),
        Binding("a", "scroll_left", "Scroll left"),
        Binding("s", "scroll_down", "Scroll down"),
        Binding("d", "scroll_right", "Scroll right"),
        Binding("t", "toggle_dimensions", "Toggle dimensions"),
        Binding("c", "colormap_mode", "Colormap selection"),
        Binding("h", "crosshair_mode", "Crosshair mode"),
        Binding("W", "window_level_mode", "Window/Level mode"),
        Binding("[", "zoom_out", "Zoom out"),
        Binding("]", "zoom_in", "Zoom in"),
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
        # Scroll offsets for WASD navigation
        self.scroll_x = 0
        self.scroll_y = 0
        # Dimension selection state
        self.dim_selected = 0
        self.dim_new_x = None
        self.dim_new_y = None
        self.dim_flipped = set()  # Set of flipped dimensions
        # Colormap state
        self.colormap_manager = ColorMapManager()
        self.current_colormap = "Grayscale"
        # Image display mode detection
        self.use_unicode_fallback = self._detect_ssh_or_limited_terminal()

    def compose(self) -> ComposeResult:
        """Create the main interface."""
        if self.use_unicode_fallback:
            # Use HalfcellImage for better Unicode block rendering over SSH
            yield Container(HalfcellImage("", id="image_display"), id="image_container")
        else:
            yield Container(Image("", id="image_display"), id="image_container")
        yield Container(Static("Loading...", id="status"), id="status_bar")

    def _detect_ssh_or_limited_terminal(self) -> bool:
        """Detect if we're in a terminal that can't display images properly."""
        # Check if COLORTERM is not set to advanced modes
        colorterm = os.environ.get("COLORTERM", "").lower()
        if colorterm not in ["truecolor", "24bit"]:
            return True

        return False

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
            remaining_axes = [
                ax if ax < self.slice_axis else ax - 1
                for ax in [self.display_x, self.display_y]
                if ax != self.slice_axis
            ]

            if len(remaining_axes) >= 2:
                slice_2d = np.transpose(slice_nd, remaining_axes)
            else:
                slice_2d = slice_nd
        else:
            slice_2d = self.array

        # Apply flipping if any dimensions are flipped
        if self.display_x in self.dim_flipped:
            slice_2d = np.flip(slice_2d, axis=1)  # Flip along x-axis (columns)
        if self.display_y in self.dim_flipped:
            slice_2d = np.flip(slice_2d, axis=0)  # Flip along y-axis (rows)

        return slice_2d

    def _constrain_scroll(self):
        """Constrain scroll offsets to stay within image bounds."""
        try:
            slice_2d = self._get_current_slice()

            # Calculate maximum scroll based on zoomed image size
            zoomed_height = int(slice_2d.shape[0] * self.zoom_level)
            zoomed_width = int(slice_2d.shape[1] * self.zoom_level)

            # Get current display size (we'll use original image size as reference)
            max_scroll_x = max(0, zoomed_width - slice_2d.shape[1])
            max_scroll_y = max(0, zoomed_height - slice_2d.shape[0])

            # Constrain scroll offsets
            self.scroll_x = max(0, min(self.scroll_x, max_scroll_x))
            self.scroll_y = max(0, min(self.scroll_y, max_scroll_y))

        except Exception:
            # If there's any issue, reset scroll to safe values
            self.scroll_x = 0
            self.scroll_y = 0

    def _get_intensity_range(self):
        """Get the intensity range of the current slice."""
        try:
            slice_2d = self._get_current_slice()
            return float(np.min(slice_2d)), float(np.max(slice_2d))
        except Exception:
            return 0.0, 1.0

    def _add_crosshair_overlay(self, pil_image):
        """Add red crosshair overlay to the PIL image."""
        from PIL import Image as PILImage, ImageDraw

        # Convert to RGBA for transparency support
        if pil_image.mode != "RGBA":
            pil_image = pil_image.convert("RGBA")

        # Create a transparent overlay
        overlay = PILImage.new("RGBA", pil_image.size, (0, 0, 0, 0))
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

            # Apply colormap
            rgb_array = self.colormap_manager.apply_colormap(
                display_array, self.current_colormap
            )

            # Convert to PIL Image
            from PIL import Image as PILImage

            pil_image = PILImage.fromarray(rgb_array, mode="RGB")  # 'RGB' for color

            # Apply zoom if not 1.0
            if self.zoom_level != 1.0:
                width, height = pil_image.size
                new_width = int(width * self.zoom_level)
                new_height = int(height * self.zoom_level)
                pil_image = pil_image.resize(
                    (new_width, new_height), PILImage.Resampling.NEAREST
                )

            # Apply scroll offset by cropping the image
            if self.scroll_x > 0 or self.scroll_y > 0:
                width, height = pil_image.size
                left = min(self.scroll_x, width - 1)
                top = min(self.scroll_y, height - 1)
                right = width
                bottom = height
                if left < right and top < bottom:
                    pil_image = pil_image.crop((left, top, right, bottom))

            # Add crosshair overlay if in crosshair mode
            if self.mode == "crosshair":
                pil_image = self._add_crosshair_overlay(pil_image)

            # Update image widget (either HalfcellImage or regular Image)
            image_widget = self.query_one("#image_display")
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
            status_parts.append(
                f"Slice: {self.current_slice + 1}/{self.shape[self.slice_axis]}"
            )

        # Display axes
        status_parts.append(f"Display: X=dim{self.display_x}, Y=dim{self.display_y}")

        # Window/Level
        status_parts.append(f"W/L: {self.window_width:.1f}/{self.window_center:.1f}")

        # Zoom level
        status_parts.append(f"Zoom: {self.zoom_level:.1f}x")

        # Scroll offset
        if self.scroll_x > 0 or self.scroll_y > 0:
            status_parts.append(f"Scroll: ({self.scroll_x}, {self.scroll_y})")

        # Colormap
        status_parts.append(f"Colormap: {self.current_colormap}")

        # Display mode
        if self.use_unicode_fallback:
            status_parts.append("Display: Unicode")
        else:
            status_parts.append("Display: Graphics")

        # Mode-specific info
        if self.mode == "crosshair":
            status_parts.append(f"Crosshair: ({self.crosshair_x}, {self.crosshair_y})")
            status_parts.append(f"Opacity: {self.crosshair_opacity:.1f}")
            # Get intensity value at crosshair
            slice_2d = self._get_current_slice()
            if (
                0 <= self.crosshair_y < slice_2d.shape[0]
                and 0 <= self.crosshair_x < slice_2d.shape[1]
            ):
                intensity = slice_2d[self.crosshair_y, self.crosshair_x]
                status_parts.append(f"Intensity: {intensity:.2f}")

        # Key bindings based on mode
        if self.mode == "normal":
            keys = "q:Quit | ↑↓/jk:Slice | wasd:Scroll | t:Dims | c:Colormap | h:Crosshair | Shift+w:W/L | []:Zoom"
        elif self.mode == "crosshair":
            keys = "ESC:Exit | ↑↓←→/hjkl:Move crosshair | Shift+↑↓/jk:Opacity"
        elif self.mode == "window_level":
            keys = "ESC:Exit | ↑↓/jk:Window(1%) | ←→/hl:Level(1%) | Shift+keys:5%"
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
            min_intensity, max_intensity = self._get_intensity_range()
            intensity_range = max_intensity - min_intensity
            increment = max(1, intensity_range * 0.01)  # 1% of intensity range
            self.window_width = max(1, self.window_width + increment)
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
            min_intensity, max_intensity = self._get_intensity_range()
            intensity_range = max_intensity - min_intensity
            increment = max(1, intensity_range * 0.01)  # 1% of intensity range
            self.window_width = max(1, self.window_width - increment)
            self._update_display()

    def action_toggle_dimensions(self):
        """Show dimension selection modal."""
        if self.mode == "normal":

            def handle_dimension_result(result: dict | None):
                if result:
                    self.display_x = result["x"]
                    self.display_y = result["y"]
                    self.dim_flipped = result["flipped"]

                    # Update slice axis
                    if len(self.shape) >= 3:
                        all_axes = set(range(len(self.shape)))
                        display_axes = {self.display_x, self.display_y}
                        remaining_axes = list(all_axes - display_axes)
                        self.slice_axis = remaining_axes[0] if remaining_axes else None
                        self.current_slice = 0  # Reset to first slice

                    # Reset scroll offsets to prevent out-of-bounds crop
                    self.scroll_x = 0
                    self.scroll_y = 0

                    self._update_display()

            modal = DimensionSelectionScreen(
                self.shape, self.display_x, self.display_y, self.dim_flipped
            )
            self.push_screen(modal, handle_dimension_result)

    def action_colormap_mode(self):
        """Show colormap selection modal."""
        if self.mode == "normal":

            def handle_colormap_result(result: str | None):
                if result:
                    self.current_colormap = result
                    self._update_display()

            modal = ColormapSelectionScreen(self.current_colormap)
            self.push_screen(modal, handle_colormap_result)

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
            old_zoom = self.zoom_level
            self.zoom_level = min(20.0, self.zoom_level * 1.2)
            zoom_factor = self.zoom_level / old_zoom

            # Scale scroll offset proportionally to maintain view position
            self.scroll_x = int(self.scroll_x * zoom_factor)
            self.scroll_y = int(self.scroll_y * zoom_factor)

            # Check bounds and constrain scroll
            self._constrain_scroll()
            self._update_display()

    def action_zoom_out(self):
        """Zoom out the image."""
        if self.mode == "normal":
            old_zoom = self.zoom_level
            self.zoom_level = max(0.01, self.zoom_level / 1.2)
            zoom_factor = self.zoom_level / old_zoom

            # Scale scroll offset proportionally to maintain view position
            self.scroll_x = int(self.scroll_x * zoom_factor)
            self.scroll_y = int(self.scroll_y * zoom_factor)

            # Check bounds and constrain scroll
            self._constrain_scroll()
            self._update_display()

    def action_scroll_up(self):
        """Scroll image up (WASD navigation)."""
        if self.mode == "normal":
            slice_2d = self._get_current_slice()
            scroll_step = max(1, int(slice_2d.shape[0] * 0.05 * self.zoom_level))
            self.scroll_y = max(0, self.scroll_y - scroll_step)
            self._constrain_scroll()
            self._update_display()

    def action_scroll_down(self):
        """Scroll image down (WASD navigation)."""
        if self.mode == "normal":
            slice_2d = self._get_current_slice()
            scroll_step = max(1, int(slice_2d.shape[0] * 0.05 * self.zoom_level))
            self.scroll_y += scroll_step
            self._constrain_scroll()
            self._update_display()

    def action_scroll_left(self):
        """Scroll image left (WASD navigation)."""
        if self.mode == "normal":
            slice_2d = self._get_current_slice()
            scroll_step = max(1, int(slice_2d.shape[1] * 0.05 * self.zoom_level))
            self.scroll_x = max(0, self.scroll_x - scroll_step)
            self._constrain_scroll()
            self._update_display()

    def action_scroll_right(self):
        """Scroll image right (WASD navigation)."""
        if self.mode == "normal":
            slice_2d = self._get_current_slice()
            scroll_step = max(1, int(slice_2d.shape[1] * 0.05 * self.zoom_level))
            self.scroll_x += scroll_step
            self._constrain_scroll()
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

                # Reset scroll offsets to prevent out-of-bounds crop
                self.scroll_x = 0
                self.scroll_y = 0

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
            elif event.key in ["shift+up", "K"]:
                self.crosshair_opacity = min(1.0, self.crosshair_opacity + 0.1)
                self._update_display()
            elif event.key in ["shift+down", "J"]:
                self.crosshair_opacity = max(0.1, self.crosshair_opacity - 0.1)
                self._update_display()
        elif self.mode == "window_level":
            min_intensity, max_intensity = self._get_intensity_range()
            intensity_range = max_intensity - min_intensity

            if event.key in ["left", "h"]:
                increment = max(1, intensity_range * 0.01)  # 1% of intensity range
                self.window_center -= increment
                self._update_display()
            elif event.key in ["right", "l"]:
                increment = max(1, intensity_range * 0.01)  # 1% of intensity range
                self.window_center += increment
                self._update_display()
            elif event.key in ["shift+left", "H"]:
                increment = max(1, intensity_range * 0.05)  # 5% of intensity range
                self.window_center -= increment
                self._update_display()
            elif event.key in ["shift+right", "L"]:
                increment = max(1, intensity_range * 0.05)  # 5% of intensity range
                self.window_center += increment
                self._update_display()
            elif event.key in ["shift+up", "K"]:
                increment = max(1, intensity_range * 0.05)  # 5% of intensity range
                self.window_width = max(1, self.window_width + increment)
                self._update_display()
            elif event.key in ["shift+down", "J"]:
                increment = max(1, intensity_range * 0.05)  # 5% of intensity range
                self.window_width = max(1, self.window_width - increment)
                self._update_display()
