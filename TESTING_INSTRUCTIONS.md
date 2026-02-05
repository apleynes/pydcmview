# Testing Instructions

## Current Status
The terminal compatibility issues have been resolved. The application now uses `textual-image`'s automatic protocol detection which provides broad compatibility across different terminals.

## Testing the Application

### Basic Test
```bash
# Run the viewer with a test image
python -m pydcmview test_volume.nrrd
```

**Expected**: You should see the medical image displayed with appropriate colors and contrast.

### Test with Different Terminals
Try running the application in different terminals to verify compatibility:

- **Kitty**: Should use TGP protocol for excellent quality
- **iTerm2/WezTerm**: Should use Sixel graphics when available  
- **Apple Terminal**: Should use HalfcellImage (colored Unicode blocks)
- **Other terminals**: Should fall back to HalfcellImage

### Create Test Data
If you need to create test data:
```bash
python create_test_nrrd.py
```

This creates a `test_volume.nrrd` file with sample medical imaging data.

## Troubleshooting

### If Images Appear Black
1. Check if the terminal supports 256-color or truecolor
2. Try adjusting the window/level settings (Shift+W to enter window/level mode)
3. Verify the image file is valid and contains meaningful data

### If Images Appear Too Dark
The test data has a max value of 129/255 which may appear dark. You can:
- Adjust window/level settings interactively
- Use the equalized colormap for better contrast

### If No Graphics Display
1. Ensure your terminal supports graphics protocols (TGP, Sixel, or at least 256-color)
2. Try a different terminal (Kitty, iTerm2, or Apple Terminal)
3. Check terminal environment variables (TERM, COLORTERM)

## Technical Details

The application uses `textual-image`'s `Image` widget which automatically detects and uses the best available protocol:
- TGP (Terminal Graphics Protocol) for Kitty
- Sixel graphics for iTerm2/WezTerm and other compatible terminals
- HalfcellImage (colored Unicode blocks) as fallback for broad compatibility

This auto-detection is more reliable than manual terminal detection and handles most edge cases automatically.
