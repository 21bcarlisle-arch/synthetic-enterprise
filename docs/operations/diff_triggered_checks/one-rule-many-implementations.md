---
paths: ["company/**/*.py", "saas/**/*.py"]
symbols: ['(?i)\bvat', '(?i)standing_charge', '(?i)direct_debit|\bdd_']
fired_on: '9739e7bad4'
claude_md_rows: [70]
claude_md: []
---
# A rule with more than one implementation (VAT, standing charge, DD)

**Check:** `git grep -n -i` the rule's name across `company/` and `saas/`, list every implementation,
and either route them through one or confirm each agrees. A fix to one is not a fix.

**Lineage:** director, 30 Aug (`c050706d33`): the VAT rule, five implementations, a defect fixed in
one in July and live in another in August. Again 20 Nov: three VAT readings that disagreed
(`9739e7bad4`). This is the diff-readable part of CLAUDE.md lineage row 70 only; the general
interconnection review is a whole-tree question no diff names, so row 70 stays always-loaded and
this item counts no characters.
