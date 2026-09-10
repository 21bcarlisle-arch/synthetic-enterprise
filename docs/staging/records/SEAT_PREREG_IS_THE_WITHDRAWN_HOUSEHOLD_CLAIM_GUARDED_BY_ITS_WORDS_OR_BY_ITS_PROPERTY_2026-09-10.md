# PRE-REGISTRATION — is the withdrawn household claim guarded by its WORDS or by its PROPERTY?

**Written:** 2026-09-10, before running anything below.
**Seat:** delivery seat, isolated worktree `/var/tmp/se-seat-executor`, HEAD `712a7fc4e` (= `origin/main`).

## Why this question exists

The drawn Lane-0 item asked me to land a value-arms withdrawal repair. It is already landed —
`8c53c35e5` put all four fields and all four page readers at HEAD. While confirming that, I read the
producer's composition of `decisions.auc_reading` and the control over it, and found a seam worth
testing rather than arguing about.

`tools/generate_value_arms_data.py::_auc_reading` gates the strong household sentence on
`household_earned` (the STRATIFIED figure clearing its null). When it is not earned, the branch
instead publishes:

> "so on this population the belief separated those who stayed from those who left."

The withdrawal's own stated reason, in the same feed, is:

> `"who"` is a household claim and the stratified figure does not carry it.

So the replacement sentence is built from the same `who`-construction the withdrawal condemns. It is
immediately followed by `BUT THE PAIRS BEHIND IT COMPARE ERAS, NOT HOUSEHOLDS`, which is a real
mitigation — this is why the question is about the GUARD, not about whether the page misleads.

The guard is `site/test_the_stratified_concordance_reaches_the_reader.py`:

```python
HOUSEHOLD_CLAIM = "real information about who stays"
...
assert "the belief carried " + HOUSEHOLD_CLAIM not in live_decisions
```

That is a literal-substring guard over ONE sentence. The project rule it is measured against is
CLAUDE.md's *"Key a control to the property, not to today's answer"*, and the R15 shape *"a grep for
a concept name is blind to the mechanism implemented without it."*

Note what is NOT in doubt and is not being tested: this control already carries
`test_a_run_whose_belief_DOES_rank_within_the_year_keeps_its_household_reading`, a genuine
reachability leg proving the gate does not refuse everything. That leg is correct and this
pre-registration does not question it.

## The question

If the un-earned branch stated a household claim **in different words**, does the guard fire?

## Predictions, recorded before running

1. **P1 — the guard stays GREEN under a paraphrase poison.** Replacing the un-earned branch's
   sentence with a blatant household claim that avoids the literal string
   (`"the belief told us which individual households would leave"`) leaves
   `site/test_the_stratified_concordance_reaches_the_reader.py` fully green. Confidence: high. This
   is the whole point of the question; if it is refuted the seam does not exist and I say so.
2. **P2 — the control is not vacuous.** A poison that DOES use the literal string
   (`"the belief carried real information about who stays"`) turns
   `test_the_withdrawal_reaches_the_rendered_page` RED. This is the poison round that makes P1
   readable: `green` under P1 means two opposite things unless P2 establishes the control can fire
   at all.
3. **P3 — a figure I expect NOT to move.** The number of tests collected in that file is unchanged
   by either poison (both poisons edit only prose inside one producer branch). Recorded so that a
   moved count is a refutation and not a shrug. This is the weaker kind of prediction and is
   labelled as such.

## What each outcome would mean

- **P1 holds, P2 holds** → the guard is phrase-keyed and structurally cannot see the withdrawn claim
  restated. That is a finding to file, and the remedy is a control leg keyed to the property.
- **P1 refuted** (paraphrase poison reds) → the guard is broader than it reads and there is nothing
  here. I record that and drop it.
- **P2 refuted** (literal poison stays green) → a much worse defect than the one I went looking for:
  the guard fires on nothing. That would take priority over P1 entirely.

## What this pre-registration does NOT claim

It does not claim the live page misleads a reader. The `BUT ... COMPARE ERAS` sentence lands in the
next breath, and I have read it. The claim under test is about what the CONTROL can detect, which is
a different and narrower thing. Conflating the two would be the same overclaim this whole withdrawal
exists to correct.

## Method

Poison in the working tree only; restore from a pre-run copy (`/tmp/se_gv_backup_425706.py`) and
verify with `md5sum -c` before recording anything.
