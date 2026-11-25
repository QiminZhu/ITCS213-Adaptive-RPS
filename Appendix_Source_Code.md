# Appendix: Source Code

The Python program runs the game. The MIPS program implements the learning function and verifies its final counts against a generated reference after 1,000 updates. Source is included as text.

## Software and execution environment

- **High-level program:** Python 3. The Python source runs using a Python interpreter; it is not compiled directly into MIPS machine code.
- **MIPS assembler and simulator:** MARS 4.5, supplied as `Resources/Mars45.jar`. MARS assembles MIPS source into machine instructions and simulates their execution.
- **Translation method:** The Python learning function is manually translated into equivalent MIPS assembly; MARS does not translate Python.
- **Required setting:** MARS delayed branching disabled.
- **Code format:** All source below is editable text, not screenshots.

These identify the project tools and intended setup. This document does not establish that the programs have been executed or passed tests.

## A. High-level program

File: `Prototype_1.py`

```python
"""
Adaptive Rock-Paper-Scissors (terminal version, single file).

The computer remembers what you tend to play after each situation, then
plays the move that beats your most likely next move.

Run:  python adaptive_rps.py      (type r / p / s, or q to quit)
"""
import random
import sys

# Make sure emojis print correctly even on terminals that default to a
# legacy encoding (e.g. older Windows consoles).
sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
# Moves are numbers so they can be used as array indexes (and later as MIPS
# integers):  0 = Rock, 1 = Paper, 2 = Scissors.
# Each move is beaten by the NEXT one in the list, wrapping around:
#   Rock < Paper < Scissors < Rock
# ---------------------------------------------------------------------------
EMOJI = ["✊", "✋", "✌️"]           # index = move number


def counter(move):
    """Return the move that beats `move`."""
    return (move + 1) % 3


# ---------------------------------------------------------------------------
# Trash talk. One line is picked at random after each decisive round.
# ---------------------------------------------------------------------------
AI_WIN_LINES = [          # shown when the AI wins
    "Skill issue 💅 gg ez",
    "Sit down, human 😼 *meow*",
    "Bruh, too easy 🥱",
    "L + ratio 🐶 woof",
    "Caught in 4K 📸",
    "No cap, I read you like a book 📖",
    "Imagine losing to a pet 🐱",
    "Cry about it 😹",
    "Living rent free in your head 🏠",
    "Yoink! Your W is mine 🐾",
]

AI_LOSE_LINES = [         # shown when the AI loses
    "NOOO 😭 that was lucky, ok?",
    "Bruh... I'm literally shaking 🥲",
    "Sus... are you cheating? 🕵️",
    "Wow, a W. Want a cookie? 🍪 (I do)",
    "Pls no ban 🥺",
    "I let you win. Totally. 🙃",
    "Mald 😤 *angry meow*",
    "Lag. Definitely lag. 📶",
    "Rigged! Rematch now 🐶",
    "Big brain moment 🧠 *sulks in corner*",
]

# ---------------------------------------------------------------------------
# The model: a flat table of 27 integers (9 situations x 3 possible moves).
#
# A "situation" (context) is what happened in the previous round:
#     ctx = 3 * (player's last move) + (computer's last move)   -> 0..8
#
# counts[3*ctx + m] = how strongly we believe that, in situation ctx,
#                     the player will play move m next.
# ---------------------------------------------------------------------------
counts = [0] * 27

MAX_ROUNDS = 30   # the game ends after this many completed rounds
DECAY_SHIFT = 3   # old evidence is multiplied by 7/8 each round (x - x>>3)
INCREMENT = 16    # weight of one new observation (big enough that x>>3 != 0)


def update(ctx, move):
    """
    KEY FUNCTION: learn from one observation.
    "Last round was situation `ctx`, and the player then played `move`."
    """
    # 1) Forget a little: shrink every count to 7/8 of its value, so that
    #    old habits fade if the player changes strategy.
    for i in range(len(counts)):
        counts[i] -= counts[i] >> DECAY_SHIFT
    # 2) Remember: add fresh evidence for what just happened.
    counts[3 * ctx + move] += INCREMENT


def predict(ctx):
    """Return the player's most likely next move in situation ctx,
    or None if we have not seen this situation yet."""
    row = counts[3 * ctx: 3 * ctx + 3]     # the 3 counts for this situation
    if max(row) == 0:
        return None                        # no evidence -> caller must guess
    return row.index(max(row))             # highest count wins (ties: lowest move)


# ---------------------------------------------------------------------------
# Game loop
# ---------------------------------------------------------------------------
def main():
    keys = {"r": 0, "p": 1, "s": 2}
    score = {"you": 0, "ai": 0, "draw": 0}
    ctx = None                             # no previous round yet

    print("✊✋✌️  Rock-Paper-Scissors! Type r / p / s (q to quit).")
    print("The more you play, the more it learns your patterns. 🐾\n")

    while sum(score.values()) < MAX_ROUNDS:
        # --- 1. Computer chooses FIRST, so it cannot peek at your move. ---
        guess = predict(ctx) if ctx is not None else None
        if guess is None:
            ai = random.randrange(3)       # nothing learned yet: play randomly
        else:
            ai = counter(guess)            # play what beats the predicted move

        # --- 2. Read the player's move (ignore invalid input). ---
        choice = input(f"Round {sum(score.values()) + 1}/{MAX_ROUNDS} - your move [r/p/s/q]: ").strip().lower()
        if choice == "q":
            break
        if choice not in keys:
            continue
        you = keys[choice]

        # --- 3. Decide the result. You win if your move beats the AI's. ---
        if you == ai:
            result = "draw"
        elif you == counter(ai):
            result = "you"
        else:
            result = "ai"
        score[result] += 1

        # --- 4. Show the round, with a random quip for a decisive result. ---
        print(f"\n  🧑 {EMOJI[you]}   vs   {EMOJI[ai]} 🤖")
        if result == "ai":
            print("  😈", random.choice(AI_WIN_LINES))
        elif result == "you":
            print("  🎉", random.choice(AI_LOSE_LINES))
        else:
            print("  🤝 Draw!")

        # Only brag when the prediction was right. If we guessed wrong, or had
        # no prediction yet, we stay quiet.
        if guess == you:
            print(f"  🔮 Called it! I predicted your {EMOJI[you]} 😼")
        print(f"  📊 you {score['you']} | draw {score['draw']} | ai {score['ai']}\n")

        # --- 5. Learn: last round's situation led to this player move. ---
        if ctx is not None:
            update(ctx, you)

        # --- 6. This round becomes the situation for the next one. ---
        ctx = 3 * you + ai

    # --- Game over: final result. ---
    total = sum(score.values())
    print(f"🏁 Game over after {total} rounds!")
    print(f"   you {score['you']} | draw {score['draw']} | ai {score['ai']}")
    if score["you"] > score["ai"]:
        print("   🎉", random.choice(AI_LOSE_LINES))
    elif score["ai"] > score["you"]:
        print("   😈", random.choice(AI_WIN_LINES))
    else:
        print("   🤝 It's a tie!")


if __name__ == "__main__":
    main()
```

## B. MIPS learning function and verification program

File: `mips/main.asm`

```asm
# ============================================================================
# Adaptive Rock-Paper-Scissors - ITCS213
# Key Function: update(counts_base, ctx, move) + 1,000-move MARS Test Harness
#
# Register Interface for update():
#   $a0 = base address of counts[27] (27 aligned 32-bit words)
#   $a1 = ctx  (0..8, where ctx = 3 * prev_player + prev_computer)
#   $a2 = move (0..2, observed player move)
#   $t0 = pointer to current word in counts[]
#   $t3 = end address (&counts[27] = $a0 + 108)
# ============================================================================

.data
.align 2
counts:         .word 0:27              # 27 words (108 bytes), initialized to 0

msg_pass:       .asciiz "PASS: All 27 entries match Python exactly.\n"
msg_fail:       .asciiz "FAIL: Mismatches found = "
msg_table:      .asciiz "Final MIPS counts table:\n"
msg_space:      .asciiz " "
msg_newline:    .asciiz "\n"

# Pulls in num_moves, test_ctx[1000], test_move[1000], expected_counts[27]
.include "test_data.asm"

.text
.globl main

# ----------------------------------------------------------------------------
# Test Harness: replays all 1,000 (ctx, move) pairs and checks against Python
# ----------------------------------------------------------------------------
main:
    la    $s0, num_moves
    lw    $s0, 0($s0)                   # $s0 = 1000
    addu  $s1, $zero, $zero             # $s1 = loop index i = 0
    la    $s2, test_ctx                 # $s2 = &test_ctx[0]
    la    $s3, test_move                # $s3 = &test_move[0]
    la    $s4, counts                   # $s4 = &counts[0]

replay_loop:
    addu  $a0, $s4, $zero               # arg 0: base address of counts
    lw    $a1, 0($s2)                   # arg 1: test_ctx[i]
    lw    $a2, 0($s3)                   # arg 2: test_move[i]
    jal   update                        # call update(counts, ctx, move)

    addiu $s2, $s2, 4                   # next test_ctx word
    addiu $s3, $s3, 4                   # next test_move word
    addiu $s1, $s1, 1                   # i++
    bne   $s1, $s0, replay_loop

    # --- Compare counts[0..26] against expected_counts[0..26] ---
    la    $t0, counts                   # pointer to MIPS result
    la    $t1, expected_counts          # pointer to Python reference
    addiu $t2, $zero, 27                # 27 entries to check
    addu  $s5, $zero, $zero             # $s5 = mismatch counter

verify_loop:
    lw    $t3, 0($t0)
    lw    $t4, 0($t1)
    beq   $t3, $t4, match_ok
    addiu $s5, $s5, 1                   # mismatch++

match_ok:
    addiu $t0, $t0, 4
    addiu $t1, $t1, 4
    addiu $t2, $t2, -1
    bne   $t2, $zero, verify_loop

    # --- Print PASS or FAIL ---
    bne   $s5, $zero, print_fail
    li    $v0, 4
    la    $a0, msg_pass
    syscall
    j     print_table

print_fail:
    li    $v0, 4
    la    $a0, msg_fail
    syscall
    li    $v0, 1
    addu  $a0, $s5, $zero
    syscall
    li    $v0, 4
    la    $a0, msg_newline
    syscall

    # --- Print final 27-word counts table ---
print_table:
    li    $v0, 4
    la    $a0, msg_table
    syscall

    la    $t0, counts
    addiu $t1, $zero, 27

print_loop:
    li    $v0, 1
    lw    $a0, 0($t0)
    syscall
    li    $v0, 4
    la    $a0, msg_space
    syscall
    addiu $t0, $t0, 4
    addiu $t1, $t1, -1
    bne   $t1, $zero, print_loop

    li    $v0, 4
    la    $a0, msg_newline
    syscall

    li    $v0, 10                       # exit
    syscall

# ----------------------------------------------------------------------------
# KEY FUNCTION: update(counts_base, ctx, move)
#   for i in range(27):
#       counts[i] -= counts[i] >> 3
#   counts[3 * ctx + move] += 16
#
# Exact dynamic instruction count per call:
#   2 (setup) + 27 * 6 (decay loop) + 9 (increment & return) = 173 instructions
# ----------------------------------------------------------------------------
update:
    addu  $t0, $a0, $zero               # $t0 = &counts[0]
    addiu $t3, $a0, 108                 # $t3 = &counts[27] (27 * 4 bytes)

decay_loop:
    lw    $t1, 0($t0)                   # $t1 = counts[i]
    srl   $t2, $t1, 3                   # $t2 = counts[i] >> 3
    subu  $t1, $t1, $t2                 # $t1 = counts[i] - (counts[i] >> 3)
    sw    $t1, 0($t0)                   # counts[i] = $t1
    addiu $t0, $t0, 4                   # next word (+4 bytes)
    bne   $t0, $t3, decay_loop          # repeat until $t0 == &counts[27]

    # Compute &counts[3 * ctx + move] = $a0 + 4 * ((ctx << 1) + ctx + move)
    sll   $t4, $a1, 1                   # $t4 = 2 * ctx
    addu  $t4, $t4, $a1                 # $t4 = 3 * ctx
    addu  $t4, $t4, $a2                 # $t4 = 3 * ctx + move
    sll   $t4, $t4, 2                   # $t4 = 4 * (3 * ctx + move)
    addu  $t4, $a0, $t4                 # $t4 = &counts[3 * ctx + move]

    lw    $t5, 0($t4)                   # load target entry
    addiu $t5, $t5, 16                  # add INCREMENT (16)
    sw    $t5, 0($t4)                   # store updated entry
    jr    $ra                           # return to caller
```

## C. Generated input and reference data

File: `mips/test_data.asm`

```asm
# Auto-generated by generate_mars_test.py (seed=42, 1000 moves)
.data
num_moves:
    .word 1000

test_ctx:
    .word 2, 2, 1, 2, 4, 2, 1, 1, 1, 4, 1, 1, 4, 4, 1, 4, 7, 3, 3, 2
    .word 1, 8, 1, 2, 1, 1, 1, 1, 1, 1, 7, 2, 1, 4, 7, 1, 1, 1, 4, 3
    .word 7, 7, 6, 1, 4, 2, 1, 2, 1, 7, 3, 4, 1, 4, 1, 2, 7, 5, 2, 0
    .word 0, 1, 1, 1, 1, 7, 8, 1, 4, 1, 7, 0, 1, 0, 4, 1, 4, 7, 1, 2
    .word 7, 4, 1, 1, 1, 4, 4, 2, 0, 1, 7, 5, 7, 8, 1, 4, 4, 5, 0, 4
    .word 2, 1, 2, 7, 6, 1, 4, 2, 6, 7, 0, 5, 4, 1, 5, 5, 5, 5, 2, 0
    .word 2, 7, 7, 6, 1, 2, 6, 7, 0, 1, 1, 4, 4, 2, 0, 4, 1, 7, 1, 0
    .word 5, 4, 1, 1, 7, 4, 1, 4, 1, 2, 1, 4, 1, 2, 1, 4, 1, 8, 7, 1
    .word 2, 4, 1, 1, 7, 4, 1, 4, 7, 2, 2, 1, 2, 1, 4, 4, 8, 1, 2, 1
    .word 7, 1, 1, 1, 1, 1, 1, 7, 1, 7, 4, 1, 7, 8, 7, 6, 7, 0, 1, 0
    .word 1, 1, 1, 7, 1, 4, 1, 1, 7, 7, 3, 4, 1, 1, 7, 5, 4, 4, 2, 4
    .word 4, 8, 1, 7, 2, 2, 4, 5, 2, 2, 7, 1, 3, 4, 2, 4, 4, 8, 1, 5
    .word 1, 2, 5, 1, 1, 4, 2, 2, 7, 7, 0, 1, 1, 7, 7, 6, 1, 1, 7, 3
    .word 4, 7, 3, 2, 7, 2, 3, 7, 1, 1, 1, 4, 0, 4, 4, 2, 5, 1, 1, 7
    .word 7, 0, 2, 2, 1, 4, 4, 2, 4, 4, 2, 1, 2, 7, 7, 3, 7, 5, 1, 1
    .word 1, 7, 5, 7, 8, 1, 1, 1, 4, 7, 2, 4, 0, 7, 7, 6, 7, 6, 0, 3
    .word 1, 7, 6, 7, 6, 0, 5, 1, 6, 7, 0, 8, 1, 0, 3, 1, 1, 1, 1, 7
    .word 7, 0, 5, 1, 7, 4, 7, 2, 7, 1, 6, 1, 0, 2, 3, 1, 4, 3, 1, 5
    .word 1, 5, 1, 8, 4, 5, 4, 5, 2, 1, 5, 1, 2, 7, 4, 2, 0, 1, 1, 1
    .word 1, 1, 7, 5, 7, 5, 0, 4, 1, 1, 1, 4, 4, 2, 1, 1, 1, 7, 5, 1
    .word 1, 4, 4, 2, 7, 5, 4, 1, 1, 1, 1, 1, 7, 2, 0, 4, 1, 4, 1, 1
    .word 4, 1, 4, 4, 1, 2, 1, 7, 4, 1, 1, 7, 2, 7, 4, 7, 5, 7, 8, 4
    .word 3, 4, 8, 5, 6, 4, 0, 1, 1, 4, 4, 5, 3, 2, 1, 2, 1, 1, 4, 2
    .word 1, 4, 4, 2, 1, 5, 1, 2, 1, 8, 4, 4, 8, 5, 1, 1, 1, 4, 8, 8
    .word 0, 4, 3, 4, 2, 1, 1, 1, 1, 4, 1, 1, 1, 1, 4, 1, 1, 4, 1, 4
    .word 1, 5, 1, 5, 4, 4, 7, 4, 7, 8, 4, 0, 1, 8, 8, 3, 7, 6, 7, 6
    .word 6, 0, 1, 0, 1, 7, 6, 3, 6, 8, 1, 6, 6, 0, 7, 6, 0, 0, 4, 7
    .word 6, 4, 6, 2, 7, 6, 1, 7, 6, 7, 0, 7, 6, 4, 3, 4, 8, 4, 6, 8
    .word 2, 7, 6, 6, 6, 3, 8, 7, 3, 6, 6, 3, 3, 8, 3, 6, 6, 0, 7, 5
    .word 4, 7, 5, 2, 7, 2, 3, 6, 3, 6, 8, 4, 0, 7, 1, 7, 4, 7, 8, 8
    .word 3, 6, 0, 3, 6, 4, 6, 5, 7, 3, 6, 5, 6, 5, 3, 0, 1, 1, 7, 8
    .word 1, 3, 4, 7, 6, 8, 4, 0, 1, 5, 1, 2, 7, 3, 8, 8, 6, 0, 7, 5
    .word 7, 8, 3, 3, 2, 1, 7, 5, 6, 4, 1, 6, 2, 1, 6, 4, 7, 2, 7, 7
    .word 6, 5, 7, 3, 4, 6, 8, 4, 6, 6, 6, 6, 3, 5, 6, 0, 1, 1, 1, 4
    .word 6, 3, 5, 6, 8, 4, 6, 6, 6, 6, 6, 6, 3, 8, 8, 6, 6, 0, 1, 4
    .word 6, 6, 3, 0, 7, 7, 6, 6, 3, 1, 2, 4, 3, 4, 2, 8, 7, 6, 6, 6
    .word 6, 3, 2, 6, 3, 7, 6, 2, 6, 7, 3, 0, 4, 4, 8, 7, 5, 7, 5, 6
    .word 6, 6, 3, 4, 3, 8, 3, 6, 6, 6, 6, 3, 0, 4, 8, 8, 6, 3, 7, 7
    .word 3, 6, 2, 7, 8, 3, 0, 7, 6, 1, 7, 6, 4, 1, 6, 5, 7, 6, 5, 6
    .word 8, 4, 7, 3, 7, 8, 8, 6, 5, 6, 5, 6, 8, 6, 5, 3, 6, 8, 3, 0
    .word 7, 4, 7, 8, 5, 5, 2, 7, 6, 3, 7, 0, 6, 8, 8, 3, 6, 6, 6, 3
    .word 0, 6, 6, 6, 6, 3, 7, 4, 7, 5, 7, 2, 4, 6, 3, 6, 8, 7, 8, 6
    .word 3, 3, 8, 6, 8, 0, 1, 7, 6, 6, 6, 3, 0, 7, 6, 3, 7, 6, 2, 7
    .word 3, 3, 2, 6, 7, 6, 0, 1, 7, 6, 4, 7, 0, 4, 3, 4, 2, 6, 8, 7
    .word 1, 4, 4, 8, 6, 3, 5, 7, 1, 5, 3, 5, 8, 6, 8, 3, 8, 8, 3, 6
    .word 6, 6, 0, 7, 4, 7, 5, 7, 8, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 3
    .word 4, 7, 7, 0, 4, 6, 0, 2, 7, 7, 6, 6, 6, 3, 7, 3, 6, 6, 3, 0
    .word 7, 2, 7, 7, 6, 6, 6, 6, 3, 7, 0, 6, 3, 6, 8, 7, 7, 6, 0, 3
    .word 0, 8, 6, 6, 3, 1, 7, 6, 5, 4, 1, 6, 5, 5, 2, 7, 0, 4, 7, 7
    .word 6, 5, 8, 1, 3, 1, 5, 3, 7, 0, 4, 4, 8, 7, 1, 8, 6, 7, 4, 3

test_move:
    .word 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 2, 1, 1, 0, 0
    .word 2, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 1, 2, 0, 0, 0, 1, 1, 2
    .word 2, 2, 0, 1, 0, 0, 0, 0, 2, 1, 1, 0, 1, 0, 0, 2, 1, 0, 0, 0
    .word 0, 0, 0, 0, 2, 2, 0, 1, 0, 2, 0, 0, 0, 1, 0, 1, 2, 0, 0, 2
    .word 1, 0, 0, 0, 1, 1, 0, 0, 0, 2, 1, 2, 2, 0, 1, 1, 1, 0, 1, 0
    .word 0, 0, 2, 2, 0, 1, 0, 2, 2, 0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0
    .word 2, 2, 2, 0, 0, 2, 2, 0, 0, 0, 1, 1, 0, 0, 1, 0, 2, 0, 0, 1
    .word 1, 0, 0, 2, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 2, 2, 0, 0
    .word 1, 0, 0, 2, 1, 0, 1, 2, 0, 0, 0, 0, 0, 1, 1, 2, 0, 0, 0, 2
    .word 0, 0, 0, 0, 0, 0, 2, 0, 2, 1, 0, 2, 2, 2, 2, 2, 0, 0, 0, 0
    .word 0, 0, 2, 0, 1, 0, 0, 2, 2, 1, 1, 0, 0, 2, 1, 1, 1, 0, 1, 1
    .word 2, 0, 2, 0, 0, 1, 1, 0, 0, 2, 0, 1, 1, 0, 1, 1, 2, 0, 1, 0
    .word 0, 1, 0, 0, 1, 0, 0, 2, 2, 0, 0, 0, 2, 2, 2, 0, 0, 2, 1, 1
    .word 2, 1, 0, 2, 0, 1, 2, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 2, 2
    .word 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 2, 2, 1, 2, 1, 0, 0, 0
    .word 2, 1, 2, 2, 0, 0, 0, 1, 2, 0, 1, 0, 2, 2, 2, 2, 2, 0, 1, 0
    .word 2, 2, 2, 2, 0, 1, 0, 2, 2, 0, 2, 0, 0, 1, 0, 0, 0, 0, 2, 2
    .word 0, 1, 0, 2, 1, 2, 0, 2, 0, 2, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0
    .word 1, 0, 2, 1, 1, 1, 1, 0, 0, 1, 0, 0, 2, 1, 0, 0, 0, 0, 0, 0
    .word 0, 2, 1, 2, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 2, 1, 0, 0
    .word 1, 1, 0, 2, 1, 1, 0, 0, 0, 0, 0, 2, 0, 0, 1, 0, 1, 0, 0, 1
    .word 0, 1, 1, 0, 0, 0, 2, 1, 0, 0, 2, 0, 2, 1, 2, 1, 2, 2, 1, 1
    .word 1, 2, 1, 2, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0
    .word 1, 1, 0, 0, 1, 0, 0, 0, 2, 1, 1, 2, 1, 0, 0, 0, 1, 2, 2, 0
    .word 1, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0
    .word 1, 0, 1, 1, 1, 2, 1, 2, 2, 1, 0, 0, 2, 2, 1, 2, 2, 2, 2, 2
    .word 0, 0, 0, 0, 2, 2, 1, 2, 2, 0, 2, 2, 0, 2, 2, 0, 0, 1, 2, 2
    .word 1, 2, 0, 2, 2, 0, 2, 2, 2, 0, 2, 2, 1, 1, 1, 2, 1, 2, 2, 0
    .word 2, 2, 2, 2, 1, 2, 2, 1, 2, 2, 1, 1, 2, 1, 2, 2, 0, 2, 1, 1
    .word 2, 1, 0, 2, 0, 1, 2, 1, 2, 2, 1, 0, 2, 0, 2, 1, 2, 2, 2, 1
    .word 2, 0, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 1, 0, 0, 0, 2, 2, 0
    .word 1, 1, 2, 2, 2, 1, 0, 0, 1, 0, 0, 2, 1, 2, 2, 2, 0, 2, 1, 2
    .word 2, 1, 1, 0, 0, 2, 1, 2, 1, 0, 2, 0, 0, 2, 1, 2, 0, 2, 2, 2
    .word 1, 2, 1, 1, 2, 2, 1, 2, 2, 2, 2, 1, 1, 2, 0, 0, 0, 0, 1, 2
    .word 1, 1, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 0, 0, 1, 2
    .word 2, 1, 0, 2, 2, 2, 2, 1, 0, 0, 1, 1, 1, 0, 2, 2, 2, 2, 2, 2
    .word 1, 0, 2, 1, 2, 2, 0, 2, 2, 1, 0, 1, 1, 2, 2, 1, 2, 1, 2, 2
    .word 2, 1, 1, 1, 2, 1, 2, 2, 2, 2, 1, 0, 1, 2, 2, 2, 1, 2, 2, 1
    .word 2, 0, 2, 2, 1, 0, 2, 2, 0, 2, 2, 1, 0, 2, 1, 2, 2, 1, 2, 2
    .word 1, 2, 1, 2, 2, 2, 2, 1, 2, 1, 2, 2, 2, 1, 1, 2, 2, 1, 0, 2
    .word 1, 2, 2, 1, 1, 0, 2, 2, 1, 2, 0, 2, 2, 2, 1, 2, 2, 2, 1, 0
    .word 2, 2, 2, 2, 1, 2, 1, 2, 1, 2, 0, 1, 2, 1, 2, 2, 2, 2, 2, 1
    .word 1, 2, 2, 2, 0, 0, 2, 2, 2, 2, 1, 0, 2, 2, 1, 2, 2, 0, 2, 1
    .word 1, 0, 2, 2, 2, 0, 0, 2, 2, 1, 2, 0, 1, 1, 1, 0, 2, 2, 2, 0
    .word 1, 1, 2, 2, 1, 1, 2, 0, 1, 1, 1, 2, 2, 2, 1, 2, 2, 1, 2, 2
    .word 2, 0, 2, 1, 2, 1, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1
    .word 2, 2, 0, 1, 2, 0, 0, 2, 2, 2, 2, 2, 1, 2, 1, 2, 2, 1, 0, 2
    .word 0, 2, 2, 2, 2, 2, 2, 1, 2, 0, 2, 1, 2, 2, 2, 2, 2, 0, 1, 0
    .word 2, 2, 2, 1, 0, 2, 2, 1, 1, 0, 2, 1, 1, 0, 2, 0, 1, 2, 2, 2
    .word 1, 2, 0, 1, 0, 1, 1, 2, 0, 1, 1, 2, 2, 0, 2, 2, 2, 1, 1, 0

expected_counts:
    .word 7, 9, 7, 7, 8, 14, 7, 7, 7
    .word 23, 7, 7, 7, 24, 11, 7, 7, 7
    .word 7, 7, 17, 15, 19, 7, 7, 7, 21
```

The MIPS program includes `test_data.asm`; keep that file in the same folder as `main.asm`. The input data can be regenerated with `generate_mars_test.py` from the Projects folder.
