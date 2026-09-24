**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# `refresh_to_head`'s ONLY affirmative grade over the whole real population is wrong in the destructive direction: a producer WHITELIST key is not a Python name, so a copy that adds two published artefact keys reads as "supplies nothing"

Claim id: `apply-the-new-staged-too-door-to-the-shared-trees-staged-stale-copies`.
Measured 2026-09-24 from an isolated worktree at `2998d0750` (== `origin/main`), surveying the
shared tree `/home/rich/synthetic-enterprise` (HEAD `430e5b00e`, 38 behind / 4 ahead).

The item that produced this was a *direction* item: run the newly-landed `--staged-too` door, which
had never been executed outside its tests. Its own premise was spent. Running the door anyway is
what found the defect below — **the first time it has ever been pointed at real bytes.**

---

## 1. The drawn premise, re-measured — SPENT

The item's premise: *"The shared tree HAS staged entries right now (`docs/direction/DIRECTION.yaml`,
`docs/direction/decisions.jsonl`)."*

```
git diff-index --cached --name-only HEAD | wc -l      ->  0
git ls-files -u | wc -l                               ->  0   (no unmerged entries either)
```

**Zero staged entries.** `_staged_paths()` is `git diff --cached --name-only`
(`tools/refresh_to_head.py:261`) — index against HEAD — so the `STAGED` branch
(`judge_copy`, line 338) cannot be entered for any path in the tree. `--staged-too` has no subject.
Not raced: **structurally unreachable** until something stages a path again.

### How it was spent — the refusal's named hazard was enacted, benignly

The two paths were not refreshed. They were **committed**, by the shared tree's own HEAD:

```
430e5b00e  delivery seat: direction for the next stretch
           touches docs/direction/DIRECTION.yaml and docs/direction/decisions.jsonl
```

That is exactly what the STAGED refusal warns of — *"A commit from that index makes the tree from
the INDEX copy, not the working one."* It happened, between the door landing and this draw.

**Benign here, and measured rather than assumed:** `origin/main`'s last landing of both paths is
`13203ed91`, and `git merge-base --is-ancestor 13203ed91 430e5b00e` is TRUE. The committed index
copy is the strictly *newer* draft of a file rewritten every stretch — a rewrite, not a revert.

**Worth keeping:** a STAGED stale copy has two exits and only one is the door. The other is *the
holder commits it* — faster, needs no flag, leaves no record that the staleness question was ever
asked. A door whose population drains through an unmonitored second exit will read as "never
needed" rather than "never ran".

---

## 2. Pre-registration — written before the survey, results beside each

Recorded before running anything. Verbatim, with outcomes appended:

* **P1** — `STAGED` fires **0 times** over the 430 dirty tracked paths at `--base origin/main`.
  → **CONFIRMED.** 0/430.
* **P2** — At least one path grades `refreshable`.
  → **CONFIRMED**, and by the narrowest possible margin: exactly **1** of 430.
* **P3** — The modal verdict is a refusal; I expect `refused_no_reader` or
  `refused_supplies_names_head_lacks` to be the largest bucket.
  → **HALF REFUTED.** Modal *is* a refusal, but I named the wrong one. The largest bucket is
  `refused_rival_values_no_key_the_base_lacks` at **239/430 (56%)**, which I did not predict at all.
  I was reasoning about code files; the population is 308 `.json`.
* **P4** — `refused_clock_could_not_answer` fires 0 times.
  → **CONFIRMED.** 0/430. No content grade below it is clock-blind.

### The full tally (430 paths, 50s, read-only)

```
239  refused_rival_values_no_key_the_base_lacks
 97  refused_supplies_names_head_lacks
 30  refused_replacement_no_landable_hunk
 30  refused_no_base
 17  refused_no_reader
 13  refused_head_does_not_supersede_it
  3  already_at_head
  1  refreshable          <- saas/reporting/annual_report.py
---
430
```

**The door runs.** It graded the whole real population without a crash, and 429 of 430 refusals are
defensible. That was the item's question and the answer is yes.

---

## 3. The defect — the one `refreshable` grade would destroy live work

The door's verdict on `saas/reporting/annual_report.py`:

> rival copy: supplies no name origin/main lacks, and the stale-copy control refuses it
> [predates_landing]. **origin/main strictly supersedes it.**
> LINES THAT WILL BE DISCARDED (29), recoverable from the preserved commit

It does not supersede it. Measured against the `origin/main` blob:

| key | `origin/main` | working copy |
|---|---|---|
| `svt_departures`  | **0** | 1 |
| `svt_decisions`   | **0** | 1 |
| `gas_shape_provider_by_customer` | 1 | 0 |
| `gas_shape_refusals` | 1 | 0 |

`svt_departures` appears **nowhere in `saas/` at `origin/main`** — the working copy is its only
home. `svt_decisions` is worse: `origin/main` already has **seven consumer modules waiting on it**
— `tools/population_anchor.py` (17 refs), `tools/fit_year_level_anchor.py` (9),
`tools/capture_departure_factors.py` (6), `tools/departure_population.py` (5),
`tools/measure_departure_level.py` (3), plus `site/data/world.json` and
`site/state/population_anchoring.json`. The producer does not publish it, so
`covers_svt_route: false` is live on the site today. **The working copy is the repair that closes
that gap**, and the door offers to discard it.

### The cause, verified in the reader and not inferred

`symbols()` (`tools/stale_copy_refusal.py:628`) for a `.py` path returns

```python
frozenset(_bound_names(tree.body) | _class_members(tree.body) | _imports_at_any_scope(tree.body))
```

— module-level bindings, class members, imports. **A string key added to a dict literal inside a
function body is none of these.** `extract_report_data` returns exactly such a dict, and that dict
is a *publication whitelist*: a key absent from it is not published however fully the runner
computes it. So a copy that adds two published artefact keys supplies **zero** new Python names,
`gains_over` returns empty, and empty is the door's licence to overwrite.

The reader's docstring anticipates the worry and dismisses it:

> *"Genuine added work still surfaces: new top-level functions and methods come through
> `_bound_names`/`_class_members`, and the lines a refresh would discard are printed for the
> operator either way."*

The second clause is the fail-open. The lines **are** printed — but they are printed underneath the
sentence *"origin/main strictly supersedes it"*, which is the sentence that tells the operator the
printing is a formality. And the drawn instruction I was working to said, literally: *"`--staged-too
--write --slug <name>` only for paths it grades REFRESHABLE."* An operator following the standing
instruction to the letter destroys this work. That is what makes it BLOCKING rather than a grading
nicety.

### The irony is load-bearing, not decoration

The 9 lines this copy *deletes* are commit `971e3680c`, whose message is *"returned is not
published: the gas shape records reached the runner's return and stopped at a **whitelist**, and
that is the fourth instance of a class this dict already counts."* The repository has paid for the
whitelist-drop class **four times in this one dict** and written each instance down beside the line.
The door cannot see the class at all, because the class is invisible to a Python-name reader.

### What the honest verdict would be

Neither `refreshable` nor holder work. This is a **mixed** copy: it adds two novel whitelist keys
*and* drops two that `origin/main` landed on 2026-09-23. It needs hunk isolation, not a grade. But
`refreshable` is the single grade that licenses destruction, and that is the one it got.

### One thread left open, flagged rather than buried

The clock returned `predates_landing`, yet the working copy's mtime (`2026-09-24 15:02`) is **newer**
than `origin/main`'s last landing to that path (`971e3680c`, `2026-09-23 13:22`). Both the content
oracle and the clock agreed with the destructive reading here, so the clock is not a backstop for
this class. Whether the clock is right by some other measure, or wrong for a third reason, is **not
established** and I am not asserting either — it is the next thing to measure.

---

## 4. Disposition

* The `--staged-too` half of the item is **spent** — no staged entries exist, and the door is
  unreachable while the index equals HEAD. The claim is released, not carried.
* The survey half is **done**: the door has now been run against 430 real paths, and it works.
* **No `--write` was run, and none should be** on `saas/reporting/annual_report.py` until the reader
  gap above is closed. The shared tree was not mutated by this turn.

### Next, in order

1. Narrow the `REFRESHABLE` gate so it cannot fire on a Python copy that adds dict-literal string
   keys the base lacks. This only ever demotes `refreshable` to a refusal — fail-closed, and the
   blast radius measured here is **1 path in 430**.
2. Rescue `svt_departures` / `svt_decisions` into `origin/main` by hunk isolation (they have seven
   consumers already waiting and `covers_svt_route: false` live on the site).
3. Settle the clock discrepancy in §3.
