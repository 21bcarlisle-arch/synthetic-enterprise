---
paths: ["**/*.py"]
symbols: ['(?i)\brefus', '(?i)\bguard', '\bdefer', '\bhold\b', '(?i)\breject', 'sys\.exit\([1-9]']
fired_on: '1b98c83609'
claude_md_rows: [23, 24, 25, 27]
claude_md: ["A mutation that does not fire", "When a branch exists to be taken rarely", "Key a control to the property", "Write refusals that name their reason"]
---
# A guard, a refusal, or a control over one

**Check:**
1. a branch taken rarely: assert it CAN be taken before asserting what it does; one control over
   the whole partition (`assert plan["restart"] and plan["defer"] and plan["hold"]`), not a leg per branch;
2. key the control to the property, not to today's answer: it must go red when the claim rots, and
   stay green when the code becomes more honest;
3. a refusal names its reason in its own text;
4. a mutation that does not fire is a missing test or an equivalence: say which.

**Lineage:** `1b98c83609` (4 Sept): the same trap three times in one afternoon, a guard refusing
everything passing every refusal test. R15, CONTROLS_THAT_CANNOT_FAIL (`a0f1a8853a`, 13 Jul).
Rewrite notes, 28 Aug: a probe keyed reachability to a constant's spelling. CLAUDE.md lineage rows
23, 24, 25, 27.
