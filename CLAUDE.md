# CLAUDE.md — working agreement for this repo

Read [CHARTER.md](CHARTER.md) first. It is the spec *and* the honesty contract.
This file is the operational layer: how to build, where things live, and the
rules that keep the experiment honest in code.

## What this repo is

A two-language experiment measuring the gap between homeostatic coherence and
teleological fidelity in a no-center swarm. `main.py` is the **Python oracle**
(reference truth); `swarm/` is the **Elixir/BEAM port** (the real experiment,
which adds delay, partition, and failure the oracle can't model).

## Toolchain (do not guess — it's pinned)

- BEAM versions are pinned in `mise.toml`: **Erlang/OTP 29.0.2**, **Elixir
  1.20.2-otp-29**. Get them with `mise install`. Activate with
  `eval "$(mise activate zsh)"` (or it's in the user's shell rc).
- Python: **uv** with a local `.venv`, deps in `pyproject.toml` (numpy only).
- `mix`, `iex`, `elixir`, `erl` only exist after mise is active. If a command
  says "not found," run `eval "$(mise activate zsh)"` first — don't reinstall.

## Build / test / run

| Task | Command |
|------|---------|
| Run the oracle | `uv run python main.py` |
| Compile BEAM | `cd swarm && mix compile` |
| Test BEAM (the reproduction gate) | `cd swarm && mix test` |
| Interactive BEAM | `cd swarm && iex -S mix` |
| Format Elixir | `cd swarm && mix format` |

Always run `mix format` before finishing Elixir work; the repo expects
formatted code.

## The honest-failure rules, in code terms

These are the CHARTER non-negotiables, restated as things you must not do:

1. **The coherence metric must never read the target.** `r_i` is computed only
   from neighbor phases. If you find yourself passing `true_target` into
   anything homeostatic, stop — that rigs `h=0` into succeeding and kills the
   experiment.
2. **Keep the two loops textually separable.** There should be an obviously
   "homeostatic" block (tune `K` to hold `r` in band) and an obviously
   "teleological" block (carriers reconstruct target, move setpoint). If they
   fuse, the gap stops being measurable.
3. **Perturbations stay novel.** The target moves *after* lock, and the seed
   must not pre-bake the post-move target.
4. **No silent caps.** If a run limits node count, skips delay, or samples `h`
   coarsely, the output must say so. Silent truncation reads as full coverage.
5. **Reproduction is the gate.** The BEAM port must reproduce the oracle's
   `h`-sweep (within noise) on a uniform, zero-delay ring before it's trusted to
   report on delay, partition, or failure.

When a change could rig the result, flag it in the commit message and the
relevant doc — mimic how the original analysis flagged its own diffusion
assumption. Honesty about a possible rig is worth more than a clean number.

## BEAM model mapping (how the oracle becomes OTP)

The port is a structural translation, not a reinvention. Hold this mapping:

| Oracle concept (`main.py`) | BEAM realization |
|----------------------------|------------------|
| One oscillator `theta[i]` | one `GenServer` holding its own phase |
| Delay-bounded neighborhood | the set of pids a node may message |
| Light-lag | per-edge `Process.send_after` delay |
| Homeostatic loop (tune `K`) | the GenServer's periodic `handle_info(:tune, …)` |
| Carrier holds intent invariant | carrier state holds the invariant; non-carriers request neighbor setpoints |
| Setpoint diffusion | message-passing of setpoints between neighbors |
| Killing carriers (fault test) | `Process.exit(pid, :kill)` — one-line fault injection |
| Nested local consensus | the supervision tree gives this structure for free |

Idiomatic OTP, not a Python transliteration: prefer message passing over shared
state, let supervisors own lifecycle, keep each GenServer's state small and
local. The locality *is* the experiment — a node knowing more than its
neighborhood would cheat.

## Conventions

- Elixir code lives under `swarm/lib/swarm_constitution/`. Tests mirror it under
  `swarm/test/`.
- The reproduction gate belongs in `mix test` so it can't silently rot.
- Don't move `main.py`; it's the oracle and external references point at it.
- Commit `mise.toml`, `pyproject.toml`, `uv.lock`, and `swarm/mix.lock` —
  reproducibility is the point of a measurement repo.
- `_build/`, `deps/`, `.venv/`, `*.beam` are build artifacts — keep them out of
  git (see `.gitignore`).

## When in doubt

The question that settles most design choices here: *does this make teleological
failure less available, or does it make the swarm better at succeeding?* The
first is rigging and is forbidden; the second is a result and is the point.
