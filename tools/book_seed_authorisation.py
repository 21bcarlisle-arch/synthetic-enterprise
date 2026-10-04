"""Whether a non-default book seed may run: the EP17 check, in a module that assembles no book.

REUSE: tools/book_seed_authorisation.py
CLASS: CUSTOM
INDEX: the check is `run_value_cycle_ab.book_seed_authorisation_refusal`, moved here verbatim and
       re-exported there. It could not be reused in place: `run_value_cycle_ab` imports
       `simulation.run_phase4c_on_phase2b` at module scope, which calls `live_population()` at
       import and so fixes the book. Any caller that imported the check from there to decide
       whether to rebind the seed would freeze the default book before the rebind. This module
       imports nothing from `simulation/` at module scope, so a caller can ask it first.

A book seed other than the default puts the company through a different cast of households. That
is `EP17_varied_population_draw`, which is R13 curriculum and the director's alone. The check
refuses until his record exists and lists the seed, and nothing here ever writes that record.
"""
from __future__ import annotations

import json
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]

#: The atom whose ruling a non-default book seed needs, named in every refusal it causes.
BOOK_SEED_ATOM = "EP17_varied_population_draw"

#: Where the director's ruling would live, in `population_draw_activation.json`'s shape. It does
#: NOT exist as of 2026-09-30, and its absence is what keeps every book-seed door refusing.
BOOK_SEED_AUTHORISATION = (
    PROJECT_DIR / "docs" / "design" / "curriculum" / "varied_population_draw_activation.json")


def default_book_seed() -> int:
    """The seed every published run's book is drawn at, read off the module that owns it.

    `simulation.live_population` only declares the seed at import; it draws no book. Read this
    BEFORE any rebind, or it returns the rebound value.
    """
    from simulation.live_population import _DEFAULT_BASE_SEED
    return _DEFAULT_BASE_SEED


def book_seed_authorisation_refusal(seeds: list[int], record: Path | None = None) -> str | None:
    """Why this family may not run without the director, or None if it may.

    Only the DEFAULT seed is free: it is the book every published run already uses. Any other
    seed needs a record that is activated and lists THAT seed. A general "yes, vary the book"
    does not authorise every seed anyone later types.
    """
    default = default_book_seed()
    foreign = sorted({int(s) for s in seeds} - {default})
    if not foreign:
        return None
    record = BOOK_SEED_AUTHORISATION if record is None else record
    head = ("book seed(s) {} are not the default {}. A different book seed draws a different "
            "cast of households, which is {} -- R13 curriculum, the director's alone".format(
                foreign, default, BOOK_SEED_ATOM))
    try:
        doc = json.loads(record.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return ("{}. No ruling is recorded: {} does not exist. It is written only on his word, "
                "in the shape of population_draw_activation.json, and never by this tool."
                .format(head, record))
    except (OSError, ValueError) as exc:
        return "{}. {} is unreadable ({}), so no ruling can be read from it.".format(
            head, record, exc)
    try:
        activated = doc["activated"]["value"] is True
        authority = str(doc["_meta"]["authority"]).strip()
        listed = {int(s) for s in doc["base_seeds"]["value"]}
    except (KeyError, TypeError, ValueError) as exc:
        return ("{}. {} is not in population_draw_activation.json's shape (needs _meta.authority, "
                "activated.value, base_seeds.value; {!r}).".format(head, record, exc))
    if not activated or not authority:
        return "{}. {} exists but is not activated with the director's words.".format(
            head, record)
    unlisted = sorted(set(foreign) - listed)
    if unlisted:
        return "{}. {} does not list seed(s) {}.".format(head, record, unlisted)
    return None
