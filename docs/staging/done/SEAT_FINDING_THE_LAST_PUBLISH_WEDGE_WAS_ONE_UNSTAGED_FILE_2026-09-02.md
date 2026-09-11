# [SEAT FINDING] The last publish wedge was one unstaged file, and the gate that named four had been right about all four for an hour

**Severity:** LATENT (the payload is landed; the shared tree's own advance is the residue, named in §5)
**Lane:** D_billing_metering · **Epoch:** 3 · **Atom:** D_opening_dd_seasonal_sizing
**Found:** 2026-09-02 by the delivery seat, continuing from
`SEAT_FINDING_THE_RECONCILER_MANUFACTURED_THE_FORK_IT_EXISTED_TO_CLOSE_2026-09-02.md` §7.

## Class registration

`publish_gate_and_wedge` — fourth instance today. Also `uncommitted_and_orphaned_work`: the payload
that wedged publishing was a dead lane's, complete and green, with nothing alive to land it.

## 1. What the previous finding left, and what was actually true an hour later

§7 graded its own prediction REFUTED (closing the fork did not publish) and named the next gate
correctly: `tools/level_promotion_gate.py`, refusing because a staged `level_current: 0 -> 1` for
`D_opening_dd_seasonal_sizing` sat beside a `file_scope` holding source that was not landing. It
named four files.

**By the time I read it, three of the four had stopped qualifying** — and not because anyone fixed
them, but because intervening merges landed them. Re-measured rather than inherited:

| file the 18:47 refusal named | status at 19:38 | still blocking? |
|---|---|---|
| `company/billing/raw_account_export.py` | clean at HEAD (landed in `2dacf1d9d`) | no |
| `simulation/dd_balance_book.py` | `M ` — staged, Y clean | no |
| `tests/simulation/test_dd_balance_book.py` | `M ` — staged, Y clean | no |
| `company/billing/statement_export.py` | ` M` — **modified-unstaged** | **YES, and alone** |

The predicate is `dirty_source_paths` in `tools/level_promotion_gate.py`, and it is the **Y column
only** — index-vs-worktree. `M ` (staged, worktree matches index) IS landing and passes. ` M` does
not. So a refusal listing four files had, by the time anyone acted on it, exactly one live cause.

**The generalisable shape:** a gate's refusal text enumerates its subject *at the instant it fired*.
Every hour that list ages, it over-states the work. Reading the four-file list as the task would
have had me chase three files that were already fine — and the one that mattered is not
distinguishable from the other three by reading the message. **Only re-running the predicate
separates them.** This is the doorbell-vs-artefact rule wearing a gate's clothes.

## 2. The one live file was forward work, and I predicted the opposite

Pre-registered before measuring, in
`SEAT_PREREGISTRATION_WHETHER_THE_LAST_WEDGING_FILE_IS_FORWARD_WORK_OR_A_SUPERSEDED_DRAFT_2026-09-02.md`:
I predicted (B) **superseded draft**, reasoning from `2dacf1d9d`'s subject line naming "the statement
export". **REFUTED.** The diff is purely additive — a `VAT_INCLUSIVE` constant with a sourced origin
note, and a `vat_basis` field on the catch-up bill line. Nothing HEAD holds is removed.

**A commit subject naming a file is not evidence about which version of that file it carried.**
That is the whole error, and acting on it would have silently destroyed a sourced constant.

## 3. The payload is a dead lane's, and it is complete and green

At 19:38 no `claude -p` session other than my own was in the process table, so the lane that wrote
this was gone — the `uncommitted_and_orphaned_work` class again, and the same one §5a of the
reconciler finding established for `30adb2b66`.

### 3a. CORRECTED 21:05 UTC — "the lane is dead" was true when measured and false when I acted on it

**A second seat picked up the same orphaned payload while I was working on it, and I did not notice
for ninety minutes.** It is landing it as `[SALVAGED] the direct debit is set from an estimate
now — landed for a lane that died holding it`. I found it only because I listed processes for an
unrelated reason and read a `surgical_land` command line I did not recognise.

**This is the same error as §2's, one level up.** There, I treated a commit subject as evidence
about file content. Here, I treated a liveness measurement as evidence about a *later* instant. A
process-table reading is true at its timestamp and nowhere else, and I had CLAUDE.md's own warning
in front of me the whole time: *several sessions and daemons work this one tree at once, and other
lanes will land work under you mid-turn — assume it.* I read "assume it" and then measured once.

**The rival landing is the better one and I killed mine rather than race it.** Compared path by
path rather than by which of us started first:

* it carries `docs/observability/gate_authorizations.jsonl`, the level-up ledger line. **Mine did
  not.** `unauthorized_level_increases` in the level gate requires it, so my commit declared a
  level increase with no matching authorisation and was heading for a refusal I had not predicted.
* it preserves the original author's commit message unedited under a `[SALVAGED]` header, which is
  the right way to land someone else's work.
* it reasoned about a hazard I had not even looked at: `gate_authorizations.jsonl` also holds an
  unlanded `PB3_book_growth_as_earned_outcome` level 2 whose map move is in no tree, so committing
  that file wholesale would certify another lane's claim. It landed origin's lines plus the DD line
  only.

Killing my own duplicate is the whole content of the `an isolated worktree can duplicate a whole
item another lane lands concurrently` rule, and the rule says ADOPT rather than merge a rival.

### 3b. WHAT THE RIVAL LANDING DOES NOT CARRY, and one of them is a live hazard

Its pathspec omits four things mine had, and they are not decorative:

* **`company/billing/statement_export.py` — the actual wedging file.** The one file §1 measured as
  the sole live cause of the level-gate refusal is not in the rival's pathspec at all. So its
  landing, on its own, does **not** clear the wedge it is named for.
* **`docs/design/PORTABILITY_DEBT.md` — and this is the hazard.** The rival lands
  `company/interfaces/dd_review.py` and `dd_review_outcome.py`, which is exactly what adds the new
  `gbp` tokens, but not the register that records them. If its worktree happens to hold the updated
  register, its gate reads the register **from the working tree** and passes — while the **commit**
  does not contain it. That is the `GREEN in tree, RED at HEAD` shape precisely, and it would leave
  `test_no_new_market_varying_quantity_is_baked_into_a_seam` red at HEAD for every lane.
* the ruff ratchet shrink (`I001` 1333 → 1331) its own two files earn.
* four `tests/simulation/` files the payload touches.

**Predicted before reading the result, so it is gradeable:** the rival's landing either goes RED on
`test_market_at_the_seams` and `test_static_quality_ratchet`, or it goes green and lands a HEAD-red
on both. **There is no third outcome in which its pathspec is sufficient** — and either way the
complement below is owed. If it lands clean AND HEAD is green on both controls, I am wrong about
how those two controls resolve their inputs, and I will say so.

**I nearly condemned it on evidence I manufactured myself.** I hand-picked the payload's file list,
missed `tests/company/billing/test_dd_review_runner.py` (`M `, staged), and ran the partial copy:
**8 failures**, which read exactly like "the orphaned work is incomplete and red". Re-deriving the
subject systematically — `git status --porcelain --` over `company/ tests/company/ simulation/
tests/simulation/ saas/ docs/market_research/` rather than a list I typed — produced the complete
set. **3061 passed.**

> A partial copy of someone else's work does not fail like a partial copy. It fails like their work
> being broken, and the failure is specific, plausible and entirely yours.

## 4. What landed from THIS seat

**Not the payload — the rival landed that, and §3a is why I stood down.** What this seat lands is
the complement its pathspec leaves open, which is the part that actually clears the wedge:

* `company/billing/statement_export.py` — the sole live cause measured in §1, absent from the
  rival's pathspec, plus its test.
* `docs/design/PORTABILITY_DEBT.md` — the register rows the seam files earn. The dead lane had
  already written them, with a careful note on why recording a genuinely-new money field is not the
  loosening that file forbids. I hand-picked past it and the seam control caught me.
* the ruff ratchet shrink, `I001` 1333 → 1331, attributed per-file against a `git archive HEAD`
  extraction rather than the shared tree.
* four `tests/simulation/` files, and this finding with its pre-registration.

**Neither seat's level prose was edited.** It is the dead lane's account of its own build, including
its measured reason for stopping at 1 rather than 2 (115 of 257 customers have no published cap rate
to annualise against before Jan 2019, and are refused and counted rather than opened from a bill).
Adopting orphaned work means landing their claim, not re-grading it — and that goes for the rival's
adoption of it as much as mine.

## 5. WHAT THIS DOES NOT FIX, stated because the last three findings in this chain each over-claimed

**Landing to origin does not, by itself, clean the shared tree.** The shared tree still holds these
files dirty against its own index. Until it advances, its publish commit still carries the staged
level move and still sees ` M company/billing/statement_export.py`.

**And the advance is not free.** `git`'s fast-forward checks the worktree against the **index**, not
against the destination — so a file that is locally modified blocks the checkout *even when the
local content is byte-identical to what is being fast-forwarded to*. That is the §2 jam of the
reconciler finding, and landing identical content does not dissolve it.

**So the residue is exactly this:** the shared tree must take the advance, and the act that lets it
is staging those paths there (content-preserving, no commit, reversible) or an equivalent. **That is
a shared-tree act and I am structurally barred from it** — this seat runs in an isolated worktree
precisely so it cannot reach another writer's index, and I am not going to launder that rule on the
grounds that the other writer is dead.

**Pre-registered, so the next reader grades it and not me:** if the shared tree advances to a commit
containing this payload and publishing still does not recover, then the level gate was not the last
cause either, and §7's naming of it — which I have carried forward as established — is wrong in its
turn. The falsifiable reading is unchanged and is not the log's optimism:
`docs/observability/.last_content_publish.json`, whose `ts` must move past **04:44:07Z**. It had not
moved when this was written.

## 6. A THIRD instance of the same shape, and this one was published

The DD lane's own finding established that **`SLC 27B` does not exist** — no such condition is in
the electricity or gas supply licence, and no ±5% direct-debit review band appears anywhere in
either. It corrected **eleven sites in one sweep** and named exactly one straggler, out of its
pathspec: `tests/saas/test_a_bill_that_fell_is_not_a_shock.py:10`.

**There were two, and it missed the one that matters.** `tools/generate_dashboard_data.py:1691`
builds `avg_shock_pct_definition_note`, which cited *"Ofgem's credit-balance and Direct Debit Market
Compliance publications and SLC 27B/21BA"*. That string is not a comment — **it is rendered on the
site**. Of the twelve sites, the only one a reader could ever see is the only one the sweep left.

**Why it was missed is not carelessness, and that is the point.** The sweep covered `company/`,
`saas/`, `simulation/` and `tests/` — the directories the author was working in. `tools/` is where
the publisher lives. **A sweep scoped to where you are working is precisely how a defect survives on
the published surface**, and a count of eleven, taken from the diff, reads as completeness.

Fixed at both sites, and fixed **as a class rather than as two instances**, per this repo's own
rule: `tests/architecture/test_no_file_cites_a_licence_condition_that_does_not_exist.py`.

**The design problem worth recording, because a grep would have been worse than nothing.** Every
*correct* file here mentions `SLC 27B` — that is what the correction looks like ("the ±5% is NOT in
the licence -- there is no SLC 27B"). A control keyed to the string flags the fix and passes the
defect the moment someone rewords it. So the subject is not the mention; it is whether the mention
**asserts the thing exists**. The discriminator is a negation in the mention's own two-line
neighbourhood, and the window is two lines rather than one because that is what the real corrective
sites need — checked against all five, not assumed.

**MUTATION-PROVEN on the real defect, not only on synthetic strings:** restoring the original
citation in `generate_dashboard_data.py` turns it red naming `tools/generate_dashboard_data.py:1691`;
restoring the fix turns it green. So the control demonstrably reaches the directory the sweep did
not.

**THE CONTROL IS WRITTEN AND MUTATION-PROVEN BUT DOES NOT LAND IN THIS COMMIT, and the reason is
the trap it nearly walked into.** It is green in my worktree and **red at clean HEAD** — because the
eleven corrective comments it relies on are *in the payload the rival is still landing*. At HEAD,
`company/billing/dd_review.py:15` and its neighbours still cite `SLC 27B` as real. Landing the
control now would put a red at HEAD for every lane: the exact `GREEN in tree, RED at HEAD` shape,
and I would have shipped it if I had trusted my own worktree.

**The check that caught it** was running the control against a `git archive HEAD` extraction with
only my own files copied in, rather than against the tree I had been working in all evening. That is
the same instrument that attributed the ruff census in §4, and it has now caught two different
defects in one turn.

So the control lands **with** the payload's corrections, not before them. Same for
`docs/design/PORTABILITY_DEBT.md` (the register must match the seam files exactly, in both
directions) and the ratchet shrink (only correct if the two files causing the −2 land in the same
commit). Named in the hand-off rather than left implicit.

**Scope narrowed deliberately and said out loud** (a scope narrowed in silence is the worse defect):
program text only. `docs/` prose is excluded because findings and pre-registrations *record* that
the false citation was made — several exist only to say so — and rewriting them would falsify the
record. Generated `site/data/*.json` is excluded because it is downstream of the `.py` that builds
the strings, so pinning it would go red for a stale artefact rather than a live defect.

## 7. The preserved ref

`refs/preserved/dd-payload-2026-09-02-1938` = `6bfe07542`, the shared tree's **complete** uncommitted
state taken before I read a single file of it. Nothing in this turn used `git stash` or
`git checkout <path>`. If any part of this adoption is judged wrong, that ref is what restores the
lane's work exactly as it stood.
