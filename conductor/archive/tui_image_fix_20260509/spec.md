# Specification: TUI Image Rendering Fix

## Problem
Images in the TUI appear "blocky" in certain terminals like WezTerm. This is due to `textual-image` falling back to half-block Unicode rendering because it fails to detect terminal support for Sixel or Kitty protocols in time.

## Requirements
- Add a new global setting `image_protocol` to `settings.json`.
- Support the following protocols:
  - `auto`: Default behavior (current `Image` widget).
  - `kitty`: Force Kitty Graphics Protocol (`TGPImage`).
  - `sixel`: Force Sixel Protocol (`SixelImage`).
  - `blocky`: Force Half-block rendering (`HalfcellImage`).
- Expose the setting in the sidebar "Settings" section.
- Ensure images are re-mounted or updated when the protocol setting changes.
