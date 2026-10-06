# animation

Make motion-graphics videos with Claude and plain JavaScript: no video
generator, no Remotion, no After Effects. **A video is a function of time.**

## Usage

```
/animation:setup
/animation:make a 30-second vertical explainer on how tides work
```

## Skills

| Skill | Purpose |
|-------|---------|
| `animation:setup` | Builds the engine (`draw(ctx, t)` seeked frame by frame in headless Chromium by Playwright, stitched into an MP4 by FFmpeg) and proves it with a 2-second test render |
| `animation:make` | Makes one video: intake, story beats, one storyboard still per beat for approval, then the full scene code, the contact-sheet check loop and the final render |

## How it works

- Every frame is `draw(ctx, t)`. Same t, same picture, so any frame can be
  redrawn or checked on its own.
- `render.mjs` seeks t in headless Chromium and FFmpeg stitches the frames
  into an MP4, muxing the soundtrack when there is one.
- Claude cannot watch the video, so before delivery it reads a contact sheet
  of the whole duration and full-size stills at every beat boundary and
  audio cue, fixes the scene code, and re-renders until a pass finds nothing
  (`references/check.md`).
- `references/engine.md` is the contract both skills share: file layout,
  scene module API, CLI, and the proof `setup` must pass.

## Requirements

Node, FFmpeg with ffprobe, and Playwright's Chromium; `setup` installs what
is missing. Optional: faster-whisper to time visuals to narration, an
ElevenLabs MCP server for voice.

Based on the workflow shown in
[Claude Now Does Video (FOR FREE) Thanks To JavaScript](https://www.youtube.com/watch?v=rscb1DgJtNg).
