# Phase 2: Image Attachments

**Status:** 📋 Planned  
**Gate:** Phase 1 chat working (message send/receive)  
**Spec source:** `POLLY_IOS_SPEC.md` §4.6.2  
**Owners:** @frontend

## Goal

Attach images to messages from camera or photo library. Images encoded and sent with the message context. Rendered inline in chat.

## Tasks

### Attachment Picker
- [ ] `+` menu in InputBar: Camera, Photo Library, Files (document picker)
- [ ] Camera: `expo-camera` permission — contextual (trigger: first time user taps Camera)
- [ ] Photo library: `expo-image-picker` — contextual
- [ ] Multi-image selection (up to 4 per message)
- [ ] Image preview strip above InputBar before send

### Encoding + Send
- [ ] Resize to max 1024px (longest edge) before encode — reduces context overhead
- [ ] Base64 encode for gateway send
- [ ] Size validation: warn if >1MB per image after resize
- [ ] Send with message text + image data in `params.images[]`

### Rendering
- [ ] Inline image rendering in ChatBubble (tappable → full-screen viewer)
- [ ] Full-screen viewer: pinch-to-zoom, share, save to photos
- [ ] Loading placeholder while image decodes
- [ ] Broken image fallback

### Lockdown Mode
- [ ] Image attachments permitted in Lockdown Mode (local camera/photos, no cloud)
- [ ] No metadata strip required (images already local)

## Done When
Camera + photo library attachment works. Images render inline. Full-screen viewer. @qa_guy confirms multi-image attach flow.
