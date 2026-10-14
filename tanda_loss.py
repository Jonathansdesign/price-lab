"""Tanda loss model: which payout order is safest for the group?

MODEL (simplifying assumptions, state these in the README):
  * N members, each pays C per round. The member in slot s gets the pot in round s.
  * A member who has NOT yet received the pot keeps paying (they still have
    something to gain). The risk is a member who ALREADY took the pot and then
    misses payments. A member in slot s still owes N - s payments afterward.
  * Each member has an unknown on-time probability p (from tanda_stats).
    Given p, the number of missed payments among n remaining is Binomial(n, 1 - p).
  * Members are independent. A late payment is treated as a missed one (conservative).

TOOLS FROM CLASS:
  law of total probability (mixing over the posterior), binomial PMF,
  convolution (PMF of a sum of independent random variables), CDF / tail
  probability, and brute-force search over all N! orders (discrete math).
"""
import random
from itertools import permutations
from math import comb

from tanda_stats import P_GRID, UNIFORM_PRIOR, simulate_history, update


def missed_pmf(posterior, n_remaining):
    """P(M = m) for m = 0..n_remaining, where M = payments missed after receiving the pot.

    Law of total probability over the grid:
        P(M = m) = sum_p  P(p | data) * Binomial(m; n, 1 - p)
    Using the whole posterior (not just its mean) keeps the uncertainty in the tails.
    """
    n = n_remaining
    return [
        sum(w * comb(n, m) * (1 - p) ** m * p ** (n - m) for p, w in zip(P_GRID, posterior))
        for m in range(n + 1)
    ]


def convolve(a, b):
    """PMF of X + Y for independent X, Y with PMFs a and b."""
    out = [0.0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def payments_still_owed(slot, n, rounds_done):
    """How many future payments could this member still miss after receiving the pot?

    * Not paid yet (slot >= rounds_done): they will be paid in round `slot`
      and then owe the rounds after it, which is n - 1 - slot payments.
    * Already paid (slot < rounds_done): they owe every round that hasn't
      happened yet, which is n - rounds_done payments.
    With rounds_done = 0 (a brand-new circle) this is the original n - 1 - slot.
    """
    return n - 1 - slot if slot >= rounds_done else n - rounds_done


def total_missed_pmf(order, pmf_cache, rounds_done=0):
    """PMF of the total number of missed payments for a given payout order."""
    n = len(order)
    total = [1.0]
    for slot, name in enumerate(order):          # slot 0 = paid first
        total = convolve(total, pmf_cache[name][payments_still_owed(slot, n, rounds_done)])
    return total


def expected_value(pmf):
    return sum(k * pr for k, pr in enumerate(pmf))


def tail_prob(pmf, k):
    """P(total missed >= k) = 1 - CDF(k - 1)."""
    return sum(pr for m, pr in enumerate(pmf) if m >= k)


def analyze_orders(histories, contribution=100, bad_threshold=3,
                   rounds_done=0, fixed_prefix=()):
    """Score every possible payout order.

    histories: {name: [1, 0, 1, ...]} payment history per member (no true_p needed).
    bad_threshold: 'bad outcome' means at least this many missed payments.
    rounds_done / fixed_prefix: for a circle already under way. fixed_prefix is the
    list of members already paid, in order; only the remaining members are shuffled.
    Returns a dict with the best order, the worst order, and the random baseline.
    """
    names = list(histories)
    n = len(names)
    fixed_prefix = list(fixed_prefix)
    remaining = [nm for nm in names if nm not in fixed_prefix]
    posteriors = {nm: update(UNIFORM_PRIOR, h) for nm, h in histories.items()}
    # Cache each member's PMF for each possible number of remaining payments.
    pmf_cache = {nm: {r: missed_pmf(posteriors[nm], r) for r in range(n + 1)} for nm in names}

    scored = []
    for tail in permutations(remaining):          # all orderings of who is still unpaid
        order = tuple(fixed_prefix) + tail
        pmf = total_missed_pmf(order, pmf_cache, rounds_done)
        scored.append({
            "order": list(order),
            "expected_loss": contribution * expected_value(pmf),
            "p_bad": tail_prob(pmf, bad_threshold),
        })

    best = min(scored, key=lambda s: (s["p_bad"], s["expected_loss"]))
    worst = max(scored, key=lambda s: (s["p_bad"], s["expected_loss"]))
    baseline = {   # a random order = the average over all orders, computed exactly
        "expected_loss": sum(s["expected_loss"] for s in scored) / len(scored),
        "p_bad": sum(s["p_bad"] for s in scored) / len(scored),
    }
    return {"best": best, "worst": worst, "random_baseline": baseline,
            "n_orders": len(scored), "contribution": contribution,
            "bad_threshold": bad_threshold}


if __name__ == "__main__":
    # TEST MODE: same simulated members as tanda_stats.py.
    rng = random.Random(42)
    true_p = {"Ana": 0.95, "Ben": 0.90, "Carla": 0.80,
              "Dev": 0.70, "Elena": 0.60, "Femi": 0.45}
    histories = {nm: simulate_history(p, 8, rng) for nm, p in true_p.items()}

    result = analyze_orders(histories, contribution=100, bad_threshold=3)
    print(f"Scored {result['n_orders']} payout orders "
          f"(bad outcome = at least {result['bad_threshold']} missed payments)\n")
    for label, key in [("BEST ", "best"), ("WORST", "worst")]:
        r = result[key]
        print(f"{label}: {' -> '.join(r['order'])}")
        print(f"       expected loss ${r['expected_loss']:.0f}, "
              f"P(bad outcome) = {r['p_bad']:.1%}")
    b = result["random_baseline"]
    print(f"RANDOM: expected loss ${b['expected_loss']:.0f}, P(bad outcome) = {b['p_bad']:.1%}")