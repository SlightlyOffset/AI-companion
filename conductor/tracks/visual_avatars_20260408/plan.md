# Implementation Plan - Visual Avatar Integration

## Phase 1: Environment & Profile Setup [checkpoint: 4280bd7]
- [x] Verify `chafa` availability in the system path. 9b7fabf
- [x] Add `avatar_path` to at least one character profile (e.g., Astgenne). 9b7fabf
- [x] Implement a `render_avatar` utility that calls Chafa (Sixel) and returns an ANSI string. a043a74

## Phase 2: UI Integration
- [ ] Update `TaiMenu.compose` to include an `#avatar_portrait` widget in the sidebar.
- [ ] Update `load_initial_state` to trigger avatar rendering on startup.
- [ ] Update CSS to ensure the portrait has proper padding and alignment.

## Phase 3: Enhanced Visuals
- [ ] Add a decorative frame around the terminal art.
- [ ] Implement expression-swapping (optional): Use different images based on mood score.

## Phase 4: Validation
- [ ] Test with different image formats (PNG, JPG).
- [ ] Verify behavior on terminals with limited color support.
