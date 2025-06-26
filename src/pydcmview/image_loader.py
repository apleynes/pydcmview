"""Image loading functionality for DICOM, NRRD, and Nifti formats."""

import SimpleITK as sitk
import numpy as np
import pydicom
from pathlib import Path
from typing import Tuple, Union


class ImageLoader:
    """Handles loading and processing of medical images."""

    SUPPORTED_EXTENSIONS = {".dcm", ".dicom", ".nrrd", ".nii", ".nii.gz"}

    def __init__(self, file_path: Union[str, Path]):
        self.file_path = Path(file_path)
        self.image = None
        self.array = None
        self.window_center = None
        self.window_width = None
        self._validate_file()

    def _validate_file(self):
        """Validate that the file exists and has a supported extension."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")

        if self.file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            # Check for .nii.gz
            if not (
                self.file_path.suffix.lower() == ".gz"
                and self.file_path.with_suffix("").suffix.lower() == ".nii"
            ):
                raise ValueError(
                    f"Unsupported file format. Supported formats: {self.SUPPORTED_EXTENSIONS}"
                )

    def load(self) -> Tuple[np.ndarray, Tuple[int, ...]]:
        """Load the image and return array and shape."""
        try:
            # Load using SimpleITK
            self.image = sitk.ReadImage(str(self.file_path))
            self.array = sitk.GetArrayFromImage(self.image)

            # For DICOM files, try to extract window/level information
            if self.file_path.suffix.lower() in {".dcm", ".dicom"}:
                self._extract_dicom_window_level()

            # If no window/level found, use min/max
            if self.window_center is None or self.window_width is None:
                self._calculate_min_max_window()

            return self.array, self.array.shape

        except Exception as e:
            raise RuntimeError(f"Failed to load image {self.file_path}: {e}")

    def _extract_dicom_window_level(self):
        """Extract window center and width from DICOM metadata."""
        try:
            ds = pydicom.dcmread(str(self.file_path))

            # Check for WindowCenter (0028,1050) and WindowWidth (0028,1051)
            if hasattr(ds, "WindowCenter") and hasattr(ds, "WindowWidth"):
                # Handle multiple values (take first)
                if isinstance(ds.WindowCenter, (list, tuple)):
                    self.window_center = float(ds.WindowCenter[0])
                else:
                    self.window_center = float(ds.WindowCenter)

                if isinstance(ds.WindowWidth, (list, tuple)):
                    self.window_width = float(ds.WindowWidth[0])
                else:
                    self.window_width = float(ds.WindowWidth)

        except Exception:
            # If DICOM reading fails, fall back to min/max
            pass

    def _calculate_min_max_window(self):
        """Calculate window/level from image min/max values."""
        if self.array is not None:
            min_val = float(np.min(self.array))
            max_val = float(np.max(self.array))
            self.window_center = (min_val + max_val) / 2
            self.window_width = max_val - min_val

    def get_default_display_axes(self) -> Tuple[int, int]:
        """Determine the two largest dimensions for default 2D display."""
        if self.array is None:
            raise RuntimeError("Image not loaded")

        shape = self.array.shape
        if len(shape) < 2:
            raise ValueError("Image must have at least 2 dimensions")

        # Find the two dimensions with the largest sizes
        sorted_dims = sorted(enumerate(shape), key=lambda x: x[1], reverse=True)
        return sorted_dims[0][0], sorted_dims[1][0]

    def apply_window_level(
        self, array: np.ndarray, center: float, width: float
    ) -> np.ndarray:
        """Apply window/level to image array for display."""
        min_val = center - width / 2
        max_val = center + width / 2

        # Clip values to window range
        windowed = np.clip(array, min_val, max_val)

        # Normalize to 0-255 for display
        if width > 0:
            windowed = ((windowed - min_val) / width * 255).astype(np.uint8)
        else:
            windowed = np.zeros_like(array, dtype=np.uint8)

        return windowed
