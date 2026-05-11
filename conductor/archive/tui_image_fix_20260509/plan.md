# Implementation Plan: TUI Image Rendering Fix

## Objective
Enable explicit image protocol selection in the TUI to resolve blocky image issues in terminals like WezTerm.

## Steps
1. **Update `menu.py` Imports:**
   - Import `SixelImage`, `TGPImage`, `HalfcellImage` from `textual_image.widget`.

2. **Implement Widget Factory:**
   - Create a helper method in `TaiMenu` to yield the correct image widget based on the `image_protocol` setting.

3. **Update Sidebar UI:**
   - Add a "Image Protocol" `Select` widget to the sidebar.
   - Populate it with `["auto", "kitty", "sixel", "blocky"]`.

4. **Handle Setting Changes:**
   - Implement logic in `on_select_changed` to update the `image_protocol` setting.
   - Trigger a re-composition or replacement of the avatar widgets when the protocol changes.

## Verification
- Test in WezTerm by forcing `kitty` or `sixel` and verifying the image becomes high-resolution.
- Test in a standard console (like CMD) with `blocky` to ensure it still works as a fallback.
