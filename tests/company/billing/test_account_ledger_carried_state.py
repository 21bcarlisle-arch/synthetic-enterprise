"""The ledger's carried state answers exactly what a full replay answers (director, 2026-10-09).

`AccountLedger` carries its replay-ordered events and memoises allocations so a read costs what
changed, not the whole history. Each test here names the defect it catches; the reference
answer is always a FRESH ledger given the same events, which carries nothing.
"""
import datetime as dt
import random

from company.billing.account_ledger import AccountLedger, LedgerEvent, LedgerEventType

TT = dt.datetime(2024, 1, 1, 12, 0, 0)
D0 = dt.date(2024, 1, 1)


def _ev(eid, kind, amount, day, ref=None, remittance=()):
    return LedgerEvent(eid, "A", kind, amount, D0 + dt.timedelta(days=day), TT,
                       invoice_ref=ref, remittance=tuple(remittance))


def _fresh(events):
    led = AccountLedger("A")
    for e in events:
        led.post(e)
    return led


def _replay_without_carry(events, disputed, as_of):
    """The allocation rule as it read before anything was carried: every event admitted by
    `as_of` replayed in order, the oldest-first pool re-sorted for every payment. An oracle
    for the rule, deliberately naive, so a defect in the carried walk cannot hide in both."""
    events = sorted((e for e in events if as_of is None or e.valid_time <= as_of),
                    key=lambda e: (e.valid_time, e.event_id))
    T = LedgerEventType
    items = {}
    for e in events:
        if e.event_type in (T.BILL_DEBIT, T.ADJUSTMENT_DEBIT) and e.invoice_ref:
            if e.invoice_ref not in items:
                items[e.invoice_ref] = [e.invoice_ref, round(e.amount_gbp, 2), e.valid_time, 0.0,
                                        e.invoice_ref in disputed]
            else:
                items[e.invoice_ref][1] = round(items[e.invoice_ref][1] + e.amount_gbp, 2)
    for e in events:
        if e.event_type in (T.ADJUSTMENT_CREDIT, T.WRITE_OFF_CREDIT) and e.invoice_ref in items:
            items[e.invoice_ref][3] = round(items[e.invoice_ref][3] + e.amount_gbp, 2)

    def owed(it):
        return round(it[1] - it[3], 2)
    allocations, unallocated = [], 0.0
    for e in events:
        if e.event_type != T.PAYMENT_CREDIT:
            continue
        left = round(e.amount_gbp, 2)
        targets = [items.get(r) for r in e.remittance]
        for it in [t for t in targets if t is not None]:
            if left <= 0.005:
                break
            if owed(it) <= 0.005:
                continue
            take = min(left, owed(it))
            it[3] = round(it[3] + take, 2)
            allocations.append((e.event_id, it[0], round(take, 2)))
            left = round(left - take, 2)
        if left > 0.005:
            pool = [it for it in sorted(items.values(), key=lambda i: (i[2], i[0]))
                    if owed(it) > 0.005 and not it[4]]
            for it in pool:
                if left <= 0.005:
                    break
                take = min(left, owed(it))
                it[3] = round(it[3] + take, 2)
                allocations.append((e.event_id, it[0], round(take, 2)))
                left = round(left - take, 2)
        if left > 0.005:
            unallocated = round(unallocated + left, 2)
    return ([(i[0], i[1], i[3], i[4]) for i in items.values()], round(unallocated, 2), allocations)


def _view(alloc):
    return ([(o.invoice_ref, o.issued_gbp, o.allocated_gbp, o.disputed) for o in alloc.open_items],
            alloc.unallocated_credit_gbp, alloc.allocations)


def test_a_post_after_a_read_is_seen_by_the_next_read():
    """Defect caught: the allocation memo is not cleared by `post()`, so a payment posted after
    the account was read is invisible to every later read of the same date."""
    led = _fresh([_ev("b1", LedgerEventType.BILL_DEBIT, 100.0, 0, "INV1")])
    on = D0 + dt.timedelta(days=30)
    assert led.allocate(as_of=on).total_outstanding_gbp == 100.0
    led.post(_ev("p1", LedgerEventType.PAYMENT_CREDIT, 60.0, 10))
    assert led.allocate(as_of=on).total_outstanding_gbp == 40.0


def test_a_backdated_post_is_replayed_in_its_place_not_appended():
    """Defect caught: the carried replay order appends a late event at the END, so a payment
    backdated before a later bill is applied after it and `events()` leaves (valid_time,
    event_id) order. The rare branch is asserted reachable first: the late post really does
    arrive after an event that sorts after it."""
    early_pay = _ev("p0", LedgerEventType.PAYMENT_CREDIT, 50.0, 5)
    later = [_ev("b1", LedgerEventType.BILL_DEBIT, 100.0, 0, "INV1"),
             _ev("b2", LedgerEventType.BILL_DEBIT, 70.0, 30, "INV2")]
    led = _fresh(later)
    led.events()                                   # carry the order before the late post
    assert (early_pay.valid_time, early_pay.event_id) < (later[-1].valid_time, later[-1].event_id)
    led.post(early_pay)
    ref = _fresh([early_pay] + later)
    assert [e.event_id for e in led.events()] == [e.event_id for e in ref.events()]
    for day in (4, 5, 29, 30, 400):
        on = D0 + dt.timedelta(days=day)
        assert _view(led.allocate(as_of=on)) == _view(ref.allocate(as_of=on))


def test_a_caller_mutating_its_allocation_does_not_reach_the_next_read():
    """Defect caught: `allocate` hands out the memoised result itself, so a caller that writes
    to an open item changes what every later reader of that account is told."""
    led = _fresh([_ev("b1", LedgerEventType.BILL_DEBIT, 100.0, 0, "INV1")])
    first = led.allocate()
    first.open_items[0].allocated_gbp = 100.0
    first.allocations.append(("x", "INV1", 100.0))
    again = led.allocate()
    assert again.open_items[0].allocated_gbp == 0.0
    assert again.allocations == []


def test_a_dated_read_between_two_events_reuses_the_replay_but_not_across_one():
    """Defect caught: the memo keyed on the wrong thing -- e.g. on the event count alone, so a
    read at a date BEFORE a held event is answered with the replay that admitted it."""
    led = _fresh([_ev("b1", LedgerEventType.BILL_DEBIT, 100.0, 0, "INV1"),
                  _ev("p1", LedgerEventType.PAYMENT_CREDIT, 100.0, 20)])
    after = led.allocate(as_of=D0 + dt.timedelta(days=25)).total_outstanding_gbp
    before = led.allocate(as_of=D0 + dt.timedelta(days=19)).total_outstanding_gbp
    assert (after, before) == (0.0, 100.0)


def test_carried_reads_equal_a_fresh_replay_over_random_histories():
    """Defect caught: any divergence between the carried path (incremental order, memo, the
    oldest-first walk started past its settled head) and the naive replay, over
    histories with remittances, disputes, credit/debit adjustments, write-offs and posts in
    random order with reads interleaved between them."""
    T = LedgerEventType
    kinds = [T.BILL_DEBIT] * 4 + [T.PAYMENT_CREDIT] * 4 + [
        T.ADJUSTMENT_CREDIT, T.ADJUSTMENT_DEBIT, T.WRITE_OFF_CREDIT, T.INTEREST_DEBIT]
    for seed in range(150):
        rnd = random.Random(seed)
        refs, events = [], []
        for i in range(rnd.randint(1, 40)):
            kind = rnd.choice(kinds)
            ref, rem = None, ()
            if kind == T.BILL_DEBIT:
                ref = f"INV{i:02d}"
                refs.append(ref)
            elif kind != T.PAYMENT_CREDIT and refs and rnd.random() < .7:
                ref = rnd.choice(refs)
            elif kind == T.PAYMENT_CREDIT and refs and rnd.random() < .3:
                rem = tuple(rnd.sample(refs, min(len(refs), 2)))
            events.append(_ev(f"E{rnd.randint(0, 999):03d}-{i}", kind,
                              round(rnd.uniform(0, 150), 2), rnd.randint(0, 300), ref, rem))
        if seed % 2:
            events.sort(key=lambda e: (e.valid_time, e.event_id))
        led = AccountLedger("A")
        for n, e in enumerate(events, 1):
            led.post(e)
            for _ in range(2):
                on = rnd.choice([None, D0 + dt.timedelta(days=rnd.randint(-3, 310))])
                disputed = set(rnd.sample(refs, min(len(refs), rnd.randint(0, 2))))
                naive = _replay_without_carry(events[:n], disputed, on)
                assert _view(led.allocate(disputed, on)) == naive, seed
                if on is not None:
                    assert led.events_through(on) == sorted(
                        (x for x in events[:n] if x.valid_time <= on),
                        key=lambda x: (x.valid_time, x.event_id))
