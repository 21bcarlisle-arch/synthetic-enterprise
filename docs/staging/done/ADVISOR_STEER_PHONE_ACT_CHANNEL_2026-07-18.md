# ADVISOR STEER — [ACT]s must be answerable from the director's phone in seconds (director, 2026-07-18)

**Type:** [STEER] — a requirement to design and build; absorb into the queue per your own prioritisation. Not an interrupt.

**The director's requirement, verbatim intent:** *"Annoying having to log in and paste."* [ACT] decisions requiring his authority must be answerable **from his phone in seconds — no SSH, no console paste.**

**The problem (not the solution — the mechanism is your design):**
- Today, an [ACT] ends with the machine expecting console input. The console is the only channel treated as unforgeable director authority. That makes every decision cost a phone-SSH-tmux-paste cycle — the exact donkey work the operating model exists to remove.
- The parts already exist: the two-way NTFY channel, the file-api's mobile `/ui/stage` form (reachable only via the director's Tailscale identity — itself an authentication factor), the dispatcher, the gate-authorization ledger with provenance records. Inbound NTFY is rightly untrusted (G-N4) — the gap is a phone path that carries **unforgeable director provenance**.
- Requirements: (1) a phone reply/tap must be verifiably the director (Tailscale-identity-gated endpoint, a director token, or your better design — but forge-proof, since this authorizes gate-opens and rulings); (2) every [ACT] is FORMATTED so the answer is a tap or a single word — the machine pre-frames the options, the director picks; (3) the ledger records phone-acts with the same provenance rigor as console acts; (4) the console remains the fallback and the channel for anything long-form or unusual; (5) fail-closed — if the phone path's authentication cannot be verified, the act does not count and the console is required.
- Safety note: this touches the authorization-trust model, so per your own H25 finding the *final activation* of a new authority channel is director-authenticated-console-only — design and build it, prove it (mutation tests: a forged/unauthenticated reply is REJECTED), then bring the switch-on to the director as one last console act. Fittingly, that should be the last routine console act ever needed.

**The bar:** the director's cost per decision becomes seconds — quiet phone → buzz → tap or word → done.

— Advisor, on the director's behalf, via the staging channel.
