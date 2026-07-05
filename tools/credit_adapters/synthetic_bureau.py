"""SyntheticBureauAdapter -- calibrated synthetic credit-bureau adapter.

Models a purchased, imperfect credit signal: the bureau observes an applicant's
true creditworthiness (SIM ground truth, never exposed to company/** code) through
noise, then thresholds the noisy read into an accept/reject decision. This creates
a genuine, non-trivial false-decline / false-accept divergence -- the point of the
epistemic boundary (see docs/design/PROCESS_MODEL.md Section 3).

Calibration (docs/market_research/findings/acquisition_funnel_benchmarks.md Section 2,
application_to_credit_check_pass targets: resi ~90-97%, SME/I&C ~80-92%, both L confidence):
5,000+ seed Monte Carlo per segment gave resi ~93.7% pass / ~5.8% disagreement with ground
truth, ic ~86.5% pass / ~9.9% disagreement -- both mid-range of the target bands, with a
real (not near-zero, not dominant) disagreement rate.
"""
from __future__ import annotations
import random
from tools.credit_bureau_port import CreditCheckResult

TRUE_CREDITWORTHY_THRESHOLD = {"resi": 0.08, "ic": 0.18}
BUREAU_NOISE_SIGMA = {"resi": 0.10, "ic": 0.12}
BUREAU_THRESHOLD = {"resi": 0.04, "ic": 0.12}

_SEGMENT_ALIASES = {
    "resi": "resi",
    "residential": "resi",
    "domestic": "resi",
    "ic": "ic",
    "i&c": "ic",
    "sme": "ic",
    "business": "ic",
}


def _normalize_segment(segment: str) -> str:
    return _SEGMENT_ALIASES.get(segment.lower(), "resi")


def _score_band(noisy_score: float, threshold: float) -> str:
    if noisy_score < threshold:
        return "decline"
    if noisy_score < threshold + 0.20:
        return "sub_prime"
    if noisy_score < threshold + 0.45:
        return "near_prime"
    return "prime"


class SyntheticBureauAdapter:
    def check_credit(self, applicant_id: str, segment: str, seed: str) -> CreditCheckResult:
        seg = _normalize_segment(segment)
        combined_seed = f"{applicant_id}_{seg}_{seed}"
        true_score = random.Random(f"credit_true_{combined_seed}").random()
        true_creditworthy = true_score >= TRUE_CREDITWORTHY_THRESHOLD[seg]
        noise = random.Random(f"credit_noise_{combined_seed}").gauss(0, BUREAU_NOISE_SIGMA[seg])
        noisy_score = true_score + noise
        threshold = BUREAU_THRESHOLD[seg]
        passed = noisy_score >= threshold
        return CreditCheckResult(
            passed=passed,
            score_band=_score_band(noisy_score, threshold),
            true_creditworthy=true_creditworthy,
        )
