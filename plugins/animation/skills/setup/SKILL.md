---
name: setup
description: Build the animation engine — a pure draw(ctx, t) seeked frame by frame in headless Chromium and stitched into an MP4 by FFmpeg — and prove it with a 2-second test render.
argument-hint: "[directory, default animation/]"
disable-model-invocation: true
---

# Set up the animation engine

1. Check Node, FFmpeg with ffprobe, and Playwright's Chromium, and install
   what is missing; report whether faster-whisper and an ElevenLabs MCP
   server are available, and ask whether to set either up.
2. Build the engine exactly as `../../references/engine.md` specifies, in
   the directory from the argument (default `animation/`).
3. Run the proof in `engine.md`. Definition of done: every proof step
   passes.
