# Phase 5 — Sound Design

Sound is half the perceived quality of an animation. A mediocre scene with great sound feels professional; a great scene with no sound feels like a tech demo. This document gives you a complete, code-only sound studio: synthesized SFX (no asset downloads needed), style-matched palettes, mixing rules, and sync.

**Table of contents**
1. [Sync architecture](#1-sync-architecture) · 2. [Web Audio SFX kit](#2-web-audio-sfx-kit-threejs-path) · 3. [ffmpeg SFX kit](#3-ffmpeg-sfx-kit-blender-path) · 4. [Per-style sound palettes](#4-per-style-sound-palettes) · 5. [Music beds](#5-music-beds) · 6. [Mixing rules](#6-mixing-rules) · 7. [Exporting the mix](#7-exporting-the-mix)

---

## 1. Sync architecture

Sound follows the **timing sheet** from Phase 2 — every row that says "sound cue" becomes a scheduled event:

- Rule of thumb: **whoosh slightly before the action peak (2–4 f), impact exactly on the contact frame, sparkle/reveal right after (1–2 f)**.
- Silence is a tool: leave 6–10 frames of quiet before a big impact so it lands.
- Max 3–4 concurrent layers (SFX + accent + ambience + music). More = mush.
- For loops, every cue must be loop-safe (schedule in loop-local time, same as the pose functions).

## 2. Web Audio SFX kit (Three.js path)

Pure synthesis — zero downloads, always license-clean. Ship as `sound-kit.js` (or inline; the starter template has a compact version):

```js
export const makeSoundKit = (opts = {}) => {
  const ctx = new (window.AudioContext || window.webkitAudioContext)();
  const master = ctx.createGain(); master.gain.value = 0.9;
  const comp = ctx.createDynamicsCompressor();           // gentle bus limiter
  master.connect(comp); comp.connect(ctx.destination);
  const out = master;                                     // also connect to MediaStreamDestination when recording

  const noise = dur => {                                   // shared white-noise source
    const b = ctx.createBuffer(1, ctx.sampleRate * dur, ctx.sampleRate);
    const d = b.getChannelData(0);
    for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;
    const s = ctx.createBufferSource(); s.buffer = b; return s;
  };

  const kit = {};
  kit.pop = (t = 0) => {                                   // soft "pomf" — puffy entrances/UI
    const o = ctx.createOscillator(), g = ctx.createGain(); const t0 = ctx.currentTime + t;
    o.frequency.setValueAtTime(520, t0); o.frequency.exponentialRampToValueAtTime(150, t0 + 0.09);
    g.gain.setValueAtTime(0.5, t0); g.gain.exponentialRampToValueAtTime(0.001, t0 + 0.12);
    o.connect(g).connect(out); o.start(t0); o.stop(t0 + 0.14);
  };
  kit.thud = (t = 0) => {                                  // landings — body, not click
    const t0 = ctx.currentTime + t;
    const o = ctx.createOscillator(), g = ctx.createGain();
    o.frequency.setValueAtTime(95, t0); o.frequency.exponentialRampToValueAtTime(45, t0 + 0.16);
    g.gain.setValueAtTime(0.7, t0); g.gain.exponentialRampToValueAtTime(0.001, t0 + 0.2);
    const n = noise(0.05), ng = ctx.createGain(), lp = ctx.createBiquadFilter();
    lp.type = 'lowpass'; lp.frequency.value = 900; ng.gain.setValueAtTime(0.25, t0);
    n.connect(ng).connect(lp).connect(out); n.start(t0);
    o.connect(g).connect(out); o.start(t0); o.stop(t0 + 0.22);
  };
  kit.whoosh = (t = 0, dur = 0.3) => {                     // movement through air
    const t0 = ctx.currentTime + t;
    const n = noise(dur + 0.05), bp = ctx.createBiquadFilter(), g = ctx.createGain();
    bp.type = 'bandpass'; bp.Q.value = 1.2;
    bp.frequency.setValueAtTime(300, t0); bp.frequency.exponentialRampToValueAtTime(2200, t0 + dur * 0.6);
    bp.frequency.exponentialRampToValueAtTime(400, t0 + dur);
    g.gain.setValueAtTime(0.0001, t0); g.gain.exponentialRampToValueAtTime(0.3, t0 + dur * 0.4);
    g.gain.exponentialRampToValueAtTime(0.001, t0 + dur);
    n.connect(bp).connect(g).connect(out); n.start(t0);
  };
  kit.boing = (t = 0) => {                                 // cartoon spring (puffy/clay)
    const t0 = ctx.currentTime + t;
    const o = ctx.createOscillator(), g = ctx.createGain(); o.type = 'triangle';
    o.frequency.setValueAtTime(300, t0); o.frequency.exponentialRampToValueAtTime(80, t0 + 0.28);
    const lfo = ctx.createOscillator(), lg = ctx.createGain();
    lfo.frequency.value = 18; lg.gain.value = 30; lfo.connect(lg).connect(o.frequency);
    g.gain.setValueAtTime(0.4, t0); g.gain.exponentialRampToValueAtTime(0.001, t0 + 0.3);
    o.connect(g).connect(out); o.start(t0); lfo.start(t0); o.stop(t0 + 0.32); lfo.stop(t0 + 0.32);
  };
  kit.pluck = (t = 0, freq = 523) => {                     // marimba note — puffy/low-poly accents
    const t0 = ctx.currentTime + t;
    const o = ctx.createOscillator(), g = ctx.createGain(), lp = ctx.createBiquadFilter();
    o.type = 'triangle'; o.frequency.value = freq;
    lp.type = 'lowpass'; lp.frequency.value = freq * 3;
    g.gain.setValueAtTime(0.35, t0); g.gain.exponentialRampToValueAtTime(0.001, t0 + 0.35);
    o.connect(lp).connect(g).connect(out); o.start(t0); o.stop(t0 + 0.4);
  };
  kit.sparkle = (t = 0) => {                               // reveals/magic — 3 quick high sines
    [0, 0.05, 0.11].forEach((d, i) => {
      const t0 = ctx.currentTime + t + d;
      const o = ctx.createOscillator(), g = ctx.createGain();
      o.frequency.value = [2093, 2637, 3520][i];
      g.gain.setValueAtTime(0.12, t0); g.gain.exponentialRampToValueAtTime(0.001, t0 + 0.25);
      o.connect(g).connect(out); o.start(t0); o.stop(t0 + 0.27);
    });
  };
  kit.blip = (t = 0, f = 880) => {                         // UI/voxel/neon
    const t0 = ctx.currentTime + t;
    const o = ctx.createOscillator(), g = ctx.createGain(); o.type = 'square';
    o.frequency.setValueAtTime(f, t0); o.frequency.setValueAtTime(f * 1.5, t0 + 0.03);
    g.gain.setValueAtTime(0.15, t0); g.gain.exponentialRampToValueAtTime(0.001, t0 + 0.08);
    o.connect(g).connect(out); o.start(t0); o.stop(t0 + 0.09);
  };
  kit.now = () => ctx.currentTime;
  kit.resume = () => ctx.state === 'suspended' && ctx.resume();
  return kit;
};
```

**Scheduling against the timeline** (loop-safe, fires once per loop pass):

```js
const CUES = [ { t: 0.50, fn: () => kit.pluck(0, 392) },   // anticipation
               { t: 0.75, fn: () => kit.whoosh(0, 0.25) }, // takeoff
               { t: 1.35, fn: () => { kit.thud(); kit.pop(0.02); } } ];
let lastT = -1;
function fireCues(loopT) {
  if (loopT < lastT) lastT = -1;                            // loop wrapped
  for (const c of CUES) if (lastT < c.t && c.t <= loopT) c.fn();
  lastT = loopT;
}
// call fireCues(loopT) inside pose()/render loop — but NOT in ?still=1 deterministic mode
```

Browsers require a user gesture before audio — resume the context on first click/keydown, or when recording starts.

## 3. ffmpeg SFX kit (Blender path)

Blender renders silent; build the soundtrack in post with pure ffmpeg (no assets):

```bash
# thud: low sine with fast decay
ffmpeg -y -f lavfi -i "sine=frequency=90:duration=0.25" \
  -af "afade=t=in:d=0.005,afade=t=out:st=0.02:d=0.22,volume=0.8" thud.wav
# whoosh: filtered pink noise sweep
ffmpeg -y -f lavfi -i "anoisesrc=colour=pink:duration=0.4:amplitude=0.5" \
  -af "bandpass=f=900:w=700,afade=t=in:d=0.12,afade=t=out:st=0.2:d=0.2,volume=0.5" whoosh.wav
# pop: short sine blip with pitch feel via two chained tones
ffmpeg -y -f lavfi -i "sine=frequency=520:duration=0.1" \
  -af "afade=t=out:st=0.01:d=0.09,volume=0.5" pop.wav
# sparkle: high pluck
ffmpeg -y -f lavfi -i "sine=frequency=2093:duration=0.25" \
  -af "afade=t=out:st=0.01:d=0.23,volume=0.25" sparkle.wav
# music-box-ish ambient bed (C major pad, 8 s, quiet)
ffmpeg -y -f lavfi -i "aevalsrc=0.08*sin(2*PI*261.63*t)+0.06*sin(2*PI*329.63*t)+0.05*sin(2*PI*392*t):d=8:s=44100" \
  -af "afade=t=in:d=1,afade=t=out:st=7:d=1" pad.wav
```

**Place cues on the timeline and mix down** (adelay is in milliseconds; one input per cue):

```bash
ffmpeg -y -i silent.mp4 -i whoosh.wav -i thud.wav -i pad.wav -filter_complex "\
[1:a]adelay=900|900,volume=0.9[s1];\
[2:a]adelay=1500|1500[s2];\
[3:a]volume=0.35[bed];\
[s1][s2][bed]amix=inputs=3:normalize=0,alimiter=limit=0.891[aout]" \
-map 0:v -map "[aout]" -c:v copy -c:a aac -b:a 192k -shortest final.mp4
```

`alimiter=limit=0.891` ≈ −1 dBFS ceiling. Loop videos: make the bed exactly `loop_length` seconds and fade it in/out 0.3 s (or crossfade two copies) so audio loops too.

## 4. Per-style sound palettes

| Style | SFX palette | Music bed | Character |
|---|---|---|---|
| Puffy | pop, boing, soft thud, airy whoosh, marimba plucks | music box / lo-fi, major, ~90 BPM | playful, soft |
| Clay | squelch, tap, wooden click, paper | ukulele + glockenspiel ~100 BPM | tactile, warm (+ quiet room tone) |
| Low-poly | marimba arp, soft clicks | clean house / chiptune-lite 110–120 | crisp, positive |
| Voxel | snap, click, 8-bit blips | chiptune 120–140 | toy-like, busy |
| Isometric | birds, breeze, distant chatter, water | music box / ambient 70–90 | quiet (−6 dB vs others) |
| Neon | digital blips, risers, tape stop | synthwave, pulsing bass | loud, driving (−14 LUFS ok) |
| Cel | taiko hits, "shing", vocal blips | dramatic orchestral-pop | punchy, cut-to-beat |
| Glass | glass ping (2–4 kHz sine, fast decay), soft clicks | minimal piano/ambient 70–90 | airy, premium |

## 5. Music beds

Priority order: (1) user-provided track, (2) CC0 library track, (3) synthesized pad (ffmpeg `aevalsrc` chords or a Web Audio pad — two detuned saws through a lowpass is a serviceable analog bed). Never fabricate a "royalty-free" claim about a specific commercial song. State the source in the delivery note. Match bed energy to the style table; duck the bed −6 dB under SFX impacts (volume automation or `sidechaincompress`).

## 6. Mixing rules

- Peaks ≤ −3 dBFS, master ceiling −1 dBFS (limiter), integrated loudness ≈ −16 LUFS (social) / −14 (Neon style ok).
- Fade the master in 0.3–0.5 s and out 0.5 s (except seamless loops: no fades — loop the bed).
- One element owns each moment: don't stack thud + boing + pop on the same frame.
- Test watch once muted (is the animation readable?) and once with sound (does it feel twice as good? if not, re-cut).

## 7. Exporting the mix

- **Three.js live/record path:** connect `master` to `ctx.createMediaStreamDestination()` and add that track to the `canvas.captureStream()` — MediaRecorder then captures video + audio in one pass (code in `pipeline-threejs.md` §7). Note: browser capture = WebM; convert to MP4 with ffmpeg after.
- **Blender path:** silent render + ffmpeg mix (§3) — deterministic and repeatable.
- **Deterministic headless path:** frames → MP4, then ffmpeg mix (§3).
- Always verify in the final container: `ffprobe final.mp4` — duration = spec, audio stream present, sync spot-check at two cue points.
