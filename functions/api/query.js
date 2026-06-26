// Cloudflare Pages Function: /api/query
// Proxies NL questions about the sim data to Claude Haiku.
// Requires ANTHROPIC_API_KEY env var set in Cloudflare Pages dashboard.

export async function onRequestPost(context) {
  try {
    const body = await context.request.json();
    const { question, queryContext } = body;

    if (!question || typeof question !== "string" || !question.trim()) {
      return jsonResponse({ error: "Missing question" }, 400);
    }

    const apiKey = context.env.ANTHROPIC_API_KEY;
    if (!apiKey) {
      return jsonResponse({ error: "API not configured — set ANTHROPIC_API_KEY in Cloudflare Pages env" }, 503);
    }

    const systemPrompt =
      "You are a data analyst for a UK energy supply business simulation (2016-2025). " +
      "Answer questions concisely and factually based only on the data provided. " +
      "If the data does not contain the information needed to answer, say so clearly. " +
      "Keep answers under 200 words unless the question requires more detail." +
      (queryContext ? "\n\nSimulation data:\n" + queryContext : "");

    const resp = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "x-api-key": apiKey,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
      },
      body: JSON.stringify({
        model: "claude-haiku-4-5-20251001",
        max_tokens: 600,
        system: systemPrompt,
        messages: [{ role: "user", content: question.trim() }],
      }),
    });

    const data = await resp.json();

    if (!resp.ok) {
      const msg = data?.error?.message || "Anthropic API error " + resp.status;
      return jsonResponse({ error: msg }, resp.status);
    }

    const answer = data?.content?.[0]?.text || "";
    return jsonResponse({ answer });
  } catch (err) {
    return jsonResponse({ error: "Internal error: " + err.message }, 500);
  }
}

export async function onRequestOptions() {
  return new Response(null, {
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    },
  });
}

function jsonResponse(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
    },
  });
}
