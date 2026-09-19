**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery, "the
checkout must fast-forward so the publisher's green commit can land"

# RESULT — the publish wedge is ONE uncommitted sentence of the seat's own prose, and the guard that catches it refuses the whole tree instead of its author

**Delivery seat, 2026-09-16.** The drawn item's premise was spent before the turn started. The
publisher is still wedged, the cause is new, and it is attributed here by a one-variable swap rather
than inferred. Pre-registration, written before any measurement:
docs/staging/records/SEAT_PREREG_ARE_THE_TWO_HERE_RELATIVE_POINTER_TESTS_RED_AT_HEAD_2026-09-16.md
— **its prediction was refuted**, and the refutation is what found the real cause.

This is the direct continuation the previous wedge finding pre-registered. That document ends:
*"when the next run_complete is processed, does last_clean_publish take a timestamp? If it refuses
again, the cause will be a new one and belongs in a new finding, not this one."* It refused again.
This is that new finding.

---

## 1. The drawn premise: spent, and a prior seat had already said so

The item asked me to clear nine paths blocking a fast-forward, then run the reconcile until
`git rev-list --count HEAD..origin/main` is zero. Measured at turn start:

| tree | HEAD | behind origin | ahead |
|---|---|---|---|
| shared, /home/rich/synthetic-enterprise | c660084bb | **0** | 0 |
| this isolated worktree | c660084bb | **0** | 0 |

There is no fork. The reconcile has nothing to merge. Of the nine named paths, five are gone and
three remain dirty for unrelated reasons. The cited commit 8dfb28f9f is an ancestor of both.

The item's stated cause — *"its newest refusal names `behind_origin` as the only thing left"* — does
not match the record either. The newest failure in the gate state reads `cause: gate_refusal`,
naming two red tests, and beside it `red_at_head: "not_established"`.

**A prior seat had already reached this conclusion and written it down.** The uncommitted
`docs/direction/DIRECTION.yaml` (oriented 14:20 today) opens: *"THE WEDGE IS NOT A LIST OF PATHS. IT
IS A REFILL, AND THIS STRETCH PROVED IT BY CLEARING THE LIST AND WATCHING IT COME BACK IN THREE
HOURS."* The path-enumeration frame was refuted before this item was drawn. It was drawn anyway
because that refutation was never committed — which is the same disease as the wedge itself.

## 2. The real cause, attributed by swapping ONE thing

`red_at_head` was `not_established` because the pre-commit gate runs in the **shared working tree**,
which carries 427 dirty paths from several lanes, so no measurement taken there is single-valued.
This worktree is clean and sits exactly on `origin/main`, which makes it the one vantage that can
answer it. The chain, each step measured:

| # | what was run | result |
|---|---|---|
| 1 | both blocking tests, clean worktree at c660084bb | **2 passed** |
| 2 | both tests, clean `git archive` extract of HEAD in ~/.cache | **2 passed** |
| 3 | same extract, `site/data/` swapped in from the shared tree — **one variable** | **2 failed**, same node ids the gate recorded |
| 4 | same extract, one sentence in `delivery.json` reworded — **one variable** | **2 passed** |

Step 3 reproduces the gate's exact refusal. Step 4 shows a single sentence carries all of it.

The carrier is `site/data/delivery.json`, field `.what_it_decided.focus[4].why`, the phrase
**`rows above`** inside:

> …it is the only ATOM-class row here, so it travels the weight-bias channel rather than lane 0 and
> **costs the four rows above it nothing**.

That field renders in **two** regions — `/harness/#delivery-decided` and `/harness/#delivery-next`
(site/harness/index.html lines 560 and 630). A sentence claiming a direction "from here" has two
heres, so it is false in at least one. **The test is correct and is doing exactly its job.**

## 3. Why nothing that was tried could ever have cleared it

The offending sentence **is not at HEAD**. `git show HEAD:docs/direction/DIRECTION.yaml` does not
contain it. It exists only in the shared tree's index and working copy, part of an unlanded
orientation rewrite (301 insertions, 251 deletions). The committed feed is green; the regenerated
one is red.

So the wedge lives entirely in bytes no commit can reach:

- the seat's orientation writes `DIRECTION.yaml` (15:27:33),
- its producer regenerates `site/data/delivery.json` from it 20 seconds later (15:27:53),
- the pre-commit gate reads the **working tree**, sees the red, and refuses,
- and it refuses **every lane's commit**, not just the author's.

40 publish attempts, 0 clean publishes, `last_clean_publish` still null. Landing anything is
powerless here, and for the reason the previous wedge finding already established:
`surgical_land --content` does not write the working tree, so a commit moves only one of the two
things the gate compares.

## 4. The class, which is the part worth keeping

The instance is one word. The class is the shape:

> **A guard whose subject is the shared working tree has the whole tree as its blast radius. It
> refuses everyone for one author's uncommitted sentence, and it names the sentence rather than the
> author, so the refusal reads to every other lane as "the tree is broken" rather than "someone has
> an unlanded edit".**

Three properties make this recur rather than resolve:

1. **The source is prose a human-shaped process writes every stretch.** "The rows above", "listed
   below", "higher up" are how anyone naturally writes a ranked list. The seat will write one again
   next orientation.
2. **The producer copies that prose verbatim into a field it renders twice.** It never checks the
   field's homes, which is precisely what the producer-side test says it fires on.
3. **The feed is generated and uncommitted, so the defect never appears in any diff.** Nobody
   reviewing a commit can see it, and `red_at_head` is honestly `not_established` forever.

This is also why 37 recorded failures each named a different, real, already-cleared cause. Every one
of them was looking at committed state for a defect that has never been committed.

## 5. What I did, and how to reverse it

Two prose edits, no producer run (regenerating in the shared tree would execute another lane's
uncommitted producer), no commit of another author's 552 changed lines:

- `docs/direction/DIRECTION.yaml` line 203 — the source, so the next regeneration is green.
- `site/data/delivery.json` `.what_it_decided.focus[4].why` — the generated copy, so the gate goes
  green now.

Both replace `costs the four rows above it nothing` with `costs the four lane-0 rows in this focus
nothing`. The meaning is preserved exactly — the other four rows are the lane-0 rows — and the
landmark is absolute, so it is true from both render sites. Reverse by substituting the original
string back in either file; nothing else was touched, and neither file is committed by this turn.

Both files were 1h46m stale when I wrote them, re-checked immediately before the write, well past any
live edit, and `DIRECTION.yaml` is this seat's own channel.

**Verified where it matters.** Both blocking tests, and then both whole files, run in the SHARED
tree — which is where the gate runs them and the only place the answer counts:

```
site/test_a_here_relative_pointer_has_one_home.py
site/test_a_producers_here_relative_pointer_has_one_home.py      13 passed in 10.89s
```

The wedge is clear. `git status` on those two paths is the check that says so, not any commit —
the second half of the remedy the previous wedge finding established.

## 5a. Eight more are already loaded, and only luck keeps them green

A census of the repaired feed for the same vocabulary:

```
.what_it_got_wrong.entries[33].what   -> 'row above'      .what_it_got_wrong.entries[104].what -> 'row above'
.what_it_got_wrong.entries[38].what   -> 'row above'      .what_it_got_wrong.entries[108].what -> 'rows below'
.what_it_got_wrong.entries[48].what   -> 'row above'      .what_it_got_wrong.entries[113].what -> 'row above'
                                                          .what_it_got_wrong.entries[115].what -> 'row above'
                                                          .what_it_got_wrong.entries[172].what -> 'row above'
```

**Eight live here-relative phrases, all passing.** Not because they are right, but because
`.what_it_got_wrong.entries[].what` happens to render in ONE region today. They are green by
topology, not by correctness. The day that panel gains a second render site — or the day the seat
writes one more into `focus[].why`, a field that already has two homes — the tree wedges again.

This is the measured basis for the prediction in section 7, and it moves it from a guess to an
arithmetic near-certainty: the seat produces this phrasing roughly eight times per feed, and one
field out of the handful it writes into is multi-homed.

## 6. What I deliberately did NOT build

**A watchdog over the publisher.** The previous finding declined it for the same reason and the
direction forbade it. The smallest thing that could fail here was a reworded sentence, and a control
that guards my own controls is usually not worth having.

**A producer-side refusal.** `generate_delivery_page.py` could refuse to emit a here-relative phrase
into a multi-home field. It would be a real class fix, and it would also crash the orientation
producer on every run until the prose was fixed — converting a commit wedge into an orientation
wedge. If it is built, it must repair-and-flag, never raise. Filed here, not built, deliberately.

## 7. The open question, registered before the answer is known

Clearing this instance does not clear the class. **Prediction: within roughly three orientations, a
new here-relative sentence will appear in a multi-home field and wedge the tree again.** If that
happens, the instance fix is confirmed insufficient and the producer-side repair in section 6 is
owed. If it does not happen within ten orientations, the class is rarer than I think and the
remaining risk does not justify the producer change. Recorded now so it cannot be back-fitted.

Section 5a is the reason I expect the short end of that range rather than the long one, and it is
also the cheap way to refute me: **if a future orientation's feed carries zero here-relative phrases
in `.what_it_got_wrong.entries[].what`, the seat's phrasing habit has changed and this prediction is
wrong at its root.** That is one grep, and it does not require waiting for a wedge.

## 8. What this does NOT claim

`last_clean_publish` is still `null` at the time of writing, and clearing the wedge is not the same
event as a clean publish. The publisher has had no completed run to process since the repair, so the
content side is untested — exactly the distinction the previous finding drew and the one this
project mis-measures most often. **Two subjects, and one figure across both would be the failure.**
The honest statement is: the named blocker is gone and both tests are green where the gate reads
them; whether the next `run_complete_*.md` publishes is the next read, and it is not this document's
to claim.
