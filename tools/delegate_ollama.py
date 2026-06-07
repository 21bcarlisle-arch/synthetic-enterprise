"""Delegate a code-generation task to the local Ollama model.

Phase 0b harness: sends a spec (plus any reference context) to qwen2.5-coder
running locally, captures the raw response and Ollama's own token-count
fields so delegation spend can be logged alongside frontier spend in
docs/observability/token-log.md.

Usage:
    python3 tools/delegate_ollama.py <prompt_file> <output_file>

Writes the model's raw response to <output_file> and prints a one-line
token-usage summary to stdout (local generations are not "reviewed code" —
the orchestrator reads, tests, and integrates the output afterwards).
"""

import json
import sys
import urllib.request

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5-coder:14b"


def delegate(prompt: str) -> dict:
    payload = json.dumps({"model": MODEL, "prompt": prompt, "stream": False}).encode()
    request = urllib.request.Request(
        OLLAMA_URL, data=payload, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(request, timeout=600) as response:
        return json.loads(response.read())


if __name__ == "__main__":
    prompt_path, output_path = sys.argv[1], sys.argv[2]
    with open(prompt_path) as f:
        result = delegate(f.read())

    with open(output_path, "w") as f:
        f.write(result.get("response", ""))

    print(
        f"prompt_eval_count={result.get('prompt_eval_count')} "
        f"eval_count={result.get('eval_count')} "
        f"-> written to {output_path}"
    )
