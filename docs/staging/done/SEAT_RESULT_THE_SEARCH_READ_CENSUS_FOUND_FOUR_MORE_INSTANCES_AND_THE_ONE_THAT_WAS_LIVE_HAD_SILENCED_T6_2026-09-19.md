**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery,
"search-read matches that are downstream subjects are uncensused"

# The tree-wide census of `.search()` reads found four more instances of the class, and the live one had been silencing T6 on the real status page

**Delivery seat, 2026-09-19, claim
`search-read-matches-that-are-downstream-subjects-are-uncensused`. Predictions in
`SEAT_PREREGISTRATION_THE_TREE_WIDE_CENSUS_OF_SEARCH_READS_WHOSE_MATCH_IS_A_REGISTERED_SUBJECT_2026-09-19.md`,
written before the instrument was run and left uncorrected beside these results.**

---

## 1. The premise, and the duplicate-work note

Both commits the item cites (`087e3ad58`, `c35593d24`) are ancestors of `origin/main`, and
**that does not spend the premise** — they are the item's prior art. Each repaired an instance
found by hand and each said in its own message that the remaining instances were *known*, not
*enumerated*. The item exists because "those were the last" rested on nobody having looked.

The duplicate-work note named
`search-read-matches-that-are-downstream-subjects-are-uncensused` as already held. That is **this
item's own id**, under this draw, `paths: []`. Not a rival claim; the work was done.

## 2. What was measured

An AST census over every tracked `.py`, splitting each `.search()` call by **what its match
becomes**, because that and not the method name is the discriminator:

| | count | |
|---|---:|---|
| `.search()` call sites | **396** | |
| BOOLEAN — the match is a truth value (`if`, `not`, `any(...)`, `bool()`, `is None`) | **240** | a narrow read answers *"is there one at all"* correctly however many there are. Not the class. |
| REGISTERED — the match is named, appended, stored, returned or yielded | **156** | it travels onward as a SUBJECT. A second match is dropped in silence. Candidates. |

The 156 were read by hand. The instrument is AST-based rather than a grep because the
boolean/registered split is syntactic and invisible to a line match — and its own first draft
was wrong in a way worth recording: it counted `any(p.search(s) for s in xs)` as REGISTERED,
because the generator expression, not the call, sits in the boolean slot. That put 10 sites in
the wrong column (166 → 156) and is fixed.

## 3. Against the predictions

| | predicted | measured | |
|---|---|---|---|
| P1 | 40–60% BOOLEAN | **60.6%** (240/396) | **refuted at the bound**, by half a point. Recorded rather than rounded into a pass. |
| P2 | 150–240 REGISTERED | **156** | held |
| P3 | 3–10 real instances, point 5 | **4** | held, low in the interval |
| P4 | ≥1 under `tools/` | **1** (`billing_axis_coverage.py`) | held |
| P5 | ≥1 census/registry-shaped | **2** | held |
| P6 | the three repaired instances do not reappear | none did | held |

## 4. THE LIVE ONE: T6 had asked nothing, and returned the same `[]` it returns when it agrees

`background/naive_organ.py::detect_t6` is the claim-vs-data contradiction detector — the organ's
tautology catcher, wired into `ALL_DETECTORS`, and it had **no test coverage of any kind** before
this commit. Its net-margin row read the claims surface with `search()`.

On `docs/status/LATEST.md` at `406276afc` the row's pattern
`net(?:\s+margin)?[^\d]{0,8}£?([\d,]+)` makes **six** matches. The first is the word **"network"**
followed by a number, whose capture is a bare comma; `int("")` raises; and the guard —
scoped to the whole ROW, not the match — swallowed it and moved on. So:

```
detect_t6(live LATEST.md, computed net margin = £42)  ->  []
```

Nothing. The page states **£1,521,070** and **£158,278** — two different net margins, which
contradict each other before anything is recomputed — and neither was ever compared with the
data. Two defects compounding: a narrow read put a false positive first, and a row-scoped
exception guard turned that one unreadable match into a total skip. **A detector returning `[]`
because it asked nothing is indistinguishable from one returning `[]` because it agreed**, and
nothing downstream of it can tell them apart. That is the class in its purest form.

Repaired: `finditer` over every claim; the exception guard scoped to the MATCH so an unreadable
one cannot retire the row; and the pattern tightened to require `net margin` AND a `£`. The
tightening was **measured across four candidates on the real page** before being chosen — it is
the only one that leaves exactly the two claims that are net margins and drops `"network,"`,
`"net margin ÷ N=19"`, `"skynet-1"` and `"…net` → `127"`. A claim written without a currency
sign is now knowingly out of scope: a stated narrowing replacing an accidental one.

After:

```
computed £42          -> 2 triggers: 1,521,070 ; 158,278
computed £1,521,070   -> 1 trigger:  158,278
computed £158,278     -> 1 trigger:  1,521,070
```

Whatever the computed figure is, T6 now fires. **It cannot agree with a page that disagrees with
itself** — which is a second finding, in the page rather than the detector, and is named in §7.

## 5. The second live one: a money constant's SECOND source was asked nothing

`tests/architecture/test_a_cited_constant_has_a_caller.py` is the enforcement named in
`CLAUDE.md`'s rules table for *"a money constant citing a source must be reached"*. Its census
read `_CITATION.search(_comment_block(...))` — one citation per constant.

Of 171 money constants, **one** cites two artefacts today:
`company/crm/customer_profitability.py::NET_NEGATIVE_UPLIFT_GBP_PER_MWH`, naming both
`price_cap_ebit_allowance.md` and `pricing_differentiation_permissions.md`. Only the first has
ever been asked whether it exists or whether the constant that cites it is reached. Both exist,
so the dangling-citation leg was not WRONG — it was **unasked**, and would have stayed unasked
had the second gone missing.

Repaired: the row's third field is now a `tuple` of every citation **with no singular beside
it**, so an un-widened consumer raises on `ROOT / cites` rather than quietly grading the first
and reporting a clean answer. `unreached_cited_constants` emits one row per unspent source,
because a refusal naming one of two is how a constant gets half-repaired. `_comment_block` now
returns its lines in source order — it built them bottom-up, invisible while one match was taken
and a small lie the moment the order is published in a refusal.

## 6. The two that are the class with no live instance, filed rather than repaired

Both are real reads of the class shape over strings that CAN state two. Neither has an instance
in the tree today, and an empty instance list is not evidence a rule-class finding is safe — so
they are recorded here with what was measured, not closed.

- **`background/staging_disposition.py:335`** — `_BLOCK_RELEASE_RE.search(raw)` registers one
  `BLOCK_RELEASE` marker per mint doc, and `_releaser_resolves` then judges it. A doc carrying
  two markers has the second releaser judged by nothing. Measured: 31 docs carry a marker, **2
  carry two** (`docs/design/BLOCKED_ITEM_LITERAL_ACTS.md`,
  `docs/staging/done/PLANNER_MINTED_unstated_reason_block_impossible_2026-07-28.md`) — and
  neither is in the `in_progress/` glob this function scans, so **zero live**.
- **`tools/billing_axis_coverage.py:286`** — `_NEEDS_SENTENCE.search(text)` reads the director's
  canon for the billing-axis list, and the list is the subject of the whole coverage census. A
  canon amended with a second "It needs …" sentence would be graded on the first and reported
  fully covered. The canon states it once today.

## 7. The reporting-only variant, and why it is NOT the same defect

Four further registered reads drop a second match **without changing any verdict** — the file is
already an offender, the doc is already stale — so the cost is that the refusal names only the
first and a repairer does a second round, rather than a hole in what is judged. All four were
measured and all four have **zero** multi-match instances today:

| site | subject | instances |
|---|---|---|
| `tests/background/test_process_reconciler.py:301` | a module's second process-kill call | 0 of ~60 modules |
| `background/status_honesty.py:69` | a stale model claim stated twice on `LATEST.md` | 0 of 5 patterns |
| `background/deadmans_switch.py:426` | a second `UNBLOCKS:`/`BLOCK_RELEASE` reason in one mint | 0 in scope |
| `background/suppression_lint.py:113` | a second waiver in one comment token | 0 of every tracked `.py` |

`suppression_lint` is additionally conservative in direction: under-reading waivers means MORE
violations reported, never fewer.

**And a separate finding, in the page rather than any reader:** `docs/status/LATEST.md` states
two different net margins, £1,521,070 and £158,278, with no stated basis distinguishing them.
They are almost certainly a book figure and a single run's figure — which is the *average unit
rate* shape `CLAUDE.md` names: one word, two quantities, differenced by whoever reads it. Not
fixed here; it is a page in another lane and this seat found it as a side effect of pointing a
detector at it. T6 will now say so on every tick until it is resolved, which is the right place
for it to be said.

## 8. What is NOT closed

- The census covers `.py` only. A `.search()` in a JS literal inside a generator is out of scope
  and unmeasured.
- The discriminator is syntactic. A REGISTERED match over a string that is single-claim **by
  construction** is not a defect, and separating those from the real ones was hand judgement
  over 156 sites — repeatable, but not mechanised, and a second reader could differ at the
  margin. The four named in §6–§7 are where that judgement is load-bearing.
- No standing control enumerates this class. P3 said one would be warranted above ten instances
  and the census found four, so building one would be a register guarding a register. The
  instrument is recorded here instead; re-running it is thirty lines.

## 9. Mutation evidence

Four mutations, each firing exactly ONE leg — the leg written for it, checked, because a
mutation caught by a different leg is the flattering reading.

| mutation | leg fired | others |
|---|---|---|
| `finditer` → `search` in `detect_t6` | `test_t6_asks_every_claim_a_surface_states_and_not_just_the_first` | 31 green |
| exception guard rescoped to the ROW | `test_t6_keeps_asking_the_other_claims_when_one_is_unreadable` | 31 green |
| loose net-margin pattern restored | `test_the_net_margin_pattern_does_not_read_a_number_out_of_an_unrelated_word` | 31 green |
| `findall` → `search` in `_money_constants` | `test_a_constant_citing_two_sources_has_BOTH_of_them_asked_about` | 11 green |

**And one mutation that did NOT fire, established rather than assumed.** The first draft of the
exception-guard leg was **vacuously green**: its fixture stated `"net margin £, then … £42"`,
which the tightened pattern does not match at all, so there was no unreadable match to survive.
Worse, *no* row in the live `_t6_rows` table can produce one any more — every capture is
digits-only by construction once the pattern was tightened — so the row-scope mutation is an
**equivalence against today's table**, not something no test covers. The flattering reading was
to call it covered. The guard's scope stays load-bearing because `_t6_rows` says in its own
comment that adding a row is the supported way to widen T6, and the next row's extractor has no
obligation to be total — so the leg now injects a row whose extractor raises on the first match
and reads the second, and drives the property directly.

Baselines: `test_naive_organ.py` 29 → **32 passed**; `test_a_cited_constant_has_a_caller.py`
11 → **12 passed**.

## 10. A side finding the landing produced: the shrink ratchet and the stale-copy guard collide by construction

`surgical_land` refused this commit's first attempt with `predates_landing` on
`tests/architecture/test_static_quality_ratchet.py`, reporting that the copy contained **not one**
of the two distinctive lines the last commit to touch that file (`dcb8c6d10`) added, and was
therefore a stale pre-landing checkout reverting it.

It was not. The worktree is a clean checkout of `origin/main` and `dcb8c6d10` is an ancestor of
its HEAD. The two lines are `"I001": 1308, # lowered 2026-09-16 …` and
`RUFF_BASELINE_TOTAL = 2285 # 2286 -> 2285 on 2026-09-16 …` — the two lines **the previous shrink
added**, and the two lines **any next shrink must rewrite**, because the ratchet's protocol is to
lower the number in place and carry the old value forward in the comment that follows it.

So the collision is structural, not incidental: **a shrink-only ratchet whose log lives on the
same line as the value it ratchets will trip `predates_landing` on every consecutive shrink of the
same code.** The guard's distinctive-line evidence and the ratchet's edit-in-place protocol are
each correct alone. The exemption used here is the sanctioned one — `--drops <path>`, which prints
the exemption in the landing output so it cannot be silent — and the removal genuinely is this
commit's and deliberate: all three removed lines are baseline entries this commit lowers, with
their prior text preserved verbatim on the continuation comment beneath each.

Not repaired here, because the repair is a change to one of two shared mechanisms and this claim's
subject is neither. Filed so the next shrink does not re-derive it: the cheap fix is for the
ratchet to carry its per-code history on its OWN line rather than trailing the value, which would
leave the previous shrink's distinctive line intact across the next one.
