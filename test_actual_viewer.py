#!/usr/bin/env python3
"""Test the actual viewer with detailed logging."""

import sys
import os

# Add src to path
sys.path.insert(0, '/Users/apleynes/dev/pydcmview/src')

from pydcmview.viewer import ImageViewer
from pathlib import Path

print("=" * 60)
print("ACTUAL VIEWER TEST")
print("=" * 60)
print()

# Check environment
print("Environment:")
print(f"  TERM: {os.environ.get('TERM', 'not set')}")
print(f"  TERM_PROGRAM: {os.environ.get('TERM_PROGRAM', 'not set')}")
print(f"  COLORTERM: {os.environ.get('COLORTERM', 'not set')}")
print()

# Check if test file exists
test_file = Path("test_volume.nrrd")
if not test_file.exists():
    print(f"Error: {test_file} not found")
    print("Run: python create_test_nrrd.py")
    sys.exit(1)

print(f"Loading test file: {test_file}")
print()

# Create viewer and check widget selection
viewer = ImageViewer(test_file)
selected_widget = viewer._select_image_widget()
print(f"Selected widget: {selected_widget.__name__}")
print()

# Monkey-patch to add debug output
original_update_display = viewer._update_display

def debug_update_display():
    """Wrapper to add debug output."""
    try:
        print(f"[DEBUG] _update_display called")
        slice_2d = viewer._get_current_slice()
        print(f"[DEBUG] Slice shape: {slice_2d.shape}")
        print(f"[DEBUG] Slice min: {slice_2d.min()}, max: {slice_2d.max()}")
        print(f"[DEBUG] Window center: {viewer.window_center}, width: {viewer.window_width}")

        # Apply window/level
        display_array = viewer.loader.apply_window_level(
            slice_2d, viewer.window_center, viewer.window_width
        )
        print(f"[DEBUG] After W/L - min: {display_array.min()}, max: {display_array.max()}")

        # Apply colormap
        rgb_array = viewer.colormap_manager.apply_colormap(
            display_array, viewer.current_colormap
        )
        print(f"[DEBUG] After colormap - shape: {rgb_array.shape}, dtype: {rgb_array.dtype}")
        print(f"[DEBUG] RGB min: {rgb_array.min()}, max: {rgb_array.max()}")

    except Exception as e:
        print(f"[DEBUG ERROR] {e}")
        import traceback
        traceback.print_exc()

    return original_update_display()

viewer._update_display = debug_update_display

print("Starting viewer...")
print("Watch for [DEBUG] messages")
print()

try:
    viewer.run()
except Exception as e:
    print(f"\nError running viewer: {e}")
    import traceback
    traceback.print_exc()
