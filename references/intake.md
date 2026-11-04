# Phase 0 — Client Intake

A professional studio never starts rendering on a guess. Ask these questions **before building anything**, batched in one message, each with a recommended default so the user can simply reply "defaults are fine".

## The six questions

1. **Subject** — "What should the animation show? (e.g., a coffee cup revealing steam, a rocket launch, your logo bouncing)"
2. **Duration** — "How long? → 5 s / 8–10 s loop / 15 s / 30 s / other"
3. **Resolution & frame rate** — "What resolution? → 1920×1080 @ 30 fps (landscape) / 1080×1920 @ 30 fps (vertical/Reels) / 1080×1080 (square) / 3840×2160 @ 60 fps (4K)"
4. **Art style** — "Which style? → Puffy & bubbly / Claymation / Low-poly / Voxel / Isometric diorama / Neon cyberpunk / Cel-shaded anime / Frosted glass / Realistic PBR / Cartoon bold / Retro PS1 / Steampunk / Dark fantasy / Minimal flat (see `art-styles.md`, or show the user the live Style Lab at `docs/style-lab/` — one subject, all 14 styles)"
5. **Sound** — "Sound design? → none / SFX only / SFX + music bed"
6. **Output format** — "Deliverable? → MP4 video / WebM / looping GIF / live interactive web page (Three.js) / PNG stills"

### Duration → pacing guidance

| Duration | What fits | Structure |
|---|---|---|
| 5 s | One gag, one reveal | setup (60%) → payoff (40%) |
| 8–10 s | One action with anticipation + settle | intro 1 s → action 5–6 s → settle 1–2 s |
| 15 s | Setup + twist | 3 beats |
| 30 s | Micro-story | 3 acts, 1 camera move per act, 1 "hero moment" |
| ∞ loop | Ambient/idle scene | **Every motion period must divide the loop length exactly** |

### Resolution presets (copy into renderer config)

| Preset | Pixels | fps | Typical use |
|---|---|---|---|
| `fhd` | 1920×1080 | 30 | YouTube, landing pages |
| `vertical` | 1080×1920 | 30 | Reels / Shorts / TikTok |
| `square` | 1080×1080 | 30 | Feed posts |
| `uhd` | 3840×2160 | 60 | Product films (render cost ×4 — warn the user) |
| `preview` | 960×540 | 30 | Lookdev and iteration passes |

## Defaults matrix (user absent, says "you decide", or automated run)

| Setting | Default | Why |
|---|---|---|
| Subject | A puffy blob character doing one charming action | Universal, style-flexible, hard to get wrong |
| Duration | 8 s (perfect loop) | Long enough for a full gag, short enough to iterate |
| Resolution | 1920×1080 @ 30 fps | Universal playback |
| Style | Puffy / Bubbly | Most forgiving, most "wow" per effort |
| Sound | SFX + soft music bed | Sound is half the perceived quality |
| Output | MP4 (+ live HTML if Three.js path) | Plays everywhere |

## Spec receipt (echo back before building)

Always confirm in exactly this compact form:

```
📋 SPEC — 8.0 s (240 f) · 1920×1080 @ 30 fps · Style: Puffy · Sound: SFX + music · Output: MP4 loop
```

If anything is ambiguous after the user's answers (e.g., "make it long-ish"), **pick the nearest preset, state it in the receipt, and proceed** — do not start a second round of questions. Professionals make the call and own it.

## Change requests mid-production

If the user changes duration/resolution after work started: update the *timing sheet first* (scale or re-pad the beat frame ranges), then the render settings, then re-render. Never change render settings without re-checking the timing sheet — a silent 12 s → 8 s trim will cut off the settle and the loop seam.
