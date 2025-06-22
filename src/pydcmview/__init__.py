"""PyDCMView - Terminal-based medical image viewer for DICOM, NRRD, and Nifti formats.

A high-quality terminal-based medical image viewer with support for:
- DICOM, NRRD, and Nifti formats
- High-quality rendering using textual-image with Sixel and Kitty graphics protocols
- Interactive crosshair mode with adjustable opacity
- Zoom controls and dimension management
- Overlay-based dimension selection with flipping support
"""

__version__ = "0.1.0"
__author__ = "Andrew P. Leynes"
__email__ = "andrew.leynes@example.com"
__license__ = "MIT"

# Main imports for convenience
from .main import main
from .viewer import ImageViewer
from .image_loader import ImageLoader

__all__ = [
    "main",
    "ImageViewer", 
    "ImageLoader",
    "__version__",
    "__author__",
    "__email__",
    "__license__",
]