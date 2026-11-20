---
paths: ["**/*.py"]
symbols:
  - '(?i)^\s*(return\b|[a-z_]\w*\s*=[^=]).*(pence|pound|gbp|tariff|standing|price|kwh|cost|charge|bill|vat|\bdd\b|debit).*[\w)\]]\s*[*/]\s*[\w(]'
  - '(?i)^\s*(return\b|[a-z_]\w*\s*=[^=]).*[\w)\]]\s*[*/]\s*[\w(].*(pence|pound|gbp|tariff|standing|price|kwh|cost|charge|bill|vat|\bdd\b|debit)'
fired_on: '9739e7bad4'
claude_md_rows: [21]
claude_md: ["Print the numbers at real inputs"]
---
# A money formula, anywhere in Python

**Check:** print the numbers at real inputs across the real range (a table) before writing the
test, not after.

**Lineage:** `3d83edffb6` (28 Aug), GAP: origin unknown (console teaching). Fired on `9739e7bad4`,
the VAT reading of a period. CLAUDE.md lineage row 21.
The first draft scoped this to `company/billing`, `payments`, `pricing` and `saas`; it would not
have fired on golden task g08, whose formula is in `tools/`. Widened 20 Nov before any golden run.
