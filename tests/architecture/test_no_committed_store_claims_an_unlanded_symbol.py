"""A committed atom STORE that names a symbol as BUILT must name one its own file_scope carries.

THE SYMBOL HALF of the `uncommitted_and_orphaned_work` class. The other three are

    tests/architecture/test_no_committed_discharge_cites_an_unlanded_falsifier.py  (markdown path)
    tests/architecture/test_no_committed_store_claims_an_unlanded_falsifier.py     (store path)
    site/test_the_site_lane_runs_no_untracked_control.py                           (SITE)

and the finding that opened this one is
`docs/staging/WORKER_FINDING_A_STORE_NOTE_CLAIMING_BUILT_IS_NEVER_CHECKED_AGAINST_ITS_OWN_FILE_SCOPE_2026-08-18.md`.

WHY A FOURTH HALF EXISTS. All three controls above take a **path** as the subject; none takes a
SYMBOL. A store note that says *"BUILT (this atom's own file_scope): `door_only`, `required_missing`,
`_abbrev`"* is asserting that named symbols exist inside named modules, and every control listed
above passes it, because the *file* it names is tracked -- it is the *symbols* that are not there.

THE SUBJECT IS HANDED OVER, WHICH IS WHAT MAKES THIS CHEAP. The store half needed a citation
grammar because a store's prose mentions files it is not claiming (9 of its 10 naive leads were
honest). This check needs none: the atom **already declares its own `file_scope`** in
`docs/design/maturity_map.yaml`, so the subject is declared by the atom rather than inferred from
its prose.

THE DISCRIMINATION IS THE INDEX/WORKTREE SPLIT, NOT A LEXICON. This is the design decision, and it
is the one that keeps the control from being born red. Three buckets, measured 2026-08-19 over the
index of HEAD `459d41aea` -- **266** committed stores whose atom declares a `file_scope` naming
modules (30 more declare only directories and are excluded, see `_is_directory_scope`), **423**
distinct (store, symbol) pairs:

    387  (91.5%)  the symbol is in the atom's own file_scope AS THE INDEX CARRIES IT
     34   (8.0%)  the symbol is in NEITHER tree's file_scope
      2   (0.5%)  the symbol is in the WORKING TREE's file_scope and NOT in the index's

Only the third bucket is the verdict, and the reason is measured rather than argued:

  * The 34 are **honest, and a control keyed on them is born red on prose.** Read out, they are
    atom ids used as ids (`D18_confounder_observable_channel`), commit SHAs (`e844ee864`,
    `bc689525a`), ordinary English inside backticks (`notes`, `evidence`, `supported`,
    `inconclusive`, `cmp`, `unstated`), kernel fields (`VmHWM`), and symbols that genuinely live in
    other modules. Naming a symbol you do not own, or one BUILD has yet to produce, is what
    DISCOVER/FRAME work IS.
  * The 2 are **both real, both live, and both in this atom's own store** -- see WHAT IT FOUND.

A symbol present on disk and absent from the index is not ambiguous the way an absent one is. It
cannot be a design-future mention, because it exists. It is the record outrunning the code, which
is the whole class. So the burden needs no disclaim vocabulary to sit the right way round, and the
fail-open a lexicon always carries (R15) is not on this control's surface at all.

THE SECOND CLAUSE OF THAT PREMISE WAS FALSE AND IS NOW A GUARD (Hour #40, 2026-08-19). As first
written this paragraph also said the symbol *"cannot be a foreign symbol, because it is inside the
file_scope this atom declared for itself"*. `file_scope` declares what an atom OWNS; it does not
declare that those files are CODE. On its first independent run this control fired on

    OPS3_first_post_ruling_publish  `git_hash`   index 0   worktree 1

whose declared file_scope is `docs/status/LATEST.md` and `docs/observability/.publish_gate_state.json`
-- two artefacts a live background daemon rewrites. `git_hash` entered the worktree as a JSON key
inside a failure record written minutes earlier, while the symbol itself has been committed at
`background/process_run_complete.py:828` for a long time -- the very module OPS3's note cites. The
verdict said "the record outran its code" about code that had landed, and its prescribed repair
(`git add` a churning state file) would have fixed nothing and been undone by the next daemon
write. Worse, the verdict was NON-DETERMINISTIC: which daemon wrote last decided whether the gate
was red.

THE GUARD IS `_is_code`, AND IT IS THE ARGUMENT THIS CONTROL ALREADY MADE. Comments are stripped
because "a comment mentioning a symbol is not the symbol being built". A JSON key and a markdown
word are that same shape -- and worse, for a non-`.py` entry `_code_of` returns RAW TEXT, so the
comment-stripping doctrine is not even applied there. So the VERDICT corpus is built only from
file_scope entries that are source someone authored; the LANDED corpus stays over every entry,
because being generous about what counts as landed can only ever REMOVE a violation and never add
one. That asymmetry is the point: the verdict side is strict, the forgiveness side is loose.

THE REPO-WIDE BACKSTOP WAS MEASURED AND REJECTED -- see
`test_MUTATION_a_symbol_landed_elsewhere_in_the_repo_is_still_a_violation`. The obvious alternative
fix is "before calling a symbol unlanded, check whether the index carries it ANYWHERE". Measured at
HEAD, `door_only` sits in 6 committed files and `dimension_caveats` in 11, so that backstop would
have forgiven BOTH of this control's founding violations and left it unable to fire on the case it
was built for. It is the dilution failure `_is_directory_scope` already warns about, arriving on a
different axis, and the mutation exists so it cannot be re-added as an obvious improvement.

COMMENTS ARE STRIPPED AND STRINGS ARE NOT, and both halves of that were measured, not guessed.
Stripping comments removes exactly one false positive:

    D27_belief_window_saturates_on_this_book  `_caveat`

whose note describes *"the lift selects by the `_caveat` SUFFIX"* -- a prose fragment, matched
against another prose fragment, a `# ... the same `*_caveat` family ...` comment in the worktree.
A comment mentioning a symbol is not the symbol being built, so a comment cannot discharge a BUILT
claim. Strings, by contrast, STAY: a dict key `"door_only"` is real code, and stripping string
tokens as well drops the resolved bucket 387 -> 315 and loses one of the two live violations.

WHAT IT FOUND ON ITS FIRST RUN, 2026-08-19, against the index at HEAD `459d41aea`: two symbols,
one atom, and it is the atom whose Expert Hour built this control --

    H27_payment_belief_gap   `door_only`         index 0   worktree 4  (3 tools / 1 tests)
    H27_payment_belief_gap   `dimension_caveats` index 0   worktree 2  (0 tools / 2 tests)

The committed `level_hold_note` states *"#37 measures them into `door_only` and deliberately does
not judge them ... and a test pins that they stay recorded-not-judged"*, and *"`door_only` is EMPTY
on the pair this commit creates"*. Those are claims about code. At the index that code was not
there. The same note's own narrative had already filed this shape as BLOCKING one Hour earlier --
*"#37's whole deliverable ... was in NO COMMIT at d12b6ab79 while three records said it was
built"* -- and reported it repaired: *"#38 landed #37's work"*. The record that reports the class
fixed is the record this control caught it in, one commit later. `required_missing` (index 0,
worktree 2) and `_abbrev` (index 0, worktree 3) are the same landing. Hour #39 recorded them as
confirmed BY HAND, "named in the note's prose without backticks, so outside this tokeniser" -- that
stopped being true the moment #39 wrote this very sentence, because backticking a symbol in order
to report it unbackticked ENTERS it into the population. Re-measured at Hour #40 the control names
all four by itself, which is the better outcome and is recorded here rather than left as a note
that quietly contradicts its own tree.

Landed rather than ratcheted, for the reason the store half gives: the code waited on nothing (573
passed in `tests/tools/test_couple_w2_11_d5.py` on the working tree before it was staged), and a
ratchet entry that names no wait is the dishonest shape. `_KNOWN_UNLANDED` therefore ships EMPTY.
"""

from __future__ import annotations

import io
import re
import subprocess
import tokenize
from functools import lru_cache
from pathlib import Path

import pytest
import yaml

PROJECT = Path(__file__).resolve().parents[2]

STORE_DIR = "docs/design/simplifications/"

# THE MAP IS TWO FILES SINCE 2026-08-26 (`docs/design/MAP_SPLIT_2026-08-26.md`, commit
# 7f11d9c7d). `maturity_map.yaml` keeps the 74 atoms that still carry a gap; the 224 that are at
# or above their own target moved to `maturity_map_closed.yaml`. Nothing was deleted and no
# record was edited -- the union is the same 298 atoms the single file held.
#
# That commit repointed 47 readers and then five more. THIS CONTROL WAS NOT AMONG THEM, and the
# failure was silent in exactly the shape the split's own design note named as the hazard: it
# went on reading one half, its subject fell from 316 declared file_scopes to 74, the store join
# collapsed from 266 stores to 58, and it kept passing every claim it could still see. What
# caught it was `test_the_symbol_population_is_not_vacuous` -- the floor that exists because a
# control whose subject quietly empties reports GREEN forever. Its message was right: *"the store
# root, the map read or the atom_id join is what changed -- fix the mechanism, do not lower the
# floor."* It was the map read.
#
# Both halves are read FROM THE INDEX, not through `tools.maturity_map_store.load_atoms()`. The
# canonical loader is right for a runtime reader and wrong here: this control judges what the
# COMMIT BEING MADE will carry, and a loader that reads the working tree would let an uncommitted
# map edit discharge a committed claim.
MAP_PATHS = ("docs/design/maturity_map.yaml", "docs/design/maturity_map_closed.yaml")
MAP_PATH = MAP_PATHS[0]  # retained for message text; the SUBJECT is MAP_PATHS

# A backticked identifier. `()` is stripped so `main()` and `main` are one symbol. Anything
# carrying `/`, `.`, `*`, `::` or a space is a path, a glob, an attribute chain or prose -- the
# path-shaped claims are the other three controls' subject and are deliberately not re-judged here.
_SYMBOL = re.compile(r"`([A-Za-z_][A-Za-z0-9_]*)(?:\(\))?`")

# Symbols are matched on WORD BOUNDARIES, hand-rolled because `\b` cannot see the edge of a
# leading-underscore name: `\b_abbrev` requires a non-word character before the `_`, which is what
# `def _abbrev(` and `self._abbrev` both have, but the rule has to be the same at both ends or a
# short symbol matches inside a longer one (`cmp` inside `cmp_to_key`).
def _boundary(symbol: str) -> re.Pattern[str]:
    return re.compile(r"(?<![\w])" + re.escape(symbol) + r"(?![\w])")


# Vacuity floors, measured 2026-08-19 at the index of HEAD 459d41aea. A moved store root, a broken
# tokeniser, a map read that silently empties, or a file_scope lookup that stops resolving would
# each make this control pass forever over nothing.
#
# THE RESOLVED FLOOR IS SEPARATE FROM THE PAIR FLOOR ON PURPOSE. The fail-open this control is most
# exposed to is a file_scope read that returns empty text: pairs stay high, resolution collapses,
# and every symbol becomes "absent" -- which reads as a green verdict for every symbol that is also
# absent from disk. That failure is invisible in the pair count and loud in this one.
_MIN_STORES = 150
_MIN_PAIRS = 300
_MIN_RESOLVED = 280

# THE RATCHET. A symbol a committed store credits that only the working tree carries, each dated
# and naming the uncommitted change set it waits on. EMPTY is the correct steady state: this is a
# defect whose repair is `git add`, so an entry here should be rare and short-lived.
_KNOWN_UNLANDED: dict[str, str] = {}


def _git(*args: str) -> str:
    """Run git, or FAIL. R15 fail-silent: an unavailable subject is a failed check."""
    try:
        r = subprocess.run(
            ["git", *args], cwd=str(PROJECT),
            capture_output=True, text=True, timeout=180,
        )
    except (OSError, subprocess.SubprocessError) as exc:  # pragma: no cover - environment
        raise AssertionError(
            f"could not run `git {' '.join(args)}` ({exc!r}) -- this control's subject is "
            "unavailable, so it cannot say anything. An unavailable check is a FAILED check "
            "(R15 fail-silent), never a pass"
        ) from exc
    if r.returncode not in (0, 1):
        raise AssertionError(
            f"`git {' '.join(args)}` exited {r.returncode}: {r.stderr.strip()!r}. An "
            "unavailable check is a FAILED check"
        )
    return r.stdout


@lru_cache(maxsize=None)
def _tracked() -> frozenset[str]:
    paths = frozenset(p for p in _git("ls-files").splitlines() if p.strip())
    assert paths, (
        "`git ls-files` listed NOTHING. Either this is not a git work tree or the index is "
        "empty -- in both cases every comparison below would be vacuous"
    )
    return paths


@lru_cache(maxsize=None)
def _index_blob(path: str) -> str:
    """A file AS THE COMMIT BEING MADE WILL CARRY IT, or '' if the commit will not carry it."""
    return _git("show", f":{path}") if path in _tracked() else ""


@lru_cache(maxsize=None)
def _is_directory_scope(entry: str) -> bool:
    """A file_scope entry naming a TREE rather than a module.

    48 of the 504 distinct entries are directories, and they run to 6,157 files (`docs/staging/`).
    Expanding one is not a stricter check, it is a DILUTED one: against a tree that size almost any
    identifier resolves, so every claim would discharge itself. Directory-scoped atoms are excluded
    from the subject and COUNTED, and `test_the_directory_exclusion_stays_a_minority` is what stops
    that exclusion from quietly becoming the population.
    """
    prefix = entry.rstrip("/") + "/"
    return (PROJECT / entry).is_dir() or any(p.startswith(prefix) for p in _tracked())


def _modules_of(scope: list[str]) -> list[str]:
    return [e for e in scope if not _is_directory_scope(e)]


# Source someone AUTHORED, as against data or prose. Measured 2026-08-19 over the 1,010 module
# file_scope entries: .py 837, .mjs 60, .html 31 are code; .md 51, (extensionless) 17, .json 9,
# .yaml 4, .xml 1 are not. Only the VERDICT corpus is narrowed by this -- see the docstring's
# `git_hash` case for why, and note the asymmetry: the LANDED corpus keeps every entry, because
# forgiving too readily can only remove a violation, never invent one.
_CODE_SUFFIXES = (".py", ".mjs", ".js", ".html")


def _is_code(path: str) -> bool:
    return path.endswith(_CODE_SUFFIXES)


def _worktree_blob(path: str) -> str:
    f = PROJECT / path
    return f.read_text(encoding="utf-8", errors="replace") if f.is_file() else ""


def _code_of(text: str, path: str) -> str:
    """The file with COMMENTS removed; string literals KEPT.

    A comment mentioning a symbol is prose about the symbol, not the symbol being built -- see the
    module docstring for the one real false positive this removes. String literals stay because a
    dict key is code, and dropping them loses a live violation.
    """
    if not path.endswith(".py") or not text:
        return text
    try:
        return " ".join(
            tok.string
            for tok in tokenize.generate_tokens(io.StringIO(text).readline)
            if tok.type != tokenize.COMMENT
        )
    except (tokenize.TokenError, IndentationError, SyntaxError, ValueError):
        # A file the tokeniser cannot read is judged on its raw text rather than skipped: a parse
        # failure must not quietly empty this atom's subject (R15 fail-open).
        return text


def _file_scopes() -> dict[str, list[str]]:
    """atom id -> declared file_scope, read from the INDEX.

    The map is the register in which an atom declares what it owns, so its committed state is what
    a committed note is claiming against.
    """
    halves = {p: _index_blob(p) for p in MAP_PATHS}
    # REFUSES RATHER THAN DEGRADES, which is the split's own rule. A missing closed half would
    # not look broken -- it would look like a smaller map, and every claim against a closed atom
    # would silently stop being judged. Each half must be present and non-empty in the index.
    for path, raw in halves.items():
        assert raw.strip(), (
            f"the index carries no {path}. The map is two files since 2026-08-26 and BOTH are "
            "this control's subject; without one, every claim against an atom living there goes "
            "unjudged -- an unavailable subject is a FAILED check"
        )
    scopes: dict[str, list[str]] = {}

    def walk(node: object) -> None:
        if isinstance(node, dict):
            atom = node.get("id")
            scope = node.get("file_scope")
            if isinstance(atom, str) and isinstance(scope, list):
                scopes[atom] = [p for p in scope if isinstance(p, str)]
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    for raw in halves.values():
        walk(yaml.safe_load(raw))
    assert scopes, (
        f"{' + '.join(MAP_PATHS)} parsed but declared NO file_scope for any atom. The map shape "
        "changed and this control's subject went empty"
    )
    return scopes


def _symbols_in(store: dict) -> set[str]:
    """Every backticked identifier a store's prose names, notes and simplifications alike."""
    prose: list[str] = [v for v in (store.get("map_notes") or {}).values() if isinstance(v, str)]
    for entry in store.get("simplifications") or []:
        if isinstance(entry, dict):
            prose += [v for v in entry.values() if isinstance(v, str)]
    found: set[str] = set()
    for text in prose:
        found |= set(_SYMBOL.findall(text.replace("\\n", " ")))
    return found


def _classify(symbols: set[str], index_code: str, worktree_code: str) -> tuple[set[str], set[str]]:
    """(landed, worktree_only). Everything else is absent from both and is not this subject."""
    landed, worktree_only = set(), set()
    for symbol in symbols:
        edge = _boundary(symbol)
        if edge.search(index_code):
            landed.add(symbol)
        elif edge.search(worktree_code):
            worktree_only.add(symbol)
    return landed, worktree_only


def _survey() -> tuple[dict[str, str], int, int, int, int, int]:
    """(violations keyed `atom::symbol`, stores, pairs, resolved, dir_only, blind) -- from the INDEX.

    A claim's authority comes from being committed. Reading the working-tree store would admit an
    uncommitted note's claim and miss a committed note whose working copy has been edited: the
    precise confusion this class is about.
    """
    scopes = _file_scopes()
    stores = sorted(p for p in _tracked() if p.startswith(STORE_DIR) and p.endswith(".yaml"))
    violations: dict[str, str] = {}
    n_stores = n_pairs = n_resolved = n_dir_only = n_blind = 0
    for path in stores:
        try:
            store = yaml.safe_load(_index_blob(path))
        except yaml.YAMLError:
            continue
        if not isinstance(store, dict):
            continue
        scope = scopes.get(store.get("atom_id") or "")
        if not scope:
            continue
        modules = _modules_of(scope)
        if not modules:
            n_dir_only += 1
            continue
        n_stores += 1
        # Asymmetric ON PURPOSE: landed over every declared entry, the verdict over code alone.
        code = [f for f in modules if _is_code(f)]
        if not code:
            n_blind += 1
        index_code = "".join(_code_of(_index_blob(f), f) for f in modules)
        worktree_code = "".join(_code_of(_worktree_blob(f), f) for f in code)
        symbols = _symbols_in(store)
        landed, worktree_only = _classify(symbols, index_code, worktree_code)
        n_pairs += len(symbols)
        n_resolved += len(landed)
        stem = path[len(STORE_DIR):-len(".yaml")]
        for symbol in worktree_only:
            violations[f"{stem}::{symbol}"] = ", ".join(code)
    return violations, n_stores, n_pairs, n_resolved, n_dir_only, n_blind


# --------------------------------------------------------------------------------------
# The population must be real before any verdict about it means anything.
# --------------------------------------------------------------------------------------

def test_the_symbol_population_is_not_vacuous():
    """VACUITY GUARD. A green verdict over an empty population is not a green verdict."""
    _, stores, pairs, resolved, _, _ = _survey()
    assert stores >= _MIN_STORES, (
        f"only {stores} committed stores whose atom declares a file_scope (floor {_MIN_STORES}); "
        "266 were measured on 2026-08-19. The store root, the map read or the atom_id join is "
        "what changed -- fix the mechanism, do not lower the floor"
    )
    assert pairs >= _MIN_PAIRS, (
        f"only {pairs} (store, symbol) pairs (floor {_MIN_PAIRS}); 423 were measured on "
        "2026-08-19. The backtick tokeniser is what changed"
    )
    assert resolved >= _MIN_RESOLVED, (
        f"only {resolved} of {pairs} symbols resolve inside their own atom's committed file_scope "
        f"(floor {_MIN_RESOLVED}); 387 were measured on 2026-08-19. THIS IS THE FAIL-OPEN FLOOR: "
        "a file_scope read that silently returns empty text leaves the pair count untouched and "
        "collapses this one, and every symbol absent from disk would then read as green"
    )


# --------------------------------------------------------------------------------------
# The verdict.
# --------------------------------------------------------------------------------------

def test_the_directory_exclusion_stays_a_minority():
    """THE CONTROL ON THE EXCLUSION. An exclusion that grows until it is the population is a
    verdict about nothing, and it would be invisible in every other floor here."""
    _, stores, _, _, dir_only, _ = _survey()
    assert dir_only < stores, (
        f"{dir_only} atoms are excluded for having a directory-only file_scope against {stores} "
        "surveyed; 30 against 266 were measured on 2026-08-19. The exclusion has become the "
        "population -- either file_scope authoring changed shape, or _is_directory_scope has "
        "widened onto ordinary modules"
    )


def test_the_code_only_verdict_exclusion_stays_a_minority():
    """THE CONTROL ON THE SECOND EXCLUSION, and it is the one `_is_code` needs most.

    Narrowing the verdict corpus to authored source is the repair for the `git_hash` false
    positive, but it is also the exact shape that quietly kills a control: widen the notion of
    "data" far enough and every atom becomes verdict-blind while every other floor here stays
    green, because the pair and resolved counts are computed off the LANDED corpus, which this
    guard does not touch. 12 of 270 were measured on 2026-08-19.
    """
    _, stores, _, _, _, blind = _survey()
    assert blind * 4 < stores, (
        f"{blind} of {stores} surveyed atoms declare a file_scope with no authored source in it, "
        "so this control can return no verdict about them; 12 of 270 were measured on "
        "2026-08-19. Either _CODE_SUFFIXES has stopped recognising a language the repo writes, "
        "or file_scope authoring has moved to data artefacts -- fix the mechanism, do not widen "
        "the exclusion"
    )


def test_no_committed_store_claims_a_symbol_its_own_file_scope_has_not_landed():
    violations, _, _, _, _, _ = _survey()
    undeclared = {k: v for k, v in violations.items() if k not in _KNOWN_UNLANDED}
    assert not undeclared, (
        "A COMMITTED atom store names a symbol that only the WORKING TREE carries. The symbol is "
        "inside the file_scope the atom declared for itself, so this is not a design-future "
        "mention -- it is a record that outran its code:\n\n"
        + "".join(
            f"    {k}\n        declared file_scope: {v}\n"
            for k, v in sorted(undeclared.items())
        )
        + "\n    Stage the code with the record, or -- if it genuinely waits on an uncommitted "
        "change set -- declare it in _KNOWN_UNLANDED with the date and the wait."
    )


def test_every_declared_exemption_is_still_a_real_violation():
    """Shrink-only. A waiver that outlives its subject is a lie in the file."""
    violations, _, _, _, _, _ = _survey()
    stale = sorted(set(_KNOWN_UNLANDED) - set(violations))
    assert not stale, (
        "_KNOWN_UNLANDED declares a symbol that is no longer worktree-only -- it landed, or the "
        "note stopped naming it. DELETE the entry:\n" + "".join(f"    {k}\n" for k in stale)
    )


def test_every_exemption_is_dated_and_names_what_it_waits_on():
    for key, reason in sorted(_KNOWN_UNLANDED.items()):
        assert re.search(r"\b20\d\d-\d\d-\d\d\b", reason), (
            f"_KNOWN_UNLANDED[{key!r}] carries no measurement date -- an undated waiver cannot be "
            "told from a permanent one"
        )
        assert re.search(r"\bwaits? on\b", reason, re.I), (
            f"_KNOWN_UNLANDED[{key!r}] does not name what it waits on. This defect's repair is "
            "`git add`; an entry that waits on nothing should be a landing instead"
        )


# --------------------------------------------------------------------------------------
# R15 mutation tests. Each names the defect it must fire on.
# --------------------------------------------------------------------------------------

def test_MUTATION_a_symbol_on_disk_but_not_in_the_index_is_a_violation():
    """THE DEFECT: H27 Hour #37/#38's shape -- the note landed and the code did not."""
    landed, worktree_only = _classify(
        {"door_only"},
        index_code="def measure(): return {}",
        worktree_code='def measure(): return {"door_only": ()}',
    )
    assert worktree_only == {"door_only"} and not landed, (
        "a symbol the working tree carries and the index does not produced NO violation -- the "
        "verdict cannot fire on its own named defect"
    )


def test_MUTATION_a_data_artefact_in_file_scope_cannot_produce_a_violation():
    """THE DEFECT: OPS3's `git_hash`, this control's own first false positive.

    An atom whose file_scope names artefacts a daemon rewrites had a token appear in the worktree
    copy and not the index, and was judged a record that outran its code -- while the symbol sat
    committed in `background/process_run_complete.py`. Without `_is_code` the verdict is decided by
    which background process wrote last.
    """
    for entry in (
        "docs/observability/.publish_gate_state.json",
        "docs/status/LATEST.md",
        "docs/design/maturity_map.yaml",
    ):
        assert not _is_code(entry), (
            f"{entry!r} is counted as authored source. A generated or narrative artefact in a "
            "file_scope makes this control's verdict a function of daemon timing, not landing"
        )
    # The corpus _survey would hand the verdict for a data-only file_scope is EMPTY, so the
    # symbol cannot reach the worktree_only bucket however loudly the artefact names it.
    landed, worktree_only = _classify(
        {"git_hash"},
        index_code="",
        worktree_code="".join(
            _code_of(t, f)
            for f, t in [("docs/observability/.publish_gate_state.json", '{"git_hash": "1aa4a3d7a"}')]
            if _is_code(f)
        ),
    )
    assert not worktree_only and not landed, (
        "a JSON key inside a daemon-written state file discharged a landing claim -- `_is_code` "
        "is not filtering the verdict corpus"
    )


def test_MUTATION_the_guard_does_not_forgive_the_founding_violations():
    """THE OPPOSITE DEFECT: a repair for the false positive that also disarms the control.

    `door_only` and `dimension_caveats` live in `.py` file_scope entries, so narrowing the verdict
    corpus to authored source must leave them judged exactly as before.
    """
    for entry in ("tools/couple_w2_11_d5.py", "tests/tools/test_couple_w2_11_d5.py"):
        assert _is_code(entry), f"{entry!r} stopped counting as source -- the verdict went blind"
    landed, worktree_only = _classify(
        {"door_only", "dimension_caveats"},
        index_code="def measure(): return {}",
        worktree_code=_code_of(
            'def measure(): return {"door_only": (), "dimension_caveats": ()}\n',
            "tools/couple_w2_11_d5.py",
        ),
    )
    assert worktree_only == {"door_only", "dimension_caveats"} and not landed, (
        "the `_is_code` repair swallowed this control's own founding violations -- the fix for "
        "the false positive has disarmed the true positives"
    )


def test_MUTATION_a_symbol_landed_elsewhere_in_the_repo_is_still_a_violation():
    """THE REJECTED ALTERNATIVE, pinned so it cannot return as an obvious improvement.

    "Before calling a symbol unlanded, check whether the index carries it anywhere" reads as a
    strictly safer backstop. Measured at HEAD it forgives BOTH founding violations -- `door_only`
    in 6 committed files, `dimension_caveats` in 11 -- because a repo this size resolves almost
    any identifier somewhere. That is `_is_directory_scope`'s dilution argument on a new axis.

    The question this control asks is whether the atom's OWN declared scope landed the symbol, not
    whether the string exists in the repository.
    """
    elsewhere = _git("grep", "--cached", "-w", "-l", "-F", "--", "door_only")
    assert len([p for p in elsewhere.splitlines() if p.strip()]) > 1, (
        "`door_only` no longer resolves in more than one committed file, so this mutation has "
        "stopped exercising the dilution it exists to rule out -- pick another symbol the repo "
        "carries widely rather than deleting the test"
    )
    landed, worktree_only = _classify(
        {"door_only"},
        index_code="def measure(): return {}",
        worktree_code='def measure(): return {"door_only": ()}',
    )
    assert worktree_only == {"door_only"}, (
        "a symbol absent from its own atom's committed file_scope was forgiven because some other "
        "committed file carries it. A repo-wide backstop cannot fire on this control's own "
        "founding case"
    )


def test_MUTATION_a_symbol_in_neither_tree_is_not_a_violation():
    """THE OPPOSITE DEFECT: born red on the 34 honest mentions, so the control gets disabled."""
    for symbol in ("D18_confounder_observable_channel", "e844ee864", "notes", "VmHWM"):
        landed, worktree_only = _classify({symbol}, "def f(): pass", "def f(): pass")
        assert not landed and not worktree_only, (
            f"{symbol!r} -- absent from BOTH trees -- was judged. Atom ids, SHAs, English words "
            "and foreign symbols are 34 of the 423 pairs; judging them makes this control born "
            "red on prose"
        )


def test_MUTATION_a_symbol_the_index_already_carries_is_not_a_violation():
    landed, worktree_only = _classify(
        {"door_only"}, 'x = {"door_only": 1}', 'x = {"door_only": 1}'
    )
    assert landed == {"door_only"} and not worktree_only


def test_MUTATION_a_comment_only_mention_does_not_discharge_a_built_claim():
    """THE REAL FALSE POSITIVE this removes: D27's `_caveat`, prose matched against prose."""
    commented = "# the same `*_caveat` family that published a band\nx = 1\n"
    stripped = _code_of(commented, "tools/x.py")
    assert not _boundary("_caveat").search(stripped), (
        "a symbol named only in a COMMENT counted as built. D27's note describes '`_caveat` "
        "SUFFIX' and the worktree comment says the same thing -- two pieces of prose agreeing is "
        "not a landing, and this control would be born red on a note telling the truth"
    )
    assert _boundary("x").search(stripped), "comment stripping ate the code as well"


def test_MUTATION_a_string_literal_still_counts_as_built():
    """THE OVER-CORRECTION: stripping strings too drops resolution 387 -> 315 and loses a live
    violation. A dict key is code."""
    stripped = _code_of('MEASURED = {"door_only": ()}\n', "tools/x.py")
    assert _boundary("door_only").search(stripped), (
        "a symbol carried as a string literal was not counted as built -- `door_only` is a dict "
        "key in the real subject, and dropping strings makes this control blind to it"
    )


def test_MUTATION_an_unparseable_file_is_judged_on_raw_text_not_skipped():
    """FAIL-OPEN: a tokeniser error must not quietly empty an atom's subject."""
    broken = "def f(:\n  `not python`\n"
    assert _boundary("f").search(_code_of(broken, "tools/x.py")), (
        "a file the tokeniser could not read returned nothing, so every symbol the atom claims "
        "would read as absent -- an unreadable subject must not silently empty"
    )


def test_MUTATION_matching_is_on_word_boundaries_not_substrings():
    landed, _ = _classify({"cmp"}, "from functools import cmp_to_key", "")
    assert not landed, (
        "`cmp` matched inside `cmp_to_key` -- substring matching discharges a claim with a symbol "
        "that is not the one named"
    )
    landed, _ = _classify({"_abbrev"}, "def _abbrev(name):\n    return name", "")
    assert landed == {"_abbrev"}, (
        "a leading-underscore symbol did not match its own definition -- `\\b` cannot see the "
        "edge of `_abbrev`, which is why the boundary is hand-rolled"
    )


def test_MUTATION_a_backticked_path_or_glob_is_not_read_as_a_symbol():
    for prose in (
        "proven by `tests/tools/test_couple_w2_11_d5.py`",
        "ten untracked `tests/**/test_*.py` on disk",
        "`docs/design/maturity_map.yaml` declares it",
        "wired at `module.function`",
        "`the door only` is empty",
    ):
        assert not _SYMBOL.search(prose), (
            f"a path, glob, attribute chain or phrase was read as a symbol: {prose!r}. Paths are "
            "the other three controls' subject and re-judging them here duplicates their verdict"
        )
    assert _SYMBOL.findall("BUILT: `door_only` and `main()`") == ["door_only", "main"], (
        "the tokeniser missed a plain symbol or failed to strip `()`"
    )


def test_MUTATION_reading_the_working_tree_store_would_admit_an_uncommitted_claim():
    """THE SIDE THAT MUST BE THE INDEX. If the note itself were read from disk, an unstaged note
    could credit unstaged code and the pair would agree with itself -- a tautology (R15)."""
    store = f"{STORE_DIR}H27_payment_belief_gap.yaml"
    assert _index_blob(store).strip(), (
        "the index carries no H27 store, so this mutation has no subject"
    )
    assert _index_blob(store) is not _worktree_blob(store), "the two reads are the same object"
    # The claim under test is structural: the record side never reads disk.
    source = Path(__file__).read_text(encoding="utf-8")
    survey = source.split("def _survey(")[1].split("\ndef ")[0]
    assert "_worktree_blob(f)" in survey and "_worktree_blob(path)" not in survey, (
        "_survey() reads a STORE from the working tree. Only the file_scope may be read from "
        "disk; the note's authority comes from being committed"
    )


def test_MUTATION_git_unavailable_fails_rather_than_passing_quietly(monkeypatch):
    def boom(*a, **k):
        raise OSError("git is gone")
    monkeypatch.setattr(subprocess, "run", boom)
    with pytest.raises(AssertionError, match="unavailable"):
        _git("ls-files")


def test_MUTATION_a_non_zero_git_exit_fails_rather_than_passing_quietly(monkeypatch):
    class R:
        returncode = 128
        stdout = ""
        stderr = "fatal: not a git repository"
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: R())
    with pytest.raises(AssertionError, match="FAILED check"):
        _git("ls-files")


def test_MUTATION_an_empty_map_is_not_read_as_a_repository_with_no_claims(monkeypatch):
    monkeypatch.setattr(
        "tests.architecture.test_no_committed_store_claims_an_unlanded_symbol._index_blob",
        lambda path: "",
    )
    with pytest.raises(AssertionError, match="no docs/design/maturity_map.yaml"):
        _file_scopes()


def test_MUTATION_a_map_declaring_no_file_scope_fails_rather_than_surveying_nothing(monkeypatch):
    monkeypatch.setattr(
        "tests.architecture.test_no_committed_store_claims_an_unlanded_symbol._index_blob",
        lambda path: "atoms:\n  - id: X\n    level_current: 0\n",
    )
    with pytest.raises(AssertionError, match="declared NO file_scope"):
        _file_scopes()
