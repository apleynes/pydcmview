#!/usr/bin/env python3
"""Main entry point for PyDCMView."""

import sys
import argparse
from pathlib import Path
from .viewer import ImageViewer


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description="Terminal-based medical image viewer for DICOM, NRRD, and Nifti formats"
    )
    parser.add_argument(
        "path",
        help="Path to image file or DICOM directory"
    )
    
    args = parser.parse_args()
    
    # Check if path exists
    path = Path(args.path)
    if not path.exists():
        print(f"Error: Path does not exist: {path}", file=sys.stderr)
        sys.exit(1)
    
    # If it's a directory, look for DICOM files
    if path.is_dir():
        # Look for common DICOM extensions
        dicom_files = []
        for ext in ['*.dcm', '*.dicom', '*.DCM', '*.DICOM']:
            dicom_files.extend(path.glob(ext))
        
        if not dicom_files:
            print(f"Error: No DICOM files found in directory: {path}", file=sys.stderr)
            sys.exit(1)
        
        # Use the first DICOM file found
        image_path = dicom_files[0]
    else:
        image_path = path
    
    try:
        viewer = ImageViewer(image_path)
        viewer.run()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()