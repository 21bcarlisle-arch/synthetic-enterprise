**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted` · **Claim:** `replay-the-retired-continuations-against-origin-evidence` (Lane 0 delivery)

# Pre-registration: how many retired continuations have no origin evidence

**2026-11-08, delivery seat. Written while the probe was running, before its output was read.**

**Question.** `617a2181e` makes `seat_continuation.retire` ask `origin_refusal`. Every row retired
before it retired on the tick's word alone. How many of those rows does `origin_refusal` refuse now,
and how many of those have work that is still missing from origin/main?

**Probe.** For every row in `seat_continuation.retired()` that is not a `focus_row_tombstone`, call
`origin_refusal(row, items=<the whole store>)`. The real stores are read through
`shared_tree_dir()`.

**Prediction, filed before the answer.**
- Most refused rows will be **false positives**: rows whose work landed under a commit that does not
  bind the id (no `--landed` bind and the id not in the message), or analysis rows that never had
  anything to land. I expect between 20% and 60% of retired rows to be refused. That is a wide band
  because I do not know how often older ticks bound by id.
- Rows whose work is **really missing**, with no later commit, file or successor carrying it: I
  expect between 0 and 3, and N15/N16 should not be among them, because they were repromoted.

**What refutes it.** Over 60% refused would mean the refusal is mostly noise for old rows, and that
the store needs a backfill rather than a re-offer. More than 3 really missing would mean the
stranding was common, not occasional.

**How "really missing" is judged.** For each refused row, look in origin/main's log for its id, for
the key terms in `what`, and for the files it names. A row is re-offered only when none of those
shows the work.
