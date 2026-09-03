**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `SITE2_two_sided_wall_exhibit`

# The mobile table control counts its own CSS rule as a wrapper, so exactly one unwrapped table always passes

**Found:** 2026-08-30, while clearing `[PUBLISHING DOWN]` — this control was the test refusing
the publish commit, and it was right about the page. It is the CONTROL that is one short.

**Not a claim that any published figure is wrong.** This is a layout control, and the page it
fired on has been repaired.

## The mechanism

`site/test_expert_doors_mobile.py::test_tables_scroll_inside_their_own_container` reads the
door's own html and compares two counts:

```python
n_tables   = len(re.findall(r"<table", html))
n_wrappers = len(re.findall(r"table-scroll", html))
assert n_wrappers >= n_tables
```

Every door that uses the class also **defines** it, once, in its own `<style>`:

```
site/capabilities/index.html:71   .table-scroll { overflow-x: auto; }
```

That definition matches `table-scroll`. So `n_wrappers` is always one greater than the number of
actual wrappers, and the assertion is effectively `real_wrappers + 1 >= n_tables` — **a door with
exactly one unwrapped table passes.** The control's stated purpose is "a wrapper for every table
(each scrollable table has its own container)"; what it enforces is "at most one table may be
missing its container".

## Why it fired anyway, and what that hid

`/capabilities/` had TWO problems at once, and they cancelled into one confusing number:

| line | table | state |
|---|---|---|
| 129, 493, 562 | three tables | wrapped in `<div class="table-scroll">` — correct |
| 347 | the funnel table | wrapped in `<div style="overflow-x:auto;">` — behaviourally identical, invisible to a control that counts the CLASS |
| 839 | the four-column belief-bucket table | **no wrapper at all** — the real defect, and the widest table on the page |

5 tables, 3 counted wrappers, +1 for the CSS rule = 4. `4 >= 5` failed by one.

So the control reported a deficit of one while the page had one genuine defect and one false
positive. Had line 347 used the class, the page would have had ONE genuinely unwrapped table and
the control would have passed — the four-column table would have shipped forcing horizontal body
scroll on a phone, and `[PUBLISHING DOWN]` would never have fired.

**The publish flap was a real defect caught by accident.**

## What was repaired, and what was not

Repaired on `/capabilities/`: line 839 wrapped, line 347 converted from the inline style to the
class. Test passes; counts are now 5 tables / 7 `table-scroll` occurrences.

**Not repaired: the control.** Fixing it while clearing a different alarm is the fix-on-sight this
project keeps paying for, and the repair has a design question inside it that deserves its own
look — counting occurrences of a class name in raw html is a weak proxy either way, since it
cannot tell a wrapper from a mention and cannot tell WHICH table is wrapped. A `<div
class="table-scroll">` immediately preceding each `<table` is the property; the count is a
stand-in for it.

## How much the off-by-one is currently absorbing: none. Counted, not assumed.

The first draft of this document said other doors "may" be hiding an unwrapped table and that
nobody had counted them. That was a measurement I could take in ten seconds and did not, which is
the same failure one level down from the one being reported. Counted:

| door | `<table` | occurrences of the string | of which CSS defs | real wrapper openings | shipped verdict | truth |
|---|---|---|---|---|---|---|
| capabilities | 5 | 7 | 1 | 5 | PASS | OK |
| explore | 9 | 10 | 1 | 9 | PASS | OK |
| harness | 1 | 2 | 1 | 1 | PASS | OK |

Only **three** of the site's doors render a table at all, and after the repair above all three are
genuinely covered. **The exposure is zero today.** The control is still wrong in shape — it would
absorb the next single unwrapped table on any of these three — but it is not currently hiding
anything, and saying otherwise would have been a scare with no number under it.

One further wrinkle the census exposed: capabilities now counts 7 occurrences against 5 wrappers,
because the repair commit's own CODE COMMENT mentions `table-scroll` twice. Prose about the class
inflates the counter exactly as the CSS rule does. A control that a comment can move is measuring
the file, not the page.

## What is owed

Count the wrapper OPENINGS — `<div ... class="table-scroll"` and any equivalent inline
`overflow-x` container opening, which is what the census above did — rather than every occurrence
of the string, and assert one per `<table`. The query is four lines and is written out in this
document's own measurement, so the repair does not start from nothing.

R15 for the repair, when it lands: delete one wrapper from `explore` (9 tables, so one deletion
leaves 8 real wrappers and 9 occurrences). The shipped control passes; the repaired one reds.
That door is the right subject precisely because it has enough tables for the off-by-one to be
invisible on it.

---

## DISCHARGED 2026-08-30 — repaired, with the mutation this document specified

**Severity: LATENT → RECORDED.** The repair landed as directed by
`DIRECTOR_BRIEF_CHOICE_AND_CHANNEL_2026-08-30`, item (d).

### What replaced the count

Not "count the wrapper openings" as this document proposed, but the property under it:
**adjacency**. `unwrapped_tables(html)` in `site/test_expert_doors_mobile.py` returns the source
offset of every `<table` **not opened immediately inside** `<div class="table-scroll">`, after
JS string-concatenation glue (`' + '`) is removed so one rule reads both the hand-written and the
built shapes.

Counting openings would have fixed the off-by-one and kept two weaknesses this document had
already half-spotted. A count still cannot tell **one table wrapped twice** from **two tables
wrapped once**; and it still measures totals rather than tables, so a page could satisfy it with
its wrappers in the wrong places. Adjacency has no slack at all, because each `<table` is judged
on its own — the CSS rule and the comment can never satisfy it, so neither needs excluding.

The failure message now names the **source line** of each loose table instead of reporting a
shortfall in a total.

### The mutation this document prescribed, run

> *"delete one wrapper from `explore` (9 tables, so one deletion leaves 8 real wrappers and 9
> occurrences). The shipped control passes; the repaired one reds."*

```
explore, one wrapper deleted -> 9 tables, 9 `table-scroll` occurrences, 8 real wrappers

  REPAIRED: explore: 1 of 9 table(s) not opened inside <div class="table-scroll">
            (near source line(s) [327]) -- a wide table there scrolls the whole body   FAIL
  OLD     : 9 >= 9                                                                     PASS (blind)
```

Prediction met exactly. Also run on `harness` (1 table, CSS rule left in place): repaired FAILs,
old PASSes. Both doors restored and the restore verified clean against HEAD.

### The comment wrinkle, closed

This document noted that the repair commit's own code comment mentioning `table-scroll` inflated
capabilities' counter further — *"a control that a comment can move is measuring the file, not the
page"*. Confirmed at 7 occurrences against 5 tables, so the slack there was **two**, not one. Under
adjacency the comment is inert: it is not an element, so it cannot open around anything.

### Proof the repair itself can fail

`test_the_table_scroll_check_can_fail` carries the blind spots as fixtures — a lone table beside
the CSS rule; capabilities' comment-plus-rule shape (expects exactly 2); one wrapped and one bare
(expects exactly 1); a wrapper that wraps something *else* not covering a later bare table; and the
honest shapes staying green, including across the `' + '` join.

**Exposure remains zero** — all three table-rendering doors are genuinely covered — but the control
now enforces what it says, rather than "at most one table may be missing its container".
