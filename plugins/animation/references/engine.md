# Engine contract

```
animation/                        # default location; setup takes another dir as an argument
  package.json                    # "type": "module"; devDependency: playwright
  render.mjs                      # the only CLI
  player.html                     # loads scenes/<name>/scene.js; window.seek(t) resolves after frame t is drawn
  lib/                            # small pure helpers: seeded random, easing, clamp/lerp, between(t, a, b)
  scenes/<name>/scene.js          # export const config = { width, height, fps, duration }
                                  # export async function setup(ctx, config)  — preload fonts/images, precompute
                                  # export function draw(ctx, t, config)      — pure: pixels depend only on t
  scenes/<name>/assets/           # images, fonts
  scenes/<name>/audio.wav|.mp3    # optional; muxed into the MP4 when present
  scenes/<name>/cues.json         # optional; named times measured from the audio, imported by scene.js
  scenes/<name>/storyboard.md     # beats: time range, what is on screen, the still's time
  out/<name>/<name>.mp4           # renders
  out/<name>/stills/              # single frames
  out/<name>/sheet.png            # contact sheet

node render.mjs new <name> [--size 1920x1080|1080x1920|1080x1080] [--fps 60] [--duration 15]
node render.mjs <name>                  # full render → out/<name>/<name>.mp4 (+ audio)
node render.mjs <name> --at 1.5,4,9     # stills → out/<name>/stills/
node render.mjs <name> --sheet          # contact sheet from the MP4: FFmpeg pulls the frames, a canvas in
                                        # headless Chromium tiles them and labels each with its time
```

`draw` is pure: time comes only from `t`, randomness only from the seeded
random in `lib/`, and state that builds up over time is simulated from 0 or
precomputed in `setup`.

## Proof

On a scene made with `node render.mjs new test --duration 2`:

1. `node render.mjs test` writes an MP4 that ffprobe reports as h264,
   yuv420p, 2.0 s, 60 fps, 120 frames.
2. With a 2-second `audio.wav` in `scenes/test/`, the re-rendered MP4 also
   has an audio stream of 2.0 s.
3. Same t, same picture: hash the still for t = 1 from `--at 1`, then run
   `--at 1.9,1`; the new still for t = 1 has the same hash.
4. `--sheet` writes its file.
