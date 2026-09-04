**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** uncommitted_and_orphaned_work

# The publish daemon committed a note DECLARATION without its CONTENT, so HEAD is self-inconsistent and only an isolated worktree can see it

Filed 2026-09-04 ~12:50Z by the delivery seat, working the Lane 0 direction *"the figures stopped
reaching the reader and no direction ever named the path"*. Found while running the cheap
pre-commit gates before landing an unrelated repair — not looked for.

---

## The measurement

`tests/design/test_atom_notes_store.py::test_declarations_match_the_store`:

| where | verdict |
|---|---|
| shared working tree `/home/rich/synthetic-enterprise` | **PASS** (1 passed in 0.56s) |
| clean `git archive HEAD` extract | **FAIL** |
| this isolated worktree at the same HEAD | **FAIL** |

```
KNIFE3_wall_crossing_paydown:
  map notes_rehomed = ['citation_correction_2026-09-03_note', 'name', 'origin_note']
  store fields      = ['name', 'origin_note']
```

Same commit, `4a4ac598b`, three trees, two answers. The difference is one **uncommitted** file.

## What actually happened

`docs/design/maturity_map.yaml` at HEAD declares `notes_rehomed: [citation_correction_2026-09-03_note,
name, origin_note]` for `KNIFE3_wall_crossing_paydown`. The store file that must hold that note,
`docs/design/simplifications/KNIFE3_wall_crossing_paydown.yaml`, holds only `name` and `origin_note`
at HEAD. The note's ~1,400 characters of content — the correction recording that **there is no SLC
27B**, that the duty is Ofgem SLC 27.15, and that the ±5% direct-debit band is a modelling convention
of ours rather than a licence threshold — exist **only in the shared tree's uncommitted working
copy**.

The declaration landed in **`2b6decd4c`**, and the commit's subject names the mechanism:

```
2b6decd4c Auto-process run complete: report + LATEST.md + site/ (git=79af956b1, net=£138,153)
```

That is the publish daemon. It rewrites and commits `docs/design/maturity_map.yaml` as part of its
cycle. It swept up the *declaration* half — which lives in the file it regenerates — and left the
*content* half, which lives in a file it has no reason to touch, sitting uncommitted in the shared
tree where another lane had written it.

This is the **exact inverse** of the shape already on the record as *"the publish daemon can commit
your uncommitted output without your source"*: here it committed the **index entry without the
record it indexes**. The general rule survives both directions — a daemon that commits a file it
regenerates will land whichever half of a two-file pair happens to live in that file, and the pairing
is invisible to it.

## Why nothing caught it, and why that is the serious part

**The control is correct and it fired.** `test_declarations_match_the_store` checks the pairing in
both directions and it goes red exactly as designed. The failure is not the control's.

The failure is **where it can be observed**. Every daemon, every supervisor tick, and every lane
working in the shared tree runs this test against a working tree that still contains the uncommitted
store file — so they all see **green**. The red is visible only from a tree that has HEAD and nothing
else: a `git archive` extract, a fresh clone, or an isolated worktree like this one.

So the population that can see the defect is exactly the population that cannot be told about it by
anything already running. And it is the population that matters most: **the isolated-worktree
landing route is the sanctioned route this seat is instructed to use.** A red at HEAD in
`tests/design/` sits in the blocking scope of any land whose pytest selection reaches it, so this one
uncommitted file can refuse other lanes' commits from every isolated worktree while the shared tree
reports itself healthy.

This is a *"green in the shared worktree measures several lanes, not your change"* case with the sign
flipped: the shared tree's dirt is **hiding** a red rather than manufacturing one, and the hiding is
what makes it durable. A defect nothing in the running system can observe does not get fixed by the
running system.

## PRE-REGISTRATION — written 12:52Z, before the answer was available

The land in flight when this was written (`background/process_run_complete.py` +
`tests/background/test_an_episode_held_open_by_its_queue_is_not_an_unbroken_outage.py`) will exercise
the open question, and the prediction is recorded here **before** its result so it can refute me:

> **Prediction:** `surgical_land` selects its pytest scope by path, and this change touches
> `background/` and `tests/background/` only. I expect the selection **not** to reach
> `tests/design/`, so I expect this land to **PASS** despite the HEAD red.
>
> **What would refute it:** a refusal naming
> `tests/design/test_atom_notes_store.py::test_declarations_match_the_store`.
>
> **Either answer is worth having.** If it passes, the blast radius is narrower than feared and the
> repair is ordinary housekeeping. If it is refused, this one uncommitted file is refusing
> *background-lane* commits from isolated worktrees, the blast radius is the whole sanctioned
> landing route, and the severity above is understated rather than overstated.

*The outcome is recorded in "THE PREDICTION" at the foot of this document, beside the forecast rather
than replacing it.*

## The repair

**Land the store side.** The declaration is already at HEAD; the pair must be whole, and the missing
half is the *content*, so the direction of the fix is not a judgement call — deleting the declaration
would discard a real citation correction that another lane researched.

This is another lane's uncommitted work, and landing it is **not** sweeping: it is completing
something HEAD already asserts. HEAD makes a checkable claim (`notes_rehomed` names this field) and
nothing on disk at HEAD honours it. `surgical_land --content` lands those bytes without taking any
other in-place edit that lane may have in the same file.

**What must NOT be done:** dispositioning the red, marking the atom, or narrowing the test's scope.
The control is right. It is the only thing that noticed, and it noticed from the one vantage point
that had no daemon watching it.

## Owed next — NOT closed here

**The observability gap is the real finding and it is untouched.** Making this one pair whole does
not make the next one visible. Nothing in this system routinely evaluates HEAD *as HEAD* — every
scheduled check runs in a working tree carrying uncommitted state from several lanes, and so is
structurally blind to any defect that state happens to conceal.

The obvious mechanism is a periodic gate run in a clean extract of HEAD whose only job is to answer
*"is HEAD green on its own terms?"* — deliberately **not** a new register or alarm document, but one
leg reporting one boolean, because a file made of rules breeds rules. It wants its own design and it
is not a bounded-tick change, so it is stated here rather than started.

The prior art it must not repeat: this project already learned that *a staged but uncommitted repair
is invisible to the publish gate forever, because the gate's subject is HEAD*. That entry and this
one are the two halves of the same asymmetry — **the gate's subject is HEAD and the gate's environment
is the working tree**, and every defect that lives in the gap between them is invisible to exactly
one of the two.

---

## THE PREDICTION — outcome, recorded 13:0xZ

*The forecast above is left exactly as written.*

**The prediction held.** The land of `background/process_run_complete.py` +
`tests/background/test_an_episode_held_open_by_its_queue_is_not_an_unbroken_outage.py` **passed**
and became `79e009c81`. `surgical_land` did not select `tests/design/`, so the HEAD red did not
refuse a background-lane commit.

**So the severity is BLOCKING for the right reason, and I was nearly wrong about which one.** The
blast radius is not "every land from an isolated worktree" — it is "every land whose pytest
selection reaches `tests/design/`", which is a smaller set and a *sharper* one: it includes any
change to the design/maturity-map machinery, i.e. **exactly the lane that would otherwise fix it**.
A defect that refuses its own repair is worse than one that refuses everything, because it is
self-preserving rather than merely loud.

It also means the ordinary way this gets discovered is the worst one: not a broad outage, but one
lane finding it cannot land and having no reason to suspect a file it never touched.

**Discharged in this same commit.** The store side is landed and
`tests/design/test_atom_notes_store.py` is 19 passed at the new HEAD. The *observability* gap under
"Owed next" is NOT discharged and remains the real finding.
