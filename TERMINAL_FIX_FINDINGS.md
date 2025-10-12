# Terminal Graphics Fix - Findings

## Problem
Graphics display only worked in Kitty terminal (TGP protocol), but failed in iTerm2 (Sixel) and Mac Terminal (HalfCell).

## Root Cause
**CSS `dock: top` and `dock: bottom` broke SixelImage rendering in textual-image.**

The original CSS was:
```css
#image_container {
    dock: top;
    height: 1fr;
    align: center middle;
}

#status_bar {
    dock: bottom;
    height: 3;
    background: $surface;
}
```

This caused SixelImage widgets to fail to render, showing only the status bar.

## Solution
Remove `dock` and use vertical layout instead:
```css
Screen {
    layout: vertical;
}

#image_container {
    height: 1fr;
    align: center middle;
}

#status_bar {
    height: 3;
    background: $surface;
}
```

## Additional Changes Required

1. **Manual widget selection in compose()**: Auto-detection at import time fails for scripts because `sys.__stdout__.isatty()` returns False. Must manually select widget class based on environment variables in `compose()`.

2. **Widget initialization**: Use empty string `""` instead of `None` when creating widget (matches working test pattern).

3. **File path for SixelImage**: SixelImage requires file paths, not PIL Image objects. Must save to temp file and pass path.

4. **Delayed update**: Use `call_after_refresh()` in `on_mount()` to ensure screen is active before first update.

## Terminal Detection Logic
```python
# Check for Kitty
if os.environ.get("KITTY_WINDOW_ID") or "kitty" in os.environ.get("TERM", "").lower():
    ImageWidget = TGPImage
# Check for iTerm2
elif "iterm" in os.environ.get("TERM_PROGRAM", "").lower():
    ImageWidget = SixelImage
# Check for other Sixel terminals
elif "xterm" in os.environ.get("TERM", "").lower():
    ImageWidget = SixelImage
# Default to HalfcellImage
else:
    ImageWidget = HalfcellImage
```

## Why It Works Now
- iTerm2: Uses SixelImage with file paths
- Kitty: Uses TGPImage
- Mac Terminal: Falls back to HalfcellImage (currently needs verification)
- Others: HalfcellImage fallback

The key discovery: **`dock` CSS property is incompatible with textual-image's SixelImage widget rendering.**
