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
