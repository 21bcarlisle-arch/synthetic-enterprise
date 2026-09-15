# [SEAT-RESULT] The declaration channel reads the field its own renderer writes, and the population it actually moves is 7 — not 53

**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `teach-the-class-declaration-channel-to-read-the-header-field-its-own-renderer-writes`) · **Class:** `controls_that_cannot_fail`

**Measured:** 2026-09-15, delivery seat, isolated worktree at `1d1b665c3`.

---

## What was asked, and what was decided

`background.finding_classes.declared_class_of` read one declaration form — `Belongs to
` + "`id`" + `` under `## Class registration` — and could not read the form the module's own
`render_class_document` emits on every register header line. The drawn item named three things
to establish before flipping it. All three are answered below, and two of them changed the
shape of the change.

## The parse, and why the anchor is a metadata line

Measured over all 7,879 staged documents *before* any rule was chosen:

| rule | live-root declarations it reads | unresolvable tokens |
|---|---|---|
| `**Class:**` anywhere, backticked value | 11 | 0 |
| `**Class:**` on a line starting `**`, backticks optional | **55** | 0 |
| `**Class:**` anywhere, backticks optional | 57 | 2 |

The anchor is the metadata line — the field must sit on a line that *starts* with `**`, beside
`**Severity:**` and `**Lane:**`. That is this form's analogue of the section scope, and it is
load-bearing: unanchored, the same corpus yields values like `a`, `the` and `one`, lifted out
of sentences that were *describing* a class of defect rather than joining one. A mention is
not a claim, and the module docstring's standing refusal survives the widening.

**The header field resolves its token where the section does not, and that asymmetry is a
measurement, not an inconsistency.** ``Belongs to `x` `` can only ever be an attempt to name a
class, so an unresolvable `x` there is a TYPO and is REFUSED. `**Class:**` is demonstrably a
different field wearing the same name: **130 of the 296 documents carrying it use it for
something else** — `**Class:** R15`, `**Class:** harness`, `**Class:** a coupling stated in a
comment` — and the habit is live, the most recent on 2026-09-05. Refusing an unresolvable
token here would have wedged every lane on the day it landed.

The fail-open that buys is made loud instead of silent: `check()` NAMES every live document
whose `**Class:**` field it could not resolve (`unresolvable_class_fields`, note not failure).
Measured zero on the live root today; keyed to the property, not to that answer.

**The resolve case-folds**, because the one near-miss this corpus actually holds is
`**Class:** MEASUREMENTS_THAT_MIRROR` — the family, spelled the way the register's *title*
spells it. Dropping that would have been this widening's own fail-open surviving on a shift
key. `R15`, `harness` and `test` resolve to nothing in either case.

## (1) The declarations, read one by one

**0 of 55 are contested.** No document's declared family disagrees with what its title matches;
where the title matches nothing, the declaration is the only routing there is. Read by title
against the six families, every one is plausible and most are unarguable.

**26 documents corpus-wide carry BOTH forms and 11 of them DISAGREE**, so a precedence had to be
chosen before the form could be read at all. **The section wins.** `## Class registration` is a
heading written for no other purpose; `**Class:**` shares its line with severity, lane, epoch
and atom. The consequence is the property worth having: **reading this form re-classifies
nothing that was already readable — the change is purely additive.**

## (2) The lane guard, exercised over the whole population at once

This was the question that had to be answered before the flip, and the answer is clean.

Of the 55 live declarations, **11 sit in `A_strategy_governance`** and every class register is
`H_harness`. The lane guard refuses all of them: they are named in each register's
`## Refused consolidation — out of lane, still live` section, stay in the staging root, keep
their own severity and stay drawable. **A declaration cannot route a document out of its own
lane's blocker list.** `refused_out_of_lane` went 2 → 13.

`test_a_header_field_declaration_cannot_route_a_document_out_of_its_own_lane` proves it on both
legs over one root — a guard that refuses *everything* passes the refusal leg, so the in-lane
sibling must consolidate from the identical shape.

## (3) Does reading a declaration imply consolidation? Measured, and the answer is mostly no

The item's framing was right — declaring your family and consenting to be archived are
different acts — and the measurement shows the mechanism **already separates them for 47 of
the 55**:

| outcome | n | what happens to the document |
|---|---|---|
| RECORDED — out of population | 36 | nothing at all; a landed record has no repair to argue |
| refused, out of lane | 11 | named in the register, stays live in the root |
| consolidated | **7** | listed as an instance, moved to `done/` |

So the population where the two acts are welded together is **7, not 53**, and for those seven
the ruling is explicit: *"Findings that share a class go to the class register as instances,
not to the root as documents."* Severity is not laundered — the register inherits the MAXIMUM
over its members, so both BLOCKING members keep their lane's blocker at the register.

**Decided: the implication stands, and no third state is built.** A "declared but not
superseded" state would be new machinery watching a population of seven, against the
smallest-mechanism rule — and `check()` offers no stable resting place for it anyway.

**That last part is worth recording as a fact about the mechanism, because it was measured
rather than assumed.** Rendering without consolidating is NOT a stable state: probed in a
scratch copy, `--render` alone turned 7 `UNCONSOLIDATED` failures into 14 (`RESURRECTED` +
`ARCHIVE MISSING`), because a live member is required to be listed by one rule and forbidden
to be listed by another. The only exit is `--consolidate --apply`. Anyone who reads a
declaration and stops at `--render` wedges the tree for every lane.

## The three archived instances that were filed against their own written declaration

The stranding leg found exactly three — predicted before the run, and the three predicted:

| archived document | register that held it | family it declares |
|---|---|---|
| `WORKER_FINDING_THE_PUBLISH_GATE_GRADES_A_LIVE_CONSTANT_AGAINST_A_COMMITTED_SNAPSHOT_2026-09-03` | publish_gate_and_wedge | `measurements_that_mirror` |
| `WORKER_FINDING_THE_SITE_GATE_COUNTS_AN_UNTRACKED_CONTROL_IN_ITS_OWN_GREEN_2026-08-18` | publish_gate_and_wedge | `uncommitted_and_orphaned_work` |
| `WORKER_FINDING_THE_SAME_TRUE_SENTENCE_IS_HONEST_SPELLED_OUT_AND_A_VIOLATION_ABBREVIATED_2026-08-19` | uncommitted_and_orphaned_work | `controls_that_cannot_fail` |

Each was filed by a keyword in its filename against a backticked declaration in its own header.
**They were re-filed, not allowlisted.** `_KNOWN_STRANDED_ARCHIVED_INSTANCES` is still empty —
adding three names to it would have been a narrowing that can only hide.

## The control I wrote and then deleted

I first wrote a live-root ratchet asserting no live document carries an unresolvable
`**Class:**` token. It passed. It was a trap: `**Class:** R15` is a live habit as recently as
2026-09-05, so the next daemon to write one would have reddened the whole tree for every lane —
the exact refusal I had argued against one layer down, rebuilt one layer up in a test. Deleted
before landing. The `check()` note is the honest surface: it states what it cannot resolve and
refuses nothing.

## End state

- `background.finding_classes --check`: **PASS (0 failures)**, before and after.
- `tests/background/test_finding_classes.py`: **86 passed** (was 79).
- Four new mutations (L, M, N, O), each killing a named test; plus the case-fold and its null
  control, and the lane guard on this form.
- `refused_out_of_lane` 2 → 13; live instances 0 → 7, now archived under their registers.

## What is next

`**Class:**` is overloaded — 130 documents use it for an R-rule or a prose noun, and this module
now silently ignores all of them. That is correct for this module and wrong for the corpus: two
different fields share one name, and nothing anywhere says which one an author meant. A
`**Family:**` field, or a rename of the other use, would end it. Not urgent; filed so the next
reader does not re-derive it.
