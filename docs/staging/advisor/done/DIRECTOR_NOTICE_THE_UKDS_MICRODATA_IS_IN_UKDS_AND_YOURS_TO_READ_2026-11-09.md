**Severity:** BLOCKING · **Lane:** G_data_learning · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-NOTICE] The UK Data Service microdata is in ~/ukds/: read it under W11 and the registration pack

**Type:** NOTICE, through the advisor channel. This is the "done" that `docs/director/UKDS_REGISTRATION_PACK.md` waits for. The director's words, from chat, Mon 9 Nov:

- 13:47 GMT: "I have registered with UK data"
- 13:59 GMT: "Smart is CSV only"
- 14:09 GMT: "Is market value not useful too?"
- 15:57 GMT, his terminal output after unzipping and locking the folder:

```
8.0G    /home/rich/ukds/UKDA-6614-tab
4.8G    /home/rich/ukds/UKDA-7215-tab
462M    /home/rich/ukds/UKDA-8963-csv
18M     /home/rich/ukds/UKDA-9315-tab
432K    /home/rich/ukds/UKDA-9593-tab
```

## What is there

- **6614** Understanding Society, waves 1-15 plus harmonised BHPS (TAB)
- **7215** Wealth and Assets Survey (TAB)
- **8963** Smart Energy Research Lab statistical data, 2020-2023, Safeguarded. **CSV, not TAB.** It is offered only as CSV.
- **9315** English Housing Survey 2022-23, household data (TAB)
- **9593** Market Value Survey 2024 (TAB). **This is an extra, not in the pack.** The director kept it on the advisor's suggestion, as a possible property-value proxy for the affluence factor. **Check whether it links to 9315, or to any household file, by a shared case identifier before relying on it.** It is a different survey year from 9315, so it may not link. If it does not, record that in one line and set it aside. Do not fit anything from it alone.
- The folder is mode 700 and the files go-rwx, as the pack asks. The licence is personal and non-commercial, under the director's own account.

## The rules that hold (no change)

- **W11 as amended on 3 Nov.** Licensed microdata is read in `~/ukds/` only. No household record leaves it. Only aggregate, non-disclosive outputs leave: fitted loadings, and cross-tabs that meet each study's disclosure rule. Cite the SN and the wave.
- **Nothing from `~/ukds/` enters git, the site, a commit message, a log line or a staging doc,** not even a row in an example. `tools/ukds_microdata_refusal.py` must still refuse a bundle, a study page, a statistical-package file and any path into `~/ukds/`. Run its test once against the real folder before the first read.
- **SERL (8963) is Safeguarded.** Follow its own output-checking conditions in its documentation, which may be stricter than the others'.
- **Data standard.** A parameter fitted here is grade D where it is a direct estimate from the record. The no-circularity rule stands.

## What is asked

1. Confirm that the guard refuses each path. Then confirm that the files open, with one line per study: the files, the waves and the unit of observation. Use counts only, no records.
2. Then follow the pack's own order: the parsimony factors (precarity, affluence, life stage) first, from 6614 and 7215, then 9315 for the precarity proxy, then 8963 for the crisis cut by group.
3. This sits behind the correctness stretch and the publish. Start it after the next publish lands, or when a book is running and the seat is otherwise idle.
4. Disk: the folder is about 13.3 GB. Say if that pressures the WSL disk.
5. The director will delete the zip copies from his Windows Downloads folder. Nothing for the machine to do there.

## Done

*Seat executor, 9 Nov 2026 ~16:30 GMT. Asks 1, 4 and 5 are done, and so is the 9593 link check. Ask 2, the fits, is
handed on as continuation `ukds-parsimony-factors-from-6614-and-7215`, behind the correctness stretch as ask 3 says.
Everything below is a count. No record, value or identifier from `~/ukds/` is in this file. Probe scripts are in
`/var/tmp/ukds-probe/`, outside the repo.*

**The guard: it had three holes against the real folder, and they are now closed.** I ran `tools/ukds_microdata_refusal.py`
over all 617 real files. Each was tested by its own path, as a bundle copied into the repo, and as a loose copy.
- **By path into `~/ukds/`: 617 of 617 refused.** This held before the fix.
- **A copied SERL bundle passed whole (8 of 8 files).** The bundle pattern listed `tab|stata|spss|sas`, and 8963 comes
  only as `UKDA-8963-csv`. Any format word is now a bundle.
- **The real study pages passed when copied loose.** They are `read<SN>.htm` and `<SN>_file_information.rtf`. The guard
  knew only the older `UKDA_Study_<n>_Information.htm` name. Both real names are now refused.
- **A loose UKDS `.tab` passed** (416 of the 617 files). `.tab` is now refused. No `.tab` file is tracked in this repo.
- **Still not caught, and named in the guard's docstring:** a SERL `.csv` copied loose under its own name, and the
  documentation (PDFs, data-dictionary spreadsheets and zips). A path cannot tell a loose SERL csv from a fresh
  aggregate. That leg rests on the resolve check and on the rule that aggregates are written fresh.
- **Control:** `tests/tools/test_a_ukds_microdata_file_cannot_be_committed.py::test_the_shapes_the_real_bundles_unpack_to_are_refused`.
  Reverting each of the three changes fails it.

**The files open: one line per study (counts only).**
- **6614 Understanding Society:** 213 UKHLS files for waves a to o (15 waves), and 182 BHPS files for waves ba to br
  (18 waves). Households are keyed by `hidp` and individuals by `pidp`. Wave 1: 30,169 households and 50,994 adult
  interviews. Wave 15: 19,586 households and 32,849 adult interviews.
- **7215 Wealth and Assets:** waves 1-5 and rounds 5-8, a household file and a person file for each (18 files).
  Households run from 30,587 (wave 1) to 15,128 (round 8), and persons from 71,182 to 32,271. The case identifiers
  carry back across waves.
- **8963 SERL:** 5 CSVs, all already aggregated statistics (quantity × period × up to three segmentation variables, with a
  mean and other summaries). Daily 2020-23 has 531,180 rows. Half-hourly has 490,320 rows for each of 2020, 2021, 2022
  and 2023. It is Safeguarded, so read its output-checking conditions (`read8963.htm` and the mrdoc PDF) before any
  output.
- **9315 EHS 2022-23:** a general file and an interview file, each with 11,205 households keyed by `serialanon`. The
  two files' keys are identical.
- **9593 Market Value Survey 2024:** 13,288 dwellings, with the key plus two value fields.

**9593 does link, and only for half of it.** The study's technical notes name `serialanon` as the EHS–MVS match key.
- 5,606 of the 11,205 EHS 2022-23 households match an MVS dwelling. If the keys were drawn uniformly over their span,
  about 15 would match by chance.
- The MVS covers two EHS years: 5,792 dwellings from the 2023 survey year and 7,496 from 2024.
- The 7,496 need EHS 2023-24, which is not held. So 9593 is usable as an affluence proxy only on that half of 9315.
- Weighting follows the notes: the MVS compensates for over-sampling, so its weights must be used. Nothing has been
  fitted from it.

**Disk (ask 4): no pressure.** The folder is about 13.3 GB. WSL's root has 526 GB free of 1,007 GB (46% used).
