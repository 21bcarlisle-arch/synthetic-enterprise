**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `land-the-ledger-guard-ratchet-repair-and-let-the-bound-fall-to-what-it-reaches`) · **Class:** controls_that_cannot_fail

# RESULT — the stem selector cannot reach 27 whole-tree ratchets, and my band said 20

Discharges **item 3** of
`SEAT_FINDING_THE_UNGUARDED_LEDGER_WRITER_RATCHET_HAS_BEEN_RED_AT_HEAD_FOR_TWO_WEEKS_AND_ITS_OWN_MESSAGE_SAYS_DO_NOT_DO_THE_EASY_THING_2026-09-09.md`
— *"find out why nothing selected this test for two weeks"* — the one item that repair left open.

Pre-registered before the census ran:
`docs/staging/records/PREREG_HOW_MANY_WHOLE_TREE_RATCHETS_CAN_THE_STEM_SELECTOR_NEVER_REACH_2026-09-10.md`.

## The answer to item 3

`tools/pre_commit_test_gate.py` selects tests two ways: a fixed `CONTROL_TESTS` list that runs
whenever any code/config file is staged, and otherwise **by filename stem** — a staged
`background/X.py` selects `tests/**/test_X.py` and `tests/**/test_X_*.py`.

`tests/background/test_live_ledger_guard.py` was not in `CONTROL_TESTS`. Its only selector was
`background/live_ledger_guard.py` itself. Its subject is every `background/*.py` that writes under
`docs/observability/`. **Subject set = a whole package; selector set = one stem.**

Proved rather than asserted, by calling `select_targets` directly on five of the modules the drift
actually landed in:

| staged module | targets selected | ratchet among them |
|---|---|---|
| `background/supervisor.py` | 18 | **no** |
| `background/notify.py` | 18 | **no** |
| `background/process_run_complete.py` | 17 | **no** |
| `background/worker_tick.py` | 17 | **no** |
| `background/disk_headroom.py` | 17 | **no** |

`tests_for("background/live_ledger_guard.py")` returns exactly `['tests/background/test_live_ledger_guard.py']`
and nothing else reaches it. The assertions were never wrong; they fired correctly the instant
anything ran them. This is R15's FAIL-SILENT killer at the **selection** layer.

> **CORRECTED 2026-09-10, beside the claim. The last sentence is wrong, and it makes this
> document's recommendation aim one layer too low.** The stem-selector measurement above is
> sound — the pre-commit gate genuinely cannot reach these tests — but that was never the binding
> constraint, so it is not a FAIL-SILENT. The **nightly unscoped census** selects everything, ran
> every night, and named this exact test id as red on seven of seven journalled nights with age
> attached; the register it renders was named in **3,421** supervisor doorbell lines and sits
> **7th of 138** in the ranked work queue. Nothing was silent. The failure is between the register
> and a reader: one undifferentiated 139-name blob, carrying no count and no age.
>
> **So recommendation (3), "change the selector", is withdrawn as the fix for this class.** It
> would make these tests run earlier at commit time, buying earlier notice of a fact already
> published 3,421 times and read zero times, at a real cost on every commit — while the budget
> finding is live. The measurement, the refuted 27-vs-11 band, and the refusal to add 27 lines to
> `CONTROL_TESTS` all stand.
> `SEAT_FINDING_THE_FOURTEEN_DAY_RED_WAS_SURFACED_3421_TIMES_AND_THE_REGISTER_EVERY_CLEAN_WORKTREE_READS_IS_THE_830_ROW_WRECK_2026-09-10.md`.

## FIXED, with the fix proven able to fail

`tests/background/test_live_ledger_guard.py` is now the eighth entry in `CONTROL_TESTS`, with its
cost stated (~1.6s for 15 tests, 0.79s of it the census assertion — 0.27% of the 600s hook budget
the standing budget finding tracks).

Three controls in `tests/tools/test_pre_commit_test_gate.py` grade it, keyed to the **property**
rather than to today's list:

- a `background/some_new_daemon.py` commit — a path that cannot match by stem — must select it;
- the entry's removal must be **visible** (poison round: both controls go red, naming the defect,
  and green returns on restore — run before the green was believed, not after);
- the five real modules above must remain stem-unreachable, so the mechanism claim in the comment
  is asserted rather than left as prose. If any gains a stem route, the comment is wrong and it reds.

The second control also pins the test's subject (`BACKGROUND_DIR.glob("*.py")`): if the census is
ever narrowed to something a stem selector *can* reach, the `CONTROL_TESTS` entry stops being
earned and the assertion says so. A control pinned to today's answer would go red when the code
became more honest; this one does not.

## The claim "not specific to this file" — CONFIRMED, by instance

The finding's closing line was that the same silence would cover any other ratchet in
`tests/background/`. **It does, and one of them is red right now**:
`test_seat_guard_daemons.py::test_every_main_entrypoint_is_guarded` — nine daemon entrypoints with
no seat guard, red in a clean HEAD extract, observed-but-not-baselined, same whole-package subject,
same stem-only selector. Filed as its own BLOCKING finding with the nine names. It is deliberately
**not** added to `CONTROL_TESTS` while red, because that would wedge every lane.

## MY PREDICTION WAS REFUTED, and this is the number that did it

Recorded beside the result rather than quietly revised.

| quantity | predicted (band) | measured | verdict |
|---|---|---|---|
| unreachable whole-tree ratchets in `tests/background/` | 3 (1–6) | **6** | held, at the band's edge |
| unreachable whole-tree ratchets across all `tests/` | 11 (5–20) | **27** | **REFUTED — 2.5x my point estimate, outside the band** |
| `CONTROL_TESTS` already holds ≥3 of this shape | ≥3 | **3** | held, at the edge |
| the one test file costs <3s | <3s | 1.6s | held |

Two of my four predictions landed on a band edge and one broke through it. The direction of the
error is the informative part: **I under-estimated how common this shape is, having just spent the
turn reading ten long comments about it.** The class is recognised in this repo and has been fixed
ten times one instance at a time; that history is exactly what made 11 feel generous.

## What I am NOT doing, per the prereg's own stated threshold

The prereg said: *"If it returns more than 20, adding them all to an always-run list is not
affordable and the answer is a different instrument, not a longer list."* It returned 27. **So I
am not adding 27 lines to `CONTROL_TESTS`**, and I am reporting the count rather than picking the
flattering half of my own rule.

The predicate is stated in the prereg and was fixed before the run. It is a **proxy that
over-counts** — it flags any test file that both globs a non-`tests/` source tree and compares a
count to an integer literal, so some of the 27 are not ratchets in the load-bearing sense, and some
have a legitimate non-stem route (the site lane gate runs `pytest site/` separately, for instance).
Over-counting is the safe direction for this to be wrong in, and **I have deliberately not narrowed
the predicate after seeing the answer** — a narrowing added to fix a false positive is asymmetric,
and only the false positives would get a comment.

The 27 by subject tree: `site` 6, `docs` 6, `company` 4, `background` 3, `sim`/`simulation` 3,
`tools` 2, `saas` 1, plus two spanning pairs. Full list in the census output; the six in
`tests/background/` are `test_live_ledger_guard.py` (now fixed), `test_seat_guard_daemons.py` (red,
filed), `test_ntfy_responder.py`, `test_publish_gate_subject_is_head.py`,
`test_the_responder_dedup_memory_survives_a_corrupt_read.py` and
`test_the_responder_refuses_to_guess_whose_a_message_is.py`.

## What is next — and the honest shape of it

Three doors, and I am not pretending the choice is settled:

1. **A longer list.** Cheapest per instance, and it is what the last ten fixes did. At 27 it stops
   being cheap: the 600s hook budget already has 393s spent by two test files.
2. **A meta-control** that refuses a new whole-tree-subject test unless it is in `CONTROL_TESTS`.
   Tempting and probably wrong per CLAUDE.md — *"a control that only guards your own controls is
   usually not worth having"*, and this would be a file of rules breeding rules. It also cannot fix
   the 27 already here.
3. **Change the selector**, so a test declaring a directory subject is selected by changes to that
   directory. This is the one that addresses the class rather than the instances, and it is a real
   piece of design work with a real cost question attached — it would widen selection on every
   commit and the budget finding is live.

**My recommendation is (3), scoped by measurement first**: count what selection actually costs
today across a sample of recent commits before designing the widening, because the whole argument
against it is a cost nobody in this thread has looked at. That is a separate atom and it is not
this turn's.

Item 3 is discharged for its named instance and the general question is now sized, pre-registered
and open with a recommendation — which is a better state than the "cheaper, separately" it was
parked at, and I am not claiming it is finished.
