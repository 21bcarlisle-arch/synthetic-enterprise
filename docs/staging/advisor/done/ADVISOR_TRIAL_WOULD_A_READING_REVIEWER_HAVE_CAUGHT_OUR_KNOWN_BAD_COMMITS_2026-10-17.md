# ADVISOR TRIAL — would a reading reviewer have caught our known-bad commits?

Staged by the advisor on the director's standing delegation of 15 Oct, 2026-10-17.
A one-off measurement, not a build. Rank it yourself among in-flight work.

**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

The director, in chat with his advisor:

- 08:54 BST: "What about big hunting agents and pr review it discusses. Do we do that?"
- 08:56 BST, on whether to stage this as a measurement trial: "Yes"

## Where it came from

The Claude Code team's account of how they review code now that agents write most of it
(https://claude.dev/blog/solving-code-review-at-anthropic/, read in full by the advisor). On
every change, several agents hunt for bugs in parallel and verifier agents vote on each finding,
and a finding is posted only when enough verifiers agree. The reviewer reads the diff against the
whole repo and the change's stated intent. They score that reviewer daily against a set of past
incident-causing changes, and they keep a change to the reviewer only if the score rises. Their
own figure: the share of changes that got a substantive comment rose from 16% to 54% after launch.

## What the advisor found here (check it; the repo wins)

- We have the parts, and some are designed better than theirs. `phase-close-evaluator` (fresh
  context, no Write/Edit). `cold-eyes-walk`. `background/naive_organ.py` (amnesia enforced at the
  process boundary). `background/judge_validation.py` (outcome correlation, consistency,
  independence, gold set). That last one is their incidents-as-evals and verifier vote, already
  designed.
- They almost never run. `docs/observability/trust_ledger.json` holds **five** recorded verdicts,
  from 2026-07-13 to 2026-10-05. `git log --since=2026-09-17` counts about **3,083** commits.
  Unrecorded runs may exist, so five is a floor, but judge validation has nothing to measure:
  no PASS has ever had a later defect attributed back to it.
- Every commit passes deterministic gates. Nothing READS a change and asks what could go wrong.
- Our two costliest recurring classes pass every gate, and a reader could plausibly catch both:
  a mechanism wired to nothing (`docs/staging/reference/CLASS_NO_CALLER_AND_NEVER_RUNS_2026-08-12.md`,
  `CLASS_UNCOMMITTED_AND_ORPHANED_WORK_2026-08-12.md`), and one rule implemented several times
  (the VAT case: five implementations, a defect fixed in one and still live in another).
- The ledger's own last entry warns of the limit: "Same-model review: blindness, not
  independence."

## The question

**Had a reading reviewer looked at our known-bad commits when they were made, how many defects
would it have caught, and at what noise on clean commits?**

Answer it from our own history, before building anything:

1. A labelled set. Commits that introduced a defect we later found: the recorded no-caller and
   orphan instances, the VAT divergence, the G14 mislabelled carbon series, and anything else on
   the head-red or standing-red registers with a known introducing commit. Then a matched set of
   commits with no defect found since. You choose the size. Say what bound it earns.
2. Review each one at its own parent, seeing only what existed then: the diff, the whole tree at
   that commit, and the commit message as stated intent. You choose the shape. Parallel hunters
   with a verifier vote is what the article used. Compare it with a single reviewer if the cost
   allows, because whether the vote earns its cost is part of the answer.
3. Score it. For each bad commit: did it name the defect we later found? For each clean commit:
   how many findings, and how many of those survive your own check? Report catches, noise and
   cost per commit as separate numbers. Do not blend them into one score.
4. Record every verdict through `judge_validation`, so this trial is also the first real data
   that store has had.

Then say what you would do with the result, with the numbers behind it. That could be review on
large or risky commits only, review on none, or something neither of us has thought of. A clear
"it would not have caught them" is a full answer and saves us building something.

## Reserved

- No new commit gate and no change to an existing one in this turn. If the trial makes the case
  for one, it goes to `for_the_director` as a proposal with the numbers.
- Its results are diagnostics, never targets (R12). Nothing tunes a reviewer prompt against this
  labelled set and then reports a score on the same set. If tuning happens, hold out a split
  before you start and say so.
- Keep the cost bounded. A sample that answers the question beats a census. Run the cheap
  searches and log-reading on Haiku or Sonnet, per CLAUDE.md. The judging is the part the
  question is about, so choose its model deliberately and state the choice.
- Fix nothing a reviewer finds during the trial. A real live defect it surfaces is a finding to
  file, not a side quest.

## Risk

Touches: a scratch worktree and judge_validation's store. No production path.
Blast radius: none to the company or the world. Compute spend is the only cost.
Probable failure mode: a labelled set the reviewer has already seen in effect, because the defect
is described in the commit message, a later file or CLAUDE.md. That would make catches look
easier than they were. Check what the reviewer can see before you trust its hit rate.
Proportionality: reversible and narrow — just do it.

## Epoch arc

Governance substrate, not company machinery. The question is whether a cheap reader would catch
what our gates structurally cannot: defects downstream of a green commit.

## Done

*Worker tick, 2026-10-17. Run as asked: a labelled set, a blind review of each commit at its own tree, scored, every verdict recorded through `judge_validation`. No gate was added or changed, nothing was tuned, and nothing the reviewers found was fixed.*

**Short answer: a blind reader would have named the specific defect we later paid for in 1 of 5 cases, and pointed at its location in 3 of 5. It flags far more than that, though. When two reviewers agreed a commit had a MAJOR problem, that separated the bad commits from the clean ones (4 of 5 against 0 of 5). On every commit, including the clean ones, it found real latent problems that the gates had passed. This does not make the case for a gate. It does make the case for a cheap, non-blocking reader on two kinds of commit: those that add a new module, and those that add a second implementation of a rule. Proposal below.**

### Design

- **Labelled set.** I picked 6 known-bad commits from fix commits that name the commit they repair (a Sonnet search agent did the census). One of the six is the VAT cap clamp (`58ec2d508`). Today's `CLAUDE.md`, which every reviewer is loaded with, describes that case, so it is scored on its own as contaminated. I also picked 5 clean commits (50–600 changed lines, in `company/`, `simulation/` or `background/`, from 2026-10-01 to 2026-10-04). None of their own files has had a fix-worded commit since. "Clean" here means only that no defect has been found yet.
- **Blindfold.** Each commit was unpacked with `git archive <sha>` into `/home/rich/rr_trial/cNN/tree` with no `.git`, so no later commit, finding or fix was readable. The reviewer saw the tree, the `.py` diff, the stat and the commit message as intent, and was told to read nothing else. The commit ids were neutral and the answer key was held outside the directory.
- **Reviewer.** `phase-close-evaluator` on **Opus**, chosen deliberately because the judging is the thing under test. Every commit got the same prompt (`/home/rich/rr_trial_prompt.txt`). Two independent reviewers (arms A and B) per commit, 22 reviews in all. The vote is the overlap between the two arms.
- **Pre-registered** before any review ran: the answer key, plus the prediction "a single reviewer catches 2 of 5 (range 1–3); clean commits draw 1–3 findings each, about half of which survive my check; the vote halves the noise".

### Catches on the 5 uncontaminated bad commits

| commit | defect we later found | arm A | arm B |
|---|---|---|---|
| `09e2bf07f` G14 carbon | NESO series spliced across the 2020-04-27 basis step; post-2020 values labelled loss-corrected | partial: both flagged that `FOOTPRINT_BASIS` and the new feed disagree on loss correction, **and both believed the wrong side** | partial |
| `b8767ebc1` | keeps the first 200 chars of hook output; the verdict is printed last | miss | miss |
| `5f6a4f15f` | new module-level import; hand-kept fixture `_MODULES` tuple not updated | miss | miss |
| `f9a22843d` | flat unsourced `RETENTION_EFFECTIVENESS = 0.20`, blind to discount size | **catch** (rated MINOR) | **catch** (MAJOR) |
| `ac6b841fb` | standing charge counted in settlement revenue and again by `bill_generator` | partial: both named the second standing-charge rule in the bill path colliding with settlement, but not the double count | partial |

- **Strict (named the mechanism): 1/5 per arm, 1/5 under the vote.** The 95% Clopper-Pearson interval for 1/5 is 0.5%–72%.
- **Lenient (pointed at it): 3/5 per arm.** Interval 15%–95%.
- **What five cases can say:** the reader catches the specific defect we paid for sometimes, not usually. It cannot say more precisely than that. My prediction (2 of 5) was a little high on the strict count.
- **Contaminated VAT case (`58ec2d508`): both arms passed it, so the leak did not help.** Arm A did name the ex-VAT against inc-VAT mismatch, but said it was older than this commit. That may be right, in which case the label is wrong: the commit moved the cap reading to the world and may not have created the mismatch. I have not settled this.
- **The misses share a shape:** a truncation that drops the wrong end, and a hand-kept list elsewhere going stale. Both are about what other code assumes; neither shows as a wrong line in the diff.
- **The partial catches share a shape too:** the reviewer finds the contradiction but trusts the confident-looking side of it.

### Noise on the 5 clean commits

- **Arm A** returned NEEDS_WORK on 4/5 (4 MAJOR, about 9 MINOR). **Arm B** returned NEEDS_WORK on 1/5 (1 MAJOR, about 9 MINOR). The two arms gave the same verdict on only 6 of 11 commits, and every disagreement was on a clean commit.
- **Most disagreements were about severity, not substance.** On `2d3b87a6b`, `e150225c9` and `c42bae117` both arms raised the same issue; one called it MAJOR and the other MINOR.
- **My check of the MAJORs on clean commits:** I read each one against the code at HEAD. None is false.
  - `471ab8960`: `measure_ageing_resolution` still ages paid-off failed bills that the scorer no longer ages, so the published caveat claims finer resolution than the scored ageing figure has. **Live at HEAD.**
  - `2d3b87a6b`: four draw-ledger writers in `delivery_lane` still write without the lock. **Live at HEAD**; the commit's own finding had disclosed this as residue.
  - `1aa97f1a4`: a withdrawn lump leaves `PeriodRecord.settled_on` set, so a switch objection lifts early. Real, but has no effect while the take-up basis is None.
  - `e150225c9`: the job-loss rate is moved to the lower, flattering end of its range. Disclosed in the commit, but an F11 judgement call.
  - `c42bae117`: clearing an "earlier-revision twin" can undo a lane's deliberate uncommitted revert. A real design risk; no harm observed.
- **So on this set the "noise" is mostly real findings our own process had not yet made**, not false alarms. My prediction ("about half survive") was wrong in the flattering-to-the-reviewer direction. The cost of a reader on this set is triage, not chasing phantoms.

### Findings beyond the answer key, on the bad commits

- **Both arms, `ac6b841fb`:** the standing charge is booked as pure margin with no cost behind it. This looks like the defect the seat found on 2026-10-14 (`SEAT_FINDING_RENEWALS_SIT_AT_THEIR_COST_FLOOR_BECAUSE_THE_FLOOR_CARRIES_THE_STANDING_CHARGES_NETWORK_AND_THE_PREMIUM_READS_THE_STANDING_CHARGE_AS_MARGIN_2026-10-14.md`), raised here at the commit that introduced it, four months earlier. I have not confirmed the match line by line.
- **Both arms, the dead-mechanism class (the one the advisor asked about):**
  - `ac6b841fb`: the new double-entry ledger had no production caller.
  - `f9a22843d`: retention cost events reach no ledger.
  - That is three instances across the set, each caught by both arms.
- **Both arms, `5f6a4f15f`:** `launch_liveness.check()` copies an unreadable register aside on every 300 s deadman cycle into a 10-slot store. After about 50 minutes the slots are full, and the next distinct corruption is overwritten with nothing kept. Each arm reproduced this by running it. **The code is unchanged at HEAD.**

**Filed, not fixed:** the three defects confirmed live at HEAD are in `docs/staging/WORKER_FINDING_A_BLIND_READING_REVIEWER_FOUND_THREE_DEFECTS_LIVE_AT_HEAD_2026-10-17.md`.

### Does the vote earn its cost?

- **Counting a finding when both arms raised it, at any severity:** this kept every catch, but 4 of 5 clean commits stayed flagged, so it cuts little.
- **Counting a commit as flagged only when both arms said NEEDS_WORK:** bad 4/5 flagged against clean 0/5 (Fisher exact, one-sided p ≈ 0.02). Two of those four bad commits were flagged for a different real defect, not the labelled one.
- **So the vote earns its cost as a commit-level triage signal.** It does not improve finding the specific defect.
- **The cost is two reviews per commit:** about 50k–137k tokens of context each, and 1–4 minutes wall time each. The `$` per review was not metered per subagent; I am not putting a figure on it.

### Through `judge_validation`

- **What was recorded:** all 22 verdicts, via `record_close_verdict` as `phase-close-evaluator`, with subjects `reading-reviewer-trial-2026-10-17:<sha>:arm<A|B>` so trial rows can be told apart from real closes. Each of the four PASSes on a known-bad commit had a post-close defect charged back with `record_post_close_defect`.
- **The store's first outcome data:** `phase-close-evaluator` 10 passes, 4 with a later defect, error rate 0.40.
- **A defect in the instrument itself:** outcome correlation grades only PASSes. A reviewer that returns NEEDS_WORK on a bad commit for the wrong reason counts as a catch. That happened on `b8767ebc1` and `5f6a4f15f`, both arms. The 0.40 therefore understates the specific-defect miss rate, which is 4/5 strict. I am recording this here rather than fixing `judge_validation` in this turn.

### What I would do

- **No commit gate.** At 1/5 strict, a blocking reader would not have stopped the defects we paid for, and as a gate it would cost every commit two reviews and a triage.
- **Run it non-blocking on two narrow triggers,** where it caught everything on this set:
  - a commit that adds a new module, for dead mechanisms;
  - a commit that adds a constant or rule something else in the tree already computes, for the second-implementation class.
- **How:** two Opus reviewers; a finding is filed only when both raise it; it is checked like any other finding. Score it for two weeks through `judge_validation`, and stop if the confirmed share of filed findings falls below half.
- **This is raised** to `for_the_director` as a proposal, because it is a standing spend.
- **Not tuned:** the prompt was not tuned on this set. Any future tuning must hold out new labelled cases.
