# Testing Instructions

## Issue Summary
User reports:
- Mac Terminal: Falls back to "unicode blocks" (unclear if colored or not)
- iTerm2: Shows "just black"

## What Works
The rendering pipeline is confirmed working:
- `render_output.png` shows correct gradient (max value 129/255)
- `render_output_equalized.png` shows enhanced gradient
- Image loading, window/level, and colormap application all work correctly

## Tests to Run

### Test 1: Verify HalfcellImage Widget
Run this in your terminal:
```bash
conda activate pydcmview
python test_halfcell_capture.py
```

**Expected**: You should see a diagonal gradient from dark (top-left) to lighter (bottom-right)

**If you see**:
- ✓ Colored gradient → HalfcellImage is working
- ✗ Black screen → HalfcellImage rendering issue
- ✗ Unicode characters without colors → Terminal color support issue

### Test 2: Check Actual Viewer
```bash
conda activate pydcmview
python test_actual_viewer.py
```

This runs the actual viewer with debug output. Watch for `[DEBUG]` messages showing:
- Slice min/max values
- Window/level settings
- RGB array values

**If RGB max is 0**: Window/level calculation issue
**If RGB max > 0 but black screen**: Widget rendering issue

### Test 3: Simple Gradient Test
```bash
conda activate pydcmview
python test_halfcell_rendering.py
```

This creates a simple red-to-blue gradient from scratch (not loading any file).

### Test 4: Terminal Color Support
Run in each terminal:
```bash
python test_colorterm_detection.py
```

This shows what the terminal advertises for color support.

### Test 5: Check What Widget is Selected
```bash
python verify_widget_selection.py
```

This verifies the widget selection logic is choosing the right widget type.

## Possible Issues

### Issue A: HalfcellImage Requires Specific Color Support
HalfcellImage uses ANSI color codes. If the terminal doesn't support 256-color or truecolor, it won't render correctly.

**Fix**: We may need to add terminal capability detection and use UnicodeImage as fallback for limited terminals.

### Issue B: Image Too Dark
The test shows max pixel value of 129/255, which might appear very dark in some terminals.

**Fix**: Add auto-contrast adjustment or modify window/level calculation.

### Issue C: Terminal Not Detected as TTY
When textual-image imports check `sys.__stdout__.isatty()`, it might return False in some contexts.

**Fix**: Already attempted - we explicitly choose HalfcellImage, but need to verify it's being used.

## Next Steps

1. Run the tests above in both terminals
2. Report back:
   - Which tests show the gradient correctly?
   - Which tests show black or no colors?
   - Any error messages in the debug output?
3. Based on results, we can narrow down if it's:
   - Widget selection issue
   - Widget rendering issue
   - Terminal color support issue
   - Window/level calculation issue
