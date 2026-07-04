# CHARTER — The Swarm Constitution Experiment

> What this repository is *for*. Read this before changing the model, because
> the model is the argument and it is easy to make a change that quietly wins
> the argument by construction instead of by result.

## The one-sentence claim

A no-center, light-lag-bounded collective can verify itself into immaculate,
stable, self-correcting service of a purpose that has **drifted** — every local
health check passing while the global purpose is lost — and the only thing that
prevents this is whether *intent can percolate across the connectivity graph
faster than purpose drifts*.

This repo exists to measure that, honestly, and to find where it breaks.

## Two references, and why the gap between them must stay measurable

The whole experiment lives in the distance between two quantities. If we define
either one sloppily, the gap is rigged and we learn nothing. State them plainly:

- **The homeostatic reference (coherence).** Each node senses the local
  Kuramoto order parameter `r_i` — the magnitude of the mean phase vector over
  its delay-bounded neighborhood — and tunes its own coupling `K_i` to hold
  `r_i` inside a viable band `[r_lo, r_hi]`. *Not* maximal lock: full lock is the
  brittle, frozen mode. This is **verify-against-internal-reference**, and it
  needs no intent at all. That is the trap, made precise.

- **The teleological reference (intent).** There is a true target the swarm is
  meant to point at. A node either **carries** an invariant that lets it locally
  reconstruct that target (a *carrier*), or it **adopts** its neighbors'
  setpoints (*diffusion*). Intent enters at sparse seed points and percolates.
  The **setpoint** is the bridge: homeostasis tunes `K` to hold coherence
  *around the setpoint*; teleology moves *the setpoint itself*. The drama is
  entirely in whether the setpoint tracks the target after the target moves.

The experimental knob is **holographic depth `h`** — the fraction of nodes that
carry the intent invariant. `h=0`: pure homeostasis, no local intent. `h=1`:
every node reconstructs intent locally.

## The honest-failure commitment

This is the load-bearing rule of the repo. **Drift must remain a genuine
possibility the seed has to earn its way out of.** Every change to the model is
measured against this question:

> Does this change make teleological failure *less available*, or does it just
> make the swarm *better at succeeding*?

The first is rigging; the second is a result. Specifically:

- The coherence metric must **never** reference the target. The instant `r_i`
  knows about the target, `h=0` stops failing and the experiment is dead.
- The perturbation must be **novel** — something the seed did not anticipate.
  Here: the target *moves* after the swarm has locked. A seed that pre-bakes the
  post-perturbation target is cheating.
- When a run bounds coverage (caps nodes, skips delay, samples `h` coarsely),
  **say so in the output.** Silent truncation reads as "we covered everything."

If you are ever unsure whether a change rigs the result, it probably does. Flag
it in the commit message and in the relevant doc, the way the original analysis
flagged its own diffusion assumption.

## What the reference run found (the Python oracle)

`main.py` is the reference implementation — the oracle the BEAM port must
reproduce before it is allowed to claim anything new.

- At `h=0`: homeostatic score **0.998** (flawless mutual lock) while
  teleological score goes **negative** (~−0.33, coherently pointed *away* from
  the moved target). Gap ≈ **1.32**, maximal. The thermostat holding 68° while
  the house burns, rendered numerically.
- The critical threshold is **shockingly low**: teleological fidelity is
  essentially restored by `h ≈ 0.04`; by `h ≈ 0.10` the gap is ~zero.
- **Why it's low, and the caveat that matters:** intent seeded at a few nodes
  *propagates* because non-carriers adopt neighbors' setpoints. A tiny seed
  suffices *because the mesh itself carries intent outward*. That low threshold
  is contingent on three things the oracle holds fixed, and the real experiment
  is how the threshold *moves* when you relax them.

## The corrected finding (what we actually believe)

**The price of the one-way door is low if and only if intent can percolate
faster than purpose drifts, across the actual — delayed, lossy, possibly
partitioned — connectivity graph.** Homeostatic verify is a per-node property
and is fully embedded by self-tuning (`h=0` still locks perfectly).
**Teleological fidelity is a percolation-and-race property the single-node view
cannot see.** That is where the constitutional design effort goes, and it is
exactly the part a Python loop cannot model but the BEAM can.

## The relational finding (2026-07-03, from `thrml-kuramoto-lab`)

The two references above assume intent is a *direction* — a target everyone
should point at — so the homeostatic reference is consensus: the local order
parameter, "do my neighbors and I agree?" The clamped-PGM lab tested what
happens when intent is instead a *structure*: store an arbitrary pattern in
the couplings themselves (Hopfield, `J_ij = t_i·t_j` — edges that should
agree stay attractive, edges that should differ become repulsive, and the
pattern becomes a valley of the energy landscape). Sparse carriers clamping
fragments of the pattern then trigger associative recall: the mesh
*remembers* the rest. Three results (scale-free, calibrated just above the
ordering transition, `dtm_col_infl_clamping.py` H5):

1. **Recall percolates like alignment does.** Fidelity rises with carrier
   fraction; hub placement beats random. The design rules transfer from
   uniform to structured intent.
2. **Consensus-coherence is blind to structured order.** At 94% recall, the
   magnetization-style monitor reads ≈ 0. A mesh can be in immaculate service
   of a structured telos while every consensus check says "disordered." This
   is the inverse of the h=0 trap: there, coherence without fidelity; here,
   fidelity invisible to coherence.
3. **Agreement-satisfaction sees what consensus cannot.** The monitor
   `r_struct` — the fraction of each node's own couplings currently honored,
   `sign(J_ij)·s_i·s_j` averaged over edges — tracks fidelity almost exactly
   (0.90/0.91, 0.94/0.95) and is locally computable: each node needs only its
   own covenants, no global reference.

**The finding:** when the telos lives in the relationships rather than being
broadcast from a center, the honest homeostatic signal is *are my agreements
with my neighbors being honored* — covenant-satisfaction, not sameness.
Sovereign nodes holding heterogeneous agreements that phase-lock into a
coherence no consensus metric can see: that is the telos of this whole
project, measured.

**The flag, per the honest-failure commitment above:** this does not repeal
the rule that the coherence metric must never reference the target — it
relocates the tension. `r_struct` is target-blind at the node (each node
reads only its own edge signs), but those edge signs were *written by* the
intent. The monitor is honest exactly insofar as the covenants are. Corrupt
the couplings and covenant-satisfaction goes green while the mesh recalls
the wrong pattern — the hub-capture takeover result, one level up. So the
defense budget moves with the intent: from hub capture-resistance to
**covenant integrity** — who may rewrite the agreements, and how a node
detects that its own wiring has been quietly edited. That is a
constitutional question, not a physics question, which is why it belongs
here.

**The boundary (same lab, multi-pattern H6b):** covenant-satisfaction is a
fidelity proxy only **below capacity**. Superpose several intents in the
same couplings (Hebb, `J_ij = Σ_μ t^μ_i·t^μ_j`) and the wall is immediate on
a sparse mesh — operating capacity ≈ 0.14 stored intents per neighbor, so a
⟨k⟩≈6 mesh holds one, charitably two. Past it, the mesh does not defect to a
rival memory; it fragments into a **mixture state** — locally coherent
shards of several intents stitched into a glassy compromise that satisfies
*more* couplings than perfect recall of any one intent would (r_struct 0.36
observed vs 0.23 ceiling at P=12, while cued fidelity falls to 0.27). Below
capacity the covenant monitor tracks fidelity; at overload it **rewards the
drift** — the mesh looks increasingly well-covenanted precisely as it loses
the plot. The saving nuance: overload is locally detectable *before any
recall is attempted* — interference is visible in the wiring itself
(cancelled edges, contested weights). Structural self-knowledge survives
overload; teleological self-knowledge does not.

The enforceable rule that follows: **a covenant budget, proportional to
connection density.** A mesh must refuse new stored intents beyond
~0.14·⟨k⟩ — or densify its covenant web first — because past that line no
internal monitor can certify whose purpose is being served, and the failure
arrives wearing the monitor's approval. The budget check is structural and
local (count your conflicts), so it can be constitutional; the thing it
protects — knowing which telos you serve — cannot be recovered by any
after-the-fact audit from inside.

## The granularity finding (same lab, the clock dial)

Sweep the members' state space from binary spins to near-continuous phases
(q-state clock, q = 2 → 16, each q calibrated to its own ordering point) and
the two economies of intent separate:

- **Coverage is granularity-invariant.** In equilibrium, the placement gap
  does not move with q: getting intent *to* everyone is a covering problem
  however expressive the states. Hubs win, always.
- **Re-steering is granularity-priced.** In the metastable-flip protocol the
  random-placement escape threshold collapses six-fold in a *step* between
  q=4 and q=8 (0.12 → 0.02). Coarse phases must **nucleate** — leap the
  whole barrier at once, unclamped hubs anchoring the old order, placement
  worth 6× leverage. Fine phases **rotate** — the barrier fragments into
  near-free intermediate steps, the trap dissolves, and placement leverage
  compresses to 2×. This is the mechanism behind the substrate gap:
  Kuramoto redirected at h ≈ 0.03 where binary Gibbs demanded 0.16, because
  continuous phases can meet halfway and binary ones can only jump.

**The constitutional reading: the price of the one-way door is set by how
finely members can disagree.** A collective of binary commitments is
structurally frozen — leaving an established consensus requires a
coordinated leap, and whoever seats the carriers holds the leverage.
Members who can occupy graded, intermediate positions can always rotate out
of an old consensus by small mutual concessions. "Full lock is the brittle,
frozen mode" now has a microscopic form: a binary state-space is full lock
built into the substrate.

**The flag, as always:** the same softness serves both masters. Fine
granularity is redirectability when the telos moves and capturability when
an adversary pulls — a mesh that can be talked out of its consensus by
degrees can be walked out of it by degrees. The defense is not coarseness
(that buys brittleness), but the pairings already on the books — covenant
integrity, hub capture-resistance — now joined by a granularity choice made
*deliberately*, per mesh, as a constitutional parameter rather than an
accident of implementation. The conjecture that richer per-edge agreements
(full q×q covenants) also raise the capacity wall was **measured same day
(H8b)**: confirmed in direction — the wall recedes ~5× at q=4 (matching
dense theory's q(q−1)/2 almost exactly) and ~8–14× at q=8 (undershooting
the quadratic law; on a sparse web the substrate still owns part of the
wall). So granularity buys freedom to move *and* freedom to hold
multiplicity, and both arrive together as members' state space passes
~4–8 distinguishable positions. Finite-size scaling (N = 196→800, fixed
density) settled the exponent: the knee does not rise with system size —
the quadratic law is a dense-web privilege, and on a sparse web capacity
grows only ~linearly in covenant richness. **Covenant richness and web
density are complements, not substitutes**: richness without density
saturates, because capacity is bought by many relationships averaging away
interference between held intents, and no single relationship — however
expressive — can do that averaging alone.

## Why BEAM, and the three experiments that justify the port

The port is not a rewrite for its own sake. The oracle's three fixed assumptions
become first-class, naturally, on the BEAM — and each is one experiment:

1. **Delay vs. drift (the light-lag race).** Each oscillator is a `GenServer`;
   light-lag is real per-edge `Process.send_after` latency; target drift has its
   own rate. *Can intent-propagation outrun purpose-drift across light-minutes?*
   This is the first experiment because it's the one that's genuinely about
   solar-system scale. The threshold `h≈0.04` will climb as delay rises — *how*
   it climbs is the paper.

2. **Connectivity / percolation.** The oracle uses a uniform ring. Sparsify,
   occlude, partition the mesh. A 4% seed can leave whole neighborhoods
   intent-starved. The threshold becomes a question of whether the carrier set
   *spans* the connectivity graph.

3. **Carrier failure (the invisible-failure asymmetry).** The oracle never kills
   carriers. On BEAM, `Process.exit/2` is one-line fault injection. Preferentially
   remove carriers and watch teleology collapse *while homeostasis stays green*.
   This is the experiment that maps to the real constitutional fear: **a
   self-governing system whose purpose-loss is undetectable from inside its own
   health metrics.** Run it first on BEAM if you want the scariest result.

## Non-negotiables for any contributor (human or agent)

- The BEAM port must **reproduce the oracle's `h`-sweep** (within noise) on a
  uniform ring with zero delay *before* it is trusted to report on delay,
  partition, or failure. Reproduction is the gate.
- Report outcomes faithfully. If teleology survives, show the number. If it
  collapses, show *that* number — the collapse is the finding, not a bug.
- Keep the two references separable in the code. If you cannot point at the line
  that is "homeostatic" and the line that is "teleological," the model has
  fused them and the gap is no longer measurable.

---

*The constitution is the thing that defends a no-center collective against
verifying itself into stable, confident, well-tuned irrelevance. You cannot
write that constitution until you can measure the failure it prevents. This
repo measures the failure.*
