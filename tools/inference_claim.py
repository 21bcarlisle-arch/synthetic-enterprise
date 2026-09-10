"""INDEPENDENCE IS NOT INFERENCE — the standing rule, in one place, applied from numbers.

Director, 2026-08-30, on what the rebuilt co-calibration guard unlocks:

    "Independence is not inference. The verdict removes the objection that we were measuring our
    own reflection; it does not establish the company knows anything. The method scores 0.614
    against a null of 0.283-0.717 and cannot be told from chance. So the belief-versus-truth gap
    may be published as a measurement, never as evidence of skill, and the two must not appear in
    one sentence without the null interval beside them. If the concordance sits inside its null,
    the page says we cannot tell, in those words. And the company being outside the band 8 of 10
    years is independence and inaccuracy at once -- a large gap is as likely to be error as
    insight, and nothing we publish should let that be misread."

WHY THIS IS A MODULE AND NOT A CORRECTED SENTENCE. The instance that prompted it was one clause
in `tools/couple_value_based_pricing._co_calibration_clause`, which read:

    "The two sides no longer share a calibration source, so that gap now speaks to the company's
     own inference."

Correcting that string would leave the RULE nowhere, and the next surface that quotes the gap
would have to rediscover it. Worse, the flag behind that clause --
`publishable_as_evidence_of_inference` -- was literally `not provenance["co_calibrated"]`, i.e.
the codebase encoded "independent therefore inferring" as an identity. That is the thing being
corrected, so it is corrected once, here, and both the summary and the ledger row read it.

THE RULE, AS THREE CLAIMS THAT ARE NOT THE SAME CLAIM:

  1. THE GAP IS A MEASUREMENT. It is always publishable as one. A real disagreement between what
     the company believed and what the world delivered is a fact about this run, and nothing in
     here withholds it.
  2. THE GAP IS EVIDENCE OF SKILL only if BOTH: the two sides were arrived at independently
     (necessary -- otherwise we are measuring our own reflection), AND the method's own ranking
     clears the interval a random signal produces on this many decisions (also necessary --
     otherwise the measurement cannot be told from chance). Independence is the first leg alone
     and was being read as the whole thing.
  3. A LARGE GAP IS NOT A LARGE RESULT, AND IT IS NOT AN ACCURACY READING EITHER. Wherever the
     company sits outside the published band, a reader must not take the SIZE of the distance as
     the size of anything -- not as the size of an error, and not as the size of an insight.

     THIS CLAUSE WAS AN ACCURACY CLAIM UNTIL 2026-08-31 AND IT WAS COMPARING TWO DIFFERENT
     QUANTITIES. It read "independence and inaccuracy at once: the gap is as likely to be the
     company being wrong as the company knowing something". That reading requires the company's
     number and the band to count the same thing. They do not.
     `docs/design/THE_ACTED_BELIEF_IS_A_BOOK_QUANTITY_2026-08-31.md` settles it: the company's
     acted belief is `prior x ratio ** w`, where the ratio is realised over predicted departures
     on ONE SUPPLIER'S OWN BOOK at w = 0.82-0.89 -- so the LEVEL of that number is a book level,
     while the published band is a market level. Supplier churn is roughly the market switching
     rate times that supplier's retention RELATIVE to the market, and the update carries no term
     that could separate the two. A sticky book in a competitive year sits far outside the band
     without being wrong about anything.

     So the distance is reported as a DISTANCE, `accuracy_reading_available` is False with its
     reason, and the prose names both populations. The withdrawal is the fail-closed direction
     even though it is also the flattering one: the page does not gain an accuracy reading, it
     loses the ability to make one, and there is no other comparison available that would give it
     back. See `record_distance` below.

     NO COUNT IS WRITTEN HERE, and that is a separate correction. This paragraph once read
     "outside the band in 8 of 10 years, by up to 17.3pp" -- a measurement of the hand-authored
     multiplier table, stated in the present tense. That table was replaced on 2026-08-31
     (`company/crm/market_conditions` now loads the absolute rate from the commons) and the
     company leg was then repointed from the prior to the posterior it actually prices on, and
     the sentence outlived both. The count is computed live in `record_distance` below from
     whatever the guard reads today; a prose copy of it is a second source for one figure and
     the stale one is always the one a reader quotes.

  WHAT THIS DOES NOT TOUCH: leg 1, INDEPENDENCE. The band test behind it is a PROVENANCE test --
  "is this side's series the record?" -- and the posterior IS the record exactly when the book
  adds nothing (ratio 1 or w 0 gives posterior = prior). Only the company's own realised
  departures can move it off, and those are not in the record. Sitting outside the band therefore
  still demonstrates the number carries information the record does not, which needs no
  commensurability. It never demonstrated the number was wrong, which does.

FAIL-CLOSED, ON BOTH LEGS. A missing skill reading, an absent null spread, an unreadable
artefact and an undecidable side all resolve to `None`, and `None` never satisfies leg 2 --
`is True` is the test, not truthiness. "We could not check" is not "it cleared".

WHAT NO EDIT TO THIS FILE CAN DO. `publishable_as_evidence_of_skill` is composed only from the
two `is True` tests; there is no string, docstring or witness anywhere in the composition, for
the same reason `shared_calibration_holds` no longer has one. The prose is DERIVED from the
verdict rather than sitting beside it, so a sentence cannot disagree with the flag it decorates.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent

from tools.reduction_dimension import declare  # noqa: E402

#: RESTATED RATHER THAN RE-EXPORTED FROM `simulation.premise_population`, deliberately. The ceiling
#: this module reports is that module's, and importing its declaration at module level would put the
#: world's package on the publishing lane's import graph -- which is the exact thing
#: `settled_book_ceiling_accounts` takes a lazy import to avoid. A declaration is a statement about
#: what a figure can see, and both statements are true of the same figure; the duplication is two
#: lines and the coupling it avoids is the whole reason that function is written the way it is.
REDUCES_OVER = declare(
    "the most accounts the settled book can hold",
    kind="ceiling",
    of=("settlement_working_set_bytes_per_account", "serialisation_bytes_per_account",
        "host_memory_mb", "wall_clock_seconds"),
    reduces_over=("bytes_per_account", "host_memory_mb"),
    derived_from={"bytes_per_account": ("settlement_working_set_bytes_per_account",
                                        "serialisation_bytes_per_account")},
    blind_to=("wall_clock_seconds",),
    joint=True,
)

#: The run artefact that carries the method's own ranking against the interval a random signal
#: produces. Read rather than recomputed: `tools/generate_value_arms_data._method_skill` rejected
#: recomputing the spread from the artefact's own n for exactly this reason -- it is
#: arithmetically identical and creates a SECOND source for one figure.
SKILL_ARTEFACT = PROJECT / "docs" / "observability" / "value_cycle_ab_s1_three_arm.json"

#: The words the director specified, verbatim, for the case where the reading sits inside its
#: own null. Held as a constant so the phrase cannot drift into a softer one ("suggestive",
#: "early evidence") while the flag beside it stays False.
CANNOT_TELL = "we cannot tell"

THE_RULE = (
    "The belief-versus-truth gap is publishable as a MEASUREMENT and never as evidence of skill "
    "unless the two sides are independent AND the method's own ranking clears the interval a "
    "random signal produces on this many decisions. Independence alone removes the objection "
    "that we were measuring our own reflection; it does not establish that the company knows "
    "anything."
)


def skill_reading(payload: dict | None = None, artefact: Path | None = None) -> dict:
    """The method's ranking and the interval a random signal reaches, or a refusal.

    `clears_the_null` is TRUE only when the run says the observed value fell OUTSIDE the
    interval. It is FALSE when the run says it fell inside, and NONE whenever the question could
    not be put -- artefact missing, unreadable, no `method_skill`, no `null_spread`, or a spread
    that does not carry `observed_inside_the_null_interval`. None is not False: one means the
    method did not clear its null and the other means we do not know, and they are reported
    apart because only the second is fixable by running something.
    """
    src = SKILL_ARTEFACT if artefact is None else artefact
    if payload is None:
        try:
            payload = json.loads(src.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return _no_reading(f"the run artefact could not be read ({type(exc).__name__})")
    ms = (payload or {}).get("method_skill") or {}
    if not ms.get("available"):
        return _no_reading(str(ms.get("reason") or "this run carried no method-skill reading"))
    spread = ms.get("null_spread") or {}
    if not spread.get("available"):
        return _no_reading(
            "this run carries a concordance but no null spread, so there is no interval to "
            "clear: " + str(spread.get("reason") or "the spread is absent"))
    inside = spread.get("observed_inside_the_null_interval")
    interval = spread.get("null_95_interval") or [None, None]
    if not isinstance(inside, bool) or interval[0] is None or interval[1] is None:
        return _no_reading("the null spread carries no decidable interval for this run")
    return {
        "available": True,
        "concordance": ms.get("concordance"),
        "null_95_low": interval[0],
        "null_95_high": interval[1],
        "null_point": ms.get("null_constant_signal_concordance"),
        "p_two_sided": spread.get("p_two_sided"),
        "decisions_scored": ms.get("decisions_scored"),
        "clears_the_null": not inside,
        "why": None,
    }


def _no_reading(why: str) -> dict:
    return {"available": False, "concordance": None, "null_95_low": None, "null_95_high": None,
            "null_point": None, "p_two_sided": None, "decisions_scored": None,
            "clears_the_null": None, "why": why}


def _independence(provenance: dict | None) -> bool | None:
    """TRUE only on a verdict that positively says the sides do not share a source.

    A provenance dict that is missing, or that carries no `co_calibrated` boolean, is None --
    the same fail-closed shape as the skill leg, and for the same reason.
    """
    if not isinstance(provenance, dict):
        return None
    co = provenance.get("co_calibrated")
    if not isinstance(co, bool):
        return None
    return not co


#: WHY THE DISTANCE IS NOT AN ERROR, held as a constant so no branch can render the distance
#: without it and no edit can soften it to "may not be" while the flag beside it says False.
#: The argument is in `docs/design/THE_ACTED_BELIEF_IS_A_BOOK_QUANTITY_2026-08-31.md`.
NOT_AN_ACCURACY_READING = (
    "the company's acted belief is this BOOK's departure hazard and the published band is the GB "
    "MARKET's switching rate, which are two different quantities. A supplier that retains better "
    "than average sits far outside the band without being wrong about anything, and the update "
    "carries no term separating how competitive the market is from how retainable this book is"
)


def record_distance(provenance: dict | None) -> dict:
    """HOW FAR THE ACTED BELIEF SITS FROM THE RECORD -- a distance, and NOT an accuracy reading.

    RENAMED FROM `accuracy_clause` ON 2026-08-31, and the rename IS the correction. The old
    version read the same list of `years_outside_the_band` as evidence that the company's
    estimator is BAD. That reading needs the company's number and the band to count the same
    thing; the determination above establishes they do not. So the count and the worst distance
    are still reported -- they are facts about this run and nothing is withheld -- but
    `accuracy_reading_available` is False with its reason, and the prose says what the distance
    is not.

    THE JOB THE OLD CLAUSE DID GETS BIGGER, NOT SMALLER. It stopped a reader taking the size of
    the gap as the size of the insight. Under the book reading the distance is evidence of
    NEITHER error nor insight, because the two numbers count different populations, so the
    warning now runs in both directions and the clause says so explicitly.

    Computed from the same record independence was computed from, so a reader who sees one sees
    the other's inputs.
    """
    sides = ((provenance or {}).get("sides") or {})
    company = sides.get("company") or {}
    outside = company.get("years_outside_the_band") or []
    checked = company.get("years_checked")
    if not outside:
        return {"applies": False, "years_outside": 0, "years_checked": checked,
                "max_distance_pp": None, "accuracy_reading_available": False,
                "why_no_accuracy_reading": NOT_AN_ACCURACY_READING, "clause": ""}
    distances = []
    for row in outside:
        band = row.get("band_pct") or [None, None]
        reads = row.get("reads_pct")
        if reads is None or band[0] is None or band[1] is None:
            continue
        distances.append(round(max(band[0] - reads, reads - band[1]), 2))
    worst = max(distances) if distances else None
    return {
        "applies": True,
        "years_outside": len(outside),
        "years_checked": checked,
        "max_distance_pp": worst,
        # ALWAYS FALSE WHILE THE COMPANY LEG READS A BOOK QUANTITY. Not a flag some branch can
        # flip: there is no comparison available on this side of the wall that would make the
        # company's belief scoreable for accuracy, so the honest value is a constant refusal.
        "accuracy_reading_available": False,
        "why_no_accuracy_reading": NOT_AN_ACCURACY_READING,
        "clause": (
            "The company's acted belief sits outside the published band in {} of {} years{}. "
            "That distance is NOT an accuracy reading: {}. It is not evidence of insight either "
            "-- the two numbers count different populations, so nothing about whether the "
            "company knows anything can be read off how far apart they are."
        ).format(len(outside), checked if checked is not None else len(outside),
                 "" if worst is None else ", by up to {:.1f}pp".format(worst),
                 NOT_AN_ACCURACY_READING),
    }


def cannot_tell_sentence(*, subject: str, observed, null_low, null_high,
                         n=None, unit: str = "decisions") -> str | None:
    """THE WORDS, for any figure on any surface that sits inside its own null.

    Returns the sentence when the reading cannot be told from chance, and `None` when it can --
    so a caller renders it or does not, and never has to decide which case it is in. Whether the
    reading clears its null is COMPUTED here from the three numbers rather than read off an
    `inside_the_null` flag the artefact happens to carry: a flag is one more thing that can be
    stale, and the comparison is two `<=`.

    UNDECIDABLE COUNTS AS CANNOT TELL. A missing observed value or a missing bound returns the
    sentence, not None. "We have no interval" and "the interval swallows the reading" are
    different reasons and the same answer to a reader.

    Written for the concordance the director named, and applied to the AUC beside it because that
    figure is the same class -- a rank statistic on a small sample, published next to a claim
    about what the company knows.
    """
    if observed is None or null_low is None or null_high is None:
        return "On {}, {}: this run carries no interval to weigh the reading against.".format(
            subject, CANNOT_TELL)
    if null_low <= observed <= null_high:
        span = "" if n is None else " on {} {}".format(n, unit)
        return ("On {}, {}: {:.3f} sits inside the {:.3f}–{:.3f} a signal carrying no "
                "information reaches{}.").format(subject, CANNOT_TELL, observed,
                                                 null_low, null_high, span)
    return None


#: THE FOUR THINGS A CONCORDANCE CAN SAY, named here before any of them is computed, because the
#: cause split follows from the definition and never the other way round. Held as a tuple so a
#: reading nobody enumerated cannot appear on a surface.
#:
#: The first two are the pair a reader conflates and they are OPPOSITE claims: one says the
#: instrument returned nothing, the other says the instrument had nothing to return with. The last
#: two exist so this is keyed to the PROPERTY rather than to today's answer -- on the day the arm
#: starts ranking its departures correctly the same code says so and nobody edits a sentence.
CONCORDANCE_READINGS = (
    "this_run_cannot_tell",
    "not_distinguishable_from_no_information",
    "worse_than_chance",
    "better_than_chance",
)


def concordance_reading(*, subject: str, observed, null_low, null_high, n=None,
                        unit: str = "decisions") -> dict:
    """WHICH of the four readings this figure supports, and the words for it.

    WHY THIS EXISTS BESIDE `cannot_tell_sentence` AND NOT INSTEAD OF IT. That function answers one
    question -- may a reader take this figure as carrying information? -- and answers it correctly
    for BOTH of the cases where the answer is no. It returns the same sentence when the interval
    swallows the reading and when there is no interval at all, and its docstring says so on
    purpose: to a reader deciding whether to believe a number, those are one answer.

    They are not one answer to a reader deciding what to DO. "The figure is flat on the sample we
    have" is fixed by a larger book; "this run carries no interval" is fixed by running something,
    costs nothing to establish, and says nothing whatever about the method. A page that renders one
    sentence for both tells the reader the wrong one half the time.

    AND THE DIRECTION IS A THIRD THING AGAIN. A concordance BELOW its own interval is not a weak
    result -- it is a strong result pointing the other way: the price ranks the value it produced
    in the wrong order, which is the director's own case for what a maximiser on a one-sided
    objective does. Publishing that as "we cannot tell" because it failed to clear upward would be
    the flattering error, and the flattering error is the one nobody checks.

    THE INSIDE/OUTSIDE TEST IS NOT REPEATED HERE. `cannot_tell_sentence` is asked, and its answer
    is what routes the first two readings, so the sentence and the key cannot come apart. Only the
    SIDE is decided below, and only once the bounds are known to exist.

    Returns `reading` (one of `CONCORDANCE_READINGS`), `distinguishable_from_no_information`
    (True/False/None -- None is "we could not ask", never False), and `sentence`, which is always
    a string: there is no state of this function in which a surface has nothing to render.
    """
    cannot = cannot_tell_sentence(subject=subject, observed=observed, null_low=null_low,
                                  null_high=null_high, n=n, unit=unit)
    undecidable = observed is None or null_low is None or null_high is None
    if undecidable:
        return {"reading": "this_run_cannot_tell",
                "distinguishable_from_no_information": None,
                "sentence": cannot}
    if cannot is not None:
        return {"reading": "not_distinguishable_from_no_information",
                "distinguishable_from_no_information": False,
                "sentence": cannot}
    span = "" if n is None else " on {} {}".format(n, unit)
    below = observed < null_low
    return {
        "reading": "worse_than_chance" if below else "better_than_chance",
        "distinguishable_from_no_information": True,
        "sentence": (
            "On {subject}, this run reads {word} chance: {obs:.3f} sits {side} the "
            "{lo:.3f}–{hi:.3f} a signal carrying no information reaches{span}. {gloss}"
        ).format(
            subject=subject, obs=observed, lo=null_low, hi=null_high, span=span,
            word="WORSE than" if below else "BETTER than",
            side="BELOW" if below else "ABOVE",
            gloss=(
                "The ranking is real and INVERTED -- which is not the same as carrying nothing, "
                "and is the worse of the two findings."
                if below else
                "The ranking carries information at this sample size.")),
    }


#: The multiples of the run's own sample the published curve is drawn at. Multiples rather than
#: absolute counts so the curve always brackets the sample it describes: a fixed ladder of round
#: numbers would sit entirely above or entirely below a small n and the reader could not place the
#: run on its own curve.
CURVE_MULTIPLES = (1, 2, 4, 8)

#: The departures from 0.5 the floor is quoted at. Fixed, and NOT derived from the observed
#: value: a ladder keyed to today's answer moves every run and stops being a scale a reader can
#: hold. The observed departure is added to this ladder as one more row, labelled.
FLOOR_EXCESSES = (0.15, 0.10, 0.05, 0.03, 0.02)

#: Scored decisions come from settled account-terms, so the book that would supply more of them is
#: the SETTLED book, and its ceiling is a memory budget on this machine rather than anything about
#: the world's housing stock. Named here so the attainability verdict says which kind of ceiling
#: it hit.
#:
#: THE WINDOW IS A FORMAT SLOT AND NOT A DEFAULT (2026-09-10). Until today this constant read
#: `years=1` and the number it produced -- 632 accounts -- was compared against a requirement
#: stated in accounts counted over the run's WHOLE window. `settled_book_ceiling` divides by
#: `years`, so the same call returns 63 at `years=10`, fewer than the 164 accounts the book
#: demonstrably settles. Two numbers that are not the same quantity, with their ratio published as
#: a verdict. The window now has to be supplied by whoever knows it, and there is no value here
#: for it to fall back to.
CEILING_SOURCE = "simulation.premise_population.settled_book_ceiling(years={years})"

#: What the ceiling counts, in one clause, so the population half of the mismatch above cannot be
#: read past either: the ceiling bounds the SETTLED BOOK, and a floor is stated in accounts that
#: carried a SCORED DECISION -- a subset of it. On the run this page publishes, 72 of 164.
CEILING_COUNTS = (
    "billing accounts the settlement path can hold at all, over ONE window of the length it is "
    "read at -- not accounts that carry a scored decision, which is a subset of them")


def _sqrt_n_law_note(n: int, k: float) -> str:
    return (
        "The half-width of the permutation null falls as {k:.3f} / sqrt(n). The constant is "
        "MEASURED, not assumed: it is half this run's own permuted interval times sqrt({n}), so "
        "the curve passes through the run's own reading by construction and the permutation is "
        "the only source. The 1/sqrt(n) law itself is checked by permutation at four sample "
        "sizes under the run's own seed in "
        "`tests/tools/test_the_concordance_curve_says_what_it_could_have_seen.py`. Because the "
        "constant is taken at n={n} it carries that sample's own small-n inflation, so every "
        "decision count below is an UPPER bound on what would be needed."
    ).format(k=k, n=n)


def settled_book_ceiling_accounts(*, window_years: int | None = None) -> dict:
    """How many accounts the settled book can hold at all, or an explicit refusal.

    LAZY IMPORT ON PURPOSE. This module is imported by the publishing lane, and a top-level
    `simulation` import here would put the world's package on that lane's import graph for a
    number only one function needs.

    The ceiling is an UPPER bound -- `settled_book_ceiling` documents both of its per-unit costs
    as floors -- which is the direction that makes an "unattainable" verdict safe: the real
    affordable book is smaller than this, so a floor this ceiling cannot reach is a floor no
    attainable book reaches either. It is NOT the direction that makes an *attainable* verdict
    safe, and that asymmetry is enforced in `_attainability` below rather than left to a reader
    of this docstring.

    `window_years` IS REQUIRED AND HAS NO DEFAULT. The figure is per customer-YEAR: the same call
    returns 632 at one year and 63 at ten. A caller that does not know the window its own accounts
    were counted over cannot use this number for anything, and saying so is the answer.
    """
    if window_years is None:
        return {"available": False,
                "reason": ("the settled-book ceiling is stated per customer-YEAR and the window "
                           "these accounts are counted over was not supplied, so there is no "
                           "window to read it at -- 632 accounts for a one-year book and 63 for "
                           "a ten-year one are the same function, and picking one would be "
                           "picking an answer")}
    if not isinstance(window_years, int) or window_years <= 0:
        return {"available": False,
                "reason": "the window supplied was not a positive whole number of years"}
    try:
        from simulation.premise_population import settled_book_ceiling
        ceiling = settled_book_ceiling(years=window_years)
    except Exception as exc:  # noqa: BLE001 -- any failure here is one answer: we cannot tell
        return {"available": False,
                "reason": "the settled-book ceiling could not be read ({}: {})".format(
                    type(exc).__name__, exc)}
    accounts = ceiling.get("max_customers")
    if not isinstance(accounts, int) or accounts <= 0:
        return {"available": False,
                "reason": "the settled-book ceiling returned no usable customer count"}
    return {
        "available": True,
        "accounts": accounts,
        "window_years": window_years,
        "source": CEILING_SOURCE.format(years=window_years),
        "bound_kind": ceiling.get("bound_kind"),
        "what_it_counts": CEILING_COUNTS,
        "what_binds": (
            "the settlement path's memory budget on this machine, not the world's housing stock "
            "-- the world has homes to spare and the settled book is what cannot be grown"),
        "why_it_is_safe_to_cite": (
            "both per-unit costs behind it are measured floors, so the affordable book is "
            "SMALLER than this number and never larger -- which lets it REFUSE a requirement and "
            "never certify one"),
    }


def detectability(*, observed, null_low, null_high, n, accounts=None, window_years=None,
                  settled_book_accounts=None, ceiling: dict | None = None) -> dict:
    """WHAT THIS READING COULD HAVE DETECTED, beside what it did.

    WHY THIS EXISTS. `cannot_tell_sentence` above publishes that the concordance sits inside its
    null. That is half a result. A null result from an instrument that had no power to return
    anything else is not evidence of no effect -- it is evidence of no instrument, and the two
    read identically on the page. The flagship figure was published for four days as
    "0.517, inside 0.429-0.572, we cannot tell" with nothing anywhere saying that 0.572 was the
    SMALLEST value the run could ever have called, so no reader could tell a flat method from an
    unresolvable one.

    NOT A SECOND MEASUREMENT OF THE NULL. Every number here is arithmetic on the interval the run
    already permuted and published: the detectable departure IS half that interval, and the scale
    constant IS that half-width times sqrt(n). There is no second permutation and therefore
    nothing that can drift away from the figure it qualifies -- which is the objection that made
    `_method_skill` read the spread rather than recompute it.

    THE FLOOR IS A DIAGNOSTIC AND NEVER A TARGET (R12). A book grown to clear this floor would be
    the failure this arm exists to be able to report. "No attainable book on this world reads an
    effect this small" is a complete answer and it is published in those words.

    THE ATTAINABILITY VERDICT IS ONE-SIDED, AND UNTIL 2026-09-10 IT WAS NOT (see `_attainability`).
    The page served, twice, "The settled book can hold 632 accounts, so a book this world can
    supply does reach it". Three separate things were wrong with the comparison behind it and each
    on its own is enough: the ceiling was read at `years=1` against a requirement in accounts
    counted over the run's whole window; it counts SETTLED accounts against a requirement in
    accounts that carried a SCORED DECISION, which is 72 of 164 of them here; and it is an UPPER
    bound, so `needed <= ceiling` establishes nothing at all -- the affordable book is smaller
    than the ceiling, and possibly smaller than the requirement. Only the refusal was ever safe.
    `window_years` and `settled_book_accounts` are what the first two need, and both refuse rather
    than default.
    """
    if observed is None or null_low is None or null_high is None or not n or n < 3:
        return {"available": False,
                "reason": ("this run carries no permuted interval and no sample size, so what it "
                           "could have detected is undecidable rather than wide")}
    half_width = (null_high - null_low) / 2.0
    if half_width <= 0:
        return {"available": False,
                "reason": "the permuted interval has no width, so no scale constant can be read"}
    k = half_width * math.sqrt(n)
    observed_excess = abs(observed - 0.5)
    per_account = (n / accounts) if accounts else None

    def decisions_for(excess):
        """How many scored decisions before a departure of `excess` clears the null."""
        return int(math.ceil((k / excess) ** 2)) if excess and excess > 0 else None

    def accounts_for(decisions):
        return (int(math.ceil(decisions / per_account))
                if decisions is not None and per_account else None)

    ceiling = (settled_book_ceiling_accounts(window_years=window_years)
               if ceiling is None else ceiling)
    ceiling_accounts = ceiling.get("accounts") if ceiling.get("available") else None

    # THE POPULATION BRIDGE, and it is a separate refusal from the window one. `accounts` counts
    # the accounts that carried a SCORED DECISION; the ceiling counts the SETTLED BOOK those were
    # drawn from. On this run they are 72 and 164, so a requirement stated in the first understates
    # the book by 2.3x when read against the second. Neither number is wrong; their ratio is not a
    # quantity unless one is first carried into the other's population, and that carry needs the
    # run's own settled book.
    settled_per_scored = ((settled_book_accounts / accounts)
                          if settled_book_accounts and accounts else None)

    def settled_accounts_for(scored_accounts):
        """A requirement in scored-decision accounts, restated in settled-book accounts."""
        return (int(math.ceil(scored_accounts * settled_per_scored))
                if scored_accounts is not None and settled_per_scored else None)

    # ...and the same bridge the other way, so the ceiling can be put on the decisions curve at
    # all. Carrying `ceiling_accounts * per_account` straight across -- which is what this did
    # until 2026-09-10 -- multiplies a settled-book count by a decisions-per-SCORED-account rate.
    ceiling_decisions = (int(ceiling_accounts / settled_per_scored * per_account)
                         if ceiling_accounts and per_account and settled_per_scored else None)
    ceiling_excess = (k / math.sqrt(ceiling_decisions)
                      if ceiling_decisions and ceiling_decisions >= 3 else None)

    def _attainability(needed_accounts):
        """ONE-SIDED BY CONSTRUCTION. Returns (verdict, why) with verdict in {False, None}.

        `True` IS NOT A VALUE THIS FUNCTION CAN RETURN, and that is the repair. The ceiling is an
        UPPER bound on the book -- its own block says so, in the words "the affordable book is
        SMALLER than this number and never larger". A requirement that EXCEEDS it therefore
        exceeds every attainable book, which is a real refusal. A requirement that fits under it
        is a requirement fitting under a number the real book does not reach, which is not
        evidence of anything. The old code returned `needed <= ceiling` and the page published the
        `True` side of it as "a book this world can supply does reach it".

        None is "we cannot tell" and carries the reason that made it so, so a reader meets the
        gap rather than a bare absence.
        """
        if needed_accounts is None:
            return None, ("this reading sits on no-information, so there is no requirement to put "
                          "against a ceiling")
        if ceiling_accounts is None:
            return None, ("the settled book's own ceiling could not be read: "
                          + str(ceiling.get("reason") or "no reason given"))
        needed_settled = settled_accounts_for(needed_accounts)
        if needed_settled is None:
            return None, ("the run does not declare the settled book its scored accounts were "
                          "drawn from, so the requirement cannot be restated in the population "
                          "the ceiling counts -- and the two are not the same set")
        if needed_settled > ceiling_accounts:
            return False, None
        return None, (
            "the requirement fits under the ceiling, and a ceiling that is an UPPER bound cannot "
            "certify that: the affordable book is SMALLER than {c:,} accounts by that block's own "
            "statement, so {r:,} fitting under it is not evidence the world can supply {r:,}. "
            "This verdict can only ever refuse.".format(c=ceiling_accounts, r=needed_settled))

    def within_ceiling(needed_accounts):
        """TRI-STATE, and now only two of the three are reachable. See `_attainability`."""
        return _attainability(needed_accounts)[0]

    curve = []
    for multiple in CURVE_MULTIPLES:
        size = n * multiple
        excess = k / math.sqrt(size)
        curve.append({
            "decisions_scored": size,
            "multiple_of_this_run": multiple,
            "detectable_excess": excess,
            "detectable_concordance": 0.5 + excess,
            "accounts_needed": accounts_for(size),
            "is_this_run": multiple == 1,
        })
    if ceiling_decisions and ceiling_decisions not in {row["decisions_scored"] for row in curve}:
        curve.append({
            "decisions_scored": ceiling_decisions,
            "multiple_of_this_run": ceiling_decisions / n,
            "detectable_excess": ceiling_excess,
            "detectable_concordance": 0.5 + ceiling_excess,
            "accounts_needed": ceiling_accounts,
            "is_this_run": False,
            "is_the_ceiling": True,
        })
    curve.sort(key=lambda row: row["decisions_scored"])

    floor = []
    rows = [(excess, False) for excess in FLOOR_EXCESSES]
    if observed_excess > 0:
        rows.append((observed_excess, True))
    for excess, is_observed in sorted(rows, key=lambda row: -row[0]):
        needed = decisions_for(excess)
        needed_accounts = accounts_for(needed)
        floor.append({
            "excess_over_no_information": excess,
            "concordance": 0.5 + excess,
            "decisions_needed": needed,
            "accounts_needed": needed_accounts,
            "within_the_settled_book_ceiling": within_ceiling(needed_accounts),
            "is_the_observed_effect": is_observed,
        })

    observed_needed = decisions_for(observed_excess) if observed_excess > 0 else None
    observed_accounts = accounts_for(observed_needed)
    attainable, why_no_verdict = _attainability(observed_accounts)
    return {
        "available": True,
        "decisions_scored": n,
        "accounts": accounts,
        "scored_decisions_per_account": per_account,
        # THE HEADLINE, and the only number a reader has to carry: the smallest departure from
        # 0.5 this run could ever have called. Measured, not modelled -- it is half the interval
        # the run permuted.
        "detectable_excess": half_width,
        "detectable_concordance": 0.5 + half_width,
        "observed_excess": observed_excess,
        # How far short the reading fell of being callable AT ALL. Reported as a ratio because
        # the two are the same quantity on the same scale, which is the test this project keeps
        # failing before dividing.
        "observed_share_of_what_was_detectable": (
            observed_excess / half_width if half_width else None),
        "scale_constant": k,
        "curve": curve,
        "floor": floor,
        "the_book_this_would_need": {
            "decisions_needed_for_the_observed_effect": observed_needed,
            "accounts_needed_for_the_observed_effect": observed_accounts,
            # ...RESTATED IN THE POPULATION THE CEILING COUNTS, because the line above is in
            # scored-decision accounts and nothing on this page may be divided by the ceiling
            # until it has been carried across. None when the run does not declare its book.
            "settled_accounts_needed_for_the_observed_effect": settled_accounts_for(
                observed_accounts),
            "scored_accounts_this_run": accounts,
            "settled_book_this_run": settled_book_accounts,
            "settled_accounts_per_scored_account": settled_per_scored,
            "what_each_account_count_counts": (
                "`accounts_needed_...` is in accounts that carry a SCORED DECISION -- what the "
                "instrument consumes. `settled_accounts_needed_...` is the same requirement in "
                "the accounts the settlement path must HOLD, which is the population the ceiling "
                "bounds. They differ by this run's own ratio between the two and the comparison "
                "is only a quantity in the second."),
            "settled_book_ceiling": ceiling,
            "scored_decisions_at_the_ceiling": ceiling_decisions,
            "detectable_excess_at_the_ceiling": ceiling_excess,
            "detectable_concordance_at_the_ceiling": (
                0.5 + ceiling_excess if ceiling_excess is not None else None),
            # FALSE OR NULL, NEVER TRUE. `_attainability` explains why an upper bound has only
            # one safe direction, and `why_no_attainability_verdict` names which cause fired.
            "the_observed_effect_is_attainable": attainable,
            "why_no_attainability_verdict": why_no_verdict,
            "the_verdict_is_one_sided": (
                "This page can say a requirement is out of reach and can say it cannot tell. It "
                "cannot say a requirement IS in reach, because the only bound it has is an upper "
                "one and an upper bound refuses or is silent."),
            "what_would_make_a_verdict_available": [
                "the window the run's accounts are counted over, declared by the producer -- the "
                "ceiling is per customer-year and is a different number at every window",
                "the run's own settled book beside its scored-account count, so a requirement in "
                "one population can be restated in the other",
                "a LOWER bound on the affordable book -- an upper bound can never certify reach, "
                "so no amount of the two above turns this verdict positive",
            ],
            "accounts_short": (
                settled_accounts_for(observed_accounts) - ceiling_accounts
                if attainable is False and observed_accounts and ceiling_accounts else None),
            # WHY A LARGER BOOK IS THE ONLY LEVER. The funnel already published beside this says
            # the 32 unscored decisions are eligibility, not a join we failed to make: the world
            # never billed under the price that was chosen, so no code we write recovers them.
            "why_only_a_larger_book": (
                "the drop-out funnel classes the unscored decisions as eligibility -- the world "
                "billed nothing under the price that was chosen -- so no widening of the join "
                "and no sourcing work adds a decision here. Only a larger settled book does."),
        },
        "method": _sqrt_n_law_note(n, k),
        "it_is_a_diagnostic": (
            "R12. This floor is a bound on what the instrument can see and NEVER a book size to "
            "grow towards. A book enlarged until this arm returns a direction is the failure "
            "this arm was built to be able to report."),
        "sentence": _detectability_sentence(
            half_width=half_width, observed=observed, observed_excess=observed_excess, n=n,
            needed=observed_needed, needed_accounts=observed_accounts,
            needed_settled=settled_accounts_for(observed_accounts),
            ceiling_accounts=ceiling_accounts, ceiling_decisions=ceiling_decisions,
            ceiling_excess=ceiling_excess, attainable=attainable,
            why_no_verdict=why_no_verdict),
    }


def _upper_first(text: str) -> str:
    """Sentence-case a reason written as a clause, WITHOUT touching the rest of it.

    `str.capitalize` lowercases everything after the first character, which would flatten the
    deliberate capitals this module writes into its refusals -- UPPER, SETTLED, SCORED. Those
    capitals are the whole point of the sentences they sit in.
    """
    return text[:1].upper() + text[1:] if text else text


def _detectability_sentence(*, half_width, observed, observed_excess, n, needed, needed_accounts,
                            needed_settled, ceiling_accounts, ceiling_decisions, ceiling_excess,
                            attainable, why_no_verdict) -> str:
    """The words, derived from the verdict rather than sitting beside it.

    Three sentences, and the third is the one the director asked for: whether any book this world
    can supply reaches the floor. It is composed from `attainable`, so a prose claim of
    unattainability cannot survive the arithmetic saying otherwise.

    THE "DOES REACH IT" CLAUSE IS GONE (2026-09-10) and no branch here can produce it, because
    `_attainability` has no branch that returns True. What replaces it is the reason: "we cannot
    tell" is a result, and it belongs in the sentence a reader gets rather than in a key beside
    it. The reason travels from the arithmetic for the same reason the verdict does.
    """
    head = (
        "On the {n} decisions it had, the smallest departure from 0.5 this instrument could have "
        "called is {hw:.3f} — a concordance of {hi:.3f} or {lo:.3f}. It read {obs:.3f}, a "
        "departure of {oe:.3f}, about {share:.0%} of that."
    ).format(n=n, hw=half_width, hi=0.5 + half_width, lo=0.5 - half_width, obs=observed,
             oe=observed_excess, share=(observed_excess / half_width) if half_width else 0)
    if needed is None:
        return head + (" The reading sits exactly on no-information, so there is no departure to "
                       "size a book against.")
    body = (" Reading a departure that small needs about {needed:,} scored decisions{acc}."
            ).format(needed=needed,
                     acc="" if not needed_accounts else
                         " — roughly {:,} accounts carrying one, at this run's rate{bk}".format(
                             needed_accounts,
                             bk="" if not needed_settled else
                                ", drawn from a settled book of about {:,}".format(needed_settled)))
    if attainable is None:
        return head + body + (
            " Whether this world can supply that book, this page cannot say. "
            + _upper_first(str(why_no_verdict).rstrip(". "))
            + ". It is a bound on the instrument either way, and never a book to grow towards.")
    return head + body + (
        " The settled book tops out at {c:,} accounts{cd}. No attainable book on this world can "
        "read an effect the size of the one measured."
    ).format(c=ceiling_accounts,
             cd="" if not ceiling_decisions else
                " — about {:,} scored decisions, which resolves {:.3f} at best".format(
                    ceiling_decisions, ceiling_excess))


def inference_claim(provenance: dict | None, skill: dict | None = None) -> dict:
    """THE ONE PLACE THE RULE IS APPLIED. Composed from two `is True` tests and nothing else.

    Returns the flags a machine reader consults AND the sentence a human reader gets, derived
    from the same verdict so they cannot disagree. The sentence always carries the interval
    whenever it names the reading, which is the director's second condition: the gap and the
    skill claim "must not appear in one sentence without the null interval beside them".
    """
    skill = skill_reading() if skill is None else skill
    independent = _independence(provenance)
    clears = skill.get("clears_the_null")
    # THE COMPOSITION. `is True` on both legs, so None -- the fail-closed value on either side --
    # can never satisfy it. `and` not `or`: independence is necessary and not sufficient, which
    # is the entire correction.
    supported = (independent is True) and (clears is True)
    distance = record_distance(provenance)
    return {
        "rule": THE_RULE,
        "the_gap_is_a_measurement": True,
        "sides_are_independent": independent,
        "the_method_clears_its_null": clears,
        "publishable_as_evidence_of_skill": supported,
        "skill_reading": skill,
        # KEYED `record_distance`, NOT `accuracy`. The old key named the reading the determination
        # withdrew, and a consumer reading `claim["accuracy"]` would be asking a question this
        # module no longer answers -- a KeyError there is the correct outcome, not a regression.
        "record_distance": distance,
        "sentence": _sentence(independent, clears, skill, distance, supported),
    }


def _interval_phrase(skill: dict) -> str:
    """The interval, in the same clause as the reading it bounds, or an explicit absence."""
    if not skill.get("available"):
        return "with no interval available to weigh it against"
    return ("{:.3f} against {:.3f}–{:.3f} for a signal carrying no information, on {} "
            "decisions").format(skill["concordance"], skill["null_95_low"], skill["null_95_high"],
                                skill.get("decisions_scored"))


def _sentence(independent, clears, skill, distance, supported) -> str:
    """The prose, DERIVED from the flags above rather than written beside them.

    Every branch that mentions the method's reading mentions its interval in the same breath,
    and every branch that is not `supported` contains the words the director specified. Every
    branch that quotes the distance to the record carries `record_distance`'s clause, which says
    in the same sentence that the distance is not an accuracy reading.
    """
    tail = (" " + distance["clause"]) if distance.get("applies") else ""
    if independent is not True:
        why = ("the two sides descend from one source, so the gap is two fits of one series"
               if independent is False else
               "whether the two sides are independent could not be established, and an "
               "unavailable check is a failed check")
        return ("The belief-versus-truth gap is a measurement and not evidence of skill: {}. On "
                "whether the method carries information at all, {} ({}).{}").format(
            why, CANNOT_TELL, _interval_phrase(skill), tail)
    if clears is not True:
        why = ("the method's ranking sits INSIDE the interval a random signal produces"
               if clears is False else
               "this run carries no decidable reading of the method: " + str(skill.get("why")))
        return ("The two sides are independent, which removes the objection that we were "
                "measuring our own reflection -- it does not establish that the company knows "
                "anything. The gap is published as a measurement only: {}, so on whether the "
                "method works {} ({}).{}").format(why, CANNOT_TELL, _interval_phrase(skill), tail)
    return ("The two sides are independent and the method's own ranking clears the interval a "
            "random signal produces ({}), so the gap is quotable as evidence that the company "
            "inferred something.{}").format(_interval_phrase(skill), tail)


if __name__ == "__main__":  # pragma: no cover - operator surface
    from tools.couple_value_based_pricing import shared_calibration_holds
    claim = inference_claim(shared_calibration_holds())
    print(json.dumps({k: v for k, v in claim.items() if k != "rule"}, indent=1))
