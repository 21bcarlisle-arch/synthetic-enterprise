# FRAME — turnkey spec for the queued forward-discovery draw FAIL-OPEN fix

**Atom:** `H_forward_discovery_draw` (maturity_map.yaml, `expert_hour: attempted_finding_open`).
**Status of THIS doc:** DISCOVER/FRAME output (design only, no BUILD code). The code change it
specifies is `background/supervisor.py` + `tests/background/test_forward_discovery_draw.py`, which
is BUILD and director/twin-gated per the atom's `blocked_on` — this doc makes that BUILD turnkey and
R15-provable so it lands in one mechanical pass when the H-lane opens.
**Provenance:** the finding was raised by the 2026-07-22 Expert-Hour red-team (commit `027e67133`) and
is LIVE-CONFIRMED — this scheduled tick fired with the register all-DISCOVER-complete, i.e. the exact
FAIL-OPEN churn the finding predicts. Framed 2026-07-22.

---

## 1. The defect (confirmed against real code, not the commit summary)

`background/supervisor.py::_forward_discovery_tracks()` (line ~1437) parses the register with
`_FWD_TRACK_RE = ^##\s*(F\d+)\s+[—-]\s+(.+?)$` and returns **one entry per section HEADER present**.
It never inspects whether that track has an OPEN item. `test_real_register_is_nonempty` asserts the
F1–F5 headers are permanently present. Therefore, in the register's real and by-design-permanent
state — **all of F1–F5 DISCOVER-complete** (today's state, and the resting state until the director
opens a BUILD track) — `_forward_discovery_draw()` returns non-None, so `_is_drained_and_gated()`
(line ~1692, via the `if _forward_discovery_draw():` guard at ~1729) can **never** return True and the
supervisor can **never** auto-rest.

Under R15 doctrine this is **FAIL-OPEN**: the control reports work-available on an all-closed
authorized set. The R15 both-ways proof only tests the two extremes — headers-present ⇒ must-not-rest,
and empty/absent FILE (`_EMPTY_REGISTER`) ⇒ may-rest — but the empty-file state is unreachable in
production (the sibling test forbids deleting the standing headers). **The most common real state —
every track present, every track closed — is untested and produces perpetual non-rest churn** (the
"re-granting a turn every ~2min with nothing new to do" class CLAUDE.md names in its B2_OPEX note).

## 2. Sharpening the fix — the register ALREADY carries a machine-readable status

The commit-message finding said "honour a `DISCOVER-complete`/status marker OR an open-item count".
On inspection the register **already has a canonical status surface**: the summary table
(`docs/design/FORWARD_DISCOVERY_REGISTER.md` lines ~19–23) has a `status` column, and each track's cell
reads `DISCOVER-complete <date> (...)` when closed. **So no new register format is needed** — the fix
is a status-aware parse of the surface that already exists.

**One latent inconsistency fixed as part of this FRAME (doc-only, agent-drawable):** F3's table cell
read `DISCOVER pass done 2026-07-22` while F3's body (line ~171) and the register summary (lines ~332,
~356) both state F3 is DISCOVER-complete. A parser keyed on the literal token `DISCOVER-complete` would
therefore have **mis-drawn F3 as open** — a second, quieter fail-*closed*-in-the-wrong-direction bug.
The F3 cell is normalised to `DISCOVER-complete 2026-07-22` in the same commit as this doc, so every
closed track's status cell now begins with the exact canonical token.

## 3. Turnkey BUILD change (for when the H-lane opens)

**3a. Parser.** Give `_forward_discovery_tracks()` an `open_only: bool = True` (default) parameter, or
add a sibling `_forward_discovery_open_tracks()`. A track is OPEN iff its **summary-table status cell
does NOT begin with `DISCOVER-complete`** (case-insensitive, after stripping markdown/whitespace).
Parse the table rows (`| **Fn** | ... | <status> |`) to read the status cell; fall back to OPEN if a
header has no matching table row (fail-*safe* toward work, never toward false-rest at the extreme —
but see the R15 test below which pins the all-closed case). `_forward_discovery_draw()` draws only
from open tracks; returns None when none are open. `_is_drained_and_gated()` then correctly returns
True in the all-closed state, and the supervisor rests.

**3b. Preserve the existing guarantees.** The must-not-rest guarantee still holds because a genuinely
OPEN track (network restores a new open item → its status cell no longer says DISCOVER-complete) is
still drawn. The genuinely-empty/absent-file guarantee is unchanged.

## 4. The R15 test the finding itself flagged as missing (BUILD, same commit)

Add to `tests/background/test_forward_discovery_draw.py`:

- `test_all_tracks_discover_complete_allows_rest` — a register with all F1–F5 headers present but every
  summary-table status cell `DISCOVER-complete`: assert `_forward_discovery_draw()` is None AND
  `_is_drained_and_gated()` is True. **This is the currently-untested common state and the mutation
  target** — it must FAIL against today's header-presence parser and PASS against the status-aware one.
- `test_one_track_reopened_must_not_rest` — same register but one track's status cell changed to an
  open marker (e.g. `OPEN: <item>`): assert the draw returns that track and `_is_drained_and_gated()`
  is False. Proves the fix did not over-correct into false-rest.

Both must be run as R15 mutation tests (kill the status check → `test_all_tracks_..._allows_rest`
fires) so the control is proven able to fail on its own named defect.

## 5. Why this stays QUEUED, not fixed on sight

§3–§4 touch `supervisor.py` and the test file — BUILD, and `H_forward_discovery_draw` is off the open
product fronts (`blocked_on` H-lane open, director/twin per EPOCH_GATING). Per SELF_INTERRUPT_DISCIPLINE
the fix is queued, not applied. What IS agent-drawable now and done in this pass: this FRAME spec, the
F3 status-cell normalisation (doc-only), and escalating the now-live-confirmed churn to the director via
NTFY (the machine is genuinely churning ⇒ the interrupt threshold SELF_INTERRUPT names is met).
