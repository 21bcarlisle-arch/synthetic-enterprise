**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# PRE-REGISTRATION — can the cadence that `_divergence_refusal`'s disjoint admission bets on ever pay?

Written **before** the measurement, under
`close-the-shared-tree-fork-that-holds-the-publisher-and-keeps-the-divergence-repair-inert`.
Graded in the SEAT_RESULT beside it.

## What prompted it

The shared tree was 1 ahead / 6 behind `origin/main` at 03:10Z. The 1 ahead is `b26362f94`, a
liveness heartbeat. Reading `_divergence_refusal` shows that commit was **not** an accident and
**not** an unchecked commit on a behind tree: the function asks `ahead > 0`, then asks whether
origin's incoming paths collide with the paths this commit writes, and when they are disjoint it
**deliberately admits one commit**, logging that it is doing so. Its own words:

> the disjoint admission is a **bet that the reconciler absorbs one**, not a licence to stack them

`_unabsorbed_publish_commits` caps the bet at one: a second publish commit stranded on our side is
refused, naming `origin_reconcile` as the remedy.

So the design is coherent *provided the bet is payable*. The question nobody appears to have asked
is whether the counterparty can pay. `_divergence_refusal`'s own docstring says, of itself, that
integrating is not its job because

> A daemon that merged unattended would be deciding, every twelve minutes, to move other people's
> work.

If `origin_reconcile` reasons the same way — and it is the same repository's same rule — then the
commit the heartbeat admits is **structurally unabsorbable by any daemon**, and only a seat can
clear it.

## Predictions

**P1 — the cadence cannot pay.** `origin_reconcile`'s unattended path will NOT close a 1-ahead
divergence. It will fast-forward when strictly behind and refuse/defer when ahead > 0, naming a
seat or the gated merge door. *Confidence: high.* If instead it has a working unattended merge leg
that closes a 1-ahead fork, P1 is refuted and the bet is payable — the fork would then be a
cadence-not-running problem, not a design gap.

**P2 — the heartbeat is currently silenced by its own cap.** With one publish commit already
stranded, `_divergence_refusal` now returns the `stranded` refusal, so
`liveness_surface_refusal` (the live field, not the stale twin) records `BEHIND_ORIGIN` and the
published heartbeat is frozen. *Confidence: high.* This is the failure the function's own comment
names — the liveness surface silent in the one state it exists for.

**P3 — the admission is reached routinely, not rarely.** Over the last ~24h of `main`'s reflog,
≥ 3 distinct `chore(liveness)` commits were minted while the tree was behind origin. *Confidence:
medium.* If it is 0–1, this is a rare race and the instance is the work; if it is many, the class
is the work.

## What would make me wrong about the whole frame

That `origin_reconcile` *does* merge unattended and simply has not run — in which case the
finding is about a stopped daemon, not about an unpayable bet. P1 is the one-variable control for
exactly that, and it is why P1 is measured against the **code path**, not against the fork's
current age.

## What this pre-registration does NOT claim

It does not claim the disjoint admission is wrong. Admitting one commit so a liveness surface can
speak on a behind tree is a reasonable trade. The claim under test is narrower and only about the
counterparty: **whether anything that runs unattended can absorb what the admission creates.**
