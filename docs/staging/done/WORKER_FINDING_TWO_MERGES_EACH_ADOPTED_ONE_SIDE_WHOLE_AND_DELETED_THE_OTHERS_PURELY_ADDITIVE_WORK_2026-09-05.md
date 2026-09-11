**Severity:** LATENT — both instances are repaired at `90917a168`; the class hazard is live and
nothing in the tree can see it · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0
delivery · **Class:** `uncommitted_and_orphaned_work`

# Two merges each adopted one side whole and deleted the other's purely additive work

Filed 2026-09-05 by the autonomous worker. The scheduled tick drew the Lane 0 direction "split the
RED TEST bucket in `tools/commit_refusal_attribution.py` by failing node id". **That work had
already been built, tested and committed — and it was not in the tree.** Neither was the analysis
it was built on. This finding is about how both left, because the leaving is the reusable part.

## 1. What was measured

| commit | what it is | module lines | `subject_report` | RED TEST split |
|---|---|---|---|---|
| `4ce048219` | lane A: the subject analysis | 752 | yes | — |
| `58b18f4a1` | lane B: ordering + masking, **branched before lane A** | 658 | no | — |
| `381dfe625` | merge of B with a parent containing A | 624 | **gone** | — |
| `57201d10b` | the drawn Lane 0 work, on top of A | 875 | yes | **yes** |
| `f81333756` | merge of `57201d10b` (first parent) with origin | 624 | **gone** | **gone** |

`58b18f4a1`'s parent is `2295fa896`, not `4ce048219` — the two lanes are parallel, and
`git log -- <path>` history simplification makes them read as one line of descent. So the subject
analysis was never *edited away*; it was dropped by a merge, twice.

**`381dfe625` — "adopt the rival lane's ordering analysis as the single definition".** The
judgement in it is right and well argued: two lanes had centralised into one file, their ordering
machinery genuinely had to collapse to one definition, and the rival's peak-rank test is better
than its own on the point that decides it. The message documents deleting its OWN ordering code and
*keeping* the subject guard and `masking_exposure`. It says nothing at all about
`subject_report` / `subject_verdict` / `SUBJECT_EXTRACTORS` / `_subject_at` — 128 lines present in
its second parent and absent from its result. `git merge-base --is-ancestor 4ce048219 05342b9a2`
is true, so that code was in the merge's input.

**`f81333756` — "thirty-five commits, nine conflicts, each side chosen by running it".** Its FIRST
PARENT is `57201d10b`. Origin's copy of both files was taken whole, so the RED TEST split died
**11 minutes after it was committed**, and the subject analysis died a second time.

## 2. Why nothing noticed, either time

**The losing side was purely additive; the winning side was a rewrite.** `4ce048219 → 57201d10b`
is `+129/−3` on the module. "Take theirs" is the correct call on the contested functions and the
wrong call on the file, and at merge time nothing distinguishes those two scopes.

**The tests left with the code.** No control went red, because the 15 controls covering the deleted
analysis were in the same deleted region of the same test file. The suite reported 28 green before
`381dfe625` and 28 green after, while 15 controls walked out of it. A suite cannot notice its own
subtraction: green means "what remains passes", never "what should be here is here".

**The commit message is not a control.** Both merges are honest about the disagreement they
settled. Neither is *wrong*; both are silent about a deletion they did not know they were making,
and silence is what a reviewer reads as "nothing else happened".

This is the third form of the same shape already in the record — a lane's work surviving the merge
that mentions it and dying in the merge that does not. It is cheap to detect and was expensive to
find: it took a scheduled tick drawing work that was already done.

## 3. Disposition — repaired, and what is NOT built

**Repaired at `90917a168`** (verified receipt, tree `c51d77eda`, gate-rc 0, on `origin/main`).
Origin's work is kept in full — its `ordering_report` is verbatim what lane A wrote and what
`381dfe625` chose (diffed function by function: identical), plus lane B's `masking_exposure`, plus
the exit-2 refusal when the log copy holds no named outcome. The additive blocks are restored on
top, verbatim from the commits that carried them. 43 tests pass (28 origin + 15 restored), and the
measurement reproduces the landed figures exactly.

**No mechanism is built here, and that is deliberate.** The direction's pre-registered action on
the RED TEST question was NOTHING, and the same discipline applies to this: a control written today
would be keyed to today's two instances.

**The candidate remedy, recorded for whoever draws it, not built:** at merge time, diff the
merged file's top-level symbol set against the UNION of both parents' symbol sets, and refuse when
a symbol present in either parent is absent from the result and unnamed in the merge message. It is
cheap (one `ast` walk per changed `.py`, three trees), it is keyed to a property rather than to an
answer, and it fails in the right direction — a deliberate deletion is one sentence in the message.
The cost is that it fires on every genuine consolidation, which is exactly the case both these
merges were; whether that is a tax worth paying is a judgement for the seat, and it needs the base
rate of consolidating merges before it can be answered.

## 4. What this changes for a reader now

`git log -- <path>` reads as a single line of descent across parallel lanes; it is not evidence
about where code went. A landed commit is not evidence its content is at HEAD. **When a doorbell
draws work whose own commit message says it is done, check the content at HEAD before rebuilding
it and before releasing the claim** — here the claim had already been released, the commit was real,
and the work was gone.
