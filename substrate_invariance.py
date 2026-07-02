"""General-graph port of the oracle (main.py) for the substrate-invariance test.

Same dynamics as main.run, same two verification loops, same scores. Two
things are parameterized, declared per the charter's truncation rule:

  - the connectivity graph is an explicit edge list, not the built-in ring
  - carrier placement: "random" (the oracle's rule -- and the RNG call is
    matched to carrier_pgm.model.build in ../thrml-kuramoto-lab, so for a
    given seed the CARRIER SETS ARE IDENTICAL across substrates), or
    "hub" (highest degree)

Honesty notes:
  - NOT bit-identical to main.run on the ring: neighbor averages here are
    vectorized edge sums, so floating-point summation order differs and
    trajectories decorrelate. Agreement is statistical; run --verify to
    see the side-by-side against the oracle.
  - The coherence metric still never references the target.
"""

import numpy as np

TAU = 2 * np.pi


def wrap(x):
    return (x + np.pi) % TAU - np.pi


def run_graph(h, n, edges, placement="random", steps=1400, perturb_at=700,
              r_lo=0.55, r_hi=0.80, dt=0.05, noise=0.015, seed=7):
    """main.run, on an arbitrary graph. Returns (hom_series, tel_series)."""
    a = np.array([e[0] for e in edges])
    b = np.array([e[1] for e in edges])
    src = np.concatenate([a, b])
    dst = np.concatenate([b, a])
    deg = np.bincount(dst, minlength=n).astype(float)
    safe_deg = np.maximum(deg, 1.0)  # isolated nodes: no neighborhood pull

    # carriers -- matched to carrier_pgm.model.build: first draw of
    # default_rng(seed) is the placement permutation
    k = int(round(h * n))
    if placement == "hub":
        carriers = np.argsort(-deg)[:k]
    else:
        carriers = np.random.default_rng(seed).permutation(n)[:k]
    mask = np.zeros(n, bool)
    mask[carriers] = True

    rng = np.random.default_rng(seed)
    theta = rng.uniform(-np.pi, np.pi, n)
    omega = rng.normal(0, 0.02, n)
    K = np.full(n, 1.5)
    setpoint = np.zeros(n)
    true_target = 0.0

    hom_series, tel_series = [], []
    for t in range(steps):
        if t == perturb_at:
            true_target = 1.9  # the purpose moves; the seed never saw this

        # local order over each node's neighborhood (edge-sum form)
        zr = np.zeros(n); zi = np.zeros(n)
        np.add.at(zr, dst, np.cos(theta[src]))
        np.add.at(zi, dst, np.sin(theta[src]))
        r = np.hypot(zr, zi) / safe_deg
        psi = np.where(deg > 0, np.arctan2(zi, zr), theta)

        # homeostatic loop: hold local r in the viable band by tuning K
        K = np.clip(K + 0.4 * dt * ((r < r_lo).astype(float)
                                    - (r > r_hi).astype(float)), 0.2, 6.0)

        # teleological loop: carriers reconstruct; the rest adopt neighbors
        sr = np.zeros(n); si = np.zeros(n)
        np.add.at(sr, dst, np.cos(setpoint[src]))
        np.add.at(si, dst, np.sin(setpoint[src]))
        mean_nb = np.where(deg > 0, np.arctan2(si, sr), setpoint)
        setpoint = setpoint + np.where(
            mask, 0.25 * wrap(true_target - setpoint),
            0.15 * wrap(mean_nb - setpoint))

        # dynamics: mutual coherence + pull to own setpoint
        dtheta = omega + K * np.sin(psi - theta) + 0.6 * np.sin(setpoint - theta)
        theta = wrap(theta + dt * dtheta + noise * rng.standard_normal(n))

        hom_series.append(float(np.mean(r)))
        tel_series.append(float(np.mean(np.cos(theta - true_target))))

    return np.array(hom_series), np.array(tel_series)


def summarize_graph(h, n, edges, placement="random", window=150, **kw):
    hom, tel = run_graph(h, n, edges, placement=placement, **kw)
    return hom[-window:].mean(), tel[-window:].mean()


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--verify", action="store_true",
                   help="ring: side-by-side against the oracle's summarize()")
    args = p.parse_args()
    if args.verify:
        import main as oracle
        N, horizon = 120, 6
        edges = [(i, (i + d) % N) for i in range(N) for d in range(1, horizon + 1)]
        print("      h   oracle hom/tel      port hom/tel")
        for h in (0.0, 0.03, 0.05, 0.10):
            oh, ot, _ = oracle.summarize(h)
            ph, pt = summarize_graph(h, N, edges)
            print(f"  {h:5.2f}   {oh:+.3f} / {ot:+.3f}    {ph:+.3f} / {pt:+.3f}")
        print("\nread: statistical agreement expected, not bit-identity.")
