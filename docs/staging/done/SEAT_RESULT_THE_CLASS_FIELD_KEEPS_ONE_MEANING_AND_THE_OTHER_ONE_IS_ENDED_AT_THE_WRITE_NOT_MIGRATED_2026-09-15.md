# [SEAT-RESULT] `**Class:**` keeps ONE meaning, and the other one is ended at the write — not migrated

**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `end-the-class-field-overload-two-different-fields-share-one-name`) · **Class:** `controls_that_cannot_fail`

**Measured:** 2026-09-15, delivery seat, extract of `origin/main` at `e046f92f0`.

---

## The decision

**`**Class:**` names the finding FAMILY and nothing else.** A lane goes in `**Lane:**`, which
already exists and already carries 67 live uses. An R-rule goes in `**Rule:**`. A description of
the defect goes in the prose, not in a `· `-separated header field.

**The other use is NOT migrated.** It is ended at the WRITE: `check()` now REFUSES a live-root
document whose `**Class:**` token resolves to no family, and the refusal names which field the
other meaning belongs in. The archive keeps what it wrote.

## Why the drawn item's own framing was not taken

The item offered two routes — rename this module's read to `**Family:**` and migrate the live
declarations, or rename the other use — and asked which population is larger and which authors
are still writing each. Both measurements point the same way, and neither route is the answer.

**The family use is the larger population and the only live one.** Over the 322 staged documents
carrying the field, by the date in the filename:

| | family id | something else |
|---|---|---|
| written in August 2026 | 27 | **124** |
| written in September 2026 | **166** | 5 |

The last non-family use was written on **2026-09-05**. The drawn item's premise — *"the habit is
live as of 2026-09-05"* — is exactly right about the date and reads it as a floor when it is a
ceiling: that date is where the habit STOPPED, ten days ago, against 166 family declarations in
the same month. Renaming the module's read to `**Family:**` would migrate the winning population
to accommodate a dead one.

## Why a refusal is landable, and the note's stated reason was measured against the wrong room

`unresolvable_class_fields` walks `classifiable_documents`, which globs the **live root and
nothing else**. Its docstring declined to refuse because *"`**Class:** R15` and `**Class:**
harness` are a live habit in this project (130 documents), and a gate that refused them would
wedge every lane"*. Where those 129 documents actually are:

| room | family id | something else |
|---|---|---|
| live root | 1 | **0** |
| `in_progress/` | 0 | 4 |
| `records/` | 32 | 2 |
| `done/` | 154 | **123** |

**Zero of them are in the room this function can see**, and none could ever have been refused by
it. The refusal is green on arrival on the real shared tree — verified against
`docs/staging/` itself, not a fixture: `unresolvable_class_fields` returns `[]`.

This is the ordinary shape of the thing: a fail-open kept open by a population count taken over a
superset of the control's own subject. The count was right; the room was not asked.

## What the archive and the records get, and why

Nothing. 123 are in `done/` — re-wording a consumed finding changes nothing any reader acts on
and costs a 123-file diff across every lane's evidence. 2 are `records/` preregistrations, and a
prereg edited after its answer is no longer evidence of what was predicted; that is the one
document class this repo must never tidy. 4 are parked in `in_progress/`, out of the control's
room, and they carry prose nouns (`a`, `work`, `alarm`) rather than a rival declaration.

Scoping is therefore load-bearing rather than incidental, so it has its own control over both
legs: the same token planted in the live root and in the archive, exactly one named.

## What this does NOT close, stated rather than left to be inferred

A document writing a **resolvable family id while meaning something else** — `**Class:**
controls_that_cannot_fail` on a finding about anything else — is indistinguishable from a correct
declaration by any reader, machine or human. This closes the half where the two meanings are
told apart by the token. The half where they are not is open, and it is unmeasurable: there is no
observable that separates a correct declaration from a confident wrong one.

## What landed

- `background/finding_classes.py` — `check()` moves the unresolved-field report from `notes` to
  `failures`; the message names `**Lane:**` and `**Rule:**`. Both docstrings that carried the
  superseded population reasoning are corrected beside the claim rather than quietly revised.
- `tests/background/test_finding_classes.py` — the refusal, its mutation (O), and the scope
  control over both legs. The two refusal tests were run against the pristine module and fail
  there; all 87 pass against the change.

## What is next

The `**Rule:**` field is named by the refusal and is not yet a field anything reads — it is a
destination, not a channel. If an author starts writing R-rules there at volume, that is the
point at which it earns a parser, and not before.
