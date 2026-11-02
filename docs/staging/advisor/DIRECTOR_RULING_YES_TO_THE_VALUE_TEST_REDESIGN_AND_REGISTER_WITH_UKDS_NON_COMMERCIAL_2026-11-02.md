**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-RULING] Yes to the value test redesign as written; the director will register with the UK Data Service under the End User Licence, non-commercial (2026-11-02)

**Type:** RULING, through the advisor channel. The director's words, from chat on Mon 2 Nov:

- 18:38 GMT: "Yes to the value test. Register (non commercial)"

This answers the two open `for_the_director` rows raised on 2 Nov. Close both as *ruled*.

## 1. The value test redesign: adopted as written

- **Adopt `docs/design/THE_VALUE_TEST_REDESIGN.md`.**
- **Baseline:** renewals use the flat baseline at Ofgem's efficient-supplier EBIT allowance. SVT households in the new tariff-placement arm use the cap as their baseline.
- **Order:** the two one-run measurements come first:
  - the 12-draw family, testing whether £5,244 is an extreme but ordinary draw;
  - PROS-2016-0098 run alone under today's write-off rule.

  They decide whether the page's current figure can be stated at all.
- **The build** waits for the correctness exit test, as the note says.
- **The two measurements are cheap.** Draw them as soon as the publish path is clear. Do not draw them before then.

## 2. UK Data Service: the director registers, non-commercial

The registration is a real-world account and a licence agreement, so **the director does it himself**. The machine does not register and does not create accounts. Prepare for him, in one short note at `docs/director/UKDS_REGISTRATION_PACK.md`:

- **The exact datasets and study numbers** to order under the EUL: Understanding Society, the Wealth and Assets Survey, the English Housing Survey (which years), and the SERL statistical dataset (SN 8963). Also say which waves or years are needed and why. Keep the list to what changes a parameter.
- **A plain project description he can paste.** It must be honest and **non-commercial**: "an independent, non-commercial research simulation of the GB domestic energy market, used to model how household needs vary; outputs published only as aggregate statistics." If any part of the intended use would be commercial, say so in the note. Do not hide it.
- **The data-handling rules, and enforce them:**
  - Microdata never enters the git repository, which is public, never the site, and never a commit.
  - It lives in a local directory outside the repo, for example `~/ukds/`, with permissions 600 and 700.
  - Only aggregate, non-disclosive outputs leave that directory: fitted factor loadings, and cross-tabs that meet the depositors' cell-size rules.
  - Add a pre-commit guard that refuses any file from that path or with a UKDS dataset signature.
  - Cite each dataset as its licence requires.
- **How the data reaches the machine.** The director downloads the files and places them in that directory, then says "done" in chat, as with the HF token.

The licensed-microdata row is answered. Until the files land, fit one attribute at a time from published cross-tabs, as now.
