# [SEAT FINDING] The executor's discharge asks a store its own claim never reaches, so the condition is never false

**Severity:** RECORDED (read down from BLOCKING 2026-09-02 by §12, which lands the larger half §11.3
left open and is mutation-proven in both directions on both routes. It had been raised
LATENT → BLOCKING earlier the same day — see §9 — because the verdict instrument was untrustworthy
on the executor's busiest route: on a PROMOTED item leg 1 could never pass, so a turn that really
landed was scored `LANDED NOTHING`. Measured, not inferred, at every step. §8 and §9.7's forward
predictions concerned the LIVE log across several turns and are now GRADED in §13 — §9.7 clause 2
SPLIT, §8's antecedent designed against rather than tested. §12.6's last open clause is closed by
§13.1: the repaired WRITER is measured in production on the promoted route.) · **Lane:** H_harness
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

§9.7's forward prediction is in **two clauses, and the first is now GRADED — it held.** Measured
against the real shared tree immediately after this turn promoted `b095fadf8`, on the promoted
route, with nothing stubbed:

```
leg 1  bound landing: 5 path(s)
leg 2  shared tree changed since 551d1aadf: 5 path(s), unreadable=''
VERDICT: moved=True -- 5 of 5 bound path(s) moved on the shared tree
```

**That is the first time this instrument has said YES in its life.** §9.2 measured the same call
answering `LANDED NOTHING` for a turn that had really landed and really promoted; the same call on
the same route now answers correctly. The constant is gone in the direction that was hardest to
see, and it is measured rather than argued.

The second clause — *`DISCHARGED` on some turns and not others* — and §8's livelock prediction are
about the LIVE log across MULTIPLE turns and remain **ungraded**. They cannot be settled from one
turn by construction. §9.7's own warning stands for whoever grades them: check the store contents
directly, not the log, because the failure mode is indistinguishable from success at a glance.

One honest caveat on the first clause, recorded rather than left for a reader to find: this turn's
own claim had to be mirrored into the delivery-lane store BY HAND before it could be bound, because
the executor that spawned this turn was running the pre-fix `run_once`. The verdict above is
therefore a true measurement of the repaired READER against a real landing, and not yet a
measurement of the repaired WRITER in production. The next executor turn is what closes that, and
it is the handed-off piece.

**§12.6 IS NOW CLOSED — see §13**, written by the turn that took the hand-off. The writer is
measured in production on the promoted route; §8 and §9.7 clause 2 are graded, and clause 2's grade
is SPLIT rather than the clean pass this section expected. One clause of the caveat above needs
correcting too: *"the next executor turn is what closes that"* was wrong for the same reason
`2635bf7fe` was filed — the next turn would have imported the pre-fix writer from the shared tree.
What closed it was a turn that ran **after a fast-forward**, and that is the third time in this
chain the distinction has cost something.

### 12.7 One thing this repair adds that no section predicted

`.gitignore` now covers `docs/observability/.delivery_lane_claims.json` and its draw ledger. The
executor writes a copy of the claim into its WORKTREE, so without this the child finds an untracked
file in `docs/observability/` every turn — noise at best, and at worst a broad pathspec committing
one lane's live claims into the shared tree. Neither store was ever tracked; this makes that
explicit rather than incidental.

---

## 13. AMENDMENT 2026-09-03 — §12.6's last clause, graded on the live record

Written by the executor turn `grade-the-repaired-writer-on-a-real-executor-turn`, which §12.6
handed the grading to. **Severity stays RECORDED.** Pre-registration for this turn's own forward
measurements, filed before `--landed` was run and before this section was written:
`docs/staging/SEAT_PREREGISTRATION_WHETHER_THE_REPAIRED_WRITER_CLOSES_THE_LOOP_ON_A_PROMOTED_ITEM_2026-09-03.md`.

### 13.1 The repaired WRITER is in production, measured on the promoted route

§12.6's honest caveat was that its `moved=True` graded the repaired *reader*, because the claim had
been mirrored into the delivery-lane store by hand. This turn needed no mirror. Read from the live
stores three minutes into the turn, before anything was written:

```
shared   docs/observability/.seat_work_in_hand.json     claimed_at 1788392160.0330517
shared   docs/observability/.delivery_lane_claims.json  claimed_at 1788392160.0330517
worktree docs/observability/.delivery_lane_claims.json  claimed_at 1788392160.0330517
                                                        = 2026-09-02 23:36:00 UTC
```

One `claimed_at` across three files is `run_once`'s `for store in _claim_stores()` loop — three
files written by one loop, not three writers that happen to agree. And the route is the one §9.1's
table said could *never* pass: this id is absent from the shared `.delivery_lane_claims.draws.json`
(54 ids, back to 2026-08-28), so it arrived through `_promote_to_handoff`, not `draw()`. §9.2
measured that exact route on the pre-fix writer and got `.delivery_lane_claims.json (shared) -> []`.

The generation was checked rather than assumed, which is `2635bf7fe`'s whole point: the shared tree
fast-forwarded to `c1e24f4bb` at 23:28:13 UTC and this tick logged `RUNNING` at 23:36 UTC, so the
parent imported the three-store `run_once`.

### 13.2 §9.7 clause 2 — GRADED, and the grade is SPLIT

The five ticks either side of the repair, with each one's writer generation taken from the shared
tree's reflog rather than from the `on <sha>` in its own log line — **that sha is `origin/main`,
which is precisely not what the executor imports**:

| Tick (UTC) | Item | Route | Shared tree at start | Verdict | `DISCHARGED`? |
|---|---|---|---|---|---|
| 21:36 | `an-exit-code-is-not-a-landing` | drawn | `c04dd0af6` (pre-fix) | LANDED NOTHING | no |
| 22:05 | `an-exit-code-is-not-a-landing` | drawn | `6d18107c7`→`9cf0aff2b`, both pre-fix | 1 of 1 moved | **yes** |
| 22:36 | `the-landing-verdict-can-never-say-yes-on-a-promoted-item` | drawn | ambiguous | 1 of 1 moved | no |
| 23:05 | `the-landing-verdict-can-never-say-yes-on-a-promoted-item` | continuation | `2635bf7fe` (repaired) | 3 of 3 moved | **yes** |
| 23:36 | `grade-the-repaired-writer-on-a-real-executor-turn` | continuation | `c1e24f4bb` (repaired) | in flight | in flight |

**As written, clause 2 holds:** `DISCHARGED` appears on some turns and not others, within a day,
which is the outcome §9.7 attached to the repair landing *with* a working store resolution.

**As meant, it is not yet demonstrated, and I am not going to let the table imply it is.** The
clause is only interesting if an absence is caused by `_still_claimed` answering True. Three
different causes produce that one absence, and the log cannot tell them apart:

1. the verdict said `LANDED NOTHING`, so the discharge branch is never reached (the 21:36 tick);
2. `_still_claimed` answered True — the branch the repair exists to make reachable;
3. `seat_continuation_drop` returned False because the id was never in the continuation store,
   which is the case for **every drawn item** — `DISCHARGED` is inside that `if`.

The 22:36 tick is cause 3 and possibly nothing else: `the-landing-verdict-…` has
`first_drawn_at 22:36:26 UTC` in its own draw ledger, so it reached that turn by `draw()` and had
no continuation record to drop. Its writer generation is ambiguous besides — it started within
about two seconds of the fast-forward to `ff563798b` — so it is evidence for neither side and is
recorded as such. Reading it as cause 2 would have been the flattering answer and it is unearned.

**What discriminates it**, stated so the next turn does not re-derive it: a **promoted** item, which
does have a continuation record, running under the repaired writer, where the child's decision to
run `--release` is the only free variable. The 23:36 tick is exactly that, the branch was fixed in
advance in P3 of this turn's pre-registration, and the reading is handed off. That is one tick's
wait, not a redesign.

### 13.3 §8 — the antecedent was designed against, and both symptoms are absent

§8 predicted that repairing §5 *without* §6's clause would make `DISCHARGED` vanish entirely and
livelock a continuation. **§6's clause was never taken** — §12.2 records it being declined on
purpose, with both readers unioning the two stores instead of `delivery_lane.CLAIMS_FILE` being
pointed at the shared tree. So §8's antecedent as written never obtained, and §8 cannot be graded
as a test of it.

Its two symptoms are checkable regardless, and both are **absent** on the live record: `DISCHARGED`
has not vanished (22:36 and 23:30 UTC carry it), and no continuation was re-offered indefinitely —
`the-landing-verdict-…` was offered twice, discharged at 23:30, and the next tick drew a different
item. The failure §8 named is real and is what §12.1 and §12.3 were built against; what it is *not*
is a prediction that was run. **Graded as: warning heeded, mechanism avoided, symptoms confirmed
absent — not as a hypothesis confirmed.** A prediction whose condition was engineered away is worth
less than one that was allowed to run, and saying so is cheaper than the alternative, which is a
record that reads as two-for-two.

### 13.4 The grading found a defect of its own: the absence names no cause, so it is now named

§13.2 could not attribute one missing `DISCHARGED` line, and that is not an accident of this
turn — it is the same complaint this whole finding makes about the *positive* result, arriving
through the negative one. Until now the only line written at that branch was `DISCHARGED`, so
every other outcome was a silence, and three different things produce it.

The smallest thing that fixes it is the one leg: say which silence it is.

```
HANDOFF STANDS <id>: the tick did not release its claim, so the continuation is re-offered
                     to the next tick rather than consumed
NO HANDOFF TO DROP <id>: the tick released its claim, but no continuation record held this id
                     -- a DRAWN item never has one, so this turn says nothing either way
                     about the discharge condition
```

Neither string contains the token `DISCHARGED`, deliberately: three existing controls assert on
that token, and a reason line that made them pass by string coincidence would be worse than no
reason line at all. Nor does either match `_TURN_LINE`, so the drawn channel's census is unmoved.

Two controls, each asserting on the branch's own observable (`routed.dropped`) as well as on the
line, so a reason attached to the wrong branch fails rather than reading plausibly:

* `test_a_turn_whose_TICK_DID_NOT_RELEASE_says_so_instead_of_going_quiet`
* `test_a_DRAWN_items_missing_discharge_is_not_read_as_the_tick_holding_on`

| # | Mutation | Result |
|---|---|---|
| A | the `if not tick_released:` arm loses its reason line — the 2026-09-02 silence restored exactly | **DIES**, and only the first test fires |
| B | the drawn arm loses its reason line | **DIES**, and only the second test fires, so each silence has a SOLE witness rather than one subject satisfying both alternations |
| C | the two reasons swapped between the branches | **DIES on both** — the reason is keyed to its branch, not merely present |

Green at rest: 31 passed, up from 29. The sole-witness separation in A and B was established by
running each mutation and reading which test failed, not by assuming the tests were disjoint.

**What this does NOT do:** it does not make §9.7 clause 2 retrospectively gradable. The lines that
would have settled it were never written. It makes the *next* one gradable from the log alone,
which is the only direction available.

### 13.5 What is closed and what is still owed

Closed: §12.6's open clause — the repaired writer is measured in production, on the promoted route,
with nothing mirrored by hand (§13.1); §8 graded (§13.3); §9.7 clause 2 graded, split (§13.2); the
absence of a discharge now names its cause, mutation-proven (§13.4).

P1 and P2 of this turn's pre-registration are **CONFIRMED**, measured after the landing was
promoted, by calling the shared tree's own `subject_moved` rather than reading the log:

```
--landed  ->  bound 2 path(s) to grade-the-repaired-writer-on-a-real-executor-turn
leg 1  bound landing: 2 path(s), at 1788392588.0 (> started 1788392160.03: True)
leg 2  shared tree changed since c1e24f4bb: 2 path(s), unreadable=''
VERDICT: moved=True -- 2 of 2 bound path(s) moved on the shared tree
```

§9.2's measurement of the same call, on the same route, was `bound NOTHING … it is NOT CLAIMED`
with `.delivery_lane_claims.json (shared) -> []`. The difference is the writer, and this time
nothing was mirrored by hand — which is precisely what §12.6 said it could not yet claim.

Owed, and handed off with its exact reading: this turn's own `DISCHARGED`/`FINISHED` pair, which
the parent writes after the child exits and which no turn can read about itself, plus the sibling
prereg's P4 — that no `seat-claim:` alarm fires for this id, now that `_hand_back` releases all
three stores. **Both are graded in §13.6.**

### 13.6 P3 and P4 — GRADED from the next turn, and both CONFIRMED

Written by the executor turn `read-this-turns-own-discharge-line-and-close-p3-and-p4`, which is the
turn §13.5 handed the reading to. It can grade them because it is a different process: the two
lines are written by the *parent* after the child exits, so §13.5's item was not an unfinished
piece of work but a measurement that structurally had to be taken from outside.

**P3 — CONFIRMED.** The pre-registration fixed the branch in advance — `--release` would be run,
therefore the log must carry `DISCHARGED` immediately before `FINISHED`. Read from the shared
tree's `docs/observability/seat-executor-log.md`, lines 188–190, consecutive and unedited:

```
[2026-09-02 23:36 UTC] RUNNING    grade-the-repaired-writer-on-a-real-executor-turn … on c1e24f4bb
[2026-09-03 00:08 UTC] DISCHARGED grade-the-repaired-writer-on-a-real-executor-turn: the tick
                                  released its claim, so the handoff is done and will not be re-offered
[2026-09-03 00:08 UTC] FINISHED   grade-the-repaired-writer-on-a-real-executor-turn: rc=0 --
                                  3 of 3 bound path(s) moved on the shared tree
```

This is what §13.2 said it lacked and could not manufacture: a **promoted** item (so a continuation
record existed and `seat_continuation_drop` could return True), under the repaired writer (so
`_still_claimed` read both delivery-lane stores), with the child's `--release` as the only free
variable — and the branch written down before the answer was visible. Causes 1 and 3 of §13.2's
three silences are excluded by construction here, so the line is attributable to the discharge
condition and to nothing else. **§9.7 clause 2 now has the discriminating case §13.2 said it was
one tick short of.** It does not retrospectively upgrade §13.2's split grade — that grade stands as
written — it supplies the leg the split was missing.

**P4 — CONFIRMED.** No `grade-the-repaired-writer-on-a-real-executor-turn` line appears in
`docs/staging/WORKER_FINDING_REPEATING_ALARM_SEAT_CLAIM_2026-08-26.md`; the id list ends at
`an-exit-code-is-not-a-landing`.

**The absence is not fail-silent, and that was checked rather than assumed** — an absent alarm and
a dead alarm-writer look identical, which is this finding's own recurring complaint:

* the sweep is **live**: `reconcile-watch.timer` (5-minute cadence, `reconcile_watch.py:167`
  calls `_seat.sweep()`) last ran 00:08:25 UTC, three minutes before this reading;
* the sweep **cannot** reach this id: it is ABSENT from all three claim stores, read at
  00:11:30 UTC. `stale_claims` iterates the store, so a released record is not "not yet stale",
  it is unreachable. The prediction's stated mechanism — the turn ends inside the 45-minute
  window, at 32 minutes — is what was observed, and the deadline at 00:21 UTC was never armed;
* the alarm writer **was working within the hour**: the same document's mtime is 22:53:23 UTC,
  when it appended `an-exit-code-is-not-a-landing`.

That last line is the contrast case and it is one tick earlier in the same file. `an-exit-code-…`
claimed at 22:05 UTC and logged `DISCHARGED`/`FINISHED` at 22:36 UTC — **finished work** — and was
alarmed on anyway at 22:53, because the pre-fix `_hand_back` released fewer stores than the claim
loop took. That is `c1e24f4bb`'s subject exactly. So P4 is not merely a nothing-happened: the same
document, the same sweep and the same live writer produced a false alarm one tick before, and did
not for the tick that ran under the three-store release.

**The check §13.4 handed forward is NOT YET GRADABLE, and the cause is `2635bf7fe`'s, again.**
This turn was also asked whether `HANDOFF STANDS` or `NO HANDOFF TO DROP` had appeared anywhere in
the log. Neither string appears — and that is uninformative, because neither string is in
production:

```
shared tree /home/rich/synthetic-enterprise   HEAD 4e8770f70
git rev-list --left-right --count HEAD...origin/main  ->  0   1
git merge-base --is-ancestor d832149bb origin/main     ->  yes (it is the origin/main tip)
grep -c 'HANDOFF STANDS' <shared tree>/background/seat_executor.py  ->  0
```

`d832149bb` landed the two reason lines and was pushed, but as of this reading the shared tree had
not yet taken it (it did at 00:13:47 UTC — see the correction below), and `seat-executor.service`
is `ExecStart=… -m background.seat_executor --once` — a fresh
process per timer tick, importing from the shared tree's `WorkingDirectory`. So every tick since
has run `4e8770f70`'s writer, which has only the `DISCHARGED` arm. **The repair for a silence was
itself silent, for the same reason the repair before it was: pushed is not imported.** §13.4's
closing claim — "it makes the *next* one gradable from the log alone" — was true of the code and
false of production, and the distinction is exactly the one `2635bf7fe` exists to force.

**Correction, written beside the claim rather than over it.** The paragraph that stood here said
this turn would fast-forward the shared tree, having checked the three differing paths were clean.
**It did not, and the fast-forward was not needed** — re-reading divergence immediately before
acting, which is the only reason this was caught, found the tree had moved under the measurement:

```
00:06:14 UTC  merge origin/main: Fast-forward   -> 4e8770f70   (shared tree acquires the PRE-emitter writer)
00:08:18 UTC  seat-executor --once starts       -> imports 4e8770f70
00:11:30 UTC  the measurement above is taken    -> 0/1 behind, emitter absent, all true as printed
00:13:47 UTC  merge origin/main (another lane)  -> a043ad67b    (d832149bb arrives; emitter IS in production)
```

So the emitter reached production at **00:13:47 UTC**, carried in by another lane's `surgical_land`
merge, not by anything this turn did. The measurement stands exactly as printed — it was true at
00:11:30 — and the conclusion drawn from it stands too: **every tick from the repair landing until
00:13:47 ran a writer that could only say `DISCHARGED`**, so the two reason lines had no chance to
appear and their absence graded nothing. What changes is only the remedy's authorship.

Two things worth keeping. First, the shared tree's reflog shows it takes code **only** when a lane
merges or fast-forwards it — eight such entries in ninety minutes, none automatic. "Pushed is not
imported" is not an occasional slip here, it is the standing condition, and any repair whose
evidence is a log line is invisible until some unrelated lane happens to move the tree. Second,
this turn's own lines are unaffected either way: its parent imported `4e8770f70` at 00:08:18 UTC,
five minutes before the emitter arrived, so the executor's **next** tick is still the first that
can emit either reason line — which is what P5 below is written against, and it is now properly
armed rather than waiting on an act.

**P5 — pre-registered here, before the answer is available.** On the first tick whose parent starts
after 00:13:47 UTC — the instant the shared tree took `d832149bb` — every
`FINISHED` line will be preceded by exactly one of the three arms — `DISCHARGED`, `HANDOFF STANDS`
or `NO HANDOFF TO DROP`. I predict **YES**, and the first non-`DISCHARGED` arm to appear will be
`NO HANDOFF TO DROP`, on a **drawn** item, because a draw writes no continuation record while the
executor is currently consuming continuations. *Refuted by:* a `FINISHED` line with none of the
three arms before it (the branch is unreachable in production, not merely unlanded), or by
`HANDOFF STANDS` appearing first, which would mean `_still_claimed` answers True more often than
the discharge path is reached and would be a more interesting result than the one predicted.

Note the shape being avoided: the arms are not being graded by the turn that landed them, and not
from the code. §13.4 mutation-proved the branch; only the log can show it firing.
