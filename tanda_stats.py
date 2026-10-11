import random
from math import comb

# Candidate values for a member's hidden on-time probability: 0.05, 0.10, ... 0.95
P_GRID = [k / 20 for k in range(1, 20)]


def simulate_history(true_p, n_months, rng):
    """Bernoulli trials: 1 = paid on time, 0 = late or missed."""
    return [1 if rng.random() < true_p else 0 for _ in range(n_months)]


def update(prior, history):
    """Bayes' theorem on the grid.
    Likelihood of k on-time payments out of n is the binomial PMF.
    The sum of prior * likelihood over the grid is P(data), by the law of total probability."""
    n = len(history)
    k = sum(history)
    unnormalized = [
        pr * comb(n, k) * p**k * (1 - p) ** (n - k)
        for p, pr in zip(P_GRID, prior)
    ]
    total = sum(unnormalized)
    return [u / total for u in unnormalized]


def predictive_on_time(posterior):
    """P(next payment on time) = sum over p of p * P(p | data)  (law of total probability)."""
    return sum(p * w for p, w in zip(P_GRID, posterior))


def credible_interval(posterior, level=0.90):
    """Read the interval off the posterior CDF."""
    lo_tail = (1 - level) / 2
    hi_tail = 1 - lo_tail
    cdf = 0.0
    lo = hi = None
    for p, w in zip(P_GRID, posterior):
        cdf += w
        if lo is None and cdf >= lo_tail:
            lo = p
        if cdf >= hi_tail:
            hi = p
            break
    return lo, (hi if hi is not None else P_GRID[-1])


if __name__ == "__main__":
    rng = random.Random(42)
    members = {"Ana": 0.95, "Ben": 0.90, "Carla": 0.80,
               "Dev": 0.70, "Elena": 0.60, "Femi": 0.45}

    uniform_prior = [1 / len(P_GRID)] * len(P_GRID)

    for name, true_p in members.items():
        history = simulate_history(true_p, 8, rng)
        posterior = update(uniform_prior, history)
        pred = predictive_on_time(posterior)
        lo, hi = credible_interval(posterior)
        print(f"{name:6} true={true_p:.2f}  history={history}  "
              f"predicted on-time={pred:.2f}  90% interval=({lo:.2f}, {hi:.2f})")