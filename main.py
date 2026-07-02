"""
Swarm Constitution Experiment
==============================
Measures the GAP between homeostatic coherence and teleological fidelity
in a no-center, light-lag-bounded collective, as a function of how
holographically intent is encoded into each node's seed.

Model: each collector is a Kuramoto phase oscillator on a ring of local
neighbors (the delay-bounded horizon). Two verification loops:

  HOMEOSTATIC  (always on): each node tunes local coupling K_i to hold
    local order parameter r_i inside a viable band [r_lo, r_hi].
    This is "verify against internal reference" -- survives light-lag.

  TELEOLOGICAL (depth-gated): each node carries `h` intent-invariants that
    let it LOCALLY RECONSTRUCT the target phase, then nudges its setpoint
    toward target-alignment. h=0 -> no local intent (pure homeostasis).
    h=1 -> full local reconstruction.

The experiment: run to coherence, then apply a NOVEL perturbation the
seed did not anticipate (a target shift -- "what this was for" moved).
Measure, per h:
   homeostatic_score  = mean local coherence  (does it stay locked?)
   teleological_score = alignment with the (moved) true target
The GAP = homeostatic_score - teleological_score is the price of the
one-way door. We look for the critical h where the gap collapses.
"""

import numpy as np

TAU = 2 * np.pi
rng = np.random.default_rng(7)

def wrap(x):
    return (x + np.pi) % TAU - np.pi

def local_order(theta, neighbors):
    """r_i and mean phase of each node's delay-bounded neighborhood."""
    n = len(theta)
    r = np.zeros(n); psi = np.zeros(n)
    for i in range(n):
        z = np.mean(np.exp(1j * theta[neighbors[i]]))
        r[i] = np.abs(z); psi[i] = np.angle(z)
    return r, psi

def run(h, N=120, horizon=6, steps=1400, perturb_at=700,
        r_lo=0.55, r_hi=0.80, dt=0.05, noise=0.015, seed=7):
    """
    h : holographic depth in [0,1] -- fraction of nodes that carry a
        locally-reconstructable intent invariant. The honest knob.
    Returns time series of homeostatic and teleological scores.
    """
    rng = np.random.default_rng(seed)
    theta = rng.uniform(-np.pi, np.pi, N)
    omega = rng.normal(0, 0.02, N)              # intrinsic drift
    K = np.full(N, 1.5)                          # per-node coupling (homeostatic actuator)
    setpoint = np.zeros(N)                       # each node's target phase (the teleological setpoint)

    # ring neighbors within horizon
    neighbors = [np.array([(i+d) % N for d in range(-horizon, horizon+1) if d != 0])
                 for i in range(N)]

    # TRUE intent: a target phase the swarm is meant to point at.
    true_target = 0.0

    # Which nodes carry the intent invariant (can locally reconstruct target).
    carriers = rng.permutation(N)[:int(round(h * N))]
    carrier_mask = np.zeros(N, bool); carrier_mask[carriers] = True

    hom_series, tel_series = [], []

    for t in range(steps):
        # ---- NOVEL PERTURBATION: the purpose moves. Seed never saw this. ----
        if t == perturb_at:
            true_target = 1.9    # ~109 deg shift in "what this is for"

        r, psi = local_order(theta, neighbors)

        # ---- HOMEOSTATIC loop: hold local r in viable band by tuning K ----
        K = np.clip(K + 0.4*dt*((r < r_lo).astype(float) - (r > r_hi).astype(float)),
                    0.2, 6.0)

        # ---- TELEOLOGICAL loop: only carriers can reconstruct & move setpoint ----
        # A carrier reconstructs the target locally from its invariant and pulls
        # its setpoint toward it; non-carriers inherit setpoint via neighbors
        # (so intent can DIFFUSE, but only if seeded somewhere).
        new_setpoint = setpoint.copy()
        for i in range(N):
            if carrier_mask[i]:
                # local reconstruction of true_target (invariant is exact-but-local)
                new_setpoint[i] += 0.25 * wrap(true_target - setpoint[i])
            else:
                # adopt neighbors' setpoints (diffusion of intent across the mesh)
                nb_sp = setpoint[neighbors[i]]
                mean_nb = np.angle(np.mean(np.exp(1j*nb_sp)))
                new_setpoint[i] += 0.15 * wrap(mean_nb - setpoint[i])
        setpoint = new_setpoint

        # ---- dynamics: Kuramoto pull to neighbors (coherence) + pull to own setpoint ----
        dtheta = omega.copy()
        dtheta += K * np.sin(psi - theta)                  # mutual coherence
        dtheta += 0.6 * np.sin(setpoint - theta)           # teleological tug toward setpoint
        theta = wrap(theta + dt*dtheta + noise*rng.standard_normal(N))

        # ---- scores ----
        hom = float(np.mean(r))                                   # are we locked?
        tel = float(np.mean(np.cos(theta - true_target)))        # locked ON TARGET?
        hom_series.append(hom); tel_series.append(tel)

    return np.array(hom_series), np.array(tel_series), perturb_at

def summarize(h, window=150):
    hom, tel, p = run(h)
    # post-perturbation steady state
    hom_ss = hom[-window:].mean()
    tel_ss = tel[-window:].mean()
    return hom_ss, tel_ss, hom_ss - tel_ss

if __name__ == "__main__":
    print(f"{'h':>5} {'homeostatic':>12} {'teleological':>13} {'GAP':>8}   regime")
    print("-"*60)
    rows = []
    for h in [0.0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.50, 0.80, 1.0]:
        hs, ts, gap = summarize(h)
        rows.append((h, hs, ts, gap))
        regime = ("FROZEN: locked, off-target" if gap > 0.5 else
                  "EDGE: self-corrects" if ts > 0.6 else
                  "transitional")
        print(f"{h:>5.2f} {hs:>12.3f} {ts:>13.3f} {gap:>8.3f}   {regime}")

    # find critical h where teleological fidelity crosses 0.6
    print("\nCritical-threshold scan (where does intent survive perturbation?):")
    prev = None
    for h in np.linspace(0, 0.5, 26):
        _, ts, _ = summarize(h)
        if prev is not None and prev < 0.6 <= ts:
            print(f"  -> teleological fidelity crosses 0.6 near h = {h:.3f}")
        prev = ts