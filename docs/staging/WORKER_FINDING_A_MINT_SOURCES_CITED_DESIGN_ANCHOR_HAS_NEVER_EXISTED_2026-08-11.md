# [WORKER-FINDING] The mint-source's cited design anchor has never existed, and the standing architecture doc says the opposite (2026-08-11)

**Severity:** LATENT · **Lane:** H_harness

**Found:** 2026-08-11, while executing step 1 (the mint) of
`DIRECTOR_INSTRUCTION_QUERYABLE_PROJECTIONS_2026-08-10`.
**Disposition:** QUEUED as a finding; the mint PROCEEDED (see "Why this did not block"). Not fixed on
sight per SELF-INTERRUPT DISCIPLINE.
**Rank:** backlog — but it must be read before G12's DISCOVER/FRAME, which is where it is due.

## Observed, with evidence

The instruction sequences itself on a design it says has "sat in canon since July":

> the full design has sat in canon since July: docs (project) DATA_LAKE_OBSERVABILITY.md — "the data
> can't be queried, filtered, visualised, or explored… a real company would have a data warehouse."

**That file has never existed in this repository.** `observed-with-evidence`:

```
$ find . -iname "*data_lake*" -not -path "./.git/*"        # (no output)
$ grep -rl "DATA_LAKE_OBSERVABILITY" docs/
docs/staging/DIRECTOR_INSTRUCTION_QUERYABLE_PROJECTIONS_2026-08-10.md   # the instruction itself
$ git log --all --oneline --name-only | grep -i data_lake
e9f5996e6 [DIRECTOR-INSTRUCTION][ADVISOR-STAGED] QUERYABLE PROJECTIONS - the July DATA_LAKE...
```

The only hit across **all** branches and all history is the instruction's own commit subject line —
not a file path. The quoted sentence ("can't be queried, filtered, visualised, or explored") also
appears nowhere else in `docs/`. So the citation resolves to nothing: this is the
declaration-without-referent class, at MINT-SOURCE rate rather than at map-record rate
(cf. `WORKER_FINDING_A_MINT_DECLARES_STORE_FIELDS_IT_NEVER_WRITES_2026-08-10`).

## The sharper half: the repo's standing architecture doc rules the opposite

`docs/architecture/SAAS_COVERAGE_MAP.md:71` classifies this exact capability as **bucket A,
eliminated by architecture**:

> | BI / data warehouse (Snowflake/dbt/Looker) | … | none needed -- `tools/generate_dashboard_data.py`
> and friends compute board-grade analytics directly off the operational data model, no separate
> warehouse/ETL | A |

That row is not incidental prose. `tools/generate_saas_coverage_data.py` computes the headline
elimination metric *from* these rows (5 of 22 eliminated, 22.7%) and checks the claims against the
real filesystem, so the row is load-bearing for a published figure. A new warehouse-shaped atom and a
published "eliminated by architecture" claim cannot both be right.

## Why this did not block the mint

Per THE STANDARD and NEVER_ASK_WITHOUT_RECOMMENDING, a missing citation is not a wall — none of the
four reserved classes is touched. The instruction is **self-sufficient**: it states the design in its
own text (derived from committed truth; rebuilt-not-mutated each publish; never a second source of
truth; v1 scope explicitly delegated to the worker). So the mint proceeded with the **instruction
text itself recorded as the anchor of record**, and the discrepancy written into `G12`'s own `name`
field where DISCOVER/FRAME cannot miss it, rather than into a doc nobody re-reads.

**Recommendation (taken):** mint now, reconcile at DISCOVER. The reconciliation is a real fork and
belongs to whoever draws G12:

- **either** the SAAS_COVERAGE_MAP row is restated (the elimination claim was about an *external
  ETL warehouse*, which an internal rebuilt-from-truth projection store genuinely is not) — in which
  case the published 22.7% figure moves and must move deliberately, not silently;
- **or** G12's scope is narrowed to internal queryability that leaves the row true as written.

The wrong outcome is the third one: G12 lands, the row still says "none needed", and the site keeps
publishing an elimination percentage that its own repo contradicts.

## The class worth an atom

Two mint-sources in two days have cited a referent that does not exist. A mint-source is the one
document that is, by construction, never gate-checked — it lives in `docs/staging/`, is prose, and
its citations are resolved by a human reader who is usually the same agent that will build the atom.
The cheap mechanism is the one already used elsewhere in this repo: a scanner that resolves every
`docs/...md`-shaped citation in a staged `[DIRECTOR-*]` document against the filesystem and reds on a
miss — the same shape as `derived_artefact_register`'s existing referent checks. Filed as a
candidate, not built.
