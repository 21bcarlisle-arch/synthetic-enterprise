**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `AO1_capability_index`

# Citing a module you rejected makes the index call it wired — so the reuse convention manufactures false callers

`tools/capability_index.py` decides a module has a caller two ways: an import edge, or its
repo-relative path appearing **anywhere in another module's text** (`_path_references`). The second
rule exists for a real case the import graph cannot see — `subprocess.run(["python3", "tools/x.py"])`
— and the index says so in its own docstring.

It cannot tell that case from a **citation**.

## Observed-with-evidence, on myself, within the hour

Building `company/analytics/household_value_share.py` (atom `A47`), the AO2 reuse convention
requires the INDEX docstring to name the near-miss modules that were checked and rejected. I named
one the obvious way, by path: `company/compliance/fair_value_assessment_register.py`. It has no
importer and no entry point, and it was one of the 241 company-side orphans ruled `unhooked`.

The next run of `python3 tools/capability_index.py --dispositions` said:

> STALE DISPOSITION: `company.compliance.fair_value_assessment_register` (line 207) is now wired,
> not an orphan — delete the row; a ruling kept past its subject is how the count stops meaning
> anything

Nothing was wired. A docstring mentioned it. The orphan count fell by one, its ruling was declared
stale, and the gate asked me to delete the row — which would have removed the only record that the
module is unreached.

## The class, and why it is worse than one bad row

**The reuse convention and this control are in direct conflict.** AO2 requires a new module to name
the candidates it examined and rejected. Doing that correctly, by path, converts each rejected
candidate from an orphan into a caller-bearing module. **The better the reuse discipline, the more
false wiring the index reports** — and the modules most likely to be cited as near-misses are exactly
the unreached ones, because that is why nobody found them.

The register's own §1 already measured this blindness for NON-Python files and ruled correctly on it:
*"258 hit — and all of them are documentation … A doc that mentions a module is not a caller."* The
same sentence is true inside a Python docstring and the index does not apply it there.

## How many, measured, and the number I first got wrong

**19** company/saas modules today have no import caller and no path reference outside a docstring or
comment — wired by prose alone.

My first measurement said **77**. It masked *every* string literal, which also masks the
`subprocess.run(["python3", ...])` case the heuristic exists for, so it counted genuine launch
references as prose. Masking only DOCSTRINGS (module/class/function first-statement) and COMMENTS
gives 19. The 77 is recorded here because a four-fold overstatement that survived to a finding would
have been the more expensive defect.

**A further 58** are named only inside non-docstring string literals — registry tables such as
`company/compliance/obligations_register.py` and `company/interfaces/internal_seams.py`, which hold
module paths as data the program reads. Whether a registry entry is a "caller" is a genuine judgement
call, and **no number is claimed for them here**. That distinction is the whole repair: two of the
three cases are decidable and one is not.

## Why this is LATENT and not a same-day fix

Making `_path_references` skip docstrings and comments would reclassify 19 modules as orphans at
once. Each then needs a disposition ruling, and `--dispositions` refuses a commit while any lacks
one — so the "fix" wedges every lane until 19 judgements are written. That is the right work and it
is not a side effect of somebody else's commit.

**The instance is already repaired**: this module's docstring now cites rejected candidates by
DOTTED MODULE NAME, and says why. That stops the bleeding and fixes nothing.

## WORK THIS CREATES

1. **`AO1_capability_index`** — teach `_path_references` the three cases: a path in executable code
   or a non-docstring string is a candidate caller; a path in a **docstring or comment** is a
   citation. R15 mutations both ways: a synthetic `subprocess.run` must still register, a synthetic
   docstring citation must not.
2. **`KNIFE4_orphan_disposition`** — rule on the 19 modules the fix exposes, in the same change, so
   the gate never sees an unruled orphan. Nineteen judgements, not a bulk stamp: the register's own
   §0 says auto-stamping empties the ruling of content while leaving the count complete.
3. **The AO2 convention needs one line**: cite rejected candidates by dotted module name. Until (1)
   lands, every writer following the reuse rule correctly damages the orphan census.
4. **Open, and deliberately unanswered here:** is a module named in a registry table a caller? 58
   modules turn on it. It is a question about what `obligations_register` and `internal_seams` ARE —
   documentation or dispatch — and it should be answered by reading those two files, not by choosing
   whichever definition makes the count look better.

## Still live
