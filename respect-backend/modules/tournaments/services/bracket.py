"""Pure bracket generation and advancement, shared by solo and team events."""
import secrets
from uuid import uuid4


def new_match(a=None, b=None):
    return {"id": str(uuid4()), "a": a, "b": b, "winner": None, "score_a": None, "score_b": None}


def generate(entries):
    entries = list(entries)
    secrets.SystemRandom().shuffle(entries)
    size = 1 << (len(entries) - 1).bit_length()
    rounds = [[new_match(entries[i], entries[i + size // 2] if i + size // 2 < len(entries) else None) for i in range(size // 2)]]
    size //= 2
    while size > 1:
        rounds.append([new_match() for _ in range(size // 2)])
        size //= 2
    return rounds


def advance(tournament):
    rounds = tournament["rounds"]
    for ri, matches in enumerate(rounds):
        for mi, match in enumerate(matches):
            if ri == 0 and bool(match["a"]) != bool(match["b"]):
                match["winner"] = match["a"] or match["b"]
            if match["winner"] and ri + 1 < len(rounds):
                rounds[ri + 1][mi // 2]["a" if mi % 2 == 0 else "b"] = match["winner"]
    if rounds[-1][0]["winner"]:
        tournament["status"] = "finished"
