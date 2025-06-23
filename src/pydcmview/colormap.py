"""Colormap utilities for medical image display."""

import numpy as np
from typing import Dict, List, Tuple
from PIL import Image as PILImage


class ColorMap:
    """Individual colormap definition."""
    
    def __init__(self, name: str, colors: List[Tuple[int, int, int]]):
        """Initialize colormap with name and color list.
        
        Args:
            name: Human-readable name of the colormap
            colors: List of (R, G, B) tuples defining the colormap
        """
        self.name = name
        self.colors = colors
        self._lut = self._create_lookup_table()
    
    def _create_lookup_table(self) -> np.ndarray:
        """Create 256-entry RGB lookup table from color points."""
        if len(self.colors) < 2:
            raise ValueError("Colormap must have at least 2 colors")
        
        # Create lookup table with 256 entries
        lut = np.zeros((256, 3), dtype=np.uint8)
        
        # Interpolate between color points
        n_colors = len(self.colors)
        for i in range(256):
            # Map intensity to position in colormap
            pos = (i / 255.0) * (n_colors - 1)
            idx = int(pos)
            frac = pos - idx
            
            if idx >= n_colors - 1:
                # Last color
                lut[i] = self.colors[-1]
            else:
                # Interpolate between two colors
                c1 = np.array(self.colors[idx])
                c2 = np.array(self.colors[idx + 1])
                lut[i] = (c1 * (1 - frac) + c2 * frac).astype(np.uint8)
        
        return lut
    
    def apply(self, grayscale_array: np.ndarray) -> np.ndarray:
        """Apply colormap to grayscale array.
        
        Args:
            grayscale_array: 2D array with values 0-255
            
        Returns:
            RGB array with shape (H, W, 3)
        """
        # Ensure input is uint8 and in range 0-255
        gray = np.clip(grayscale_array, 0, 255).astype(np.uint8)
        
        # Apply lookup table
        rgb = self._lut[gray]
        return rgb
    
    def get_preview_bar(self, width: int = 64, height: int = 16) -> PILImage.Image:
        """Create a horizontal color bar preview of the colormap.
        
        Args:
            width: Width of the preview bar
            height: Height of the preview bar
            
        Returns:
            PIL Image showing the colormap gradient
        """
        # Create gradient from 0 to 255
        gradient = np.linspace(0, 255, width, dtype=np.uint8)
        gradient_2d = np.tile(gradient, (height, 1))
        
        # Apply colormap
        rgb = self.apply(gradient_2d)
        
        # Convert to PIL Image
        return PILImage.fromarray(rgb, mode='RGB')


class ColorMapManager:
    """Manager for built-in colormaps."""
    
    def __init__(self):
        self.colormaps = self._create_builtin_colormaps()
        self.names = list(self.colormaps.keys())
    
    def _create_builtin_colormaps(self) -> Dict[str, ColorMap]:
        """Create built-in colormaps for medical imaging."""
        colormaps = {}
        
        # Grayscale (default)
        colormaps['Grayscale'] = ColorMap('Grayscale', [
            (0, 0, 0),      # Black
            (255, 255, 255) # White
        ])
        
        # Inverse Grayscale
        colormaps['Inverse Gray'] = ColorMap('Inverse Gray', [
            (255, 255, 255), # White
            (0, 0, 0)        # Black
        ])
        
        # Hot (medical thermal)
        colormaps['Hot'] = ColorMap('Hot', [
            (0, 0, 0),       # Black
            (128, 0, 0),     # Dark red
            (255, 0, 0),     # Red
            (255, 128, 0),   # Orange
            (255, 255, 0),   # Yellow
            (255, 255, 255)  # White
        ])
        
        # Jet (blue to red)
        colormaps['Jet'] = ColorMap('Jet', [
            (0, 0, 128),     # Dark blue
            (0, 0, 255),     # Blue
            (0, 128, 255),   # Light blue
            (0, 255, 255),   # Cyan
            (128, 255, 0),   # Light green
            (255, 255, 0),   # Yellow
            (255, 128, 0),   # Orange
            (255, 0, 0),     # Red
            (128, 0, 0)      # Dark red
        ])
        
        # Cool (cyan to magenta)
        colormaps['Cool'] = ColorMap('Cool', [
            (0, 255, 255),   # Cyan
            (128, 128, 255), # Light blue
            (255, 0, 255)    # Magenta
        ])
        
        # Bone (blue-tinted grayscale)
        colormaps['Bone'] = ColorMap('Bone', [
            (0, 0, 0),       # Black
            (32, 32, 64),    # Dark blue-gray
            (64, 64, 96),    # Blue-gray
            (128, 128, 144), # Light blue-gray
            (192, 192, 208), # Very light blue-gray
            (255, 255, 255)  # White
        ])
        
        # Viridis (perceptually uniform)
        colormaps['Viridis'] = ColorMap('Viridis', [
            (68, 1, 84),     # Dark purple
            (59, 82, 139),   # Blue-purple
            (33, 144, 140),  # Blue-green
            (94, 201, 98),   # Green
            (253, 231, 37)   # Yellow
        ])
        
        # Rainbow
        colormaps['Rainbow'] = ColorMap('Rainbow', [
            (128, 0, 128),   # Purple
            (0, 0, 255),     # Blue
            (0, 255, 255),   # Cyan
            (0, 255, 0),     # Green
            (255, 255, 0),   # Yellow
            (255, 128, 0),   # Orange
            (255, 0, 0)      # Red
        ])
        
        return colormaps
    
    def get_colormap(self, name: str) -> ColorMap:
        """Get colormap by name."""
        if name not in self.colormaps:
            raise ValueError(f"Unknown colormap: {name}")
        return self.colormaps[name]
    
    def get_names(self) -> List[str]:
        """Get list of available colormap names."""
        return self.names.copy()
    
    def apply_colormap(self, grayscale_array: np.ndarray, colormap_name: str) -> np.ndarray:
        """Apply named colormap to grayscale array."""
        colormap = self.get_colormap(colormap_name)
        return colormap.apply(grayscale_array)