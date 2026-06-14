# Fix: Two-Way NTFY Command Channel

## Problem

Rich currently has no low-friction way to send short instructions or
questions to the agent from his phone. Every instruction requires staging
a file via /ui/stage, which involves copy-paste. For short diagnostic
questions ("explain the capital cost calculation") this is disproportionate
effort.

Rich already has the ntfy app on his phone and is subscribed to
`ntfy.sh/skynet-synthetic`. The app has a built-in publish button — he
can type a message and tap send in one gesture.

## Outcome Required

Rich can send a short message to the agent from the ntfy app on his phone.
The agent receives it, acts on it, and responds via NTFY. One tap to send,
one notification back.

This is not a replacement for staged instructions — those remain the right
path for multi-phase work. This is for short questions, quick diagnostics,
and steering mid-run without breaking the async flow.

## Your Job

You know the environment. Design and implement whatever mechanism achieves
this reliably — whether that's a subscriber daemon, a systemd unit polling
the ntfy topic, a webhook, or something else.

Consider:
- The agent should distinguish incoming commands from Rich vs its own
  outgoing notifications (don't create a feedback loop)
- Short questions should get short answers via NTFY
- If the message looks like a staged instruction it should be treated as one
- The mechanism should survive session restarts and usage-limit pauses

NTFY Rich when it's working with a one-line confirmation of how it works,
then immediately demonstrate it by answering this question via the new
channel: "Explain in plain English how capital cost is calculated in the
simulation and why it might be running at 41% of gross margin."
