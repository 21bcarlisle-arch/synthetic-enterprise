"""R15 mutation proof for `tools/segment_case_guard.py`.

R15: no control counts as evidence unless a MUTATION TEST proves it fires on
its own named defect. The guard's named defect is "a segment string compared
in a non-canonical case somewhere in `simulation/`", so the tests below
reintroduce exactly the two literals that caused the original mis-billing and
assert the guard goes red.

The three killer patterns are each tested explicitly:

  TAUTOLOGY   -- the guard derives canonical spellings from
                 `segment_vocabulary`, and the fixtures below are written as
                 raw source text, so the check is not comparing a value to
                 itself.
  FAIL-OPEN   -- a missing root, an unparseable file, and an empty scan must
                 all FAIL (rc=2), not pass with "no violations found".
  FAIL-SILENT -- rc=2 is distinct from rc=0, so a caller cannot mistake "the
                 guard could not run" for "the guard passed".

Every fixture is written into a tmp_path, never into the real tree -- a
mutation test that edits the repo and restores it can lose an unrelated
in-flight edit.
"""
from __future__ import annotations

import textwrap

import pytest

from tools.segment_case_guard import main, scan


def _write(tmp_path, name, source):
    path = tmp_path / name
    path.write_text(textwrap.dedent(source), encoding="utf-8")
    return path


class TestFiresOnItsOwnDefect:
    """MUTATION: reintroduce the real defect, assert the guard goes red."""

    def test_fires_on_the_original_arrears_engine_comparison(self, tmp_path):
        # The exact line that mis-billed C5 and C6 for the whole history.
        _write(tmp_path, "mutated.py", '''
            def payment_method(segment, amount_gbp):
                if segment == "sme":
                    return "bacs"
                return "direct_debit"
        ''')
        messages, scanned = scan(tmp_path, tmp_path)
        assert scanned == 1
        assert len(messages) == 1
        assert '"sme"' in messages[0] or "'sme'" in messages[0]
        assert "SME" in messages[0], "the message must name the canonical spelling"

    def test_fires_on_the_original_payment_behaviour_source_tuple(self, tmp_path):
        _write(tmp_path, "mutated.py", '''
            def core(segment):
                return "bacs" if segment in ("ic", "I&C", "sme") else "direct_debit"
        ''')
        messages, _ = scan(tmp_path, tmp_path)
        # "ic" and "sme" are non-canonical; "I&C" is canonical and must NOT
        # be flagged -- a guard that fires on correct code gets switched off.
        assert len(messages) == 2, messages

    def test_fires_on_the_ic_segments_constant_coming_back(self, tmp_path):
        _write(tmp_path, "mutated.py", '_IC_SEGMENTS = ("ic", "I&C")\n')
        messages, _ = scan(tmp_path, tmp_path)
        assert len(messages) == 1, messages
        assert "ic" in messages[0]

    def test_fires_on_the_same_constant_under_an_innocent_name(self, tmp_path):
        """The guard's own first fail-open: keying on the NAME.

        `_IC_SEGMENTS` would have been caught by a name-based rule; the
        identical hazard called `_RAILS` would not. Contents, not name.
        """
        _write(tmp_path, "mutated.py", '_RAILS = ("ic", "I&C")\n')
        messages, _ = scan(tmp_path, tmp_path)
        assert len(messages) == 1, messages

    def test_fires_on_a_lowercase_ic_spelling(self, tmp_path):
        _write(tmp_path, "mutated.py", 'x = seg == "i&c"\n')
        messages, _ = scan(tmp_path, tmp_path)
        assert len(messages) == 1
        assert "I&C" in messages[0]


class TestDoesNotFireOnCorrectCode:
    """A control with no false-negative AND no false-positive story is theatre."""

    def test_canonical_comparisons_pass(self, tmp_path):
        _write(tmp_path, "clean.py", '''
            RESIDENTIAL = "resi"
            def f(segment):
                if segment == "resi":
                    return 1
                if segment in ("SME", "I&C"):
                    return 2
                return 3
        ''')
        messages, scanned = scan(tmp_path, tmp_path)
        assert scanned == 1
        assert messages == []

    def test_normaliser_based_code_passes(self, tmp_path):
        _write(tmp_path, "clean.py", '''
            from simulation.segment_vocabulary import SME, normalise_segment
            def f(segment):
                return normalise_segment(segment) == SME
        ''')
        messages, _ = scan(tmp_path, tmp_path)
        assert messages == []

    def test_a_different_vocabulary_is_not_flagged(self, tmp_path):
        """A collection carrying non-alias members is a different vocabulary
        with its own normalisation (e.g. `segment_debt_obligation`'s label
        sets, which lower-case their input before matching), not a
        re-spelling of this one."""
        _write(tmp_path, "clean.py", '_SME_LABELS = {"sme", "small_business", "microbusiness"}\n')
        messages, _ = scan(tmp_path, tmp_path)
        assert messages == []

    def test_the_real_simulation_tree_is_clean(self):
        """The live assertion -- the class is actually closed right now."""
        assert main([]) == 0


class TestAnnotatedAssignment:
    """W2_15 MUTATION: the fail-open a type hint used to open.

    `_IC_SEGMENTS = (...)` is an `ast.Assign`; `_IC_SEGMENTS: Tuple[str, ...] =
    (...)` is an `ast.AnnAssign`. The constant-collection channel visited only
    the first, so adding a type annotation switched the control off. These
    tests are the pair: the same defect, annotated and bare, must both fire.
    """

    def test_the_annotated_constant_is_flagged_like_the_bare_one(self, tmp_path):
        _write(tmp_path, "mutated.py", '''
            from typing import Tuple
            _IC_SEGMENTS: Tuple[str, ...] = ("ic", "I&C")
        ''')
        messages, _ = scan(tmp_path, tmp_path)
        assert len(messages) == 1, messages
        assert "'ic'" in messages[0]

    def test_annotated_and_bare_forms_agree(self, tmp_path):
        """The property, not one instance: annotation must not change the
        verdict for ANY of the shapes the guard claims to catch."""
        bodies = [
            '_SEGS{ann} = ("ic", "I&C")',
            '_SEGS{ann} = ["sme"]',
            '_SEGS{ann} = ("SME", "I&C")',
        ]
        (tmp_path / "a").mkdir()
        (tmp_path / "b").mkdir()
        for body in bodies:
            _write(tmp_path / "a", "m.py", body.format(ann=""))
            _write(tmp_path / "b", "m.py", body.format(ann=": tuple"))
            n_bare, _ = scan(tmp_path / "a", tmp_path)
            n_ann, _ = scan(tmp_path / "b", tmp_path)
            assert len(n_bare) == len(n_ann) > 0, (body, n_bare, n_ann)

    def test_an_annotated_clean_constant_still_passes(self, tmp_path):
        """The new visitor must not fire on correct annotated code."""
        _write(tmp_path, "clean.py", '''
            from typing import Tuple
            _LABELS: Tuple[str, ...] = ("small_business", "household")
        ''')
        messages, _ = scan(tmp_path, tmp_path)
        assert messages == []


class TestDuplicatedCanonicalVocabulary:
    """W2_15 MUTATION: a SECOND copy of the canonical vocabulary.

    The named defect is `simulation/sme_distress.BUSINESS_SEGMENTS = ("SME",
    "I&C")` -- every literal canonical, so the case-check had nothing to flag,
    while `segment in BUSINESS_SEGMENTS` was case-SENSITIVE and a lower-case
    "sme" was not a business segment. The comparison itself is out of an AST
    scan's reach; the private copy that makes it possible is not.
    """

    def test_fires_on_the_real_sme_distress_constant(self, tmp_path):
        _write(tmp_path, "mutated.py",
               'BUSINESS_SEGMENTS: Tuple[str, ...] = ("SME", "I&C")\n')
        messages, _ = scan(tmp_path, tmp_path)
        assert len(messages) == 1, messages
        assert "re-declared" in messages[0]
        assert "segment_vocabulary" in messages[0], (
            "the message must name where to import it from, or the reader's "
            "obvious fix is to spell it differently"
        )

    def test_fires_on_all_three_segments_and_on_a_list_or_set(self, tmp_path):
        for source in (
            'ALL = ("resi", "SME", "I&C")\n',
            'ALL = ["resi", "SME"]\n',
            'ALL = {"SME", "I&C"}\n',
        ):
            _write(tmp_path, "mutated.py", source)
            messages, _ = scan(tmp_path, tmp_path)
            assert len(messages) == 1, (source, messages)

    def test_a_single_canonical_literal_is_not_a_vocabulary(self, tmp_path):
        """Threshold check -- one literal in a collection is a value, not a
        re-declaration, and flagging it would make the guard noise."""
        _write(tmp_path, "clean.py", 'DEFAULTS = ("resi",)\n')
        messages, _ = scan(tmp_path, tmp_path)
        assert messages == []

    def test_the_vocabulary_module_itself_is_exempt(self, tmp_path):
        """The canon declaring the canon is the point, not a duplicate.

        This drives the EXEMPT path mechanism rather than asserting it from
        the real tree: `simulation/segment_vocabulary.py` happens to build
        `CANONICAL_SEGMENTS` from names, not literals, so a green real-tree
        run would prove nothing about the exemption. Same source, two paths,
        opposite verdicts -- that is the exemption actually doing work.
        """
        source = 'CANONICAL_SEGMENTS = ("resi", "SME", "I&C")\n'
        elsewhere = tmp_path / "elsewhere"
        elsewhere.mkdir()
        _write(elsewhere, "anywhere.py", source)
        assert len(scan(elsewhere, tmp_path)[0]) == 1, "flagged off the exempt path"

        canon = tmp_path / "simulation"
        canon.mkdir()
        _write(canon, "segment_vocabulary.py", source)
        messages, scanned = scan(canon, tmp_path)
        assert scanned == 0 and messages == [], (
            "the alias table's own declaration must be exempt -- and the "
            "exemption is keyed on the repo-relative path, so it must resolve"
        )


class TestCannotFailOpen:
    """FAIL-OPEN / FAIL-SILENT: not-run must never read as passed."""

    def test_missing_root_is_a_failure_not_a_pass(self, tmp_path):
        missing = tmp_path / "does_not_exist"
        with pytest.raises(FileNotFoundError):
            scan(missing, tmp_path)
        assert main(["--root", str(missing)]) == 2

    def test_empty_scan_is_a_failure_not_a_pass(self, tmp_path):
        """The vacuity guard: 0 violations over 0 files proves nothing."""
        empty = tmp_path / "empty"
        empty.mkdir()
        messages, scanned = scan(empty, tmp_path)
        assert (messages, scanned) == ([], 0)
        assert main(["--root", str(empty)]) == 2, (
            "an empty scan reported success -- that is the vacuity fail-open"
        )

    def test_unparseable_file_is_a_failure_not_a_skip(self, tmp_path):
        _write(tmp_path, "broken.py", "def f(:\n")
        with pytest.raises(SyntaxError):
            scan(tmp_path, tmp_path)
        assert main(["--root", str(tmp_path)]) == 2, (
            "a syntax error was skipped -- a violation could hide behind it"
        )

    def test_violation_and_could_not_run_are_distinguishable(self, tmp_path):
        _write(tmp_path, "mutated.py", 'x = seg == "sme"\n')
        assert main(["--root", str(tmp_path)]) == 1
        # rc=1 (found a violation) and rc=2 (could not run) must not collide,
        # or a caller checking `rc != 0` learns nothing about which happened.
        assert main(["--root", str(tmp_path / "nope")]) == 2
