# Problem: Rich Can't Get Urgent Attention When It Matters

## The Problem

Rich communicates with the agent via ntfy. But right now all messages are
treated equally — they land in staging and get processed in order. There
is no way for Rich to interrupt work in progress, no way for the system
to recognise that a question about fundamental correctness should stop
everything else, and no way to distinguish "FYI" from "this is wrong,
stop building on it."

Today's example: Rich spotted that gross margin is 4.4% of revenue and
CLV is negative for 8 of 9 customers — a fundamental problem that should
halt Phase 8a immediately. The message went into staging like any other.
The agent may not see it until the current task completes.

A real company doesn't work this way. An MD who spots a fundamental
problem with the P&L gets immediate attention. A routine status update
waits its turn.

## What We Need

An intelligent routing layer between Rich and the agent system. Rich
sends one message to one place. The routing layer decides what it means,
how urgent it is, who needs to know, and makes sure the right thing
happens — immediately if necessary.

The routing layer must:
- Always be on and always responsive, regardless of what else is running
- Never compete for GPU with simulation work
- Use genuine intelligence to classify messages — not keyword matching
- Interrupt active work when something genuinely urgent arrives
- Route instructions to the right place with the right priority
- Confirm to Rich immediately what it understood and what it did
- Be the foundation for routing to multiple specialist agents in future

## What You Know That We Don't

You know the environment — tmux sessions, Qwen via Ollama, the staging
directory structure, the ntfy pub/sub system, how to interrupt a running
Claude Code session, what's cheap to run continuously and what isn't.

You know what tools are available and what's practical on this hardware.

## What We're Asking

Design and build whatever intelligent routing layer you judge will solve
this problem reliably and durably. It should be smart enough to recognise
that "gross margin looks wrong" is urgent without being told explicitly.
It should be cheap enough to run always-on without affecting simulation
performance. It should be robust enough to survive restarts and usage
pauses.

Don't ask for approval on the design — you have the context and the
environment knowledge to make good decisions here. Build what works.

## One Constraint

The solution must scale to multiple specialist agents in future. Today
there is one main Claude Code session. Soon there may be a sim specialist,
a saas specialist, and others. The routing layer should be designed so
that adding a new agent destination is straightforward — not a rebuild.

## When Done

NTFY Rich with:
1. What you built and how it works in plain English
2. How it classifies messages (what makes something urgent vs normal vs FYI)
3. A live demonstration — re-route the gross margin question that's
   sitting in staging right now as if it had arrived via the new system
