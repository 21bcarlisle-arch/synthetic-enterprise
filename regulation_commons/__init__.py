"""Regulation commons -- published facts every lane may read, owned by none.

REGULATION_COMMONS_DOCTRINE.md (CLAUDE.md, 2026-07-12): "the regulatory TEXT
is a shared commons, readable by every lane -- law is published in reality."

This package is the *neutral* home for that commons. It exists because the
alternative homes both break a wall:

* under ``company/**`` -- ``simulation/bacs_rails.py`` would have to import it,
  creating a SIM -> company edge (``simulation/self_rationing.py`` states the
  rule outright: WORLD/sim code "MUST NOT import ``company.*`` or ``saas.*``");
* under ``simulation/**`` -- the company would be reading a SIM internal to
  decide its own regulatory deadline, which is the epistemic wall itself.

So it lives outside both. The hard constraint on anything added here:

    IT PUBLISHES FACTS, NEVER JUDGEMENTS.

A bank-holiday date is a fact (GDS publishes it; every real supplier reads the
same one). "A complaint must be acknowledged within 3 working days" is a
JUDGEMENT about what the law requires, and stays in the lane that holds the
belief -- company compliance code, WORLD enforcement physics and HARNESS
validators each keep their own reading, so a company misreading the law stays
structurally possible (exactly as real suppliers get fined for).

Nothing in here may import ``company.*``, ``saas.*``, ``sim.*`` or
``simulation.*``. That direction of dependency is enforced by
``tests/regulation_commons/test_working_days.py``.
"""
