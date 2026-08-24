**Severity:** LATENT · **Lane:** H_harness

# The memory governor entered pressure, lost two processes and recovered without saying a word

**Found by:** worker tick 2026-08-24 15:45–16:30 BST, drawn on the RUNG-1d "PRODUCER SILENT
(PRIORITY ZERO)" doorbell, while re-deriving `CLASS_WEIGHTS_MB["sim_run"]` from systemd's
record.

**Not repaired here.** The weight this tick landed had to be right before anything is wired to
it — a governor wired to a constant that is 2.2x short admits jobs into memory that is not
there, which is worse than a governor nobody calls. Filed rather than fixed on sight
(SELF-INTERRUPT DISCIPLINE: the machine is not blocked).

## Class registration

Belongs to `no_caller_and_never_runs`.

Declared rather than left to the title regex: this document's title names its MECHANISM (an
alarm that did not speak), not its FAMILY, and would classify as `None` — the silent
fail-open the classifier's own comment block describes.

## Observed, with evidence (R9)

`background/resource_headroom.py` has four outputs. **One of them reaches a human.**

| output | caller | reaches anyone? |
|---|---|---|
| `observe()` → episode file | `background_worker.py:612` | **yes** |
| `alarm_line()` | none anywhere | no |
| `note_line()` | none (`daily_self_note.py:436` imports `suite_duration_watch`'s, not this one) | no |
| `admit()` / `reservation()` | none | no |

**The wired caller reads a key this module never sets.** `background_worker` does
`_reading.get("alarm")`; `resource_headroom.observe()` returns `{sample, episode, transition}`
and never sets `"alarm"`. `disk_headroom` — described in its own docstring as "the same
shape" — *does* set `payload["alarm"]` at line 439. The two modules diverge at exactly the
point where the message reaches a person. `alarm_line()`, the function that converts a
`transition` into that message, is the orphan in the table above.

**The counted proof.** In `docs/observability/background-worker-log.md` (6,675 lines):

```
disk-headroom: 29        console-record: 9        lane-formation: 3
memory-headroom: 0       two-rooms-repair: 0
```

The loop runs and its other observers speak. `memory-headroom` has never logged once.

**And it had something to say.** `docs/observability/.resource_headroom_episode.json`, live:

```json
{"state": "ok", "since": "2026-08-24T11:22:55Z",
 "recovered_from": {"since": "2026-08-24T10:22:54Z",
                    "worst_available_mb": 324.3, "victims": 2}}
```

The governor entered pressure, watched available memory fall to **324 MB**, recorded **two OOM
victims** inside that episode, and recovered — on the same day the producer was OOM-killed
fourteen times. Both transitions fired. `transition` was `"entered"` and then `"recovered"`.
Nothing printed, because the only function that renders those into a sentence has no caller.

This is not a design gap. The module's R5 doctrine, its hysteresis gap, and `alarm_line`'s
two carefully-written payloads are all built and correct. They are *unreachable*.

## Why this is the class, not an instance (R10)

The instance fix is one line. The class is `no_caller_and_never_runs`, and this module is
already its most-cited member: `tests/tools/test_console_instruction_record.py:171` names
`resource_headroom` as the class exemplar — *"sat unwired for nine days after being built
for"* — and `background/disk_headroom.py:10-22` says the same commit that built disk_headroom
wired `resource_headroom` into the worker loop. **That wiring was real and it was partial.**
The observer got a caller; the three things it computes for a human did not. So the module
that this repository holds up as the cautionary tale of unwired code is *still* three-quarters
unwired, and the test that names it passes because it only ever asserted the module was
imported somewhere.

The class-level question this raises, and the reason it is filed rather than patched: **the
orphan ratchet checks that a MODULE has a caller, not that its OUTPUTS do.** Every finding in
`no_caller_and_never_runs` so far is a whole module nobody reached. This is the next shape —
a reached module whose reachable surface is one function of four — and the ratchet is
structurally blind to it. A control that counts imports cannot see this.

## What it cost

Nothing yet, and that is why it is LATENT rather than BLOCKING. But the counterfactual is
specific: on 2026-08-24 the box lost 14 producer runs and 2 further processes to the OOM
killer over six hours, and the alarm designed to announce exactly that — built after 64
lifetime kills, for this exact failure — was silent throughout. The four hours the RUNG-1d
doorbell spent asserting the wrong diagnosis are four hours a `MEMORY PRESSURE: 324 MB
available … lifetime oom kills 262` line would have ended immediately.

## Recommended, in priority order

1. **Set `result["alarm"] = alarm_line(result)` in `observe()`.** One line; R5 is already
   satisfied because `alarm_line` returns `None` on a `None` transition. Needs a test that
   fails on the current code — assert the wired caller's key, not the function's return, or
   the test re-passes on the same orphan.
2. **Give `note_line()` its caller** in `daily_self_note.py`, beside the
   `suite_duration_watch` one already imported there.
3. **Widen the orphan ratchet from modules to public outputs**: a public function nothing
   calls is the same defect one level down. This is the R10 closure and the only one of the
   four that stops the class recurring; it is also the one that needs designing rather than
   typing, because "public function with no caller" over this repo will have a long tail of
   legitimate CLI/API surface to exempt.
4. **Wire `admit()`/`reservation()` into `sim_runner.py`** — the 13.5 G job the governor was
   built for still never asks. Deliberately LAST and deliberately not now: with `sim_run`
   correctly declared at 13,824 MB against a 24 GB guest, an `admit()` call would defer runs
   whenever another heavy job holds a reservation, and a deferral loop that takes the site
   stale is the outage this doorbell exists to catch. It needs the deferral-retry path thought
   through first, which is a design pass, not a wiring change.
