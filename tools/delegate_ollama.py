"""Delegate a task to a local Ollama model, routed by task type.

Two local models are available, each suited to a different kind of work
(running one at a time — never both simultaneously, per Rich's housekeeping
note: swap as needed rather than competing for the same GPU/RAM):

  qwen3:14b         — code generation, file writing, data transformation,
                      test scaffolding ("coder" tasks)
  qwen2.5:7b        — result analysis, summary drafting, structured output,
                      README updates, PHASE_SUMMARY drafts, STATUS.md
                      updates ("analysis" tasks)

Routing is automatic: pass --task-type coder|analysis (or rely on the
default), and the right model is selected. The orchestrator still reads,
reviews, and integrates everything the local model produces — local output
is a draft, never a commit-ready artefact (this applies doubly to analysis
drafts, which the frontier reviews and edits before anything reaches a
PHASE_SUMMARY or STATUS.md per the Delegation Protocol).

Usage:
    python3 tools/delegate_ollama.py <prompt_file> <output_file> [--task-type coder|analysis]

Writes the model's raw response to <output_file> and prints a one-line
token-usage summary (plus which model/task-type was used) to stdout.
"""

import json
import sys
import urllib.request

OLLAMA_URL = "http://localhost:11434/api/generate"

MODELS_BY_TASK_TYPE = {
    "coder": "qwen3:14b",
    "analysis": "qwen2.5:7b",
}
DEFAULT_TASK_TYPE = "coder"


def delegate(prompt: str, task_type: str = DEFAULT_TASK_TYPE) -> dict:
    model = MODELS_BY_TASK_TYPE[task_type]
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"num_predict": 2048},
    }).encode()
    request = urllib.request.Request(
        OLLAMA_URL, data=payload, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        result = json.loads(response.read())
    result["_model"] = model
    result["_task_type"] = task_type
    return result


if __name__ == "__main__":
    prompt_path, output_path = sys.argv[1], sys.argv[2]
    task_type = DEFAULT_TASK_TYPE
    if "--task-type" in sys.argv:
        task_type = sys.argv[sys.argv.index("--task-type") + 1]
    if task_type not in MODELS_BY_TASK_TYPE:
        raise ValueError(f"Unknown task type {task_type!r} — expected one of {list(MODELS_BY_TASK_TYPE)}")

    with open(prompt_path) as f:
        result = delegate(f.read(), task_type)

    with open(output_path, "w") as f:
        f.write(result.get("response", ""))

    print(
        f"model={result['_model']} task_type={result['_task_type']} "
        f"prompt_eval_count={result.get('prompt_eval_count')} "
        f"eval_count={result.get('eval_count')} "
        f"-> written to {output_path}"
    )
