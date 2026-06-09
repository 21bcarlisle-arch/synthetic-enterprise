"""Task dispatcher — invoked by background_worker.py when queued tasks are found.

Parses docs/instructions/background-tasks.md, picks up the first QUEUED task,
runs it via Ollama (qwen2.5-coder:14b or qwen2.5:7b per task spec), then moves
the task header from QUEUED to DONE. One task per cycle. Logs structured
performance metrics (wall time, prompt/eval token counts, output file) to the
background worker log and sends an ntfy.sh notification on completion.
"""

import re
import subprocess
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

TASKS_FILE = Path("docs/instructions/background-tasks.md")
LOG_FILE = Path("docs/observability/background-worker-log.md")
NTFY_TOPIC = "https://ntfy.sh/skynet-synthetic"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _log(message: str) -> None:
    entry = f"\n- [{_timestamp()}] {message}"
    with open(LOG_FILE, "a") as f:
        f.write(entry)
    print(entry)


def _send_ntfy(message: str) -> None:
    try:
        urllib.request.urlopen(
            urllib.request.Request(
                NTFY_TOPIC,
                data=message.encode(),
                headers={"Content-Type": "text/plain"},
            ),
            timeout=10,
        )
    except urllib.error.URLError as exc:
        _log(f"NTFY send failed: {exc}")


def _parse_ollama_tokens(stderr: str) -> tuple[int, int]:
    """Parse prompt eval count and eval count from ollama --verbose stderr output."""
    prompt_tokens = 0
    eval_tokens = 0
    for line in stderr.splitlines():
        m = re.search(r"prompt eval count:\s+(\d+)", line)
        if m:
            prompt_tokens = int(m.group(1))
        m = re.search(r"eval count:\s+(\d+)", line)
        if m:
            eval_tokens = int(m.group(1))
    return prompt_tokens, eval_tokens


def _run_ollama(model: str, prompt: str, task_name: str, timeout: int = 600) -> tuple[str, int, int, float]:
    """Run a task via local Ollama with --verbose flag.

    Returns (output, prompt_tokens, eval_tokens, wall_time_seconds).
    """
    _log(f"Ollama({model}) starting task: {task_name}")
    t0 = time.monotonic()
    result = subprocess.run(
        ["ollama", "run", "--verbose", model, prompt],
        capture_output=True, text=True, timeout=timeout,
    )
    wall_time = time.monotonic() - t0

    prompt_tokens, eval_tokens = _parse_ollama_tokens(result.stderr)

    if result.returncode != 0:
        _log(f"Ollama task FAILED: {task_name} — {result.stderr[:300]}")
        return "", prompt_tokens, eval_tokens, wall_time

    _log(f"Ollama task complete: {task_name} — {wall_time:.1f}s, P={prompt_tokens} E={eval_tokens}")
    return result.stdout.strip(), prompt_tokens, eval_tokens, wall_time


def _log_performance(
    task_name: str,
    started: str,
    completed: str,
    wall_time: float,
    prompt_tokens: int,
    eval_tokens: int,
    output_path: Path | None,
    status: str,
) -> None:
    output_info = "(none)"
    if output_path and output_path.exists():
        size_kb = output_path.stat().st_size / 1024
        output_info = f"{output_path} ({size_kb:.1f} KB)"

    entry = f"""
### Task: {task_name}
- Started: {started}
- Completed: {completed}
- Wall time: {wall_time:.1f}s
- Ollama tokens: prompt={prompt_tokens} eval={eval_tokens}
- Output produced: {output_info}
- Status: {status}
- Consumed by: pending — filled in by main pipeline
"""
    with open(LOG_FILE, "a") as f:
        f.write(entry)


def _update_status_table(task_name: str, prompt_tokens: int, eval_tokens: int, wall_time: float, output_path: Path | None) -> None:
    """Update the Background Worker Performance table in STATUS.md."""
    status_file = Path("STATUS.md")
    if not status_file.exists():
        return
    content = status_file.read_text()
    output_info = "-"
    if output_path and output_path.exists():
        size_kb = output_path.stat().st_size / 1024
        output_info = f"{output_path.name} ({size_kb:.1f}KB)"
    old_row = f"| {task_name} | -/- | - | pending | pending | pending |"
    new_row = f"| {task_name} | {prompt_tokens}/{eval_tokens} | {wall_time:.0f}s | {output_info} | pending | pending |"
    if old_row in content:
        status_file.write_text(content.replace(old_row, new_row))


def _move_task_to_done(task_name: str) -> None:
    content = TASKS_FILE.read_text()
    pattern = rf"(### Task: {re.escape(task_name)}\n.*?)(?=\n### Task:|\n---|\Z)"
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        _log(f"Could not locate task block for '{task_name}' to move to DONE")
        return
    task_block = match.group(1)
    content_without = content.replace(task_block, "", 1)
    done_entry = f"\n### Task: {task_name}\nCompleted: {_timestamp()}\n\n"
    if "## DONE\n(none)" in content_without:
        content_without = content_without.replace("## DONE\n(none)", f"## DONE\n{done_entry}", 1)
    elif "## DONE\n" in content_without:
        content_without = content_without.replace("## DONE\n", f"## DONE\n{done_entry}", 1)
    else:
        content_without += f"\n## DONE\n{done_entry}"
    TASKS_FILE.write_text(content_without)
    _log(f"Task '{task_name}' moved to DONE")


def _find_first_queued_task():
    content = TASKS_FILE.read_text()
    queued_section = re.search(r"## QUEUED\n(.*?)(?=\n## |\Z)", content, re.DOTALL)
    if not queued_section:
        return None, None, None
    task_match = re.search(
        r"### Task: (\S+)\nDescription: (.*?)\n.*?Model: ([\w.:]+)",
        queued_section.group(1), re.DOTALL,
    )
    if not task_match:
        return None, None, None
    return task_match.group(1), task_match.group(2).strip(), task_match.group(3)


# --- Main dispatch ---
task_name, description, model = _find_first_queued_task()
if task_name is None:
    _log("run_queued_tasks: no parseable QUEUED task found")
else:
    started = _timestamp()
    prompt = (
        f"You are a code and data assistant for a UK energy supplier simulation. "
        f"Complete the following task and output only the result — no explanation, no fences:\n\n"
        f"{description}"
    )
    output, prompt_tokens, eval_tokens, wall_time = _run_ollama(model, prompt, task_name)
    completed = _timestamp()

    output_path = None
    status = "FAILED"
    if output:
        out_file = Path(f"docs/observability/background-task-{task_name}.md")
        out_file.write_text(
            f"# Background Task Output: {task_name}\n"
            f"Completed: {completed}\n"
            f"Model: {model}\n"
            f"Wall time: {wall_time:.1f}s | Tokens: P={prompt_tokens} E={eval_tokens}\n\n"
            f"## Output\n\n{output}\n"
        )
        output_path = out_file
        status = "DONE"
        _move_task_to_done(task_name)

    _log_performance(task_name, started, completed, wall_time, prompt_tokens, eval_tokens, output_path, status)
    _update_status_table(task_name, prompt_tokens, eval_tokens, wall_time, output_path)

    output_desc = f"{output_path} ({output_path.stat().st_size / 1024:.1f}KB)" if output_path and output_path.exists() else "none"
    _send_ntfy(
        f"Background task {status}: {task_name} — "
        f"{wall_time:.0f}s, P={prompt_tokens}/E={eval_tokens} local tokens, "
        f"output: {output_desc}. Cache consumed by main pipeline: pending"
    )
