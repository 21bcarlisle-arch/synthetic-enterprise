# CLAUDE.md DECAY AUDIT — second performance, 2026-08-27

**Trigger:** director, 2026-08-27 — *"don't raise the limit, run the decay audit — a rulebook that
has to grow to hold rules nothing enforces is the problem, not the ceiling."*
**Doctrine under audit:** MAKE_IT_STICK — *"a rule lives in CLAUDE.md AND as enforced code, or not
at all; prose-only is worse than no rule."* CLAUDE.md's own instruction: *"re-run when that record
is stale."*
**Prior performance:** `CLAUDE_MD_DECAY_AUDIT_2026-08-12.md`, whose five dispositions
(MECHANISED / DELETE / STALE FACT / OUT-OF-TREE / BEHAVIOURAL) and their bars are adopted
unchanged here rather than re-invented.

---

## 0. State at audit time

| | 2026-08-12 | 2026-08-27 (before) | 2026-08-27 (after) |
|---|---|---|---|
| CLAUDE.md | 34,734 chars / 128 lines | **34,990** / 120 | **34,430** / 120 |
| Headroom (35,000) | 266 | **10** | **570** |
| `background.claude_md_integrity` | green | green | green |

**The file grew 256 characters in the fifteen days SINCE the audit that exists to stop it
growing**, and arrived at ten characters of headroom. The next rule anybody wrote would have been
refused. That is the finding that justifies the trigger: an audit performed once is an event, and
what CLAUDE.md commits to is a practice.

Some of that growth is this seat's: R18 was added the same morning (the waiter that pgrep-ed its
own command line), and it is 1,167 characters.

---

## 1. Method

Unchanged from the first performance. Every rule was read and searched for an enforcing
mechanism. A rule is **MECHANISED** only if a named module or test would FAIL on its violation;
"the doctrine is mentioned in a docstring" is not a mechanism. Where a search came back empty,
that is stated as a search.

Two automated halves ran first and both are green, so they are reported and not re-derived:

* `dangling_pointers` — every concrete path CLAUDE.md names exists.
* `inert_rules` — the `.claude/rules/` claim is live and every rule file has firing frontmatter.

**A gap in the automated half, found this turn and NOT yet closed.** `dangling_pointers` checks
backticked *paths*. CLAUDE.md also cites documents by BARE FILENAME — `MAKE_IT_STICK.md`,
`DIRECTOR_TWIN.md`, `SELF_INTERRUPT_DISCIPLINE.md`, `COMPOUNDING_WORK_FIRST.md` and others — and
those are invisible to it. All eleven checked by hand this turn resolve (three live in
`docs/staging/in_progress/` rather than `done/`, which is why a first, wrong search said they were
missing). But nothing would catch it if one were deleted tomorrow. Recorded as owed; see §5.

---

## 2. MECHANISED — verified this turn

Of 34 rule-bearing lines over 200 characters, **22 name a mechanism** (14,142 chars). Spot-checked
rather than exhaustively re-verified, since the first performance did that work and
`dangling_pointers` covers the naming half continuously.

Two were **mechanised but did not say so**, which is the same defect as prose-only from a reader's
point of view — a rule whose enforcement is invisible reads as an exhortation:

* **COUPLED TRIAD** ("no world atom reaches L3 until the gap is measured"). Enforced by
  `tests/test_coupled_triad_gate.py` (17 tests) and by the supervisor's own BUILD-draw exclusion,
  which refuses an L3 target with no registered twin or an unmeasured gap — its refusals are
  visible in every draw log. **Now named in the rule.**
* **NEVER SPAWN A BACKGROUND WAIT THAT POLLS.** Prose-only for its whole life, and MECHANISED as
  of this morning by `tools/wait_for.py` + R18 (41 tests). See §3.

---

## 3. DUPLICATION — created this morning, removed this afternoon

R18 landed at 09:0xZ and restates the prohibition that the concurrency bullet already carried.
Two statements of one rule is the shape MAKE_IT_STICK warns about from the other direction: a
reader who obeys one has no way to know whether the other adds anything.

The bullet now keeps only what is ITS OWN — the measured cost (each poll exit is a full-context
turn; 33 ran on 2026-08-03) and the instruction not to wait at all when a notification is coming —
and points at R18 for the mechanism that governs waiting when it is genuinely unavoidable.

**This seat wrote the duplication and removed it in the same day.** Recorded because the audit's
value is the record, and an author trimming his own morning's work is the cheapest possible case
of it.

---

## 4. BEHAVIOURAL, RETAINED — and made to earn its characters

The first performance retained the **two design-lens sets** (portability, scale-readiness) as
BEHAVIOURAL, and stated the standard for retained prose: *"prose that survives an audit should
still have to earn its characters."*

Measured this turn, that line was **990 characters — the single largest in the file** — despite
opening with the words "full text in their docs, not here" and then reproducing the docs. It had
grown back.

Compressed to 684 (**−306**), keeping every imperative: both lens sets and their doc pointers, all
three shared rules (design by CONSTRAINT not infrastructure; SIMPLICITY GUARD; remediation-on-touch)
and the scope wall ("no second market/product and no horizontal-scale infra in any current epoch").

**What was dropped was verified present in the docs first**, and the verification is worth
recording because it nearly went wrong: a grep for "idempotent" and "async wall" returned ZERO from
`PRODUCTION_READINESS_SCALE_ADDENDUM.md`, which would have meant deleting text that existed nowhere.
Reading the file showed **C-S2 Idempotency and deterministic replay** and **C-S3 Asynchronous wall
contracts** in full. The search terms were wrong, not the doc. Nothing was dropped that the docs do
not hold in fuller form.

---

## 5. OWED — stated, not done

* **The bare-filename citation gap** (§1). `dangling_pointers` cannot see `MAKE_IT_STICK.md` cited
  without a path. A code point plainly exists — the same function, widened to resolve a bare
  `*.md` against the docs tree — so by the doctrine's own bar this is a DELETE-or-mechanise, not a
  BEHAVIOURAL. It is mechanise. Not built this turn.
* ~~The largest line in the file is line 34 (1,351 chars).~~ **DONE, later the same turn.** It was
  listed here as owed and then paid, because leaving headroom at 177 would have meant the next
  rule anybody wrote was refused — which is the director's original complaint, reproduced by the
  audit meant to remove it. `docs/design/COMPANY_HAS_NO_ROUTE_TO_THE_REAL_WORLD.md` now carries
  the reasoning; the rule keeps all three lane answers, the capability-not-hosts axis, the
  harness clause, the not-the-boundary warning about `egress_allowlist.py`, and both enforcement
  pointers. 1,351 → 907 (**−444**).
* **A full re-verification of all 22 mechanised rules** was not performed. The first performance
  did it; this one spot-checked and relied on `dangling_pointers` for the naming half. Said
  plainly so the next reader does not inherit a stronger claim than was earned.

---

## 6. Result — measured

| | before | after |
|---|---|---|
| chars | 34,990 | **34,430** |
| headroom | **10** | **570** |
| rules naming a mechanism | 20 of 34 | **22 of 34** |
| statements of the no-polling rule | 2 | **1** |
| rules whose full text lives in a doc | — | **+1** (network isolation) |

Net **−560 characters**, from −306 (design lenses) and −444 (network isolation), less the
characters spent naming two mechanisms and pointing at this record. That trade is the one the
doctrine asks for: a rule that names its enforcement is worth more per character than one that
does not, so the audit is allowed to spend on naming and must earn it back on narrative.

**57× the headroom it started with**, and above the re-run trigger in §8 — which matters, because
a trigger the audit's own result fires immediately is not a trigger.

---

## 7. Alongside this audit: the refusal was made legible

Director, same message: *"a commit refused because the file is full should say so, not look like a
stalled session. That single confusion has cost us days of my attention across the last fortnight."*

The rule was already enforced — `test_real_claude_md_within_hard_limit` is on
`CANON_SURFACE_TESTS` and reds. But it reds as a pytest assertion inside a gate run of several
minutes, so the only symptom visible from outside is a session that has gone quiet. A refusal
indistinguishable from a hang is the R18 shape exactly, and it costs the same thing: somebody's
attention, spent working out whether anything is happening.

`tools/pre_commit_test_gate._canon_size_check` now runs FIRST, in milliseconds, and prints a banner
that says it is a refusal and not a hang, names the file and the overage, forbids raising the limit
in the director's own words, and gives the decay-audit command. The test is untouched and stays —
this is the fast reading for the human, that one is the thorough reading for the tree. Seven tests,
including that a healthy rulebook passes, that a commit not touching it is not checked, and that an
unreadable canon file fails closed.

---

## 8. Next audit

When this record is stale. Two concrete triggers rather than a date: headroom under 500
characters, or any rule added without a named mechanism.
