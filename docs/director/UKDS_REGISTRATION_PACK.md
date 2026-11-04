# UK Data Service registration pack (for the director, 2 Nov 2026)

Your ruling of 2 Nov 18:38: "Register (non commercial)". You register; the machine does not. This note is what to
order, what to paste, how the files are handled, and two things to read before you click.

## Read first: two things the registration touches

1. **W11 says no household data enters the system.** Canon W11: "Published aggregates and cross-tabs only. The
   ratified pitch stakes a public claim that no household data has entered the system; that must stay true." EUL
   files are de-identified survey records, but they are household-level records, so once they are on this machine
   that public claim is no longer true as worded. I have raised this as one `for_the_director` row
   (`your-2-nov-ruling-to-register-with`) with a recommendation. **Registering is safe either way. Do not put the files on
   the machine until you have answered that row.**
   *(3 Nov: answered yes. W11 now reads "No personal microdata in the repository, the site, the world or the company.
   Licensed, de-identified survey microdata may be read on this machine outside the repository, under its licence, and
   only non-disclosive aggregates ... leave it." The pitch claim reads "no household record leaves a licensed local
   store". The files still wait for a control that refuses any commit carrying them, proven to fire.)*
2. **Is this use commercial?** The UKDS End User Licence lets you use the data for non-commercial purposes and asks
   for permission for anything commercial. Today Poesys is a simulation: no customers, no revenue, nothing sold. But
   the mission says it is "creating enterprise value", and M4 says the enterprise value is the method. If the fitted
   factors later become part of a method that is sold or used to trade, that later use would be commercial and would
   need the UK Data Service's permission first. The description below says what the work is now. It does not claim
   the project will never be commercial, because that is not known.

## What to order (all End User Licence; each study number checked on the UKDS catalogue 2 Nov)

| Study | SN | Why it changes a parameter | Which part |
|---|---|---|---|
| Understanding Society: Waves 1-15, 2009-2024 and Harmonised BHPS | **6614** | Income, tenure, household type, age, arrears and energy payment method on the same households. It is the only source that can fit the precarity, affluence and life-stage factors the 30 Oct parsimony ruling keeps, and test "age outweighs income" (corpus page 4) on one record rather than across tables | The recent waves, which cover the 2022-23 crisis, and whichever waves carry the risk-attitude question (to confirm from the study's documentation once you have access) |
| Wealth and Assets Survey, Waves 1-5 and Rounds 5-8, 2006-2022 | **7215** | Liquid savings by age and income: the size of the cash-flow need and the headroom that sets consumption elasticity. Today that is an assumption with a range | Rounds 7-8 (2018-2022) |
| English Housing Survey, 2022-2023: Household Data | **9315** | Tenure, household type and payment method on one record, which tightens which observable a supplier could use as a precarity proxy | That year only. The 2022 housing stock data is Special Licence (SN 9316), so it is **not** on this list |
| Smart Energy Research Lab: Statistical Data, 2020-2023 (Safeguarded) | **8963** | Smart-meter consumption by household attribute through the crisis: how much each group cut its use, which the price-sensitivity page could only state from survey answers | The whole study. It is already aggregated, not per-home |

Nothing else. The SERL per-home Observatory needs a university partnership and is not recommended.

## Project description to paste

> An independent, non-commercial research simulation of the GB domestic energy market, used to model how household
> needs vary. The data will be used to estimate a small number of aggregate relationships (for example, how income,
> tenure, age and household type relate to difficulty paying energy bills). Outputs are published only as aggregate
> statistics that meet the depositors' disclosure rules. No record-level data is shared, published or stored in any
> repository.

## How the files are handled

- They live in `~/ukds/`, outside the repository: directory permissions 700, files 600. They never enter git, the
  site or a commit. The repository is public.
- Only aggregate, non-disclosive outputs leave that directory: fitted factor loadings, and cross-tabs that meet each
  depositor's minimum cell size. Each is cited as the licence requires.
- A pre-commit guard refuses any file from that path or carrying a UKDS dataset signature: a download-bundle
  directory (`UKDA-6614-tab`), a study information page, or a `.dta`/`.sav`/`.por`/`.sas7bdat` file
  (`tools/ukds_microdata_refusal.py`, wired into `tools/git-hooks/pre-commit`).
- You download the files, put them in `~/ukds/`, and say "done" in chat, as with the HF token.

Until then, every factor is fitted one attribute at a time from published cross-tabs, as now.
