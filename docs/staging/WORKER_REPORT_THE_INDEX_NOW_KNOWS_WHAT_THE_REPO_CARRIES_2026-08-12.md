# [WORKER-REPORT] The index now knows what the REPO carries, and G6 asks for disclosure instead of a phrasing (2026-08-12)

**Severity:** INFO · **Lane:** H_harness
**Closes:** `WORKER_FINDING_THE_INDEX_READS_THE_WORKING_TREE_2026-08-09.md` (both findings)
**Advances:** AO1_capability_index, AO2_write_time_reuse_gate
**Drawn by:** RUNG 1c blocking-finding lane precedence (OPS12 clause 3) — the oldest live BLOCKING
finding in lane H_harness.

---

## Finding 1 — an untracked file could read `wired`

**Was.** `build_rows` derives every row from a filesystem WALK, so a module `git ls-files` does not
carry was indistinguishable from a committed one. Three composition roots really did read `wired`
with five callers each while HEAD held none of them: the artefact whose whole job is answering
"do we already have this?" was answering about ONE WORKING TREE, and on a fresh checkout the honest
answer was no.

**Now.** `tools/capability_index.py`:

* `tracked_paths()` — the git oracle as a set, deliberately NON-raising (unlike
  `tracked_python_files`), because `build_rows` runs against scratch trees that are not git
  repositories at all (`tools/orphan_ratchet.py` builds an index of one). "Could not tell" returns
  `None`; it never returns "tracked".
* `_mark_trackedness()` stamps `tracked: true|false|null` on every row and restates the status:
  a row git does not carry is `untracked`, **overriding** `wired`/`entrypoint`/`orphan`. Local
  callers do not put a file in the repo. `unparsed` is left standing, and check 5 keys off the
  `tracked` FIELD rather than the status, so the two findings cannot mask each other.
* Integrity check **5 UNTRACKED ROW** — fails `--check` on any such row.
* Integrity check **6 TRACKEDNESS UNRESOLVED** — fails on `tracked: null`. Without it, check 5
  would silently stop firing exactly when git stopped answering (an unavailable check is a FAILED
  check).

**The vacuity trap the finding itself flagged, and how it was answered.** A clean tree holds ZERO
untracked capability modules, so a guard asserted against the live repo would pass without ever
running. Every new test SEEDS one. Proven on the LIVE tree, both directions:

```
$ cat > company/billing/_seeded_untracked_probe.py <<'EOF' ... EOF
$ python3 tools/capability_index.py --check
  UNTRACKED ROW: 1 row(s) have no committed file behind them, so a fresh checkout does not
  have them and the index is answering for one working tree:
  company/billing/_seeded_untracked_probe.py                                        rc=1
$ python3 tools/capability_index.py --find "seeded untracked probe"
  company.billing._seeded_untracked_probe    untracked   Seeded probe ...
$ rm company/billing/_seeded_untracked_probe.py && python3 tools/capability_index.py --check
                                                                                     rc=0
$ python3 tools/capability_index.py
  CAPABILITY INDEX: 914 rows -- 561 wired, 64 entrypoint, 267 orphan, 0 untracked, ...
```

**A fixture the new check caught.** `test_a_no_consumer_claim_holds_when_the_package_really_has_no_door`
wrote its subject module without ever `git add`-ing it, so the register was ruling on a module the
fixture repo did not carry. Corrected in the fixture (the register rules on what the REPO holds),
not by narrowing the check.

## Finding 2 — G6 refused a phrasing, not a non-disclosure

**Was.** `_NOTHING_CLAIMED` is a regex for `none|nothing|no existing|...` **anywhere** in the INDEX
field. Two honest records were refused by it: one naming three neighbours and saying *"each
considered, none extended"*, one naming its three matches and saying *"nothing else composes this"*.
Both are the MOST informative form of the record and therefore the most likely to trip.

**Now.** `tools/write_time_gate.py::_guard_index_contradiction` gained two exclusions:

1. **The record's own subject.** A row for the module being added is the file in the commit, not
   prior art. `explain`'s `_index_matches` already dropped it; G6 was the half that did not.
2. **A record that NAMES a match.** `names_a_match()` asks the structural question — did you
   disclose? — instead of the lexical one. A dotted name, a repo path, or a distinctive final
   segment (≥4 chars, word-boundary anchored) all count.

**The false negative this could have bought, and the guard against it.** `disclosure_text()`
subtracts the QUOTED SEARCH TERMS before looking for names. Without that, searching `"dunning"`
would count as disclosing `company.billing.dunning` and G6 would be gutted while looking fixed.
`test_g6_still_fires_when_only_the_searched_term_resembles_the_match` is that direction.

**The wall kept.** G6 is the only guard with an INDEPENDENT source (R15 anti-tautology), so
weakening it into never-fires is the worse failure. Both directions are proven:
`test_g6_contradicted_by_the_live_index` still refuses a record that discloses nothing, and the
mutation table entry `("G6 index contradiction", ...)` re-proves it after every edit.

**A prose trap closed by mechanism.** `--explain` prints a template naming the live nearest match;
under the old regex, pasting it and writing "none of these fit" was itself a refusal. It now passes,
because the record names what it found. The standing advice "keep the word none out of the INDEX
field" is retired — it was a workaround for the defect.

---

## Evidence

* `tests/tools/test_capability_index.py` — 5 new tests + 1 fixture correction (seeded untracked
  module with a real caller; the committed direction; unparsed×untracked not masking; fail-silent
  `tracked: null`; a non-git tree still deriving).
* `tests/tools/test_write_time_gate.py` — 5 new tests (both refused instances now pass, the
  searched-term false negative still refuses, the subject's own row is not prior art, and a
  unit-level guard on `names_a_match` against short/glued tokens).
* Live CLI evidence quoted above, seeded and cleaned.

**Filed by:** the scheduled worker tick that drew the blocker.
