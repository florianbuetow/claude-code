---
name: make
description: Make one animated video end to end — intake, story beats, storyboard stills for approval, then scene code, the check loop and the final render.
argument-hint: "[what the video is about]"
disable-model-invocation: true
---

# Make a video

When `scenes/<name>/` already exists, resume at the first unfinished step.

1. Intake: settle subject, type, length, aspect ratio, style (cut paper,
   crosshatch, risograph, sketchbook, isometric, chalkboard math, Swiss
   kinetic typography, or one taken from a reference), audio (a supplied
   track, narration, or a soundtrack written as code), a recurring hero
   character, and references; ask the user for whatever the prompt leaves
   open. The hero is an original design; insert images the user supplies
   as given; from a style reference take only the look, never its
   characters or artwork.
2. Read `../../references/engine.md`; if the project has no engine
   (default `animation/`), build and prove it per that file. Create the
   scene with `node render.mjs new <name>` at the intake's size, fps and
   length.
3. With narration or music, have the track before writing the beats and
   time them to it, because the audio is the clock. With narration, the
   script is the story: write it first, make the track from it (ElevenLabs
   MCP, a local TTS, or the user's recording), and measure its word times
   with faster-whisper into `cues.json`.
4. Write the story as a beat sheet in `scenes/<name>/storyboard.md` and
   agree it with the user.
5. Draw each beat's keyframe in `scene.js`, render one still per beat,
   open the stills for the user, and list each beat beside its still's
   path.
6. Write the full scene code only after the user approves the stills;
   revise beats and stills until they do.
7. Run the check loop in `../../references/check.md` before delivering the
   final render.
