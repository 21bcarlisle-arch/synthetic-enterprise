**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Pre-registration: trial E-e, a minimal CLAUDE.md against the full one, on real seat turns (2026-11-16)

*Seat executor, Mon 16 Nov 2026, about 05:45 GMT. Written before any turn has run on the draft.
The steer is `docs/staging/advisor/DIRECTOR_STEER_TEST_CLAUDE_MD_BY_DELETING_AND_ADDING_BACK_AND_AUDIT_WHAT_EACH_SEAT_LOADS_2026-11-15.md`,
item 1. Backlog row: `docs/operations/EFFICIENCY_BACKLOG.md` E-e.*

## The arms

- **Full:** the live `CLAUDE.md`, 23,803 characters.
- **Minimal:** `docs/operations/EFFICIENCY_E_E_MINIMAL_CLAUDE_MD_DRAFT.md`, 9,052 characters (38%). It keeps,
  verbatim: the mission and canon quotes, the walls, "Where the rules live" and the Build line. It keeps,
  condensed: commit mechanics, map headroom, knowledge-first (K2, K8), what waits for the director, and
  pointers. It drops "How to behave when no rule applies" (6,771 characters) and the operating model's
  mechanics, which are enforced in code and published in `docs/operations/OPERATING_MODEL.md`.

The live `CLAUDE.md` and its 35,000-character cap are unchanged until the result.

## Design

- **Which seat:** seat_executor only. It already runs each turn in its own worktree reset to origin,
  so the arm is a file written into that worktree after the reset, never committed, and the base's
  bytes are written back after the turn. Assignment is a salted hash of the work id
  (`seat_executor.claude_md_arm`), so both arms draw from the same queue in the same hours, a re-drawn
  item keeps its arm, and the buckets are independent of the P2 model pilot's. **Opus turns only**,
  so the model is not a second variable. Window: 21 Nov to 28 Nov, UTC, after the Friday read of E-f; the first 25 per arm count.
  *(Corrected before any turn ran: the first draft of this paragraph said "alternates by turn".)*
- **Sample:** 25 turns per arm (about two days at 25 turns a day). Named turns: the session ids of the
  50 turns, listed in the result.
- **Confounds:** E-f (plugins off, 9554dcf49f) is live in both arms equally, and its after-window is read
  on Friday 20 Nov, before this trial opens, so neither trial moves the other's measure.
- **Guard:** a session cannot land the draft as `CLAUDE.md`. Staging CLAUDE.md runs
  `tests/tools/test_claude_md_integrity.py` in the pre-commit gate, and the draft fails three of its
  tests (it has no operating-model section). Measured 16 Nov by writing the draft over CLAUDE.md.

## Measures, and the predictions

| Measure | Source | Prediction (minimal against full) |
|---|---|---|
| Tokens per turn, first call | `tools.tick_burn_rate` per session | **Lower by 5,000–7,200** (14,751 characters at 0.416 tokens each is 6,100) |
| Context tokens per turn, whole turn | same | Lower by 5–15%; turn length may change, so this is the uncertain one |
| Gate refusals per turn (pre-commit and commit-msg) | surgical_land logs | No difference the sample can see |
| Wall-hook denials (`.claude/hooks`) | hook logs | 0–2 per arm; no difference |
| G5 and one-way-door refusals | `background/one_way_door.py` log | 0 in both arms |
| Landed share (turns with a promoted landing) | executor ledger | Within 15 points of the full arm |
| Reverts or corrections of landed work within 7 days | git log on bound paths | 0–1 per arm; no difference |

**Direction I expect:** cheaper, with no measurable loss in these measures. **What would refute it:** the
minimal arm shows more gate refusals or wall denials by 3 or more, or lands 15 or more points less, or
any landed commit from it is reverted for a reason a dropped line names.

## The bound the sample earns

At 25 turns per arm, an event that never occurs bounds its rate below 12% per turn at 95% (rule of
three). Only a large difference in refusals or landing (about double) would show. **What this sample
cannot see:** the dropped habits are mostly about method: pre-registering, printing numbers before
shipping, naming what a divisor counts, keying a control to the property. Their failures show weeks
later as a wrong published figure, not as a refusal in the turn. So a "no difference" result licenses
dropping those lines only from the always-loaded file, not from the project: each dropped habit tied to
a named past incident moves to a pointed-at file, and the result names the evidence for each line kept.

## Built with this pre-registration

- `background/seat_executor.py`: `claude_md_arm`, the write and the restore, and the arm on the
  `RUNNING` log line. Reverse by emptying `CLAUDE_MD_TRIAL_WINDOW`.
- `tests/background/test_the_claude_md_trial_never_lands_its_draft.py`: both arms reachable and off
  outside the window or on Sonnet; the draft written and the base restored; and the draft fails
  `claude_md_integrity.check`, which is what keeps it off origin.
