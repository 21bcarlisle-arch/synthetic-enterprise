**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The unpin item is spent; the next book is the sim-runner's, held behind the level-DD landing (2026-11-07)

Drawn at ~22:40 GMT as `unpin-the-shared-tree-then-grade-the-next-book`. Re-measured before any work:

- **The unpin is done.** 2e8ef7e472 (21:10 GMT) took the shared tree from fa915ac0d7 to f248d5ffa, and
  reconcile-watch has since fast-forwarded it. At 22:45 the shared tree's HEAD is e9d95aa8fe, which is origin/main.
  The four superseded paths the item names are identical to origin.
- **The book is not this seat's to start.** `sim-runner.service` runs the next book by itself. Its log since 21:34
  shows two kinds of deferral, both correct. One is "landings come before experiments", which is the level-DD fix
  (`fix-level-dd-households-dunned-per-bill`) sitting in its commit gate. The other is "imported files are not
  origin's" for `monthly_bill_assembly.py`, `domain_invariants.py` and `run_phase4c_on_phase2b.py`. At 22:45 all
  three equal origin on the shared tree. A book started by hand now would duplicate the runner's. It would also
  miss the level-DD fix, the only unexcepted red standing in the way of the 9 Nov publish. So it would be a book
  that cannot pass the gate.
- **The grade has an owner.** `grade-the-bscp504-ceiling-on-the-first-book-carrying-8b6316995` is live and reads
  that book against its pre-registration. The whole-gate grade is handed on below, keyed to the first book carrying
  the level-DD fix.

Nothing was built. The claim is released.
