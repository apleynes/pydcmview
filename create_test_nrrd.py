#!/usr/bin/env python3
"""Create a simple test NRRD file for testing the viewer."""

import numpy as np
import SimpleITK as sitk

# Create a simple 3D gradient volume
size = (64, 64, 64)
volume = np.zeros(size, dtype=np.float32)

for z in range(size[2]):
    for y in range(size[1]):
        for x in range(size[0]):
            # Create an interesting pattern
            volume[z, y, x] = (x * y * z) / (size[0] * size[1] * size[2]) * 1000

# Convert to SimpleITK image
sitk_image = sitk.GetImageFromArray(volume)

# Set some metadata
sitk_image.SetSpacing([1.0, 1.0, 1.0])
sitk_image.SetOrigin([0.0, 0.0, 0.0])

# Save as NRRD
output_path = "test_volume.nrrd"
sitk.WriteImage(sitk_image, output_path)
print(f"Created test volume: {output_path}")
print(f"Shape: {volume.shape}")
print(f"Min: {volume.min()}, Max: {volume.max()}")
