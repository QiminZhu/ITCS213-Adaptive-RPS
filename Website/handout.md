# Adaptive Rock–Paper–Scissors — Web UI & Animation Handout
## Summary of HTML, CSS, Media & Canvas Modifications

**Date:** 24 November 2026  
**Target files:** `Website/index.html` and `Website/assets/*`  
**Core model preserved:** 27-entry decaying frequency table (`counts[27]`, `DECAY_SHIFT = 3`, `INCREMENT = 16`, `MAX_ROUNDS = 30`), identical to the Python/MIPS implementation.

---

## 1. Overview of Modifications

Starting from the baseline single-column HTML interface (which rendered static emojis `✊ ✋ ✌️` and plain text outcomes), we upgraded the web application across five areas while keeping the underlying learning algorithm (`update` and `predict`) untouched:

1. **+20% Larger Arena & Layout Scaling:** Expanded the main container, battle stage, and sticker frames across desktop, portrait mobile, compact phones, and landscape viewports without introducing vertical button shift during gameplay.
2. **Exaggerated Matchup Strike Animations (+20% Winner Choice Size):** Replaced static round reveals with hardware-accelerated Web Animations API (WAAPI) fight choreography tailored to each winning rule (`Rock > Scissors`, `Paper > Rock`, `Scissors > Paper`) and increased the winning choice scale by ~20%.
3. **8 Custom Pink Rabbit Reaction Stickers:** Wired images 1–7 to AI round wins via a non-repeating shuffle deck (with a clean spring pop-in inside the battlefield) and reserved image 8 (`"adios..."`) exclusively for whole-game AI victories.
4. **End-of-Game Battlefield Fold Transition:** When Round 30 concludes, `#arena` smoothly folds closed (`perspective(920px) rotateX(0deg → -86deg)` + height collapse) and `#final` unfolds directly in its place.
5. **7-Act 60fps Pink Rabbit Soda-Can Gunslinger Cutscene (Ending Sticker Overlay):** Built a high-DPI HTML5 `<canvas>` finale sequence inside `#final` where generated **Coca-Cola** and **Pepsi** cans are thrown into the sky (~`2.5×` the rabbit's height), the pink rabbit rolls in, tracks & shoots all 4 cans in mid-air with carbonated soda bursts, blows barrel smoke with its mouth, performs a 3× revolver circle spin trick, holsters the gun at its waist, turns to face the screen, and steps directly onto `#finalMedia` to overlay the `"adios..."` ending sticker.

---

## 2. Project File Structure

```text
Website/
├── index.html                      # Complete responsive UI, WAAPI strike engine & 2D Canvas cutscene
├── handout.md                      # Documentation of all HTML/CSS/JS modifications
└── assets/
    ├── ai-round-1-smirk.jpg        # Round win sticker 1: Smug chuckle behind hand
    ├── ai-round-2-boss.jpg         # Round win sticker 2: Suit & tie boss tapping temple
    ├── ai-round-3-glasses.jpg      # Round win sticker 3: Glowing anime glasses
    ├── ai-round-4-laugh.jpg        # Round win sticker 4: Laughing-crying pointing
    ├── ai-round-5-stare.jpg        # Round win sticker 5: Deadpan head tilt
    ├── ai-round-6-judge.jpg        # Round win sticker 6: Unimpressed arms crossed
    ├── ai-round-7-sparkle.jpg      # Round win sticker 7: Sparkling mewing face
    └── ai-final-adios.jpg          # Match win sticker 8: "adios..." whole-game AI victory
```

All 8 images are stored locally inside `assets/` and preloaded on initialization (`new Image()`) so transitions work offline and without network flicker.

---

## 3. Container & Sticker Scaling (+20% Upgrade)

To give the battle choreography and reaction stickers room to breathe while preventing the `Rock` / `Paper` / `Scissors` buttons from jumping vertically between rounds, both the arena container and media frames were scaled up by ~20%:

| Element / Property | Original HTML | Updated `index.html` (+20%) | Purpose |
|---|---|---|---|
| `.wrap` max-width | `520px` (`780px` landscape) | `624px` (`880px` landscape) | Wider horizontal runway for strikes & cutscene |
| `.arena` min-height | `clamp(145px, 24dvh, 210px)` | `clamp(260px, 33dvh, 306px)` (`296px` desktop) | Fits battle stage + sticker banner with zero layout shift |
| `.faces` stage & font | `clamp(38px, 11vw, 58px)` | `clamp(44px, 12vw, 62px)`, `min-height: 98–120px` | Headroom so high-arc jumps never clip at top border |
| Winning hand scale | `1.0x` (static text) | `1.36x` resting (`1.68x–1.84x` peak strike) | +20% visual dominance + golden `.winner-aura` glow |
| Defeated hand scale | `1.0x` (static text) | `0.76x`, `opacity: 0.42`, `grayscale(0.55)` | Clear visual hierarchy between winner and loser |
| Round-win sticker (`.ai-media-wrap`) | None (`84×84px` initial) | `102×102px` (`112×112px` desktop, `78×78px` compact) | Crisp `1:1` frame for pink rabbit round reactions |
| Match-win sticker (`.final-media`) | None (`215px` initial) | `min(260px, 76%)` (`174px` / `160px` compact) | Full uncropped display of `"adios..."` finale |

---

## 4. Exaggerated Winner-Beats-Opponent Animations

Instead of replacing `#faces` with plain text, `showRoundClash()` constructs two `.fighter` stages (`#fYou` and `#fAi`), dynamically measures the pixel distance (`gapPx`) between their `.stage-slot` centers via `getBoundingClientRect()`, and drives GPU-accelerated `translate3d`, `scale`, `rotate`, `skewX`, and `opacity` keyframes over `780ms`:

| Matchup | Action Pill | Winner Motion (`#handYou` / `#handAi`) | Loser Reaction & Impact VFX |
|---|---|---|---|
| **Rock beats Scissors** (`0 > 2`) | `✊ CRUSHES ✌️` | High meteor leap wind-up (`-22px` Y), colossal squash-and-stretch double slam (`scale(1.82, 1.54)`), victory bounce (`1.45x → 1.36x`) | Scissors pancaked flat (`scale(1.56, 0.28)`), double shockwave rings + `💥`, `±7px` arena camera shake |
| **Paper beats Rock** (`1 > 0`) | `✋ COVERS ✊` | Rises wide (`1.30x`), swoops completely over Rock at `1.84x` scale, energetic left-right smother wiggle (`+15° → -12° → +9°`), settles at `1.36x` | Rock compressed to `0.42x` (`opacity: 0.14`) underneath, dashed wrap rings + `💨` |
| **Scissors beats Paper** (`2 > 1`) | `✌️ SLICES ✋` | Deep sword-draw wind-up, rapid twin X-slash combo across Paper (`1.68x` / `1.62x`), victory bounce to `1.36x` | Paper sheared diagonally (`skewX(±38deg)`), crossing blade streaks (`.impact-slash` + `.impact-slash-alt`) + `✂️` |
| **Same move** (`Draw`) | `⚡ CLASH` | Both hands dash `36%` toward center (`1.24x`) and bounce back cleanly (`460ms`) | Central clash badge, neutral `1.0x` settle |

- **Interruptibility:** `clearActiveAnims()` cancels all active WAAPI animations and `<canvas>` frames immediately if the player clicks or presses `R` / `P` / `S` rapidly, ensuring zero input lock.
- **Accessibility:** Respects `@media (prefers-reduced-motion: reduce)` by skipping spatial lunges and shakes while preserving the `1.36x` winner highlight and reaction stickers.

---

## 5. AI-Win Sticker Logic & Battlefield Fold Transition

- **In-Game Round Wins (`result === "ai"`, Rounds 1–29):**
  - Uses `AI_ROUND_WIN_MEDIA` (stickers 1–7) inside `#aiMediaWrap` with a crisp `280ms` spring pop-in (no gunslinger cutscene on in-game stickers).
  - Managed by `drawRoundWinMedia()`, which implements a **Fisher–Yates shuffle-bag** over indices `[0..6]` plus boundary de-duplication (`lastDrawnIdx`) so all 7 stickers are shown before any sticker repeats, with no immediate back-to-back duplicates across reshuffles.
- **End of Round 30 — Battlefield Fold & Summary Replacement:**
  - Once Round 30's clash lands, `finish()` calls `foldArenaIntoFinal()`, which smoothly **folds `#arena` closed** (`perspective(920px) rotateX(0deg → -86deg)` + height collapse) and unfolds `#final` directly in `#arena`'s slot.
  - When `score.ai > score.you`, `#final` displays `AI_FINAL_WIN_MEDIA` (`assets/ai-final-adios.jpg`) inside `#finalMedia` and runs the 7-act Pink Rabbit Soda-Can Gunslinger cutscene overlaying the `"adios..."` ending sticker.

---

## 6. 7-Act Pink Rabbit Soda-Can Gunslinger Cutscene (`<canvas>`)

When the AI wins the 30-round match, `<canvas class="rabbit-canvas" id="rabbitCanvas">` overlays `#final` (`z-index: 13`, scaled to `window.devicePixelRatio` up to `2x`) and executes `renderRabbitCutsceneFrame(t)` across a `5.34s` 60fps timeline:

| Act | Time Window | Choreography & Visual Effects |
|---|---|---|
| **Act 1: Roll In** | `0.18s – 0.78s` | After `#arena` folds and `#final` unfolds in its place, the pastel-pink rabbit (`#f8b7ce` fill, `#d795ae` cel-shadow, `#18181b` ink outline) rolls in from the right edge (`-360°` somersault) kicking up 5 floor dust puffs. |
| **Act 2: 4 Sky-High Soda Can Shots** | `0.68s – 2.48s` | 4 procedurally generated **Coca-Cola** and **Pepsi** cans (`drawSodaCan()`) launch into the sky to **`~2.5×` the rabbit's height**. The rabbit tilts its gaze upward, dynamically tracks each rising can (`Math.atan2`), and fires **4 skyward shots** (`1.18s`, `1.50s`, `1.82s`, `2.14s`) with angled muzzle flashes, golden tracers, shell casings, mid-air can dents, `"BANG!"` starbursts, and pressurized Coke/Pepsi soda splashes. |
| **Act 3: Mouth Blows Smoke** | `2.48s – 3.22s` | Bends elbow to lift the smoking barrel beside its puckered mouth, closes eyelids smugly, and blows wind streaks + 3 expanding smoke rings drifting leftward. |
| **Act 4: Revolver Circle Trick** | `3.22s – 3.88s` | Extends arm forward and spins the revolver 3 full rotations (`1080°`) around its finger with dual silver/gold circular spin-blur trails and a `✦` catch sparkle. |
| **Act 5: Holster to Waist** | `3.88s – 4.26s` | Swings the revolver down into the hip holster on its charcoal waist belt (`#27272a`), leaving the wooden grip peeking out of the pouch with a metallic click glint. |
| **Act 6: Turn & Step to Ending Sticker** | `4.26s – 4.88s` | Smoothly interpolates `yaw` from `-1` (left profile) to `0` (front-facing screen view), steps up-center, and scales into `#finalMedia`'s exact full-body coordinates while `.final-details` fades in below. |
| **Act 7: Overlay Ending Sticker** | `4.80s – 5.34s` | Overlays directly on top of `#finalMedia` (`assets/ai-final-adios.jpg`) as the `"adios..."` ending sticker crossfades `opacity: 0 → 1` beneath it and the canvas cleanly dissolves into the sticker. |
