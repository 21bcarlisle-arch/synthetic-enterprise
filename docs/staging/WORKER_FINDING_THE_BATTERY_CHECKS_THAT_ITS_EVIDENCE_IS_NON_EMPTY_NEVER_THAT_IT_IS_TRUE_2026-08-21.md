**Severity:** LATENT · **Lane:** H_harness

# The cold-eyes battery checks that its evidence is non-empty, never that it is true — and the obvious repair is theatre, measured

**Found:** 2026-08-21, pass 44 of `EP6_wall_protocol_typing`, while landing pass 43's work
(`131b86df7`). Everything below is observed-with-evidence unless labelled inferred (R9).

**Class:** `controls_that_cannot_fail`.

---

## What prompted it

Pass 43 built `WallNotification`, wired it into the live triad, wrote 30 tests, downgraded
Q2's reconciliation row to `PARTLY REPAIRED, pass 43`, and **committed none of it**. Eight
source files and the store's rolled archive half sat in the shared worktree across at least
one further tick. Landed this pass as `131b86df7`, verified by the tree (`WallNotification`
at HEAD, archive chunk 32 in the same commit, `simplifications_count: 42`), 840 tests passing.

The landing is not the finding. The finding is that **while that state existed, EP6's own
reconciliation file asserted a repair against code that was in no commit, and the control this
atom built in pass 37 to replace a fail-open predicate could not tell.**

## Observed, with evidence

`tools/cold_eyes_battery.py:85` — `RECONCILIATION_KEYS = ("capability", "n", "verdict", "evidence")`,
enforced at `load_reconciliations` by `missing = [k for k in RECONCILIATION_KEYS if not row.get(k)]`.
That is a **truthiness** test. It refuses an absent or empty evidence string and accepts every
non-empty one. The module's docstring claims the reconciliation is "twelve falsifiable claims a
reader can check against the code" (line 45) — but nothing in the module ever opens the code.

The control is genuinely fail-closed against *silence*: no row blocks, an absent file blocks,
an unreadable file raises. Its direction-of-failure argument (pass 37: "to GREEN this the lane
must record twelve falsifiable claims, each citing a file a reader can open; to RED it the lane
need do nothing") holds for omission and **does not hold for a claim that cites something that
does not exist**. Nobody has to open the file for the claim to pass.

## The obvious repair is theatre, and this is measured rather than argued

The natural fix — require every repo path cited in `evidence` to resolve at HEAD — was tested
against the real pre-landing commit `2c0ba712b`, i.e. the tree as it stood while the defect was
live. Extracting every `path/like/this.{py,json,md,yaml,jsonl}` from all twelve rows and asking
`git cat-file -e 2c0ba712b:<path>` for each:

    n=1 PASS paths=1  · n=2 FAIL paths=6 · n=3 FAIL paths=1 · n=5 FAIL paths=11
    n=6 FAIL paths=4  · n=9 FAIL paths=1 · n=10 FAIL paths=1 · n=11 PASS paths=1
    n=13 FAIL paths=5 · n=14 FAIL paths=2 · n=15 FAIL paths=0 · n=17 PASS paths=2
    unresolvable at pre-landing HEAD: 0

**Zero.** A path-existence control would have been GREEN throughout the defect. Pass 43 added a
new *symbol* to `interface/contracts/wall_envelope.py`, a file that already existed at HEAD — so
the location resolved and the claim was still false. This is the inverse of the recorded lesson
that a symbol-presence control is fail-open because the claim carries a location: here the claim
carries **both**, and checking only the location is the fail-open half.

## What would have caught it, also measured

Resolving `path::symbol` citations — extract `<path>.py::<Symbol>` and require `<Symbol>` to
appear in `git show <ref>:<path>` — against the same pre-landing commit:

    interface/contracts/wall_envelope.py::WallNotification      NOT AT PRE-LANDING HEAD
    simulation/payment_seam_adapter.py::MandateNotificationStream NOT AT PRE-LANDING HEAD
    path::symbol citations found: 11, unresolvable at pre-landing HEAD: 2

Both hits are pass 43's, and they are the only two. The subject must be **HEAD, not the working
tree** — a symbol present only in the worktree is exactly the defect, and `surgical_land`
materialises HEAD-plus-pathspec as a real repo, so a row citing a symbol authored in the same
commit resolves correctly inside the gate and nowhere else. That property is what makes the
check landable at all.

## The honest limit, stated rather than buried

**Both rows this would have caught are FAIL rows.** FAIL blocks anyway, so the check would not
have changed EP6's outstanding set by one question. Its value is that it would have caught the
*unlanded state* — a record describing code in no tree — not that it would have moved a verdict.
Claiming it would have protected the exit criterion would be the overclaim this atom's own walk
exists to stop.

Two further limits, both fail-open residue that must be named if this is built:

- Only 11 citations across twelve rows use `path::symbol`. `n=11` cites
  `company/interfaces/wall_protocol.py:176-179` (a line range, which drifts and cannot be
  resolved by name), and prose citations resolve to nothing. The check covers the notation, not
  the claim.
- **A PASS row citing no path at all stays unchecked, and that is correct, not an oversight.**
  `n=17` is a PASS whose reviewer-specified right answer is an absence — *"an honest 'they don't,
  they're outside this' is fine and expected"*. A rule requiring every PASS to cite a resolvable
  symbol would red the one question the reviewer pre-authorised a negative answer for. Any
  repair must leave absence-claims alone.

## Why this was queued and not fixed on sight

SELF-INTERRUPT DISCIPLINE: a harness finding is registered, not fixed in the tick that found it.
It is also the shape pass 37 refused — tightening EP6's own instrument inside an EP6 draw. The
mitigating direction is worth recording for whoever takes it: this repair can only **add**
blockers to EP6 and never remove one, so unlike the pass-37 case there is no path by which the
lane tightening the control benefits from having tightened it.

## What would discharge it

`tools/cold_eyes_battery.py` resolves `path::symbol` citations against HEAD and raises
`BatteryUnavailable` when one does not resolve, with R15 mutation both ways: the two pass-43
citations above, read out of `2c0ba712b`, must RAISE, and the same rows read out of `131b86df7`
must clear — a null control that proves the check is not always-red. The two named fail-open
residues above go in the module docstring, where this atom already puts its named limits.

**Suggested rank:** backlog. EP6 carries six payable exit criteria ahead of it (Q3, Q5, Q6, Q10,
Q13, Q14), and Q3 — *"show me a conversation with more than two legs"* — is the only one no pass
has ever touched; it still carries its pass-33 reconciliation while 39–43 each repaired one of
the others.
