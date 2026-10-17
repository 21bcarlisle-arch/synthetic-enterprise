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
