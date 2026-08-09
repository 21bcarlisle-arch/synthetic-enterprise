"""W2_15 -- three segment vocabularies, and the seams between them.

The DISCOVER question was whether the rival segment spellings in `simulation/`
are one vocabulary that drifted or several that were never the same thing. The
answer (`docs/design/W2_15_SEGMENT_VOCABULARIES_DISCOVER.md`) is:

  ONE was drift  -- `sme_distress.BUSINESS_SEGMENTS` was a private copy of the
                    canon, compared case-sensitively. Merged.
  TWO are real   -- the company's OBSERVED book label and the population
                    COHORT id are different things from the world-true market
                    segment, and coercing either onto the canon deletes a
                    measurement. Sealed, not merged.

These tests pin BOTH answers, because the failure mode of a "three
vocabularies" finding is that someone later tidies it into one.
"""
from __future__ import annotations

import pytest

from simulation import segment_debt_obligation as w29
from simulation import segment_vocabulary as vocab
from simulation import sme_distress


class TestTheDriftOneWasMerged:
    """The latent defect the atom named: a lower-case spelling CRASHED the
    twin rather than mis-routing it, because the private copy was compared
    case-sensitively."""

    def test_the_lowercase_spelling_no_longer_raises(self):
        # MUTATION reference: before W2_15 this returned False and the caller
        # below raised ValueError on a perfectly real microbusiness.
        assert sme_distress.is_business_segment("sme") is True
        assert sme_distress.is_business_segment("SME") is True
        assert sme_distress.is_business_segment("i&c") is True
        assert sme_distress.is_business_segment("IC") is True

    def test_every_alias_of_a_business_segment_agrees(self):
        """The property, not the two instances -- the twin and the canon must
        never disagree about who is a business, for ANY known spelling."""
        for spelling in vocab._ALIASES:
            assert sme_distress.is_business_segment(spelling) == vocab.is_business(
                spelling
            ), spelling

    def test_residential_and_unknown_are_still_not_business(self):
        assert sme_distress.is_business_segment("resi") is False
        assert sme_distress.is_business_segment("domestic") is False
        # Unknown is False rather than an exception: the caller's own error
        # message is the better one (it names the residential stream).
        assert sme_distress.is_business_segment("gold_tier") is False

    def test_the_twin_still_refuses_a_household(self):
        """The case fix must not have widened the gate. A household must never
        receive an insolvency event."""
        with pytest.raises(ValueError, match="not a business segment"):
            sme_distress.generate_business_distress(
                customer_id="C-RESI",
                segment="resi",
                sim_start_year=2020,
                sim_end_year=2021,
            )

    def test_the_vocabulary_is_sourced_not_re_declared(self):
        """The structural half. Equal values would also pass if someone typed
        the same tuple again, so assert the CONTENT matches the canon and let
        `tools/segment_case_guard.py` enforce that it is not a second copy
        (TestDuplicatedCanonicalVocabulary)."""
        assert tuple(sme_distress.BUSINESS_SEGMENTS) == tuple(
            vocab.BUSINESS_SEGMENTS
        )


class TestTheCompanyBookVocabularyIsSealed:
    """V2 -- what the company RECORDED, which is allowed to be wrong."""

    def test_observed_labels_carry_their_provenance(self):
        label = w29.observed_segment("sme", "CUST-001")
        assert isinstance(label, vocab.CompanyBookLabel)

    def test_the_seal_holds_for_every_label_not_just_the_odd_one(self):
        """THE POINT OF THE TYPE. 'iandc' was already refused by the canon
        (it is not an alias), but 'resi' and 'sme' ARE valid aliases and would
        have coerced silently -- so a string-based block passed two labels in
        three and raised on the third. A pipe from the company's book to the
        canon would have run green through any resi/SME population and failed
        the first time an I&C customer appeared.

        MUTATION: make `observed_segment` return a bare `str` and this test
        goes red on 'resi' and 'sme' while still passing on 'iandc' -- which
        is precisely the partial silence being closed.
        """
        for true_segment in ("resi", "sme", "iandc"):
            for i in range(200):
                label = w29.observed_segment(true_segment, f"W15-{i:04d}")
                with pytest.raises(vocab.UnknownSegmentError):
                    vocab.normalise_segment(label)

    def test_the_refusal_survives_a_default(self):
        """`default=` exists for an ABSENT segment. A present-but-foreign
        vocabulary is not absent, so no default may rescue it."""
        with pytest.raises(vocab.UnknownSegmentError):
            vocab.normalise_segment(vocab.CompanyBookLabel("resi"), default="resi")

    def test_iandc_is_still_not_a_canon_alias(self):
        """The tripwire on the tempting one-line 'fix'. Adding "iandc" to
        `_ALIASES` would make the canon silently accept the company's book
        spelling, and this test is where that decision has to be argued."""
        assert "iandc" not in vocab._ALIASES
        with pytest.raises(vocab.UnknownSegmentError):
            vocab.normalise_segment("iandc")

    def test_the_seal_does_not_break_the_real_consumer(self):
        """A seam that broke its own consumers would just be reverted. The
        label must still behave as the plain string C11 acts on -- so this
        drives the ACTUAL consumer (`company.compliance.segment_debt_policy`,
        via the W2_9/C11 coupling), not a stand-in for it."""
        import datetime as _dt

        from company.compliance.segment_debt_policy import select_debt_terms

        label = w29.observed_segment("iandc", "CUST-002")
        assert label in ("resi", "sme", "iandc")
        assert select_debt_terms(label, _dt.date(2024, 1, 1)) is not None
        assert select_debt_terms(label, _dt.date(2024, 1, 1)) == select_debt_terms(
            str(label), _dt.date(2024, 1, 1)
        ), "the marked label and the bare string must resolve identically"
        assert {label: 1}[str(label)] == 1

    def test_the_company_vocabulary_is_case_insensitive_by_construction(self):
        """W2_9's own label sets are deliberately exempt from the segment-case
        class: `_norm` lower-cases before matching, so no spelling of a label
        can take the wrong branch here."""
        for spelling in ("SME", "sme", " Sme ", "I&C", "iandc", "IANDC"):
            assert w29.is_business_segment(spelling) is True


class TestTheCohortVocabularyIsSealed:
    """V3 -- the population cohort id, a different axis entirely."""

    def test_a_cohort_id_is_refused_by_the_canon(self):
        from simulation.segments import SEGMENTS

        for segment in SEGMENTS:
            with pytest.raises(vocab.UnknownSegmentError):
                vocab.normalise_segment(segment.segment_id)

    def test_the_refusal_is_not_an_accident_of_spelling(self):
        """`sme_standard` must not be guessable as SME by prefix. If someone
        adds prefix matching to the normaliser, this is what stops it."""
        for guessable in ("sme_standard", "sme_smart", "resi_smart", "gas_resi"):
            with pytest.raises(vocab.UnknownSegmentError):
                vocab.normalise_segment(guessable)
