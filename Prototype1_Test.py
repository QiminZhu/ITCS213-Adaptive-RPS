"""
Adaptive RPS: decaying count-table model + test harness.

Moves: 0=Rock, 1=Paper, 2=Scissors. Counter of m is (m+1) % 3.
Run:
    python adaptive_rps_test.py          # learning tests (simulated players)
    python adaptive_rps_test.py --play   # play against it yourself
"""
import random
import sys
from math import sqrt

N_CTX = 9           # ctx = 3*prev_player + prev_computer
DECAY_SHIFT = 3     # counts -= counts >> 3  (decay to 7/8)
INCREMENT = 16      # new evidence; large enough that >>3 doesn't zero small counts


def counter(move):
    return (move + 1) % 3


def beats(a, b):
    """True if move a beats move b."""
    return a == counter(b)


class CountModel:
    """Same logic you will port to MIPS: flat int array of 27 words."""

    def __init__(self, rng):
        self.counts = [0] * (N_CTX * 3)
        self.rng = rng

    def predict_player(self, ctx):
        row = self.counts[3 * ctx: 3 * ctx + 3]
        if max(row) == 0:
            return None                      # no evidence yet -> caller plays random
        return row.index(max(row))           # tie -> lowest move code

    def choose(self, ctx):
        """Computer's move, chosen BEFORE seeing the player's current move."""
        if ctx is None:
            return self.rng.randrange(3), None
        pred = self.predict_player(ctx)
        if pred is None:
            return self.rng.randrange(3), None
        return counter(pred), pred

    def update(self, ctx, move):
        """KEY FUNCTION: decay whole table, then add the new observation."""
        for i in range(len(self.counts)):
            self.counts[i] -= self.counts[i] >> DECAY_SHIFT
        self.counts[3 * ctx + move] += INCREMENT


# ---------------- simulated players (never see the computer's current move) ----------------

class Biased:
    name = "biased (50/30/20)"
    def __init__(self, rng): self.rng = rng
    def move(self, t, hist): return self.rng.choices([0, 1, 2], [5, 3, 2])[0]

class Cycle:
    name = "cycle R-P-S"
    def __init__(self, rng): self.rng = rng
    def move(self, t, hist): return t % 3

class WinStayLoseShift:
    name = "win-stay/lose-shift"
    def __init__(self, rng): self.rng = rng
    def move(self, t, hist):
        if not hist:
            return self.rng.randrange(3)
        p, c = hist[-1]
        if beats(p, c):  return p                 # won -> stay
        if beats(c, p):  return (p + 1) % 3       # lost -> shift
        return self.rng.randrange(3)              # draw -> random

class Switcher:
    name = "changes pattern at t=150"
    def __init__(self, rng): self.rng = rng
    def move(self, t, hist):
        if t < 150:
            return self.rng.choices([0, 1, 2], [7, 2, 1])[0]
        return self.rng.choices([0, 1, 2], [1, 2, 7])[0]

class UniformRandom:
    name = "uniform random (control)"
    def __init__(self, rng): self.rng = rng
    def move(self, t, hist): return self.rng.randrange(3)


def run_game(player_cls, strategy, rounds, seed):
    rng = random.Random(seed)
    player = player_cls(random.Random(seed + 1))
    model = CountModel(random.Random(seed + 2))
    hist, wins, hits, ctx = [], [], [], None
    for t in range(rounds):
        # 1) computer commits first
        if strategy == "adaptive":
            cmove, pred = model.choose(ctx)
        else:
            cmove, pred = rng.randrange(3), None
        # 2) player moves (independent of cmove)
        pmove = player.move(t, hist)
        # 3) score
        wins.append(1 if beats(cmove, pmove) else 0)
        hits.append(None if pred is None else int(pred == pmove))
        # 4) learn from (previous context -> this player move)
        if strategy == "adaptive" and ctx is not None:
            model.update(ctx, pmove)
        # 5) new context for next round
        hist.append((pmove, cmove))
        ctx = 3 * pmove + cmove
    return wins, hits


def mean_ci(xs):
    n = len(xs)
    m = sum(xs) / n
    sd = sqrt(sum((x - m) ** 2 for x in xs) / (n - 1))
    return m, 1.96 * sd / sqrt(n)


def evaluate(player_cls, rounds=300, seeds=300):
    early, late = {"adaptive": [], "random": []}, {"adaptive": [], "random": []}
    acc = []
    for s in range(seeds):
        for strat in ("adaptive", "random"):
            w, h = run_game(player_cls, strat, rounds, seed=s * 10)
            early[strat].append(sum(w[:15]) / 15)
            late[strat].append(sum(w[-100:]) / 100)
            if strat == "adaptive":
                used = [x for x in h[-100:] if x is not None]
                if used:
                    acc.append(sum(used) / len(used))
    print(f"\n{player_cls.name}")
    for strat in ("random", "adaptive"):
        e, ee = mean_ci(early[strat]); l, le = mean_ci(late[strat])
        print(f"  {strat:9s} win rate: first 15 rounds {e:.3f}±{ee:.3f} | last 100 rounds {l:.3f}±{le:.3f}")
    a, ae = mean_ci(acc)
    print(f"  adaptive prediction accuracy (last 100): {a:.3f}±{ae:.3f}  (chance = 0.333)")
    gain = mean_ci([a_ - r_ for a_, r_ in zip(late["adaptive"], late["random"])])
    verdict = "LEARNS" if gain[0] - gain[1] > 0 else "no significant gain"
    print(f"  late win-rate gain over random: {gain[0]:+.3f}±{gain[1]:.3f}  -> {verdict}")


def tests():
    # Unit checks on the model itself
    m = CountModel(random.Random(0))
    for _ in range(5):
        m.update(ctx=4, move=2)
    assert m.predict_player(4) == 2, "should predict the repeated move"
    assert m.predict_player(0) is None, "unseen context must give no prediction"
    assert counter(2) == 0 and counter(0) == 1 and counter(1) == 2
    # decay: a stale habit must eventually lose to a new one
    for _ in range(30):
        m.update(ctx=4, move=0)
    assert m.predict_player(4) == 0, "decay should let the model adapt"
    print("unit checks passed")


def play():
    names = ["rock", "paper", "scissors"]
    keys = {"r": 0, "p": 1, "s": 2}
    model, ctx = CountModel(random.Random()), None
    score = [0, 0, 0]
    print("r/p/s to play, q to quit. Counts shown as the AI's current belief about you.")
    while True:
        cmove, pred = model.choose(ctx)          # committed before your input
        k = input("> ").strip().lower()
        if k == "q":
            break
        if k not in keys:
            continue
        pmove = keys[k]
        res = 0 if cmove == pmove else (1 if beats(cmove, pmove) else 2)
        score[res] += 1
        print(f"  you {names[pmove]}, AI {names[cmove]} "
              f"({'AI predicted ' + names[pred] if pred is not None else 'AI guessed randomly'}) "
              f"-> {['draw', 'AI wins', 'you win'][res]}   [draw {score[0]} AI {score[1]} you {score[2]}]")
        if ctx is not None:
            model.update(ctx, pmove)
        ctx = 3 * pmove + cmove


if __name__ == "__main__":
    if "--play" in sys.argv:
        play()
    else:
        tests()
        for cls in (Biased, Cycle, WinStayLoseShift, Switcher, UniformRandom):
            evaluate(cls)