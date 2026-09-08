**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The census finds 117 where three hand passes found nine, and five of them were the wall

Continues `SEAT_RESULT_THE_SUBSTRING_RESIDUE_IS_FIVE_MEMBERS_NOT_EIGHT_AND_TWO_FIXES_WERE_MISSING_TESTS_2026-09-08.md`.
Both prior results closed with the same recommendation — *write it as an AST guard over the scan's
SUBJECT expression* — and neither turn built it. The second added a second recommendation on top:
*stop sweeping, the population is now enumerated exactly.* **That second one was wrong, and the
guard is how we know.**

## The number

`tools/substring_source_scan_census.py`, run over `tests/**/*.py`: **117 scan sites** where a test
reads a file in the tree and matches the text by substring or regex without routing it through
`tools/python_code_text.py`. Three hand passes over this same class converged on **nine**.

They are not 117 defects. Most are a test reading one named module for one token, where the prose
hazard is small and the fix is not obviously worth the churn. **The number is the finding anyway:**
the population was never enumerable by hand, and each of the three attempts to enumerate it
exhibited the class it was screening for. The claim "the class is closed on the enumerated
population" was true of the enumeration and false of the tree.

## The guard found itself wrong three times before it shipped, which is the argument for it

Recorded because a census that shipped green on its first draft is the thing this repo pays for:

1. **`ast.walk` at module scope reached every function body**, so each scan was reported twice —
   once at its own test, once at `<module>` carrying the whole file's literals as path evidence.
   That is the second hand pass's file-level verdict, in a new spelling. `_walk_own` fixed it.
2. **The taint sweep was ORDER-DEPENDENT.** `_walk_own` yields in stack order, so
   `body = src.split(...)` could be visited before `src = path.read_text()` and the chain was
   lost. The member it lost — `tests/hooks/test_pull_next_work.py` — is one I had already found by
   hand, so the census disagreed with a known answer and the known answer was right. Fixed point.
3. **"Reaches the tree" meant "spells its root as `Path(__file__)`".**
   `tests/saas/test_channel_attribution.py` reads `pathlib.Path("saas/channel_attribution.py")` —
   a bare relative literal — and `tests/hooks/test_pull_next_work.py` the same off a module
   constant. Requiring the usual spelling is the aimed-left shape a third time. Top-level packages
   are now derived from the tree, and that one clause took the census from 68 to 122.

Each was caught by running the census against members found by hand, not by reading it.

## Five of the 117 were the epistemic wall, and they are fixed

`test_module_does_not_import_company_or_saas` — **four verbatim copies** under `tests/sim/` and
`tests/simulation/`, plus its mirror with the arguments swapped in `tests/saas/`:

```python
for banned in ("import company", "from company", "import saas", "from saas"):
    assert banned not in src
```

This is the FIRST wall in CLAUDE.md, asked of a file's punctuation. Both directions are live:

- **The rule punishes its own documentation.** The most natural line to write in a world module is
  `# the wall: this module must never import company or saas` — and that comment IS the violation
  under a substring reading. `tests/saas/test_channel_attribution.py` is the sharpest case: its own
  module docstring contains the sentence *"imports nothing from the SIM"*, four lines above the
  code that enforced it, and the control was green only because the twin's path was read rather
  than the test's.
- **`from ..company.billing import engine` contains neither banned spelling** and is an import.

All five now call `forbidden_wall_imports` in `tools/epistemic_wall.py` — which already existed as
the single source of what a crossing IS, so no new module was minted. **A `seam_exempt` parameter
was written and DELETED before shipping**, refuted by its own poison round: `imported_modules`
expands prefixes, so `from company.interfaces import sim_interface` yields a bare `company` that is
not under the seam, and no exemption resting on one endpoint can tell that artefact from a real
`import company`. `crossings_at` answers the seam question from real two-ended edges. The leg that
replaced it pins the strict reading as *intended* rather than as an oversight.

**What neither reading reaches, said here and in the code rather than in a footnote:** a DYNAMIC
import. `import_module("company." + name)` is invisible to the substring list and to the import
graph alike. My own first draft of the docstring claimed otherwise; the claim was wrong and is
corrected beside itself. This fixes the false red — the failure this class has actually paid for,
four times — and the import spellings above. Nothing more.

## Mutation batteries, both run

**The probe** (`tests/architecture/test_epistemic_wall_single_source.py`, +5 legs): substring
reading instead of the import graph → **4 red** (including the prose leg, the class defect);
probe always reports clean → **3 red**; fail-open on unparseable source → **1 red**.

**The census** (`tests/architecture/test_a_control_reads_python_as_code.py`, 6 legs): single taint
pass → 3 red; drop `UNFILTERED` from the member verdict → 1; skip unparseable instead of reporting
→ 1; routing no longer clears taint → 2; bare package literals stop reaching the tree → 2; module
scope walks nested functions → 3. Six mutations, six distinct blast radii, no survivors.

The poison round runs BEFORE the floor in both files, and asserts the found set EQUALS the planted
members — the four non-member shapes are half of that one assertion, not separate quiet-on-clean
legs. The fixture failed on its first run because it had no `saas/` directory, so the census's
derived package set could not classify a bare literal: the derivation was untested until it wasn't.

## A fourth self-correction, found by another lane landing mid-turn

Kept beside the claim rather than folded into it. `9b26e6fc2` landed, and `origin/main` had moved
two commits — one of them adding `tests/tools/test_the_value_arms_pages_undriven_pointers.py`. The
floor reported its `_reading_order` as a new member. It is not one: that function reads
`site/capabilities/index.html`.

**The cause was mine and it was the file-level verdict again, arriving through the evidence rather
than through the walk.** When module-scope evidence was added so a helper reading the tree at
import time and a test searching it would be seen as one scan, it was CONCATENATED with the scope's
own — so any `.py` literal anywhere in the file made every scan in it a Python scan. The scope's own
evidence now wins, and module evidence is a fallback for a scope that says nothing.

The count is 117 either way, which is a coincidence and not a confirmation: **four rows left and
four arrived.** The four that left were false positives of exactly the kind above. The four that
arrived — `makefile_lint_scope`, `test_exemplar_preserved_verbatim_from_constitution`,
`test_robots_points_at_the_sitemap`, `test_the_published_dashboard_provenance_agrees_with_the_run_it_names`
— all report `subject=unknown`: their scope's own evidence says nothing about what kind of file is
read, and an unknown subject is a member by the fail-closed rule. Previously a stray `.md` or
`.json` from elsewhere in the same file had been enough to excuse them.

That is four self-corrections before this class was mechanised, three of them found by disagreeing
with an answer already established by hand and one by another lane's work arriving. It is the
argument for the guard, not against it.

## The floor, and what it deliberately does not hold

`docs/observability/substring_source_scan_baseline.json` — 117 rows, keyed `(path, function)`,
shrink-only in BOTH directions. A new row is the 118th instance and refuses; a stale row is a fixed
control whose exemption outlived it and must be deleted, because a dead exemption is a
pre-authorised re-entry.

**Scoped to `tests/`, which is the drawn subject and not the whole class.** `--scope tools
background` returns about thirty more, of which `tools/canon_drift_check.py` and
`tools/capability_index.py` are the two worth a reader. Those are production scanners whose subject
is largely prose claims about the tree, so "is this a member" is a genuinely different question
there and answering it by reflex would retire rows that ought to fire. A green census means *no
test control reads Python as text*, never *no scanner does*.

## What is next

- **The floor is the mechanism; the 117 rows are not a work queue.** Route a row through the remedy
  when its file is being touched for another reason and delete the row. A sweep to zero would be
  churn against controls that are mostly harmless today.
- **The `tools`/`background` population is unread.** Thirty-odd rows, two of them worth a reader.
  That is a separate item and should be drawn as one, not folded in here.
- The prior result's *"stop sweeping unless a new instance appears"* is now answered: instances do
  not announce themselves, which is what the guard is for. Nothing here needs another hand pass.
