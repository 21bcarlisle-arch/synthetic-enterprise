"""F1b — COMPANY comms (in front of the epistemic wall, allowed to be wrong).

The supplier's outbound-messaging brain: a situation-keyed, segment-gated
message generator (``conversation_generator``) and a per-customer Bayesian
susceptibility estimator (``susceptibility_estimator``) that learns which
levers land on which customer FROM OBSERVED REPLIES ALONE.

Both build to the seam contract ``interface/contracts/conversation_seam.py``
and import NOTHING from ``sim``/``simulation``: the customer's true hidden
``FramingSusceptibility``/``ToneSusceptibility`` scalars live behind the wall
and never reach this package. The company's belief is explicitly permitted to
diverge from that truth -- the belief-vs-truth GAP is F1c's score
(``tests/harness/test_conversation_gap.py``, not this package).
"""
