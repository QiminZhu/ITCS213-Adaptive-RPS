# Adaptive Rock–Paper–Scissors (MIPS Class Project)

> **Course Project — ITCS213: Computer Organization and Architecture (MIPS Assembly)**  
> *"The more you play, the more it learns your patterns."* 🐾  
> **Live Web Demo (GitHub Pages):** [https://qiminzhu.github.io/ITCS213-Adaptive-RPS/](https://qiminzhu.github.io/ITCS213-Adaptive-RPS/)

**Adaptive Rock–Paper–Scissors** is a **MIPS assembly class project** developed for **ITCS213 (Computer Organization and Architecture)**. It implements a pattern-learning Rock–Paper–Scissors opponent across three layers of abstraction—**MIPS32 assembly**, **Python 3**, and a **self-contained interactive Web application**—all powered by the exact same hardware-friendly, integer-only Markov frequency table.

Rather than relying on floating-point math or external machine-learning libraries, the AI learns player habits in real time using a **27-word aligned memory table** updated exclusively with **bitwise right-shifts (`>> 3`)** and **integer additions (`+ 16`)**.

---

## Architecture & MIPS Design

### 1. Move & Context Encoding
Moves are encoded as integers `0..2` so they map directly to array offsets and cyclic modular arithmetic:

| Code | Move | Beaten By (`(move + 1) % 3`) |
|:---:|---|---|
| `0` | ✊ Rock | `1` (✋ Paper) |
| `1` | ✋ Paper | `2` (✌️ Scissors) |
| `2` | ✌️ Scissors | `0` (✊ Rock) |

Each completed round forms a **context** (`ctx`) describing what just happened:

$$\text{ctx} = 3 \times \text{prev\_player} + \text{prev\_computer} \in \{0, 1, \dots, 8\}$$

Across `9` possible previous-round situations and `3` possible next player moves, the entire model fits in **27 aligned 32-bit words (`108` bytes)**:

$$\text{index} = 3 \times \text{ctx} + \text{move} \in \{0, 1, \dots, 26\}$$

### 2. Key Function: Shift-Decay `update(counts, ctx, move)`
To adapt when a human player changes strategy mid-game—without floating-point instructions (`mul.s` / `div.s`) or integer division—every round multiplies all 27 counts by $\frac{7}{8}$ via an arithmetic/logical shift-and-subtract before adding `16` to the observed transition:

```python
DECAY_SHIFT = 3   # counts[i] -= counts[i] >> 3   (scales old evidence by 7/8)
INCREMENT   = 16  # large enough that x >> 3 does not truncate small counts to 0

def update(ctx, move):
    for i in range(27):
        counts[i] -= counts[i] >> DECAY_SHIFT
    counts[3 * ctx + move] += INCREMENT
```

In **MIPS32 assembly** (`mips/main.asm`), even multiplication by `3` is avoided in favor of bit shifts (`(ctx << 1) + ctx`), yielding a deterministic **173 dynamic instructions per call** (`2` setup + `27 × 6` loop + `9` index/update/return):

```mips
update:
    addu  $t0, $a0, $zero       # $t0 = &counts[0]
    addiu $t3, $a0, 108         # $t3 = &counts[27] (27 * 4 bytes)

decay_loop:
    lw    $t1, 0($t0)           # $t1 = counts[i]
    srl   $t2, $t1, 3           # $t2 = counts[i] >> 3
    subu  $t1, $t1, $t2         # $t1 = counts[i] - (counts[i] >> 3)
    sw    $t1, 0($t0)           # store decayed count
    addiu $t0, $t0, 4           # advance to next 32-bit word
    bne   $t0, $t3, decay_loop

    sll   $t4, $a1, 1           # 2 * ctx
    addu  $t4, $t4, $a1         # 3 * ctx
    addu  $t4, $t4, $a2         # 3 * ctx + move
    sll   $t4, $t4, 2           # byte offset = 4 * (3 * ctx + move)
    addu  $t4, $a0, $t4         # &counts[3 * ctx + move]

    lw    $t5, 0($t4)
    addiu $t5, $t5, 16          # counts[3 * ctx + move] += 16
    sw    $t5, 0($t4)
    jr    $ra
```

### 3. Fair Commit-Before-Input Protocol
On every round (in both Python and the Web UI), the AI inspects `counts[3*ctx .. 3*ctx+2]`, predicts the player's highest-scoring move (playing `(predicted + 1) % 3`, or uniformly at random if all three entries are `0`), and **locks in its choice before reading the player's input**.

---

## Repository Structure

```text
ITCS213-Adaptive-RPS/
├── README.md                   # Project overview, MIPS architecture, and usage guide
├── mips/
│   ├── main.asm                # MIPS32 update() implementation + 1,000-move verification harness
│   └── test_data.asm           # Auto-generated 1,000-move trace & expected 27-word reference table
├── Prototype_1.py              # Single-file interactive terminal game (30 rounds)
├── Prototype1_Test.py          # Monte Carlo evaluation suite (5 simulated player archetypes)
├── generate_mars_test.py       # Reproducible generator (seed=42) for mips/test_data.asm
├── Appendix_Source_Code.md     # Combined Python & MIPS source reference and MARS setup notes
└── Website/
    ├── index.html              # Self-contained interactive Web edition (desktop, mobile & Google Sites)
    ├── handout.md              # Documentation of UI layout, strike animations & canvas cutscene
    └── assets/                 # Original source Pink Rabbit reaction stickers (8 JPEGs)
```

---

## Interactive Web Edition (`Website/index.html`)

`Website/index.html` brings the exact 27-word MIPS/Python learning engine to browsers and mobile devices as a **zero-dependency single HTML file** (with all 8 reaction stickers embedded inline as Base64 Data URIs so it works standalone or inside a **Google Sites** embed `<iframe>`):

- **Custom Matchup Strike Choreography:** Frame-accurate `requestAnimationFrame` fight animations tailored to each outcome (`✊ CRUSHES ✌️`, `✋ COVERS ✊`, `✌️ SLICES ✋`, and `⚡ CLASH` draws) with dynamic stage-gap measurement and camera shake.
- **Non-Repeating Reaction Sticker Deck:** 7 custom Pink Rabbit reaction stickers managed by a Fisher–Yates shuffle-bag on AI round wins, plus an exclusive `"adios..."` match-victory sticker.
- **3D Battlefield Fold & 7-Act `<canvas>` Gunslinger Cutscene:** After Round 30, the arena folds closed in 3D (`perspective(920px) rotateX`) and—when the AI wins the match—triggers a 60fps high-DPI HTML5 `<canvas>` sequence where the Pink Rabbit somersaults in, blasts 4 sky-launched **Coca-Cola** and **Pepsi** cans in mid-air, blows barrel smoke, spins and holsters its revolver, and steps onto the `"adios..."` ending card.
- **Mobile & Embed Hardened:** Built-in touch `.scroll-shell` container and cross-origin `<iframe>`-safe animation loop tested for Mobile Safari (iPhone) and Google Sites embeds.

---

## Getting Started

### 1. Play the Web Version
Open `Website/index.html` directly in any modern browser, or serve it locally:

```bash
cd Website
python3 -m http.server 8765
# Open http://localhost:8765 in your browser (click buttons or press R / P / S)
```

To embed on **Google Sites**, copy the contents of `Website/index.html` into **Insert → Embed → Embed code**.

### 2. Run & Verify the MIPS Assembly in MARS 4.5
1. Launch **MARS 4.5** (`java -jar Mars45.jar`).
2. Ensure **Settings → Delayed branching** is **unchecked** (disabled), and **Settings → Initialize Program Counter to global 'main' if defined** is enabled if needed.
3. Open `mips/main.asm` (keep `mips/test_data.asm` in the same `mips/` folder so `.include "test_data.asm"` resolves).
4. Click **Run → Assemble (`F3`)**, then **Run → Go (`F5`)**.
5. MARS replays all `1,000` `(ctx, move)` observations and verifies all 27 memory words against Python:
   ```text
   PASS: All 27 entries match Python exactly.
   ```

To regenerate `mips/test_data.asm` from Python:

```bash
python3 generate_mars_test.py
```

### 3. Run the Python Terminal Game & Statistical Benchmark
Play the 30-round terminal version:

```bash
python3 Prototype_1.py
```

Run unit tests and the Monte Carlo evaluation (`300` seeds × `300` rounds across `Biased`, `Cycle`, `WinStayLoseShift`, `Switcher`, and `UniformRandom` control players):

```bash
python3 Prototype1_Test.py
```

---

## Academic Context

Created as a class project for **ITCS213 — Computer Organization and Architecture**, demonstrating how an adaptive pattern-recognition game can be co-designed in high-level Python/JavaScript and low-level **MIPS32 assembly** with bit-exact state equivalence.
