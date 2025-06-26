# PyDCMView

Terminal-based medical image viewer for DICOM, NRRD, and Nifti formats with high-quality graphics rendering.

## Installation

```bash
pip install pydcmview
```

## Usage

```bash
pydcmview <path_to_image_file_or_dicom_directory>
```

When using over remote SSH, I've only gotten advanced graphics rendering to work with [kitty](https://sw.kovidgoyal.net/kitty/) with the following remote SSH command
```bash
kitty +kitten ssh <typical_ssh_arguments_here>
```

e.g., `kitty +kitten ssh -p 6000 my_server_address`

With other remote SSH connections, it falls back to Unicode block rendering. Adjust the terminal font zoom to increase/decrease rendering resolution.
Each character block represents 2 pixels.


## Features

- **Format Support**: DICOM, NRRD, and Nifti formats
- **High-Quality Rendering**: Uses textual-image with Sixel and Kitty graphics protocols for superior image quality
- **2D Slice Viewing**: Navigate through N-dimensional images slice by slice
- **Interactive Dimension Selection**: Overlay-based dimension selection with axis assignment and flipping
- **WASD Scrolling**: Pan across images with 5% step size, zoom-aware navigation
- **Zoom Controls**: Zoom in/out functionality with scroll position preservation (0.01x to 20.0x)
- **Crosshair Mode**: Interactive crosshair with adjustable opacity and pixel intensity display
- **Window/Level Adjustment**: Percentage-based contrast and brightness control (1% and 5% increments)
- **Colormap Selection**: Multiple colormap options for enhanced visualization
- **Smart Navigation**: Arrow keys and vim motion keys supported throughout
- **Comprehensive Status Bar**: Real-time display of image info, coordinates, and available commands

## Key Bindings

### Normal Mode
- `q`: Quit application
- `↑/↓` or `j/k`: Navigate through slices
- `w/a/s/d`: Scroll image (up/left/down/right) - 5% of image size per step
- `t`: Toggle dimension selection overlay
- `c`: Enter colormap selection
- `h`: Enter crosshair mode
- `Shift+W`: Enter window/level mode
- `[/]`: Zoom out/in (preserves scroll position)

### Dimension Selection Overlay
- `↑/↓` or `j/k`: Navigate dimensions
- `x`: Assign dimension to X-axis (swaps if already assigned to Y)
- `y`: Assign dimension to Y-axis (swaps if already assigned to X)  
- `f`: Toggle flip for selected dimension (marked with *)
- `Enter`: Confirm and apply changes
- `Esc`: Cancel and return to normal mode

### Crosshair Mode
- `↑/↓/←/→` or `h/j/k/l`: Move crosshair position
- `Shift+↑/↓` or `J/K`: Adjust crosshair opacity
- `Esc`: Exit crosshair mode

### Window/Level Mode
- `↑/↓` or `j/k`: Adjust window width (1% of intensity range)
- `←/→` or `h/l`: Adjust window center/level (1% of intensity range)
- `Shift+↑/↓` or `J/K`: Adjust window width (5% of intensity range)
- `Shift+←/→` or `H/L`: Adjust window center/level (5% of intensity range)
- `Esc`: Exit window/level mode

## Technical Details

### Rendering Engine
- **Primary**: textual-image library with Terminal Graphics Protocol support
- **Fallback**: Unicode block characters for broader terminal compatibility
- **Graphics Protocols**: Sixel (xterm, mintty) and Kitty graphics for high-resolution display

### Navigation and Zoom
- **WASD Scrolling**: 5% of image dimensions per step, scaled with zoom level
- **Zoom Preservation**: Scroll position maintained during zoom operations with bounds checking
- **Zoom Range**: 0.01x to 20.0x with nearest-neighbor interpolation for medical accuracy
- **Smart Constraints**: Automatic scroll boundary enforcement to prevent out-of-bounds navigation

### Dimension Management
- Dynamic axis assignment for N-dimensional data
- Independent dimension flipping with visual indicators
- Automatic slice axis calculation for 3D+ datasets

## Requirements

- Python 3.8+
- textual>=0.70.0
- textual-image>=0.3.0 (replaces rich-pixels for better graphics)
- SimpleITK>=2.3.0
- numpy>=1.21.0
- pydicom>=2.3.0
- Pillow>=8.0.0

## Recent Updates

### Graphics Engine Upgrade
- Migrated from rich-pixels to textual-image for superior rendering quality
- Added support for Sixel and Kitty terminal graphics protocols
- Maintained backward compatibility with Unicode block rendering

### Enhanced Navigation
- **WASD Scrolling**: Added image panning with percentage-based movement (5% of image size)
- **Zoom Position Preservation**: Zoom operations now maintain current view position with bounds checking
- **Improved Window/Level**: Percentage-based adjustments (1% and 5%) relative to image intensity range
- **Colormap Integration**: Multiple colormap options for enhanced medical image visualization
- **Extended Zoom Range**: Increased zoom capability from 5.0x to 20.0x maximum

### UI/UX Improvements
- Real-time status bar updates with zoom level and opacity display
- Context-sensitive key binding hints
- Smooth overlay transitions with semi-transparent backgrounds
- Improved dimension swapping logic for intuitive axis assignment

## Terminal Compatibility

**Best Experience:**
- Kitty terminal (full graphics protocol support)
- iTerm2 (with graphics support)
- xterm with Sixel support

**Good Experience:**
- Most modern terminals (Unicode block fallback)
- Windows Terminal
- GNOME Terminal
- Terminal.app (macOS)
