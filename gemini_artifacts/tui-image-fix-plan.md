# Plan: TUI Image Rendering Fix (WezTerm/High-Res)

## Objective
Introduce explicit control over the image rendering protocol in the TUI to ensure high-resolution images in terminals like WezTerm.

## Background
WezTerm supports high-resolution protocols like Kitty (TGP) and Sixel. However, `textual-image` often fails to detect these capabilities due to timing issues within the Textual app lifecycle, falling back to "blocky" half-block Unicode rendering.

## Technical Details

### 1. `menu.py` Enhancements
- **Imports:** Import `SixelImage`, `TGPImage`, and `HalfcellImage` from `textual_image.widget`.
- **Dynamic Mounting:** Modify `TaiMenu.compose` and `update_sidebar` to use a factory-style selection based on the `image_protocol` setting.
- **Factory Logic:**
  - `auto` -> Use standard `Image` (AutoImage).
  - `kitty` -> Use `TGPImage`.
  - `sixel` -> Use `SixelImage`.
  - `blocky` -> Use `HalfcellImage`.

### 2. Settings Integration
- Add `image_protocol` to the sidebar "Settings" section as a `Select` widget.
- Options: `[("Auto-Detect", "auto"), ("Kitty (High-Res)", "kitty"), ("Sixel (High-Res)", "sixel"), ("Blocky (Fallback)", "blocky")]`.

## Implementation Steps
1. Update `menu.py` imports.
2. Add the "Image Protocol" Select widget to the sidebar.
3. Update `update_sidebar` logic to re-instantiate widgets if the protocol changes (or handle it via reactive properties if possible).
4. Update `engines/config.py` default settings.

## Verification
1. Open t.ai in WezTerm.
2. Change "Image Protocol" to "Kitty".
3. Verify that the avatar image becomes sharp/high-resolution.
