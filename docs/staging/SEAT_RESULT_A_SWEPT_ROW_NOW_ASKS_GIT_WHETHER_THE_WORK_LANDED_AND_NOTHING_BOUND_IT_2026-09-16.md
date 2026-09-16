**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** none — Lane 0
delivery, "a-swept-row-must-ask-git-whether-the-work-landed-under-another-name"

**Class:** controls_that_cannot_fail

# A swept row now asks git whether the work landed and nothing bound it

Delivery seat, scheduled tick, 2026-09-16. Discharges the Lane 0 item
`a-swept-row-must-ask-git-whether-the-work-landed-under-another-name`. The defect is R15
fail-silent: the two non-residual answers were both written by hand-run commands, nobody ran one
in eleven weeks, so `NOT_DONE` was not a residual — it was the only reachable value. A dial wired
to a constant, and the dial is the one the seat grades itself with every stretch.

**Landed:** `background/delivery_lane.py`, `background/delivery_seat.py`,
`tests/background/test_a_swept_row_asks_git_whether_the_work_landed_under_another_name.py`.

---

## What was wrong

`background/delivery_lane._disposition` answers which of three things a window that closed with no
landing was. The three are correctly named and documented. Two of them —  `LANDED_ELSEWHERE` from
`note_landing_under`, `PREMISE_SPENT` from `note_premise_spent` — require somebody to have called a
function by hand. Nobody does. So every row the orientation brief has ever shown a seat reads
`not_done` with an empty evidence string, and the brief has to tell each reader to go and check
`git status` for themselves before starting anything.

The reading cannot distinguish LANDED-BUT-UNBOUND from NEVER-STARTED, and those want opposite
actions: bind and carry on, versus start. This is the sixth recorded instance of the class in this
lane, and the same shape one layer up (a repair that landed, an archival that was never committed)
has had SITE4 frozen for a week.

## What was built

`LANDED_UNBOUND` — a fourth disposition, and the first that **asks** rather than waiting to be
told. For a row whose window closed with no landing of its own:

1. the paths the item's own prose named are taken from `row["named_paths"]` — stamped at draw time
   by `record_draw(text=...)` from the whole doorbell, not the 200-char claim note — or, for rows
   that predate the stamp, re-read live from `DIRECTION.yaml` and the continuation store;
2. every candidate token is confirmed against `git ls-files`, peeling one dotted suffix at a time
   and offering `.py` at each step, because this project's prose spells a module
   `background/delivery_lane._disposition`. Nothing unconfirmed survives, so this is a join and not
   a guess;
3. `git log --all --since=@drawn --until=@(drawn+100min) -- <those paths>` is asked what landed on
   them **inside the window the item was actually given**;
4. any commit whose instant is already credited to some row of this ledger is dropped. That is what
   makes the answer *unbound* rather than *something happened*: several lanes commit into this tree
   every hour and share files constantly, and without this leg the busiest files would read as
   delivered work forever.

If anything in that chain cannot be answered — git silent, no confirmable path, prose gone from
both stores — it returns `None` and the row falls to the loud residual. An unavailable check is a
failed check.

### What the name means, and what it does not

`LANDED_UNBOUND`, not `DELIVERED`. It says *work landed on this item's paths inside its window and
nothing bound it*. That is what was measured. Calling it delivered would infer that the item
finished from the fact that its files moved, and the reader can only tell the difference if the
label does. The brief says so in the same words and gives the action that follows: read the commit
it names, `--landed <id> --commit <sha>` if it is the work, carry on rather than start.

## Keyed to the property, never to today's three ids

The property is: **a window that closed with a commit on its own named paths inside it is never
reported as evidence-free.** Nothing in the control names `some-id`, the gas-tariff row, or any
live id; the fixtures are synthetic ids and synthetic paths, and the one leg that touches the real
repo asks `git ls-files` a question whose answer is true on any checkout (`background/delivery_lane
._disposition` resolves to a tracked `.py`).

The partition is asserted in **one statement over all five readings** —
`assert saw_not_done and saw_landed_elsewhere and saw_premise_spent and saw_landed_unbound and
saw_delivered` — because a disposition that answers `NOT_DONE` to everything passes every
per-branch test ever written for it, which is the trap this lane has walked into through three
separate doors.

---

## PRE-REGISTRATION (written before the join was run against the live ledger)

Two rows are live in `drawn_without_landing()` at the time of writing, both `not_done` with empty
evidence:

| row | drawn | prediction |
|---|---|---|
| `some-id` | 8.7h ago | **`not_done`, unchanged.** It is a placeholder id no direction row names, so `_item_text` returns "" and no path can be confirmed. If it came back `landed_unbound` I would be reading someone else's commit. |
| `the-gas-tariff-type-read-becomes-the-c1b-roll-now-that-the-18-can-leave` | 13.6h ago | **`not_done`, unchanged** — but for a reason I cannot yet name. Either the row has left the live stores (no paths, join silent) or it names paths and the four commits inside its window are all about other subjects. The four subjects I read in that window are blind-arm artefacts, a worktree live-record resolver and two merges; none is a gas tariff. |

Neither prediction is the one this repair is for. The rows it is for are the ones the *next* sweep
sees, and the honest statement is that the live ledger does not currently hold a witness — the
control carries the witness instead, which is why the partition leg is synthetic and why it is one
statement.

### SECOND PRE-REGISTRATION — the retrospective sweep

Before running it: replaying the join over **every** never-landed row in the 339-row ledger. I
predict **zero** rows come back `landed_unbound`, and I predict it for a reason that is a claim
about the mechanism and not about the history: the durable `named_paths` stamp is new, so no
historical row carries one, and `_item_text` can only reach a row whose prose is still in
`DIRECTION.yaml` or the continuation store — which a finished stretch clears. If more than a
handful fire I have the reach-back wrong, and if one fires on a row whose window closed weeks ago
I should suspect the commit belongs to another lane and the `bound_at` leg is too weak.

### RESULT

**The two live rows: both predictions held.** `some-id` and the gas-tariff row both stay
`not_done`. But the two are `not_done` for *different reasons* and the reading still says one word
about both, which is the honest limit of this repair and is stated here rather than discovered
later: for `some-id` the join **could not run** (no direction row, no confirmable path); for the
gas-tariff row the join **ran and found nothing** — it names `simulation/run_phase2b.py` and
`tests/simulation/test_the_tariff_type_read_has_one_home.py`, and no commit touched either inside
its 100 minutes. I did not split those into two values. `git log` answers "did it land", and the
brief's `git status` instruction is about work that never left the working tree, which the join
cannot see at all — so both rows still need the same action from the reader, and a fifth value
that changed nobody's next move would be ceremony.

**The retrospective sweep: my prediction was WRONG, and being wrong found a defect.** I predicted
zero. Over 81 never-landed rows the join returns **4 `landed_unbound`, 3 `premise_spent`, 74
`not_done`**, and it could run at all on 15 of the 81. The prediction's *reasoning* was what
failed: I assumed a finished stretch clears the prose out of `DIRECTION.yaml` and the continuation
store, so the reach-back would reach nothing. It does not — the direction record accumulates, so
older items are still readable and the join has a subject for far more rows than I expected.

| row | commit it names |
|---|---|
| `a53-the-supplier-cm-charge-reaches-nothing` | `f4a645402` *the sim side reads the CM levy from the commons* — `company/regulatory/capacity_market.py`, `saas/opex_ledger.py` |
| `clear-the-unrecorded-level-bump-then-publish-once-...` | `a61ddd3e3` — `docs/design/maturity_map.yaml`, `docs/observability/gate_authorizations.jsonl` |
| `the-page-says-our-advantage-is-selection-...` | `62334dc76` *the honest concordance now carries the bound its own sample earns* — `site/capabilities/index.html` |
| `the-stretch-split-seven-and-seven-and-the-prereg-exists-twice` | `fb7aad35e` `SALVAGE(auto)` — that row's own pre-registration document |

All four read as the same subject as the row that named them. The last is the class in its purest
form: an auto-salvage commit preserving that stretch's work, bound to nothing, on the row's own
pre-registration file.

**What the wrong prediction caught.** The first draft kept a bare directory as a pathspec prefix,
reasoning that `git log -- docs/staging` asks the question the prose asked. Because I had expected
zero hits I read all four before believing them — and one of them was firing on `docs/design`, a
room every lane writes in, from prose that said "file it in docs/design". That is evidence in the
flattering direction and it is the failure this repair exists to end. `_paths_named_in` now keeps
**files only**; the control asserts `docs/staging/` extracts to `[]`, keyed to the property that a
place is not a subject. The same four rows survive the narrowing, on file evidence alone.

Had I predicted four and got four, I would have shipped the directory prefix.

## Mutations, all nine proven to fire

`_landed_unbound` call deleted · `NOT_DONE` returned always · the `bound_at` leg dropped · the
window's upper bound dropped · the pathspec dropped · paths returned unconfirmed · the `.py`
peel-back dropped · `record_draw` ignoring its new `text` · a git failure allowed to raise. The
partition control reds on the first two, which are the two that reproduce the defect itself.

The eighth is listed because a **gained parameter is this project's ungraded mutation** — every
fixture that stubs a function with `lambda *a, **k:` swallows a new argument silently. It was
mutated and it fires.

## What this still cannot see

- **Uncommitted work.** The join is over commits. The `git status` instruction in the brief stays,
  and stays for every `not_done` row, because nothing here looks at the working tree.
- **A row whose prose named no tracked file.** 66 of 81. They fall to the residual and say so by
  carrying no evidence, which is the loud direction.
- **Whether the commit FINISHED the item.** `LANDED_UNBOUND` says work landed on this subject and
  nothing bound it. The reader is told to read the commit, not to trust the label.

