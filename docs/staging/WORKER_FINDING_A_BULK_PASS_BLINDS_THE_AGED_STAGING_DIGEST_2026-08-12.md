# FINDING — a bulk pass over staging resets every ageing clock, and the aged digest goes blind

**Severity:** BLOCKING · **Lane:** H_harness

**Date:** 2026-08-12 · **Atom:** `OPS14_aged_staging_named_daily` · **Class:** instrument blinded by a sibling mechanism
**Status:** NOT repaired. Filed for disposition.

## Observed, with evidence

`390e8f1f2` (OPS9, the severity-field pass) inserted a `**Severity:** … **Lane:** …` line into
every finding in the staging root — **128 files changed**. Filesystem mtimes moved with them:

```
120 docs/staging/*.md now share mtime   2026-08-12 10:05
```

`tests/background/test_aged_staging_digest.py::test_the_four_documents_that_motivated_clause_5_are_flagged_aged`
is consequently RED at HEAD:

```
AssertionError: ADVISOR_FINDINGS_MONEY_CORE_CHARACTERIZATION_2026-08-06.md should be flagged
aged (>=72h untouched) but was not -- the mechanism may be looking at the wrong population
assert 'ADVISOR_FINDINGS_MONEY_CORE_CHARACTERIZATION_2026-08-06.md' in set()
```

The assertion's own hint is right about the symptom and wrong about the cause: the population is
correct, the CLOCK was reset. That document has genuinely sat undispositioned since 2026-08-06.
It is six days aged and the digest now reports it as fresh.

## Why this is BLOCKING rather than LATENT

The instrument is not merely wrong on one document — it reports **zero** aged docs across the
whole staging root, which is the fail-open direction. `OPS14_aged_staging_named_daily`
(`d14736452`) exists to name aged staging in the daily digest *unconditionally*; that mechanism
is now silently inert, and inert is indistinguishable from "nothing is aged" in the digest a
reader actually sees. A control whose only output is silence cannot be trusted to be working.

## The class

**Ageing measured from filesystem mtime is destroyed by any bulk pass.** This is not specific to
OPS9. Any future sweep — a header migration, a reformat, a licence banner, a `sed -i` across the
root, even a careless `touch` — silently resets the ageing signal for every document it walks,
and nothing anywhere goes red at the time it happens. The blast radius is proportional to how
thorough the sweep was, so the more complete the pass, the more total the blinding.

It is also self-concealing: the digest does not report "I found nothing because everything was
touched an hour ago", it just prints no aged docs.

## Recommended remedy — NOT applied

Age from **git history**, not the filesystem: the last commit whose diff touched the document's
*content*, which a bulk header insert does move but a `touch` does not — and better, the last
commit that changed anything other than the severity/lane header block. `git log -1
--format=%cI -- <path>` is the cheap version and already survives `touch`, checkout, clone and
worktree, all of which mtime does not.

R15 both ways: a doc genuinely dispositioned yesterday must NOT be flagged aged, and a doc
untouched since 2026-08-06 must be flagged even immediately after a bulk pass rewrites its
header. The second direction is the one this finding is about and the one an mtime
implementation cannot satisfy.

Queued per self-interrupt discipline, not fixed on sight. Note the interaction is bidirectional:
whoever repairs this should check that the severity pass's own re-runs do not re-blind it.
