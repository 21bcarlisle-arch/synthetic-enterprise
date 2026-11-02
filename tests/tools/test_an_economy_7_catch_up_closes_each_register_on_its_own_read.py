"""An actual read on an Economy 7 meter closes each register on its own index, not on a share of the total.

The bb58608b91 book refused its publish on INV_READ_MONOTONIC 2 (PROS-2017-0336 Night, -795;
PROS-2024-0010 Night, -170) and INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS 1. At the actual read
the ledger split the total catch-up over the printed bands by this month's printed kWh, so a
downward catch-up whose over-estimate sat on Day was taken mostly from Night, the band with most of
this month's use, and Night closed below its last actual read. A read gives each register its own
index; the assembly now passes each register's advance since the last read
(`register_advance_kwh`), and the ledger closes each band on it.

Mutation: drop the `own_read` branch in `catchup_shares` -> the first test reds (Night closes at
16,546.0, below May's 18,563.9). The second test is the other side of the partition: with no
register reads the split is the printed-share one it was.
"""
import pytest

from tools.generate_billing_ledger import catchup_shares

_MAY_READ = {"Day": 5000.0, "Night": 18563.9}
# A summer of estimates that put 6,000 kWh on Day and 1,000 on Night.
_OPENING = {"Day": 11000.0, "Night": 19563.9}
# November's printed use, 93% Night, and each register's index at November's actual read.
_PRINTED = {"Day": 50.0, "Night": 650.0}
_AT_READ = {"Day": 6100.0, "Night": 21213.9}


def _close(read_indices):
    bands = [{"label": label, "consumption_kwh": _PRINTED[label]} for label in ("Day", "Night")]
    openings = [_OPENING[b["label"]] for b in bands]
    band_advance = round(sum(_AT_READ.values()) - sum(openings), 1)
    shares = catchup_shares(bands, band_advance, openings, read_indices)
    assert sum(shares) == pytest.approx(band_advance - sum(_PRINTED.values()))
    return {b["label"]: round(o + b["consumption_kwh"] + s, 1)
            for b, o, s in zip(bands, openings, shares)}


def test_each_register_closes_on_its_own_read_and_never_below_the_last():
    closing = _close([_AT_READ["Day"], _AT_READ["Night"]])

    assert closing == pytest.approx(_AT_READ)
    assert all(closing[r] >= _MAY_READ[r] for r in closing)


def test_without_register_reads_the_split_follows_the_printed_share():
    closing = _close(None)

    # The defect the read-led split removes, kept visible: this is the shape that refused the publish.
    assert closing["Night"] < _MAY_READ["Night"]
    assert sum(closing.values()) == pytest.approx(sum(_AT_READ.values()))


def test_a_band_the_read_did_not_give_falls_back_to_the_printed_share():
    assert _close([_AT_READ["Day"], None]) == _close(None)
