# PyDCMView

Terminal-based medical image viewer for DICOM, NRRD, and Nifti formats.

## Installation

```bash
pip install -e .
```

## Usage

```bash
pydcmview <path_to_image_file_or_dicom_directory>
```

## Features

- Support for DICOM, NRRD, and Nifti formats
- 2D slice viewing of N-dimensional images
- Slice navigation with arrow keys or vim motion keys (j/k)
- Dimension selection menu (t key) for choosing display axes
- Crosshair mode (c key) with pixel position and intensity display
- Window/level adjustment mode (w key)
- Status bar showing current image information and available keys

## Key Bindings

### Normal Mode
- `q`: Quit application
- `↑/↓` or `j/k`: Navigate through slices
- `t`: Open dimension selection menu
- `c`: Enter crosshair mode
- `w`: Enter window/level mode

### Dimension Selection Menu
- `↑/↓` or `j/k`: Navigate dimensions
- `x`: Assign dimension to X-axis
- `y`: Assign dimension to Y-axis
- `Enter`: Confirm selection
- `Esc`: Cancel

### Crosshair Mode
- `↑/↓/←/→` or `h/j/k/l`: Move crosshair
- `Esc`: Exit crosshair mode

### Window/Level Mode
- `↑/↓` or `j/k`: Adjust window width
- `←/→` or `h/l`: Adjust window center (level)
- `Esc`: Exit window/level mode

## Requirements

- Python 3.8+
- textual>=0.70.0
- rich-pixels>=2.1.0
- SimpleITK>=2.3.0
- numpy>=1.21.0
- pydicom>=2.3.0
- Pillow>=8.0.0