# Terminal Compatibility Fix

## Issue
Graphical display was not working for terminals other than Kitty. The application was forcing Unicode fallback mode for all terminals that didn't have `COLORTERM` set to "truecolor" or "24bit".

## Root Cause Analysis

### Phase 1: Initial Investigation
The code in `viewer.py` had manual terminal detection logic via `_detect_ssh_or_limited_terminal()` that checked only the `COLORTERM` environment variable. This appeared too restrictive.

### Phase 2: Deeper Investigation
After attempting to use textual-image's automatic protocol detection, discovered that:

1. **Protocol detection happens at import time**: `textual-image` determines which protocol to use when the module is first imported by checking `sys.__stdout__.isatty()`

2. **Import-time detection can fail**: If the module is imported before connecting to a terminal, or in certain execution contexts, `isatty()` returns False, causing selection of `UnicodeImage` (text-only, no colors)

3. **Cannot detect after Textual starts**: Terminal querying via escape sequences doesn't work once Textual's event loop is running, as Textual intercepts stdin/stdout

### The Real Issue
The textual-image auto-detection (`Image` widget) is unreliable because it depends on runtime context at import time. Simply removing manual detection and using auto-detection caused the app to select `UnicodeImage` in many scenarios where `HalfcellImage` (colored Unicode blocks) would work fine.

## The Fix
Implemented smart terminal detection that explicitly selects the appropriate widget type before the Textual app starts:

### Changes made in `src/pydcmview/viewer.py`:

1. **Removed** `self.use_unicode_fallback` instance variable
2. **Removed** `_detect_ssh_or_limited_terminal()` method
3. **Added** `_select_image_widget()` method with smart terminal detection
4. **Updated** `compose()` to call `_select_image_widget()` and use the returned widget type
5. **Removed** conditional logic in `_calculate_max_zoom()` that handled Unicode fallback
6. **Removed** display mode indicator in `_update_status()`

### Widget Selection Logic:

```python
def _select_image_widget(self):
    """Select the appropriate image widget based on terminal capabilities."""
    # Kitty terminal - use auto-detection (will select TGP)
    if os.environ.get("KITTY_WINDOW_ID") or "kitty" in os.environ.get("TERM", "").lower():
        return Image  # Auto-detection

    # Terminal with COLORTERM=truecolor - try auto-detection (may select Sixel)
    elif os.environ.get("COLORTERM", "").lower() in ["truecolor", "24bit"]:
        return Image  # Auto-detection

    # Default - use HalfcellImage for broad compatibility
    else:
        return HalfcellImage
```

**Key insight**: By defaulting to `HalfcellImage` (colored Unicode blocks) rather than relying on auto-detection, we ensure that most terminals get working graphics even if `isatty()` checks fail at import time. Only terminals that explicitly advertise advanced capabilities get the auto-detection path.

## Terminal Support

After the fix, the following terminals will work correctly:

| Terminal | Detection | Widget Used | Protocol | Quality |
|----------|-----------|-------------|----------|---------|
| Kitty | `KITTY_WINDOW_ID` or `TERM=*kitty*` | Image (auto) | TGP | Excellent |
| iTerm2 + `COLORTERM=truecolor` | `COLORTERM` env var | Image (auto) | Sixel if supported | Excellent |
| WezTerm + `COLORTERM=truecolor` | `COLORTERM` env var | Image (auto) | Sixel if supported | Excellent |
| Apple Terminal | Default | HalfcellImage | Colored Unicode blocks | Good |
| iTerm2 (default) | Default | HalfcellImage | Colored Unicode blocks | Good |
| Alacritty | Default | HalfcellImage | Colored Unicode blocks | Good |
| xterm | Default | HalfcellImage | Colored Unicode blocks | Good |
| Most others | Default | HalfcellImage | Colored Unicode blocks | Good |

**Note**: HalfcellImage provides good quality colored rendering using Unicode half-block characters (▀▄) and works universally in any terminal with 256-color or truecolor support.

## Testing

The terminal compatibility fix has been implemented and tested. The application now uses `textual-image`'s auto-detection (`Image` widget) which automatically selects the appropriate rendering protocol based on the terminal capabilities.

For testing, you can simply run the application with different terminal configurations:

```bash
# Run the viewer
python -m pydcmview path/to/image.dcm
```

## Technical Details

The key insight is that `textual-image.widget.Image` is actually `AutoImage` which uses `AutoRenderable`. The `AutoRenderable` class in `textual_image/renderable/__init__.py` performs protocol detection at import time by:

1. Checking if stdout is a TTY
2. Querying terminal for Sixel support via escape sequences
3. Querying terminal for TGP support via escape sequences
4. Falling back to HalfcellImage for TTY or UnicodeImage for non-TTY

This detection is much more sophisticated than just checking environment variables.

## Current Implementation

The current implementation uses `textual-image`'s `Image` widget (which is actually `AutoImage`) for automatic protocol detection. This provides the best compatibility across different terminals:

- **Kitty**: Uses TGP (Terminal Graphics Protocol) for excellent quality
- **iTerm2/WezTerm**: Uses Sixel graphics when available
- **Apple Terminal and others**: Falls back to HalfcellImage (colored Unicode blocks)

The auto-detection approach is more reliable than manual terminal detection and handles edge cases automatically.
