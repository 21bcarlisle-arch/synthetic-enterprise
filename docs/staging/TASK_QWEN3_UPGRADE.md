# Task: Upgrade local model to qwen3:14b

Run: ollama pull qwen3:14b

Set environment: OLLAMA_FLASH_ATTENTION=1, OLLAMA_NUM_CTX=8192 in background/start_worker.sh

Smoke test: run a representative simulation task against qwen3:14b and confirm it completes correctly.

Update any config references from qwen2.5-coder:14b to qwen3:14b.

Run make check, commit, push, NTFY: qwen3:14b live, smoke test result and tok/s reported.