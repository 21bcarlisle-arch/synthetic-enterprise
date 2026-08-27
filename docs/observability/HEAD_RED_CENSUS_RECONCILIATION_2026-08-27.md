# The 33 are closed, and the 33 and the 28 were never the same population — 2026-08-27

Answering `docs/staging/DIRECTOR_CONSOLE_2026-08-27.md` (05:39Z): *"33 newly failing tests at HEAD
since 03:16Z."* He reported a number and the machine answered him with commit messages. This is the
number.

Every verdict below is a RE-RUN against a clean checkout of HEAD, built by
`tools.head_green_census.head_subject_checkout` — the census's own subject builder, not a second
implementation of "a checkout of HEAD", and not the shared working tree.

**Subject:** `a7c78de18` · **re-run:** 2026-08-27, 31 passed / 1 xfailed in 42.48s.

---

## The answer, in three lines

1. **All 33 are closed at HEAD.** 31 pass, 1 is `xfail(strict=True)` by design, 1 was renamed at
   08:26 and passes under its new name.
2. **The 33 and the 28 counted different things.** The 33 was TREE-WIDE at 03:16Z; the 28 was
   `tests/tools`-ONLY, measured six hours later. They overlap on 18 node ids and neither contains
   the other — so `33 − 28 = 5` was never a count of anything, and there were never "five left".
3. **"Newly" did not mean "since yesterday".** Measured against the previous census, 23 of the 33
   were genuinely new and 10 were carried over — and 20 of the previous day's reds had been fixed
   and went unreported.

---

## Where each number came from

| | the 33 | the 28 |
|---|---|---|
| producer | `tools/head_green_census.py`, systemd `head-green-census.service` | the `tests/tools` sweep, this seat |
| subject | clean checkout of `15c2bec75` | clean checkout of `49387e0ce` |
| clock | started 03:33:20 BST, verdict 04:16:43 BST = **03:16:43Z** | ~08:50 BST |
| scope | `tests/` tree-wide, `-m "not operational and not join_report_only and not scale_report_only"`, 8 heavy `--ignore`s | `tests/tools` only |
| record | **journald + one NTFY page. Nothing in the repo.** | three commit messages |

`15c2bec75` was HEAD when the service started (committed 03:30:04 BST; the next commit, `24ef65af0`,
did not land until 04:48 BST). **Nineteen commits** separate that subject from the one re-run here.

The sweep closed its 28 across `3e3105468` (15 of them), `fd18cda4c` (to 27 of 28) and `d01f1cb38`
(the 28th). Of the census's 33, **18 are in `tests/tools`** and 15 are not — the 15 were closed by
the same morning's other commits, which is why the sweep's own count could never have accounted for
them.

### The one line, so the next census does not repeat it

> A tree-wide census count and a directory-scoped sweep count are not on the same axis. Subtracting
> one from the other produces a number with no referent. Say the SCOPE and the SUBJECT SHA beside
> every red count, or the count cannot be reconciled by anyone, including its author.

---

## Each of the director's 33, at HEAD `a7c78de18`

The node ids are taken from the census's own journal output, not retyped.

**PASSED (31).**

`tests/architecture/test_no_committed_store_claims_an_unlanded_falsifier.py` —
`test_every_declared_honest_absence_is_still_absent_and_still_silenced`,
`test_no_committed_store_credits_a_falsifier_the_repository_does_not_have`.
`tests/architecture/test_no_committed_store_claims_an_unlanded_symbol.py` —
`test_the_symbol_population_is_not_vacuous`.
`tests/background/test_defect_backlog_draw.py::test_rung_is_in_authorized_set_enumeration`.
`tests/background/test_publish_gate_stub_roots_are_repo_shaped.py::test_every_module_that_drives_the_gate_uses_the_shared_root_shape`.
`tests/background/test_seat_guard_daemons.py::TestStructuralLock::test_every_main_entrypoint_is_guarded`.
`tests/background/test_suppression_lint.py::test_live_tree_passes`.
`tests/saas/test_drawn_customer_shape_class.py::test_the_premise_holds_drawn_records_really_do_lack_those_fields`.
`tests/simulation/test_phase27a_ic2_customer.py` — all five (`test_c_ic1_and_c_ic2_both_present`,
`test_c_ic2_eac_derived_in_simulation`, `test_c_ic2_in_elec_customers`,
`test_elec_customers_count_includes_both_ic`, `test_total_elec_eac_includes_c_ic2`).
`tests/simulation/test_phase_b_life_events.py::test_lowgated_demographic_events_hold_on_real_roster_seed42`.
`tests/tools/test_bill_correctness_addendum_defect4.py::test_billed_total_never_less_than_gross_margin_for_any_real_customer_year`.
`tests/tools/test_capability_index.py::test_the_live_register_rules_on_every_live_orphan`.
`tests/tools/test_evidence_pages.py::test_the_record_store_actually_supplies_the_citations`.
`tests/tools/test_generate_customer_sample.py::test_business_customer_home_type_is_the_business_premises_type`.
`tests/tools/test_generate_customer_sample_population_seam.py` — all three.
`tests/tools/test_generate_hh_data_population_seam.py` — all three.
`tests/tools/test_pre_commit_gate_store_surface.py` — all three.
`tests/tools/test_site1_proof_citations_resolve.py` — all three.
`tests/tools/test_site_structure.py::test_customer_json_accounts_present`.

**XFAIL, by design, and CLOSED rather than owed (1).**
`tests/tools/test_year_spotlight.py::test_crisis_year_2022_worse_than_2020` — `xfail(strict=True)`
against `docs/staging/done/WORKER_FINDING_THE_2022_CRISIS_IS_NOT_VISIBLE_IN_DOMESTIC_BILL_SHOCK_2026-08-27.md`.
Three independent denominators agree 2022 is not the worse year, and the reason is that a capped
domestic tariff cannot pass a wholesale spike through at the moment it happens. Not reopened here.

**RENAMED — the node id is gone, the coverage is not (1).**
`tests/architecture/…_falsifier.py::test_MUTATION_the_word_only_predicate_fires_this_contradiction_on_the_real_corpus`
became `…::test_MUTATION_the_word_only_predicate_MISREADS_the_spelling_this_control_was_built_for`
in `71cdda78a` (08:26 BST) — a pure rename, verified in that commit's diff, and green at HEAD.

---

## What "newly" actually meant, and why it was not what it sounded like

`head_red_baseline.json` has carried `"known_red": []` since 2026-08-12. `new_red` is
`failures − baseline`, so with an empty baseline **every red reads as new** and "33 newly failing"
means, exactly, "33 failing". Nothing in that page was a claim about the last thirteen hours.

The day-over-day delta the phrase implies is computable — but only by diffing two journald runs,
which is what was done here:

| against the 2026-08-26 census (30 reds) | count |
|---|---|
| genuinely new on 2026-08-27 | **23** |
| carried over from 2026-08-26 | **10** |
| red on 2026-08-26, fixed by 2026-08-27, never reported as fixed | **20** |

---

## Three defects this reconciliation exposed — queued, not fixed here

Named so they are not re-discovered. None is fixed in this commit; fixing on sight is the treadmill.

1. **The census's red list exists nowhere in the repo.** It goes to journald and to one NTFY page.
   Reconciling the director's number required `journalctl`, which is not a repo artefact and fails
   the reconstruct-from-repo-alone test the operational layer is held to. A run RECORD is not a
   baseline, so writing one does not breach the anti-laundering property — but
   `tests/tools/test_head_green_census.py::test_nothing_in_this_module_writes_the_baseline` forbids
   `write_text` and `json.dump(` anywhere in the module body, so its scope is wider than its own
   claim and it would red on a record-write too. Both halves need moving together.
2. **"Newly failing" is measured against a baseline that has been empty for a fortnight**, so the
   word does no work and the alarm cannot distinguish a fresh regression from a fortnight-old one.
   The census has no memory of its own previous run.
3. **A renamed test leaves the census silently.** Node ids are the key, so a rename neither passes
   nor fails — it vanishes, and a red that disappears by rename is indistinguishable from a red that
   was fixed. One of the 33 was exactly this.
