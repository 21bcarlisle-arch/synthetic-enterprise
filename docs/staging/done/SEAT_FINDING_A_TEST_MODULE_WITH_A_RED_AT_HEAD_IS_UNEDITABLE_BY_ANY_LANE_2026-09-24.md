**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# FINDING — a test module carrying a red at HEAD cannot be EDITED by anyone, so its own repairs are locked behind an unrelated defect

Found while landing `dead-no-head-skips-in-the-published-feed-control-family` (`ba1ad7797`), which
repaired three of the family's four modules and could not touch the fourth.

## The mechanism

The gate selects a changed test file as its own subject. So a commit that edits
`tests/tools/X.py` runs `tests/tools/X.py`. If that module already holds a red at HEAD, **every
commit touching it is refused for a defect it did not introduce** — including commits whose whole
purpose is to repair that module.

This is not the same shape as "a red blocks the lane". A red test blocks only commits the gate
selects it for, which is why this one has stood 7 census runs without anybody tripping over it. It
becomes visible only when someone tries to edit the file, and at that moment it reads like their
own breakage: the refusal names an assertion far from their diff.

## The instance, measured

`tests/tools/test_a_published_surface_is_reproducible_from_its_committed_input.py` holds
`test_the_published_customer_book_is_reproducible_from_the_run_output_committed_beside_it`, red
since 2026-09-17 (HEAD_RED_REGISTER line 44, 7 consecutive census runs):

```
site/data/customers.json           publishes   154 households / 226 legs
docs/reports/run_output_latest.json regenerates 164 households / 251 legs
```

Confirmed red at a clean HEAD, not merely in the shared working tree: a gate extract was built by
the production path (`git archive HEAD | tar -x` then `surgical_land._make_standalone_repo`) and
the family run inside it. Same failure, same counts, with no working-tree contamination.

**That red is a real publishing defect** and the control is doing its job — the published customer
book is not derivable from the run output committed beside it, in either direction (10+ published
households absent from the regeneration, 10+ derivable households absent from the publication).
It is not this item's subject and is not repaired here.

**What it locked out.** The same module carries four instances of the defect `ba1ad7797` closed
everywhere else: its own `_head_resolves` with the false docstring "The landing checkout does not",
a dead disk fallback in `_as_committed` guarded by it, one more dead `pytest.skip`, and the same
false premise asserted in its module docstring. All four repairs were written and measured green,
then backed out of the commit, because the gate refused the tree they were in for the unrelated red.
The intended landing is recorded in `tools/published_feed_regeneration_check.head_resolves`'s
docstring so the next reader meets it where the work is.

## Why this is worth a finding and not just a note

The cost is not the one blocked edit. It is that **the block is invisible until someone pays for
it**, and what they see when they do is a refusal naming an assertion they have never read, in a
file they were trying to improve. The cheapest reading available to them is "I broke it". The
second cheapest is to back their change out — which is what happened here, and which leaves the red
standing and the repair unlanded, so the next lane to try pays the same cost again.

There is no register anywhere that relates *"this module is red at HEAD"* to *"this module is
therefore frozen against all edits"*. HEAD_RED_REGISTER counts the red and how long it has stood;
it does not say that the red has made its own file uneditable, which is the property that actually
costs an invocation.

## What would close it

Two candidates, and the first is not obviously right:

1. **Fix the red.** Correct, and it is a real defect that should be fixed regardless — but it does
   not generalise. The next module to go red re-creates the same trap silently.
2. **Have the refusal say so.** When the gate refuses a commit on a test that was ALREADY red at
   the parent commit, and the commit does not claim to fix it, say that in the refusal: *"this test
   was red before your change; your diff did not cause it; it is selected because you edited its
   file."* That is one comparison the gate can already make — it has the parent — and it converts
   the expensive reading into a cheap one.

Recommendation: **(2), and then (1) as ordinary work.** (2) is the one-leg mechanism that catches
the class; (1) is an instance that also needs doing. Filed rather than built because it is the
harness lane's subject and this claim is released.

## What is NOT claimed

That the red is new, that it is anyone's fault, or that the customer book's 154-vs-164 split has a
known cause. None of that was measured here. What was measured is that the red is at HEAD, not in
the working tree, and that it refuses edits to its own file.
