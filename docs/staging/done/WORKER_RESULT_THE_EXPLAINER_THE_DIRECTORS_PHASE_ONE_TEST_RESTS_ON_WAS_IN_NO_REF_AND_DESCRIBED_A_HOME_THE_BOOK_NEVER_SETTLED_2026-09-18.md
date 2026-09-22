**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:**
W2_31_people_phase1_the_physical_layer_stands_alone

# The explainer the director's phase-one test rests on was in no ref, and explained a three-person home the book settles as one

Worker, 2026-09-18. Discharges the owed item in
`SEAT_RESULT_THE_CENSUS_HEADCOUNT_REACHED_EVERY_CALLER_EXCEPT_THE_ONE_THE_BOOK_IS_SETTLED_ON_2026-09-16.md`
§*"What I did NOT do, and it is owed"*.

---

## The premise I re-asked, and it had changed direction

That result left `tools/explain_premise_year.py` uncorrected for a stated reason: the file was
untracked, so it was *"another lane's work in progress, and landing it would land their unfinished
module inside mine under a REUSE block I cannot honestly write."*

Both halves of that are now false, and neither was checked by asking again:

* **It is in no ref at all** — `git log --all -- tools/explain_premise_year.py` is empty, and no
  worktree branch carries it. Not a lane's WIP: a two-day orphan (mtime 2026-09-16 18:16, the hour
  that result was written). It is the `uncommitted_and_orphaned_work` class, not a neighbour.
* **It carries its own REUSE block**, lines 3–10, written by whoever drafted it — `CLASS: CUSTOM`,
  with the index terms searched and the three near-neighbours it distinguishes itself from. The
  block the refusal said could not be honestly written was already in the file.

## What it was doing wrong, measured

The tool answers the director's phase-one test verbatim: *"look at a household's half-hourly gas and
electricity for a year and believe it, and be able to say why it looks like that — this fabric, this
weather, **these people**, this heating pattern."* It drew its own headcount from
`_PEOPLE_BY_BEDROOMS`, so the people it named were not the book's people. Same premises, same
weather, same fabric, one variable — the headcount source:

| premise | bedrooms draw | census-anchored | electricity kWh | hot water kWh |
|---|---|---|---|---|
| C1 | 3 people | **1 person** | 3,011.7 → **1,688.7** (−44%) | 1,651.1 → **907.4** (−45%) |
| C2 | 2 | **4** | 2,287.2 → 3,348.2 (+46%) | 1,343.2 → 2,124.2 (+58%) |
| C3 | 4 | **2** | 3,662.5 → 2,478.7 (−32%) | 2,106.3 → 1,331.9 (−37%) |
| C4 | 2 | **3** | 2,245.0 → 2,917.9 (+30%) | 1,290.5 → 1,665.7 (+29%) |

Not a rounding difference in an explanation: a different household. Gas moves little because the
fabric dominates space heat, which is the tell — the explanation's *fabric* reconciliation closed
the whole time, over a home with the wrong number of people in it.

## The remedy is one line larger than the one that was owed

The owed remedy named the reporting call at line 95. That alone would have printed the census count
beside kWh produced from the bedroom count, because the *generator* draws its own profile when a
caller omits `behaviour=`. So the profile is built ONCE, before the trace, handed to
`generate_premise_trace(behaviour=...)`, and the same object is what the PEOPLE section reports. One
draw, one household, and the number shown is the number that produced the kWh above it.

Also removed: `if hasattr(pt, "behaviour_profile_for") else None`, a fail-open on a module this file
hard-depends on — it would have reported `people_count: null` rather than failing.

## The control

Third leg on
`tests/simulation/test_the_settled_book_draws_its_headcount_from_the_census_and_not_from_bedrooms.py`,
the file that already holds the "which callers get the census count" question. Behavioural, over the
real archive and a real year (~1s), and it asserts the fallback and the census DISAGREE for the
premise it uses before asserting anything else — a green over a premise where they happen to agree
would prove nothing.

Mutation-proven, each mutant loaded from outside the shared tree so no lane's in-flight gate saw it:

* drop `people_count=` → RED on leg 1 (*"the explanation is about a 3-person home the book never
  settled as one"*)
* drop `behaviour=profile` → RED on leg 2 (*"asked for the census headcount and then let
  generate_premise_trace draw its own"*) — **which leg 1 cannot see**, and is why there are two.
* unmutated → GREEN.

## What is still owed, and what I refused to bank

* **`premise_trace.generate_premise_trace`'s own fallback stays**, unchanged and deliberate. It is
  the legitimate default for a caller with no customer to key on; removing it is a different change.
* **The P&L effect of the 2026-09-16 headcount change is still unmeasured.** That result deferred it
  under R13 (measuring before landing would have made P&L part of a fidelity decision) and asked for
  it after. It is after. Not done here.
* **The ruff ratchet is red in the shared tree at I001 1307 against a baseline of 1308, and I did
  not bank it.** Measured in a `git archive HEAD` extract overlaid with exactly this commit's two
  files: 1308, green. The −1 is another lane's uncommitted fix, and banking it would leave a floor
  no committed tree reaches and wedge every lane — the standing rule in that file's own SHRINK LOG.

## Class registration

`no_caller_and_never_runs`, in the same mirror shape the 2026-09-16 result named: not a mechanism
without a caller, but a caller nobody enumerated. With a second edge worth stating — **the reason a
caller is left unfixed is itself a claim with a shelf life.** "It belongs to another lane" was true
when written and was an orphan two days later, and nothing would have re-asked it.
