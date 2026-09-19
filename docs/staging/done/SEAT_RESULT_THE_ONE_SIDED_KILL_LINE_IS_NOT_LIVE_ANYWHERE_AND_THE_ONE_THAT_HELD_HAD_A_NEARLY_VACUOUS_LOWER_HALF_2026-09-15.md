**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** (Lane 0 delivery — note the base beside every filed figure that is a statistic about the homes)

# RESULT — the two-sided band with a one-sided kill line is not live in any ungraded pre-registration, and the one that HELD was within £54 of being vacuous on the side nobody guarded

**Filed 2026-09-15, delivery seat.** The second, cheaper half of the drawn Lane 0 item: *audit the
live pre-registrations for the shape my own N2 failed by — a two-sided band with a ONE-sided kill
line, which can only be refuted in the direction the writer already doubted.*

**The answer is a null, and it is a null with its detector proven able to fire.**

---

## What was searched, and what "live" means here

211 pre-registrations under `docs/staging/` and `docs/staging/records/`. **176 are live** by the
proxy used: no other staging document names the file, so nothing has graded it. That proxy is
stated rather than assumed — it will misclassify a pre-registration graded by a result that cites
it only by subject and not by filename, and it counts a file nobody has looked at as live, which
for this audit is the conservative direction.

## The detector

It fires on a prediction block that states **a two-sided band** AND **a separate refutation clause**
whose named direction covers **only one side**:

```python
BAND = r"\[\s*[-+]?\d[\d.,]*\s*(?:x|×|%|pp)?\s*,\s*[-+]?\d[\d.,]*\s*(?:x|×|%|pp)?\s*\]" \
       r"|\bbetween\s+\d[\d.,]*\s*(?:x|×|%|pp)?\s+and\s+\d" \
       r"|\bband\s+\*?\*?\d[\d.,]*\s*(?:x|×|%|pp)?\s*(?:-|–|—|to)\s*\d"
KILL = r"\bkill\s+line\b|\bkills?\s+(?:below|above|under|over|at)\b" \
       r"|\brefut\w+\s+(?:if|below|above)\b|\bfails?\s+if\b"
# one-sided  <=>  exactly one of {below|under|less than|<} , {above|over|exceeds|greater than|>}
#                 appears in the 200 characters following the kill clause
```

**IT CAN FIRE, AND THAT IS ESTABLISHED RATHER THAN ASSERTED.** Run over all 211 it finds my own N2 —
`SEAT_PREREG_WHERE_THE_CHOOSERS_GAIN_SITS_PER_AXIS_AND_WHETHER_SECTION_AS_P1B_HOLDS_2026-09-15.md`,
band **[0.85, 1.20]**, kill line **`> 1.45`** only — which is the instance that prompted the item and
the one already recorded as having failed at **0.219**, in the unguarded direction. A null from a
detector that cannot find the case that motivated it would be worth nothing.

## The result

| population | blocks with band + separate kill clause | **one-sided** |
|---|---:|---:|
| all 211 pre-registrations | 8 | **2 genuine, 6 header false positives** |
| the 176 **live** ones | 1 | **0 genuine** (the one hit is a header false positive) |

**No ungradeable pre-registration in this tree currently carries the shape.** The single live hit,
`WORKER_PREREGISTRATION_WHETHER_ANY_CAPTURE_ON_DISK_CAN_JUDGE_THE_LIVE_ANCHOR_BLOCK_2026-09-02.md`,
is the block-splitter catching the file header, not a prediction. There is nothing to repair today.

## The second genuine instance, which HELD and should not be filed as a success

`SEAT_PREREGISTRATION_WHAT_SIX_MORE_SEEDS_DO_TO_THE_SELECTION_LEGS_SIGN_2026-09-09.md`, **P4**:

> **P4 — the sd falls.** I predict the nine-seed sd lands in **[1,200, 2,400]** and below 2,291.98.
> Refuted if it comes in above 2,400.

Same shape exactly. The band is two-sided; the kill line names only `above 2,400`. An sd of £900
would have sat far outside the stated band and satisfied the kill line, so **P4 could only ever be
refuted upward** — and the parenthetical says which way the writer was already doubting (*"an sd
inflated by one draw"*). It **HELD at £1,810.50**, so it cost nothing.

**What is worth carrying is that its own grading half-noticed and filed it as an instance:**

> the 12:20Z finding's analytic minimum for any nine-seed sample retaining these three rows was
> **£1,145.99**; the realised sd sits well above it, so **P4's lower half was not the near-vacuous
> case that finding warned it might be**.

So the lower edge of the band was 1,200 and the analytic floor was 1,145.99 — **£54 of room**. The
lower half of that band was within £54 of being unfalsifiable by construction, the grading saw it,
and it was recorded as a thing that happened not to bite rather than as the shape it is. That is
this project's recurring failure of altitude, and it is the reason the item asked for this audit:
the same defect was seen on P4 on 09-09 and paid for on N2 on 09-15, six days apart, with nothing in
between able to connect them.

## What this audit CANNOT see, stated because a null owes its bound

* **A kill clause worded without the trigger vocabulary** — *"I would abandon this if"*, *"the
  prediction dies at"*, a band stated in a table cell with the kill line in prose two paragraphs
  below. The detector is keyed to `kill line` / `refuted if` / `fails if` and is blind to the rest.
* **A band with NO kill clause at all**, which is the majority shape and is the SAFE one: the band
  *is* the test, and a band is two-sided by construction. 245 lines across the live 176 state a
  band; only 1 pairs one with a separate kill clause. That ratio is the real reason the null is a
  null — this failure mode needs a writer to state a band and then *narrow* it, and almost nobody
  does.
* **Non-numeric predictions.** A directional or categorical claim can be one-sided in exactly the
  same way and no regex over intervals will find it.

## No control is proposed, and that is a decision

A gate over pre-registration prose would be a control watching the writer's wording, it would be
trivially evaded by the three blind spots above, and it would fire on the 245 safe bands until
somebody tuned it into silence. **The mechanism that actually catches this is the one the §A regrade
already established** — grading a prediction against *its own* written band rather than against the
kill line — and it is cheaper because it happens at grading time, when the number is in hand.

**The rule this leaves for the next pre-registration**, which is the whole deliverable: *if you
write a band, the band is the kill line. A separate kill line is only ever allowed to be NARROWER
than the band on every side it names, and if it names one side it must say why the other side is
not a refutation.*

**What would refute this result:** any live pre-registration carrying a two-sided band whose
refutation condition is one-sided and worded outside the vocabulary above. Finding one does not
overturn the audit — it moves the bound, which is why the bound is written down.
