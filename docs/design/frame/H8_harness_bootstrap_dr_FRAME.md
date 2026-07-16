# H8_harness_bootstrap_dr — FRAME (canonical per-atom, doc-only)

**Atom:** `H8_harness_bootstrap_dr` · lane `H_harness` · epoch 5
· `level_current: 0` → `level_target: 2` · `loop_stage: idle` · dial 1 (`dial_inherited`)
· `depends_on: [H4_go_live_nfr_register]` (confirmed **already met** — H4 is at
`level_current: 1` = `level_target: 1`, `loop_stage: harden`, i.e. at its own target and no
longer idle; see §5).

**Turn:** H17 Lane-3 FRAME (doc-only, no BUILD code — EPOCH_GATING Rule 1; no map edit — F1,
level reported via `docs/design/atom_status/H8_harness_bootstrap_dr.yaml`).

---

## Why this doc exists (and why it is NOT churn)

H8's sole cited `evidence` entry, `docs/staging/ACTION_NEEDED_REDESIGN_AND_BOOTSTRAP.md`, **does
not exist on disk** (confirmed: `ls` returns "No such file or directory"). The atom therefore had
**no genuine canonical FRAME terminus** — its only recorded evidence pointer is dead, so the
intrinsic frame-saturation guard (`background/supervisor.py::_atom_has_frame_doc`, which requires
a resolvable `docs/design/**` path with `FRAME` in the filename) correctly reads H8 as
**un-saturated**, and the idle DISCOVER/FRAME draw keeps correctly re-offering it. This is that
missing terminus.

Rather than re-derive the requirement from nothing, the atom's own `simplifications` history
(2026-07-13 entry, QUEUE disposition) already carries a **real, precise, staged-doc-sourced**
scope: the missing `ACTION_NEEDED_REDESIGN_AND_BOOTSTRAP.md` was read and summarised *before* it
went missing, and that summary survives in the map. This FRAME **consolidates that surviving
record** against the **actual current runtime** (grounded by reading the real files below, not
assumed) into one canonical doc with a single stated BUILD-unblock gate. It does not duplicate the
runtime files' own docstrings — it cites them and states what reproducing/recovering *them*
requires.

---

## 1. What "the machine" actually is (grounded against real code, not assumed)

H3's own Part A finding (`docs/staging/done/PRODUCTION_READINESS_BASELINE.md`) already confirmed
`company/data/*.db` — the company's *operational data* — is backed up via the GitHub mirror. H8's
scope is the **complement**: the running processes and configuration that operate on that data,
none of which is "the data" itself. Enumerated from the real files (read, not guessed):

| Component | Real artifact | What must be reconstituted |
|---|---|---|
| Session watchdog | `background/session_watchdog.py` | The `claude` tmux session it monitors; `MAX_RESTARTS_PER_HOUR` cap; the `--dangerously-skip-permissions` authorization (a Tier-1 grant, per its own docstring — R7: this is a WALL, not something a bootstrap script may silently re-grant) |
| Autonomous turn runner | `background/autonomous_runner.py` | `claude -p` non-interactive launch path; `MAX_TURNS_PER_HOUR` rate limit; idle-detection threshold |
| Turn-granting authority | `background/supervisor.py` | The single dumb poll loop (`POLL_INTERVAL_SECONDS`) — "sole authority for turn-granting"; its own docstring names this as a R3 architecture-level rebuild after a real doorbell failure, i.e. it is *itself* a DR-relevant artifact (a prior single point of failure) |
| Fleet health | `background/health_check.py` | `EXPECTED_PANES` — the named tmux pane topology (`ntfy-responder`, `staging-watcher`, `session-watchdog`, `supervisor`, `dispatcher`, …) that constitutes "the stack" |
| Secrets | `background/secrets_location.py` | `~/.config/synthetic-enterprise/` (new, out-of-tree, 700/600-permissioned) + `background/.env.*` (old, in-tree fallback, mid-transition per the module's own docstring) — **both locations are currently live**, a named transitional SPOF this FRAME must record, not silently resolve |
| Egress control | `background/egress_allowlist.py` | Application-level allowlist only (no root/iptables — sudo is hook-banned); the named endpoints it guards |
| Concurrency safety | `background/tree_lock.py` | `fcntl.flock` on `docs/observability/.tree.lock`; auto-released on crash (no manual cleanup step needed — confirmed from its own docstring, a genuine DR-relevant property) |
| Turn-granting inputs | `docs/design/maturity_map.yaml`, `docs/design/atom_status/*.yaml` | The living plan-state itself — see DR scenario (b) below, the map is data *and* a machine dependency simultaneously |
| Model routing | CLAUDE.md's own "Model routing" section | `MAIN_SESSION_MODEL`, `TWIN_MODEL`, `AUTONOMOUS_TURN_MODEL` env/constant bindings — not versioned as a single file, a real inventory gap |
| Cron/scheduling | (not yet inventoried in this pass — see §6 simplification) | Whatever `CronList`/`RemoteTrigger`-class scheduled routines exist outside the tmux daemon set |

None of this is hypothetical: every row cites a file this fork actually read. What is **not yet
done** (correctly, since BUILD is epoch-gated) is turning the table into a tested runbook.

## 2. DR scenarios (named, not designed — the actual failure modes this atom answers)

1. **Lost/corrupted `maturity_map.yaml` or an `atom_status/*.yaml` inbox.** The map is the sole
   priority authority (P-1) and the sole turn-granting input for `supervisor.py`'s self-refill
   draw. Recovery path today: git history (the map is tracked, unlike `company/data/*.db` which
   needed the separate H3 finding to confirm backup coverage) — but **restore-from-git has never
   been drilled** for this specific file; a corrupt-but-committed map (bad YAML that still parses
   but drops atoms) is a distinct failure from a missing file and git alone doesn't catch it.
2. **Dead host (Skynet itself lost).** Every row in §1's table assumes Skynet. Recovery requires:
   the repo (GitHub-mirrored, confirmed by H3), the secrets (`~/.config/synthetic-enterprise/` —
   **NOT** GitHub-mirrored, by design, per `secrets_location.py`'s own stated purpose — so this is
   the one component whose recovery is NOT "clone the repo"), and re-establishing the tmux/pane
   topology `health_check.py::EXPECTED_PANES` names. No second machine has ever run this stack.
3. **Secrets-out-of-tree recovery.** The dual-location transition in `secrets_location.py`
   (new dir authoritative, old in-tree path a fallback for daemons not yet restarted onto new
   code) is itself a live DR risk: a bootstrap onto a clean checkout has **no secrets at all**
   until they are provisioned out-of-band — the repo, by design, cannot carry them (Option 2
   floor). The runbook must state the manual provisioning step, not assume it away.
4. **Backup/restore posture, honestly split.** `company/data/*.db`: confirmed backed up (GitHub
   mirror), per H3. The harness/config layer (§1's table): **currently zero backup posture beyond
   "it's in the repo" for the parts that are in the repo**, and explicitly *not* in the repo for
   secrets. This asymmetry — data DR is measured, machine DR is not — is the precise gap H8 exists
   to close, matching its own `real_world_twin`: "a real ops team's disaster-recovery runbook and
   its own tested RTO, not just an offsite database backup."

## 3. What level 1 and level 2 mean for THIS atom (H_harness terms)

- **Level 1 (documented, reproducible-bootstrap runbook + inventory):** §1's table completed into
  a full, verified inventory (every env var, tmux session name, systemd/cron unit if any, external
  service dependency) plus a written sequence that would reconstruct a working harness from
  {a clean checkout + a provisioned secrets directory}. Documentation only — not yet executed
  end-to-end. This is the natural next FRAME/DISCOVER-adjacent increment, but **still BUILD**
  (it produces a runbook artifact + likely a bootstrap script) — not doable in this doc-only fork.
- **Level 2 (tested cold-restart / restore-from-clean-checkout drill):** the runbook from L1
  actually **executed** against a clean directory or second host (per the existing 2026-07-11
  advisor amendment already on file: "to a SCRATCH location, never over live state"), with a
  **measured** time-to-working (RTO) recorded — not assumed, per R9. That measured RTO is the
  atom's own stated downstream consumer: it feeds `H4_go_live_nfr_register`'s recoverability
  entry (H4's `evidence` already includes `docs/design/H4_GO_LIVE_NFR_REGISTER.md`, which has a
  recoverability row waiting on exactly this number).

## 4. Known simplifications (R10 — named, not hidden)

- **Cron/scheduled-routine inventory is not yet done in this pass.** §1 flags it as an open row;
  a real BUILD-stage inventory must enumerate any `CronCreate`/`RemoteTrigger`-class routines
  alongside the tmux daemon set — a routine is just as much "part of the machine" as a pane.
- **Model-routing bindings are prose in CLAUDE.md, not a versioned config artifact** — a bootstrap
  that only clones the repo gets the routing *intent* but must cross-check the actual env vars
  MAIN_SESSION_MODEL/TWIN_MODEL/AUTONOMOUS_TURN_MODEL resolve to at runtime; this FRAME does not
  resolve that gap, it names it as BUILD scope.
- **This FRAME does not attempt the inventory or the drill itself** — per EPOCH_GATING Rule 1,
  producing the runbook and running the drill are both BUILD, correctly deferred to when the gate
  below opens. Naming the DoD is not meeting it.

## 5. Dependency status (verified against the map, not assumed)

`H4_go_live_nfr_register`: `level_current: 1`, `level_target: 1`, `loop_stage: harden` — **at its
own target already**, no longer `idle`. `depends_on: [H4_go_live_nfr_register]` is therefore
**already satisfied**; H8's remaining block is purely the epoch/BUILD-open dial below, not a
stalled upstream atom. (H4 is itself the eventual *consumer* of H8's L2 output — the measured RTO
— but that is a data dependency at L2, not a gate on H8 starting L1 work.)

---

## 6. The single BUILD-unblock gate (HELD at L0)

| Atom | Epoch | Level (held) | Single BUILD-unblock gate | Gate class |
|------|-------|--------------|---------------------------|------------|
| `H8_harness_bootstrap_dr` | 5 | **0 (→2)** | `depends_on` already met (H4 at target, §5); the sole remaining condition is **Epoch-5 BUILD-open** (TWIN, within the open epoch, per EPOCH_GATING_AND_ATOM_AUTHORSHIP.md §3a) — then BUILD does the §1 inventory + §3 L1 runbook, and separately the §3 L2 scratch-location drill with a measured RTO feeding `H4_go_live_nfr_register`'s recoverability entry. | DIAL (epoch sequencing) |

**Pre-BUILD action items (named, not done here — out of this Lane-3 doc-only scope):**
- Complete the cron/routine inventory row (§4) alongside the tmux pane table.
- Draft the actual bootstrap sequence/script from §1's table.
- Design and run the scratch-location restore drill (advisor amendment: never over live state).
- Record the measured RTO into `docs/design/H4_GO_LIVE_NFR_REGISTER.md`'s recoverability entry.

**Disposition:** level **HELD at 0** (idle, epoch-5, BUILD-gated per EPOCH_GATING Rule 1). This
FRAME is H8's canonical terminus; the next idle draw reads H8 as frame-saturated and yields to
genuinely-un-FRAMEd work instead. No BUILD code, no map edit (F1).

---

*Sources consolidated (not re-derived): H8's own `simplifications` (2026-07-13 QUEUE entry,
carrying the surviving summary of the now-missing `docs/staging/ACTION_NEEDED_REDESIGN_AND_
BOOTSTRAP.md`), `docs/staging/done/PRODUCTION_READINESS_BASELINE.md` (H3 Part A, data-backup
finding), `docs/design/H4_GO_LIVE_NFR_REGISTER.md` (the downstream consumer of the measured RTO),
and direct reads of `background/session_watchdog.py`, `background/autonomous_runner.py`,
`background/supervisor.py`, `background/health_check.py`, `background/secrets_location.py`,
`background/egress_allowlist.py`, `background/tree_lock.py` (the real machine this atom must be
able to reproduce). The missing evidence doc is flagged, not fabricated (R9/R7).*
