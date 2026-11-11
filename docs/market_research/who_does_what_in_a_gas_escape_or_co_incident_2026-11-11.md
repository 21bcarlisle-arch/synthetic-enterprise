# Who does what in a gas escape or CO incident: the supplier, the network, the engineer, HSE (2026-11-11)

**Knowledge:** none -- no published Knowledge page covers gas safety yet; this is item 4 of the front-line-gaps steer (`DIRECTOR_STEER_KNOWLEDGE_FIRST_FRONT_LINE_GAPS_2026-11-10.md`) and its first reader is `company/billing/gas_safety_incident_register.py`

**The question.** `company/billing/gas_safety_incident_register.py` says that a gas supplier notified of an
incident must "make the supply safe immediately (isolate if required)", "arrange Gas Safe registered engineer
response", report RIDDOR events to HSE "within 15 days", and "maintain records for 3 years (GSIUR Reg 35)". The
advisor believed that the make-safe duty belongs to the network, not the supplier. This page settles that from the
statute.

**Sources.** All of them are the current revised text on legislation.gov.uk, read on 11 Nov 2026. Quotes are verbatim.
- Gas Safety (Management) Regulations 1996 (GSMR), SI 1996/551: reg 6 and reg 7, current text including the SI 2023/284 amendments.
- Gas Safety (Installation and Use) Regulations 1998 (GSIUR), SI 1998/2451: regs 35, 36 and 37.
- RIDDOR 2013, SI 2013/1471: reg 11.
- Gas Act 1986: s7A.

## Who does what (piped natural gas from a GB network: every domestic gas customer we model)

| Step | Who | Source |
|---|---|---|
| Shut off the supply at the emergency control, if there is a smell of gas | The **responsible person** for the premises (the occupier or owner): "shall immediately take all reasonable steps to cause the supply of gas to be shut off" | GSIUR 37(2) |
| Take reports of escapes on one GB number, staffed around the clock | The **emergency reporting service provider**: "must provide a continuously staffed telephone service"; it must be "contactable within Great Britain by the use of one telephone number" | GSMR 7(1)(a), 7(1B) |
| Pass a report on to whoever has to stop the escape | **Any** reporting provider that is not responsible must "report it forthwith to the person who is" | GSMR 7(2) |
| **Supplier: pass the report on** | The holder of a s7A(1) licence (a gas **supplier**, by s7A(11)) "who discovers or is notified of any such escape" must "report it forthwith to the emergency reporting service provider for the relevant network" | GSMR 7(3); Gas Act 1986 s7A(1), (11) |
| **Attend, and stop the escape within 12 hours** | The **conveyor** (the gas distribution network): "as soon as is reasonably practicable ... attend the place where the gas is escaping, and within 12 hours of being so informed ... prevent the gas escaping". For an escape from a fitting, this falls on the person conveying gas immediately upstream of the emergency control. | GSMR 7(4), 7(5) |
| Supplier's own 12-hour "prevent the escape" duty | Exists in GSIUR 37(1), but **switched off for network gas**: "Nothing in paragraphs (1) to (6) above shall apply to an escape of gas from a network" | GSIUR 37(7) |
| **Supplier: advise on a reported CO escape** | Where the user reports carbon monoxide, the supplier's duty is "limited to advising that person of the immediate action to be taken". It must also advise that the fitting needs examining and, where necessary, repairing "by a competent person". | GSIUR 37(8) |
| Notify HSE of a gas death, loss of consciousness or hospitalisation | The **conveyor**, for gas "through a fixed pipe distribution system": notify "without delay" and "send a report ... within 14 days of the incident". The word "supplier" in 11(1) covers only LPG in refillable containers. | RIDDOR 11(1) |
| Tell the supplier about such an incident | The **conveyor** must "inform the relevant gas supplier of that fact" | GSMR 7(15) |
| **Supplier: investigate a RIDDOR 11(1) CO incident** | "the person who supplied the gas shall, as soon as is reasonably practicable after receiving notice of the incident, cause an investigation to be carried out", and HSE is told before the investigation and sent its report | GSMR 7(14), 7(16) |
| Report a dangerous fitting | The **approved (Gas Safe registered) person**, "within 14 days of acquiring that information" | RIDDOR 11(2) |
| Keep landlord gas safety records | The **landlord**, "until there have been two further checks", or for 2 years after the last check of a removed appliance | GSIUR 36(3)(c) |
| Maintain appliances at a workplace | The **employer or self-employed person**; this is what reg 35 is about | GSIUR 35 |

## What this means for the module

1. **"Make the supply safe immediately (isolate if required)" is wrong for the supplier.**
   - Stopping an escape on network gas is the conveyor's duty, within 12 hours of being told (GSMR 7(4)/(5)).
   - Shutting off at the emergency control is the occupier's job (GSIUR 37(2)).
   - The supplier's own 37(1) duty is disapplied for network gas by 37(7).
   - **The advisor's belief is confirmed.**
2. **"Arrange Gas Safe registered engineer response" is wrong as a supplier duty.**
   - On an escape, the supplier must report forthwith to the emergency service (GSMR 7(3)).
   - On a CO report, it advises the user of immediate action, and advises that a competent person examine the appliance (GSIUR 37(8)).
   - No provision read here makes the supplier dispatch an engineer.
3. **"Report RIDDOR events to HSE within 15 days" is wrong twice.**
   - For piped gas, the RIDDOR 11(1) duty is the conveyor's.
   - Its report is due in **14** days, not 15. Nothing in reg 11 gives 15 days. Where the 15 came from is not established here; it was not
     checked against RIDDOR's other regulations.
   - The supplier's HSE contact on a gas incident is the GSMR 7(14)/7(16) investigation, started "as soon as is reasonably practicable" after the conveyor tells it.
4. **"Maintain records for 3 years (GSIUR Reg 35)" cites the wrong regulation for the wrong duty.**
   - Reg 35 is the employer's maintenance duty.
   - The only retention period in GSIUR is the landlord's, in 36(3).

## What the company can see (the seam)

The supplier learns of an escape when a customer calls it (it must then pass the report on), or when the
conveyor tells it of a RIDDOR 11(1) incident (GSMR 7(15)). It sees neither the attendance nor the make-safe
directly. What it holds is the report it passed on, and what the network tells it back. So the world owns:
- the incident;
- the conveyor's attendance and its 12-hour clock;
- the conveyor's RIDDOR report.

The company owns:
- the forthwith onward report;
- the 37(8) advice;
- the 7(14) investigation.

Nothing new crosses the seam today, because the module is not wired into a run. It is reached only by name, from
`company/compliance/obligations_register.py`.

## Design choices, and what is left undone

- **This landing corrects the statements and the clock, not the state machine.** The docstring now states the
  statutory split. The deadline becomes RIDDOR 11(1)(b)'s 14 days, and is labelled as the conveyor's report that
  the supplier is told about under GSMR 7(15).
- **The state machine still models the wrong party.** Its states are `ENGINEER_DISPATCHED`, `SUPPLY_ISOLATED`
  and `MADE_SAFE`, with transitions `dispatch_engineer` and `isolate_supply`, and 89 tests are built on that
  shape. Making it the supplier's own record is a rebuild:
  - "passed to the emergency service at *t*";
  - "advised (37(8))";
  - "conveyor reports made safe";
  - "7(14) investigation opened / HSE notified / report sent".

  That rebuild is filed as a finding, not done in this tick.
- **GAP: the supplier's investigation clock.** GSMR 7(14) says "as soon as is reasonably practicable". No day
  count was found in the regulation text. HSE guidance (L80, the GSMR guidance) may give one, but it has not been
  read. Until it is, the module carries no supplier investigation deadline, rather than an invented one.
- **GAP: the supplier's record retention period for safety incidents.** None was found in GSIUR, GSMR or
  RIDDOR 11. The supply licence conditions (Ofgem) have not been searched. RIDDOR reg 12 (records) was not read.
- **GAP: whether the gas supply licence adds a duty.** Examples would be giving customers the emergency number on
  bills, or PSR-related safety steps. Reg 7 itself places no duty to publicise the number. The licence was not
  searched for this page.

## Reverse

Delete this file; revert the docstring and the constant in the module.
