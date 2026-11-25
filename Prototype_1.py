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