# [SEAT FINDING] The executor's discharge asks a store its own claim never reaches, so the condition is never false

**Severity:** RECORDED (read down from BLOCKING 2026-09-02 by §12, which lands the larger half §11.3
left open and is mutation-proven in both directions on both routes. It had been raised
LATENT → BLOCKING earlier the same day — see §9 — because the verdict instrument was untrustworthy
on the executor's busiest route: on a PROMOTED item leg 1 could never pass, so a turn that really
landed was scored `LANDED NOTHING`. Measured, not inferred, at every step. The forward predictions
of §8 and §9.7 concern the LIVE log and remain ungraded; see §12.6.) · **Lane:** H_harness
**Epoch:** 3 · **Atom:** none — this is Lane 0 delivery machinery
**Found:** 2026-09-02 by the delivery seat, while building the subject-reading verdict that
`an-exit-code-is-not-a-landing` asked for. Found by the live-ledger guard refusing a test fixture,
not by looking for it.

## Class registration

Belongs to `controls_that_cannot_fail`. The specific shape is R15's fourth: a branch whose
condition is never false, so the verdict is a constant. Same shape as the thirty-two consecutive
stand-downs `background/seat_executor.py` already documents against itself — *"a refusal whose
condition is never false is not a control; it is a disconnected wire that reports itself as
safety"* — arriving through the opposite door: a DISCHARGE whose condition is never false.

## 1. The two stores

`background/seat_executor.py:735`, inside `run_once`, before the session is spawned:

```python
delivery_lane.claims_mod.claim(work_id, note=str(item.get("what") or "")[:200], paths=[])
```

No `path=`. `claims_mod` is `background/seat_work_in_hand.py`, so this writes
`docs/observability/.seat_work_in_hand.json`.

`_still_claimed`, after the session, asks `delivery_lane.held()`, which is

```python
return set(claims_mod.held(path=path or CLAIMS_FILE))   # delivery_lane.CLAIMS_FILE
```

— `docs/observability/.delivery_lane_claims.json`. **Two different files.** The executor writes its
claim into one and reads for it in the other.

## 2. Measured, not inferred

On disk at 2026-09-02 22:1x UTC, with a turn's claim live:

```
.seat_work_in_hand.json    -> ['compose-with-origin-and-land-the-census-repair-that-is-the-publish-wedge']
.delivery_lane_claims.json -> []
```

The claim is in the store nobody asks, and the store that is asked is empty.

## 3. What that makes true

`_still_claimed` returns False for every turn the executor takes by the PROMOTED CONTINUATION
route — which is its busiest route, because `_promote_to_handoff` is how a re-derived focus item
reaches a tick at all, and a promotion never goes through `delivery_lane.draw()`, which is the only
thing that writes the delivery-lane claim.

So the discharge fires unconditionally. `docs/observability/seat-executor-log.md` for 2026-09-02
carries a `DISCHARGED ... the tick released its claim` line after **every single turn** — 15:46,
16:42, 17:56, 18:55, 20:17, 20:48 — and the reason it gives is false in all six: no tick released
anything, because no tick ever held a claim in that store.

The discharge's own comment says what it was for: *"RE-OFFERING IS DELIBERATE while work is
unfinished ... If it did not release, the continuation stands and the next tick continues."* That
sentence describes a mechanism that has never run. Every handoff has been consumed after one turn,
whether or not the work was finished.

## 4. Why this is LATENT rather than BLOCKING, as of this commit

The discharge is now downstream of the subject-reading verdict landed alongside this finding: a
turn that did not move its bound paths on the shared tree returns before reaching
`_still_claimed` at all. So the unconditional discharge can only fire on a turn that genuinely
landed something, where consuming the handoff is at worst premature rather than a silent loss.

That is a narrowing of blast radius, **not a fix**, and it should not be read as one. A piece of
work bigger than one turn still gets its continuation dropped after the first increment lands.

## 5. Why I did not fix it here

Because which store owns which question is a real design call and I could not settle it inside this
turn without guessing:

* `seat_work_in_hand` is the CROSS-LANE PATH GUARD's store. `refuse_if_duplicated` reads it, and
  the executor genuinely needs its work declared there so another writer cannot take the same
  paths. Claiming there is correct.
* `delivery_lane`'s store is where a tick's `python3 -m background.delivery_lane --release <id>`
  goes, and where `draw()` records a handout. Asking it "did the tick say it was done" is correct.

Both halves are individually right. What is missing is anything that makes the executor's OWN
claim visible to the release channel — and note the second-order trap in §6 before choosing the
obvious repair.

## 6. The trap any repair has to clear first

`delivery_lane.PROJECT_DIR` is `Path(__file__).resolve().parent.parent`. The executor's child runs
with its cwd inside the worktree, so `python3 -m background.delivery_lane --release <id>` from
there imports the WORKTREE's copy of the module and writes the WORKTREE's store, which
`ensure_worktree` resets at the start of the next turn. The shared store never hears it.

So "make the executor claim into the delivery-lane store" would move the discharge from
*never false* to *never true* — the mirror-image constant verdict — unless the child is also told
to run its `--release` against the shared tree. The charter landed with this finding now names
that for `--landed`; it does not yet name it for `--release`.

## 7. What would settle it

A control that runs one real turn and asserts the discharge fires when the tick released and does
NOT fire when it did not — i.e. one that exercises both branches. Today no test reaches
`_still_claimed` with a True answer, which is why a condition that has never once been false has
survived in a module whose own docstring is about exactly this failure.

## 8. Prediction, written before the repair

If the repair in §5 is made without §6's clause, `seat-executor-log.md` will stop carrying
`DISCHARGED` lines entirely, and the first symptom will be a continuation re-offered indefinitely
after the work is finished — a livelock, not a silence. If §6's clause is included, the log should
carry `DISCHARGED` on some turns and not others within a day. **Neither has been observed yet.**

---

## 9. AMENDMENT 2026-09-02, later the same day — it is worse than §4, and §4's narrowing is what hides it

Written by the next seat turn, which was the FIRST turn to run under the new verdict, and which
found this by having the verdict refuse its own genuine landing.

**Severity raised: LATENT → BLOCKING.** Not because the blast radius grew, but because §4's
narrowing — "the discharge is now downstream of the verdict, so it can only fire on a turn that
really landed" — turns out to be the *other* half of a constant. §4 is true and its consolation is
false.

### 9.1 The two claims are not one bug, they are a matched pair

```
delivery_lane.draw()      claims_mod.claim(..., path=store)   # store = delivery_lane.CLAIMS_FILE
seat_executor.run_once()  claims_mod.claim(...)               # no path= -> seat_work_in_hand
```

`draw()` passes the path. `run_once` does not. So the store a work id's claim lands in **depends on
the route it arrived by**:

| Route | Claim lands in | `--landed` | Verdict leg 1 |
|---|---|---|---|
| `draw()` | delivery-lane store | binds | **can pass** |
| `_promote_to_handoff` | `seat_work_in_hand` only | refuses `NOT CLAIMED` | **can never pass** |

The promoted route is the executor's busiest, by §3's own argument.

### 9.2 Measured, on this turn, not inferred

This turn landed `8cb73c627`, promoted it to `origin/main`, and then ran the binding step the
charter requires:

```
$ python3 -m background.delivery_lane --landed an-exit-code-is-not-a-landing
bound NOTHING to an-exit-code-is-not-a-landing: it is NOT CLAIMED -- nothing holds a deadline
for it, so there is nothing to inform.

.seat_work_in_hand.json    (shared) -> ['an-exit-code-is-not-a-landing']
.delivery_lane_claims.json (shared) -> []
```

A real commit, really promoted, whose paths really moved on `origin/main` — and leg 1 cannot see
it, so the turn is scored `LANDED NOTHING`.

### 9.3 What that makes the new verdict

**A constant, on the promoted route.** R15's fourth shape again, and the mirror of the defect the
verdict was built to remove: the old verdict could never say *no*, and the new one can never say
*yes*. `test_the_verdict_is_not_the_exit_code` pins both directions against a FIXTURE, so it is
green and honest; nothing pins the production claim path, which is where the route decides the
store. §7 predicted exactly this gap — *"today no test reaches `_still_claimed` with a True
answer"* — and it is now measured rather than predicted.

It fails in the safe direction: work is re-offered, never falsely consumed. Eleven hours of false
success is a worse failure than a repeated turn. But an instrument that cannot say yes is not
reporting on its subject either, and the item churns.

### 9.4 §6's trap now has a proven mechanism, which it did not when this was filed

§6 declined the repair because a child running `--landed`/`--release` from the worktree imports the
worktree's `delivery_lane` and writes a store `ensure_worktree` wipes next turn.

**That is the same defect, in the same class, as the one this turn just fixed and landed for
`LOG_FILE` in `8cb73c627`:** a path constant derived from `__file__` resolving to whichever tree
imported it. The repair there is `_shared_tree_log()` — ask `git rev-parse --git-common-dir` where
the real tree is, keep an explicit `path=` override so tests still get a fixture, and fall back so
the resolution can never lose a readable artefact. Mutation-proven, including one guard pair
established as an equivalence rather than assumed.

So §6's blocker is no longer "we have no way to do this". It is now one design call, stated below.

### 9.5 The design call this leaves, stated so the next turn does not have to re-derive it

Both stores are individually right (§5), and the missing thing is that the executor's own claim is
invisible to the release channel. Two candidate repairs, and I did not pick one because picking it
inside this turn would have been the guess §5 correctly refused:

* **A —** `run_once` claims in BOTH stores (add `path=delivery_lane.CLAIMS_FILE`), and the
  delivery-lane store resolves shared-tree-first by §9.4's mechanism. Smallest diff. Risk: two
  claims to keep in step, and a partial failure leaves them disagreeing.
* **B —** `delivery_lane.held()` asks `seat_work_in_hand` as well — one store stays the writer,
  the reader unions. Risk: it widens what "claimed" means for every other caller of `held()`.

**A is the recommendation**, because the release channel's store should be the one a tick's
`--release` writes, and B leaves `--landed` still refusing.

### 9.6 The control that settles it, restated with what §7 was missing

§7 asked for a control exercising both branches of the discharge. It needs one more clause: it must
exercise both **routes**, because the route is what selects the store, and a fixture that claims
directly will pass whichever repair is chosen. Concretely — a promoted item and a drawn item, each
taken through a turn that binds a landing, asserting the verdict says *yes* for both.

### 9.7 Prediction, written before the repair, alongside §8's which still stands

If repair A lands with §9.4's shared-tree resolution, `seat-executor-log.md` will carry its **first
`FINISHED ... bound path(s) moved` line on a promoted item**, and `DISCHARGED` will appear on some
turns and not others. If A lands *without* it, the log will show `LANDED NOTHING` on every turn
including ones that landed — indistinguishable at a glance from today, which is the reason to check
the store contents directly and not the log.

**This turn's own line will be `LANDED NOTHING` for a turn that landed and promoted `8cb73c627`.
That is the prediction most easily checked, and it is written before the log was read.**

---

## 10. `--release` reports success unconditionally, and that is the mechanism behind §3's six false lines

Found immediately after §9, by running `--release` and then looking at the store instead of the
message. The same turn's two commands disagreed about whether one id was claimed:

```
$ python3 -m background.delivery_lane --landed  an-exit-code-is-not-a-landing
bound NOTHING: it is NOT CLAIMED
$ python3 -m background.delivery_lane --release an-exit-code-is-not-a-landing
released an-exit-code-is-not-a-landing          <- and the claim is STILL in the other store
```

`background/delivery_lane.py:605`:

```python
if args.release:
    claims_mod.release(args.release, path=CLAIMS_FILE)
    print(f"released {args.release}")
```

`release()` returns `None`. **The success line is unconditional** — it prints whether or not
anything was there, and it releases from `CLAIMS_FILE`, which is the store the executor's claim
never reaches (§1). Measured after the call above: `.seat_work_in_hand.json` still held the id and
`.delivery_lane_claims.json` was still `[]`.

### 10.1 Why this closes the loop on §3

§3 established that `_still_claimed` is never true, so the discharge always fires. §10 supplies the
other end: the tick's `--release` **cannot** release the executor's claim, and tells the tick it
did. So the discharge's stated reason — *"the tick released its claim"* — is false in a second,
independent way, and a tick that never released reads a success message confirming it had.

Three instruments in one chain, each reporting on itself rather than its subject: the exit code,
the claim store, and now the release message. That is why §7's control has to assert against the
STORE, never against a return value or a printed line.

### 10.2 What this adds to repair A

Repair A (§9.5) is necessary but **not sufficient on its own**. Making `run_once` claim into the
delivery-lane store gives `--release` something real to remove, but the unconditional `print`
remains: a `--release` that refuses, or that finds nothing, would still tell the tick it succeeded,
and the next reader of that line has the same problem this whole finding is about.

**So repair A gains a clause: `--release` must report what it actually did.** `claims_mod.release`
should say whether a record was removed, and the CLI should print the refusal and its reason when
it was not — the same discipline `record_landing`'s `refusal_reason` already follows, in the module
that already owns the pattern.


---

## 11. AMENDMENT 2026-09-02, later still — §10.2's clause is LANDED. §9.5's clauses 1, 2 and 4 are NOT

Written by the turn drawn on `an-exit-code-is-not-a-landing`, which found this finding already on
origin and its clause 3 still open.

**Discharged: only the release-reporting clause of repair A.** claims_mod.release now returns
whether a record was actually removed, and the delivery-lane CLI prints released NOTHING for the
id followed by a named reason and exits non-zero, matching what the landed binding step already
does one branch below it. Evidence: 20 tests in the control file, four mutations run in an
isolated worktree, each killing the test that names it — release returning True unconditionally
kills two, the unconditional print kills one, collapsing the reason to a single generic string
kills three, and dropping the worktree comparison kills one.

### 11.1 The reason SEPARATES the causes, because that was the whole point

Three, ordered, and the ordering is load-bearing rather than incidental:

1. **Held in the other store** — §9.1's matched pair, and the only one that means STOP AND LOOK.
   The work is still in hand and the release could never have found it.
2. **Standing in a linked worktree** — §6's trap. Checked second because it is a property of the
   PROCESS, not of the id, so once it fires it fires for everything.
3. **Not claimed anywhere** — the ordinary reading, which must not borrow the alarming one.

### 11.2 A defect in the repair, caught by the repair's own discipline

The first draft of the control passed from the shared tree and FAILED, unmutated, from a linked
worktree — because clause 2 above reads the tree the process is standing in, and the test left
that ambient. That is the same class as the executor-log defect fixed the day before: a control
whose verdict depends on who launched it. The fixture now pins the project directory to a plain
repository, and a separate test pins the worktree clause against a real linked worktree, so the
environment is an input rather than an accident. Both trees now agree at 20 passed.

### 11.3 What is still open, and it is the larger half

§9.5 clauses 1, 2 and 4 are untouched and deliberately so — which store a claim should land in is
the design call §5 declined to guess at, and it is still handed off as
the-landing-verdict-can-never-say-yes-on-a-promoted-item. Until it lands, leg 1 of the verdict
remains a constant on the promoted route. **This amendment narrows the chain from three
self-reporting instruments to two; it does not close it.** §8's prediction is untouched and
still unobserved.

---

## 12. §11.3's larger half is LANDED, and the repair is not the one §9.5 proposed

Written by the turn that drew `an-exit-code-is-not-a-landing`, found §10.2 already landed by a
concurrent lane as `551d1aadf`, adopted it rather than rebuilding it, and landed the complement.
**Severity reads down: BLOCKING → RECORDED.**

### 12.1 §9.5's repair A had a second-order cost that §9.5 did not name

`delivery_lane.next_item` filters on `held(store)`. **A claim in the delivery-lane store is exactly
what stops an item being offered again.** So "make `run_once` claim there too", applied as written,
buys the verdict's *yes* by spending the re-offer that `an-exit-code-is-not-a-landing` exists to
produce: a `LANDED NOTHING` turn would leave its own claim standing, `next_item` would skip the
continuation, and the item would wait for the 100-minute sweep rather than the next tick. The
verdict would say *no* correctly and the work would not come back — the same defect one door along,
and it would have been the third mirror-constant in this one chain.

So `run_once` now claims in all three stores, each answering a different question, and `_hand_back`
releases the one it took — matched on `claimed_at`, so it releases what it took rather than
whatever is there — once the verdict has been read. The claim is real and load-bearing FOR THE
DURATION OF THE TURN: it is what stops a concurrent draw handing the same item to a second writer.
Pre-registered before the repair, with this consequence named in advance, in
`docs/staging/SEAT_PREREGISTRATION_WHETHER_CLAIMING_IN_BOTH_STORES_RESTORES_THE_YES_WITHOUT_KILLING_THE_REOFFER_2026-09-02.md`.

### 12.2 §9.4's shared-tree resolution was deliberately NOT taken

§9.5A asks for `delivery_lane.CLAIMS_FILE` to resolve shared-tree-first by `_shared_tree_log`'s
mechanism. It is unnecessary and it would cost something: both readers (`bound_landing` and
`_still_claimed`) now union the two stores, and pointing that module-level constant at the shared
tree would have every worktree child writing the live shared records — the opposite of what the
worktree exists for. `_worktree_claims()` names the second store in one place instead.

The recommendation was followed where it was right and departed from where it was not, and the
departure is recorded here rather than left for the next reader to infer from the diff.

### 12.3 ORDER is load-bearing, and getting it wrong rebuilds the defect out of its own repair

`_still_claimed` asks *did the TICK release*; `_hand_back` is the executor's own bookkeeping. Run
the hand-back first and the two are indistinguishable — every turn would look like a tick reporting
itself finished, and the unconditional discharge this finding is about would be back, built this
time out of the repair.
`test_the_executors_OWN_hand_back_is_not_read_as_the_tick_releasing` dies to exactly that
transposition.

### 12.4 What discharges §7 and §9.6

§7 asked for a control exercising both branches of the discharge; §9.6 added that it must exercise
both **routes**, because the route selects the store. Both now exist in
`tests/background/test_an_exit_code_is_not_a_landing.py`, and none of them stub anything between
`run_once` and the stores — a fixture that claimed directly would pass under the defect, which is
exactly how `test_the_verdict_is_not_the_exit_code` stayed green and honest while production was a
constant:

* `test_the_verdict_can_say_YES_on_the_PROMOTED_route` — dies to dropping `_worktree_claims()` from
  `run_once`'s claim loop, which restores the measured behaviour of §9.2 exactly.
* `test_the_verdict_can_say_YES_on_the_DRAWN_route` — dies to dropping the shared store from
  `bound_landing`, **and the promoted test stays green under that same mutation** (verified by
  running it, not assumed), so the two routes are separately witnessed rather than one subject
  satisfying both alternations.
* `test_a_LANDED_NOTHING_turn_leaves_the_item_DRAWABLE_AGAIN` — dies to deleting `_hand_back`. This
  is §12.1's cost, pinned.
* `test_the_tick_RELEASING_really_does_discharge` — **the pass branch, reached for the first time
  in this module's life.** §7's *"today no test reaches `_still_claimed` with a True answer"* is now
  false. `_still_claimed` dies to a constant in EITHER direction: True fails this test, False fails
  §12.3's.
* `test_the_hand_back_releases_only_the_claim_THIS_turn_took` — dies to dropping the `claimed_at`
  match.

Ten mutations were run against the full repair and ten died.

### 12.5 The three instruments are now all reporting on their subject

§10.1 named them: the exit code, the claim store, and the release message. `551d1aadf` closed the
third; this closes the second; the first was closed by `6d18107c7`. **The chain is complete.**

### 12.6 §8 and §9.7's predictions, graded

§9.7's *"this turn's own line will be `LANDED NOTHING` for a turn that landed and promoted
`8cb73c627`"* — **correct**, and measured in §9.2 before the log was read.

§8 and §9.7's FORWARD predictions are about the LIVE log and are **not yet gradeable**: they need
the next real executor turn under this code. §8 predicts that a repair without §6's clause makes
`DISCHARGED` vanish entirely and the continuation re-offer indefinitely — a livelock. The repair
landed here includes the clause (`_still_claimed` reads the worktree store, which is where the
tick's `--release` lands), so the prediction to check is §9.7's: **the log should carry its first
`FINISHED ... bound path(s) moved` line on a promoted item, and `DISCHARGED` on some turns and not
others.** Neither has been observed yet, and §9.7's own warning stands — check the store contents
directly, not the log, because the failure mode is indistinguishable from success at a glance.

### 12.7 One thing this repair adds that no section predicted

`.gitignore` now covers `docs/observability/.delivery_lane_claims.json` and its draw ledger. The
executor writes a copy of the claim into its WORKTREE, so without this the child finds an untracked
file in `docs/observability/` every turn — noise at best, and at worst a broad pathspec committing
one lane's live claims into the shared tree. Neither store was ever tracked; this makes that
explicit rather than incidental.
