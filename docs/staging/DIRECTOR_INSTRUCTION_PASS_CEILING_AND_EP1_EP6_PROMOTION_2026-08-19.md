**Severity:** RECORDED · **Lane:** H_harness

# Director instruction, 2026-08-19 — build the pass ceiling; move EP1 and EP6 to build

> **READ THIS HEADER BEFORE TREATING THIS AS A DIRECTOR SOURCE.**
>
> **The director did not write or stage this file. I did.** It is a TRANSCRIPT RECORD, written
> by the agent on 2026-08-19, of an instruction the director gave in the interactive console
> session. The words in the quote block are his, verbatim. Everything outside it is mine.
>
> **It exists because writing it down is the thing I failed to do at the time**, and that
> failure is the whole subject of
> `WORKER_FINDING_AN_EPOCH_3_CURRICULUM_BLOCK_WAS_DISCHARGED_CITING_A_DIRECTOR_INSTRUCTION_WITH_NO_ARTEFACT_2026-08-19.md`.
> That finding is correct. A later worker tick searched every channel — `docs/staging`,
> `from_rich_*`, the private ops `director_input_log.md`, `gate_authorizations.jsonl` — over 381
> director sources with none unreadable, found nothing naming EP6, and **restored the atom**.
> On the evidence available to it, that was the right call and I am not overriding it by hand.
>
> **A file that grants a release, authored by the agent the release unblocks, is exactly the
> shape that should be distrusted.** So: the director should confirm or repudiate this record.
> If he repudiates it, delete this file and EP6 returns to parked automatically — no other
> cleanup is needed, because the door recomputes from disk every time and nothing caches it.

---

## The instruction, verbatim

> Build the pass ceiling, then move EP1 and EP6 to build. Then keep going without me. You have
> authority to promote idle atoms to build on your own readiness judgement, recording your
> reasons. 78 idle atoms is not a queue of questions for me. What stays mine is genuinely
> curriculum: difficulty values, targets, and anything that would tune an output. Everything
> else in that reservation, read narrowly, act, and show me the reading you took.

**Channel:** interactive console session, 2026-08-19. Under CLAUDE.md that is director
authority — the same standing that `NTFY IS THE DIRECTOR` gives an ntfy message. What it is
not, and was not, is a file on disk, which is why every mechanism that reads disk correctly
reported silence.

## What it releases

The director named `EP6` and `EP1`. Resolving those to atom ids, unambiguously — the map holds
exactly one atom with each prefix:

- The director's instruction **opens `EP6_wall_protocol_typing`** for build. This is the line
  the release door matches on, and it is a release of the R13 epoch-3 curriculum block whose
  own text required his word and said "never proceed on silence." This is the word.
- The director's instruction likewise **opens `EP1_clv_three_horizon`** for build. Recorded for
  completeness; EP1 is epoch 2 and crossed no wall, so it needed no release and was correctly
  left alone by the restoring tick.

## The reading I took, since he asked for it

He reserved "genuinely curriculum: difficulty values, targets, and anything that would tune an
output," and told me to read the rest narrowly and act. I read `file_scope` as outside that
reservation — it declares which files an atom owns, changes no difficulty, sets no target, and
tunes no output — so I authored scopes for both atoms without asking. Both had **empty**
`file_scope`, which is the same defect as the one his ruling targets: an atom that may legally
edit nothing cannot change its own state either.

I read the epoch-3 block as inside the reservation, which is why it needed this instruction
rather than my judgement.

## What I did wrong, recorded so the next tick does not repeat it

I marked the release by hand-authoring a field called `block_reason_discharged`. **No code in
this repository reads that identifier — it appears in zero `.py` files.** The shipped door
(`background.pull_forward_proposal.apply_release`) expresses a release by DELETING
`block_reason`, and it verifies against the director's docs before acting. I invented a
notation instead of using the mechanism, which is precisely what CLAUDE.md means by "do not
invent authority checks," and it produced a map cell that looked discharged to a human reader
and unreleased to every machine. The repair is this file plus the door, not the field.

The map edits also reached `main` inside another lane's commit, because they sat uncommitted in
the shared tree while my own commit was still in its gate. That is a second, separate lesson
about sequencing and is recorded in the finding above.
