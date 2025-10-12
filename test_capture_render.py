#!/usr/bin/env python3
"""Test that captures the rendered output to an image file for inspection."""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, '/Users/apleynes/dev/pydcmview/src')

from pydcmview.image_loader import ImageLoader
from pydcmview.colormap import ColorMapManager
from PIL import Image as PILImage
import numpy as np

print("=" * 60)
print("RENDER CAPTURE TEST")
print("=" * 60)
print()

# Check if test file exists
test_file = Path("test_volume.nrrd")
if not test_file.exists():
    print(f"Creating test file: {test_file}")
    import SimpleITK as sitk
    size = (64, 64, 64)
    volume = np.zeros(size, dtype=np.float32)
    for z in range(size[2]):
        for y in range(size[1]):
            for x in range(size[0]):
                volume[z, y, x] = (x * y * z) / (size[0] * size[1] * size[2]) * 1000
    sitk_image = sitk.GetImageFromArray(volume)
    sitk.WriteImage(sitk_image, str(test_file))
    print(f"Created test volume with shape {volume.shape}, min={volume.min():.2f}, max={volume.max():.2f}")
    print()

# Load the image
print(f"Loading: {test_file}")
loader = ImageLoader(test_file)
array, shape = loader.load()

print(f"  Shape: {shape}")
print(f"  Data type: {array.dtype}")
print(f"  Min value: {array.min()}")
print(f"  Max value: {array.max()}")
print(f"  Window center: {loader.window_center}")
print(f"  Window width: {loader.window_width}")
print()

# Get a 2D slice (middle slice)
if len(shape) >= 3:
    slice_idx = shape[0] // 2
    slice_2d = array[slice_idx, :, :]
    print(f"Extracting slice {slice_idx} from first dimension")
else:
    slice_2d = array

print(f"  Slice shape: {slice_2d.shape}")
print(f"  Slice min: {slice_2d.min()}")
print(f"  Slice max: {slice_2d.max()}")
print()

# Apply window/level
print("Applying window/level...")
display_array = loader.apply_window_level(slice_2d, loader.window_center, loader.window_width)
print(f"  After W/L min: {display_array.min()}")
print(f"  After W/L max: {display_array.max()}")
print(f"  After W/L dtype: {display_array.dtype}")
print()

# Apply colormap
print("Applying colormap (Grayscale)...")
colormap_manager = ColorMapManager()
rgb_array = colormap_manager.apply_colormap(display_array, "Grayscale")
print(f"  RGB array shape: {rgb_array.shape}")
print(f"  RGB array dtype: {rgb_array.dtype}")
print(f"  RGB min: {rgb_array.min()}")
print(f"  RGB max: {rgb_array.max()}")
print()

# Convert to PIL Image and save
print("Creating PIL Image...")
pil_image = PILImage.fromarray(rgb_array, mode='RGB')
output_path = "render_output.png"
pil_image.save(output_path)
print(f"✓ Saved rendered image to: {output_path}")
print()

# Also save a version with histogram equalization for comparison
print("Creating histogram-equalized version for comparison...")
from PIL import ImageOps
equalized = ImageOps.equalize(pil_image)
equalized.save("render_output_equalized.png")
print(f"✓ Saved equalized image to: render_output_equalized.png")
print()

# Print some statistics about the output
r_channel = np.array(pil_image)[:, :, 0]
g_channel = np.array(pil_image)[:, :, 1]
b_channel = np.array(pil_image)[:, :, 2]

print("Output image statistics:")
print(f"  R channel - min: {r_channel.min()}, max: {r_channel.max()}, mean: {r_channel.mean():.1f}")
print(f"  G channel - min: {g_channel.min()}, max: {g_channel.max()}, mean: {g_channel.mean():.1f}")
print(f"  B channel - min: {b_channel.min()}, max: {b_channel.max()}, mean: {b_channel.mean():.1f}")

# Check if image is all black
if r_channel.max() == 0 and g_channel.max() == 0 and b_channel.max() == 0:
    print("\n⚠️  WARNING: Output image is completely black!")
    print("   This suggests a problem with window/level or colormap application.")
elif r_channel.max() < 10 and g_channel.max() < 10 and b_channel.max() < 10:
    print("\n⚠️  WARNING: Output image is very dark (max pixel value < 10)")
    print("   This suggests the window/level might be incorrect.")
else:
    print("\n✓ Output image appears to have reasonable pixel values.")

print()
print("=" * 60)
print("Inspect the generated images:")
print(f"  - {output_path}")
print(f"  - render_output_equalized.png")
print("=" * 60)
