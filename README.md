# homeostasis_telos

Measuring the gap between **homeostatic coherence** (does the swarm stay locked?)
and **teleological fidelity** (is it locked *on the right target*?) in a
no-center, light-lag-bounded collective.

The short version: a self-tuning swarm can hold perfect internal coherence while
its actual purpose drifts out from under it — every local health check green,
the global goal lost. This repo measures when that happens and what prevents it.
**Read [CHARTER.md](CHARTER.md) for the why; it is the spec and the honesty
contract.**

## Layout

This is one repo with two halves that share a conceptual model but **not** a
build system:

```
homeostasis_telos/
├── CHARTER.md          # the claim, the two definitions, the honest-failure rule
├── README.md           # you are here
├── CLAUDE.md           # working agreement for AI agents in this repo
├── mise.toml           # pinned Erlang/OTP 29 + Elixir 1.20 (reproducible)
├── main.py             # ← the PYTHON ORACLE: the reference run, the source of truth
├── pyproject.toml      # Python deps (numpy), managed by uv
└── swarm/              # ← the ELIXIR/BEAM port: the real experiment
    ├── mix.exs
    └── lib/swarm_constitution/
```

- **`main.py` is the oracle.** It is small, fast, and correct, and its
  `h`-sweep is the number the BEAM port must reproduce before claiming anything.
  It does *not* model delay, partition, or failure — and that's the point: those
  are exactly what the BEAM half exists to add.
- **`swarm/` is the experiment.** Each oscillator becomes a `GenServer`,
  light-lag becomes real per-edge message latency, and carrier failure becomes
  `Process.exit/2`. See the three experiments in [CHARTER.md](CHARTER.md).

## Prerequisites

The BEAM toolchain is pinned in `mise.toml` (Erlang/OTP 29.0.2, Elixir
1.20.2-otp-29). To get an identical toolchain on any machine:

```bash
brew install mise          # if you don't have it
mise install               # reads mise.toml, installs the pinned versions
eval "$(mise activate zsh)" # or add this to your ~/.zshrc once
```

Python side uses [uv](https://docs.astral.sh/uv/) with a local `.venv`.

## Running the Python oracle

```bash
uv run python main.py
```

Expected shape of the output (the finding, not a fluke):

```
    h   homeostatic  teleological      GAP   regime
------------------------------------------------------------
 0.00        0.998        -0.325    1.323   FROZEN: locked, off-target
 0.05        ...           ...      ...     EDGE: self-corrects
 ...
```

`h=0` locks perfectly and points the wrong way; teleological fidelity is
restored at a startlingly low `h` (~0.04) because intent percolates across the
mesh. That low threshold is the thing the BEAM experiments stress-test.

## Running the BEAM port

```bash
cd swarm
mix deps.get      # once
mix test          # the reproduction gate: BEAM h-sweep must match the oracle
iex -S mix        # interactive: drive a swarm, inject faults, watch the gap
```

> Status: scaffold only. The reproduction gate (BEAM `h`-sweep matching the
> oracle on a uniform, zero-delay ring) is the first milestone. Until that
> passes, the BEAM numbers are not trusted — see CHARTER's "reproduction is the
> gate."

## The three experiments (priority order)

These are why the port exists. Each relaxes one assumption the oracle holds fixed:

1. **Delay vs. drift** — real per-edge `Process.send_after` latency raced against
   target-drift rate. *Can intent outrun purpose-drift across light-minutes?*
2. **Percolation** — sparsify / partition the connectivity graph. *Does the
   carrier set span it, or are neighborhoods intent-starved?*
3. **Invisible failure** — `Process.exit/2` on carriers. *Does teleology collapse
   while homeostasis stays green?* The scariest, and the most constitutionally
   important.

Full rationale in [CHARTER.md](CHARTER.md).

## A note on honesty

The experiment is only worth running if failure is genuinely available. It is
very easy to make a change that helps the swarm succeed instead of revealing
whether it *can*. The coherence metric must never reference the target; the
perturbation must stay novel; bounded coverage must be reported, not hidden. If
you touch the model, measure your change against CHARTER's honest-failure rule.
