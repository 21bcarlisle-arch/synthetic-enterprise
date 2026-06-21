#!/usr/bin/env python3
"""Local HTTP proxy for the Anthropic API — tracks token usage across all sessions.

Sits between Claude Code (or any SDK client) and api.anthropic.com.
Intercepts /v1/messages responses, extracts usage fields from streaming SSE,
and accumulates per-session and daily totals.

Set ANTHROPIC_BASE_URL=http://localhost:8801 before starting any tracked process.

Endpoints:
  POST /v1/messages   — transparent proxy to Anthropic, logs usage
  GET  /usage         — current session totals + today's aggregate
  GET  /usage?days=N  — last N days aggregate

Usage:
  python3 -m background.token_proxy          # start (default port 8801)
  python3 -m background.token_proxy --port 8801 --query  # query and exit

Log: docs/observability/token-usage-log.jsonl
     One JSON line per API call: {ts, session_id, input, output, cache_read, cache_write, cost_usd}
"""

import argparse
import gzip
import json
import os
import ssl
import sys
import threading
import time
import urllib.request
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = PROJECT_DIR / "docs" / "observability" / "token-usage-log.jsonl"

UPSTREAM = "https://api.anthropic.com"
DEFAULT_PORT = 8801

# Anthropic pricing per million tokens (Sonnet 4.6 / sonnet-4-6)
_PRICE = {
    "input": 3.00,
    "output": 15.00,
    "cache_read": 0.30,
    "cache_write": 3.75,
}

_session_id = f"{os.getpid()}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}"
_lock = threading.Lock()


def _cost(usage: dict) -> float:
    inp = usage.get("input_tokens", 0)
    out = usage.get("output_tokens", 0)
    cr = usage.get("cache_read_input_tokens", 0)
    cw = usage.get("cache_creation_input_tokens", 0)
    return (
        inp * _PRICE["input"] / 1_000_000
        + out * _PRICE["output"] / 1_000_000
        + cr * _PRICE["cache_read"] / 1_000_000
        + cw * _PRICE["cache_write"] / 1_000_000
    )


def _log_usage(usage: dict) -> None:
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "session_id": _session_id,
        "input_tokens": usage.get("input_tokens", 0),
        "output_tokens": usage.get("output_tokens", 0),
        "cache_read_tokens": usage.get("cache_read_input_tokens", 0),
        "cache_write_tokens": usage.get("cache_creation_input_tokens", 0),
        "cost_usd": round(_cost(usage), 6),
    }
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with _lock:
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(record) + "\n")


def _extract_usage_from_sse(body: bytes) -> dict:
    """Parse usage fields from a response body (SSE streaming or plain JSON)."""
    usage = {}
    text = body.decode("utf-8", errors="replace").strip()

    # Try plain JSON first (non-streaming response)
    if text.startswith("{"):
        try:
            doc = json.loads(text)
            if "usage" in doc:
                return doc["usage"]
        except json.JSONDecodeError:
            pass

    # SSE streaming: parse each data: line
    for line in text.split("\n"):
        line = line.strip()
        if not line.startswith("data: "):
            continue
        raw = line[6:].strip()
        if raw == "[DONE]" or not raw:
            continue
        try:
            chunk = json.loads(raw)
        except json.JSONDecodeError:
            continue
        # message_start carries input tokens + cache figures
        if chunk.get("type") == "message_start":
            msg_usage = chunk.get("message", {}).get("usage", {})
            usage.update(msg_usage)
        # message_delta carries final output_tokens
        if chunk.get("type") == "message_delta":
            delta_usage = chunk.get("usage", {})
            output = delta_usage.get("output_tokens")
            if output is not None:
                usage["output_tokens"] = output
    return usage


def _read_log_lines(days: int | None = None) -> list[dict]:
    if not LOG_FILE.exists():
        return []
    lines = []
    cutoff = None
    if days is not None:
        from datetime import timedelta
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    with open(LOG_FILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                if cutoff is None or rec.get("ts", "") >= cutoff:
                    lines.append(rec)
            except json.JSONDecodeError:
                pass
    return lines


def _aggregate(records: list[dict]) -> dict:
    totals = {"calls": 0, "input_tokens": 0, "output_tokens": 0,
               "cache_read_tokens": 0, "cache_write_tokens": 0, "cost_usd": 0.0}
    for r in records:
        totals["calls"] += 1
        totals["input_tokens"] += r.get("input_tokens", 0)
        totals["output_tokens"] += r.get("output_tokens", 0)
        totals["cache_read_tokens"] += r.get("cache_read_tokens", 0)
        totals["cache_write_tokens"] += r.get("cache_write_tokens", 0)
        totals["cost_usd"] += r.get("cost_usd", 0.0)
    totals["cost_usd"] = round(totals["cost_usd"], 4)
    return totals


def _log_proxy(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)  # tee in tmux writes this to log file


class ProxyHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # suppress default access log

    def do_GET(self):
        if self.path.startswith("/usage"):
            self._handle_usage_query()
        else:
            self.send_error(404)

    def do_POST(self):
        if "/v1/messages" in self.path:
            self._proxy_messages()
        else:
            self.send_error(404)

    def _handle_usage_query(self):
        days = None
        if "days=" in self.path:
            try:
                days = int(self.path.split("days=")[1].split("&")[0])
            except (ValueError, IndexError):
                days = 1

        all_records = _read_log_lines(days)
        session_records = [r for r in all_records if r.get("session_id") == _session_id]

        result = {
            "session_id": _session_id,
            "session": _aggregate(session_records),
            "window": _aggregate(all_records),
            "window_days": days,
        }
        body = json.dumps(result, indent=2).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _proxy_messages(self):
        # Read request body — handle both Content-Length and chunked
        te = self.headers.get("Transfer-Encoding", "").lower()
        cl = self.headers.get("Content-Length")
        if te == "chunked":
            # Read chunked body manually
            chunks = []
            while True:
                size_line = self.rfile.readline().strip()
                chunk_size = int(size_line, 16)
                if chunk_size == 0:
                    self.rfile.readline()  # trailing CRLF
                    break
                chunk = self.rfile.read(chunk_size)
                self.rfile.readline()  # CRLF after chunk
                chunks.append(chunk)
            body = b"".join(chunks)
        elif cl:
            body = self.rfile.read(int(cl))
        else:
            body = b""

        url = UPSTREAM + self.path
        headers = {k: v for k, v in self.headers.items()
                   if k.lower() not in ("host", "content-length", "transfer-encoding")}
        # Always set Content-Length for upstream request
        headers["Content-Length"] = str(len(body))

        _log_proxy(f"→ {self.command} {self.path} ({len(body)}B body)")

        ctx = ssl.create_default_context()
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, context=ctx, timeout=300) as resp:
                resp_body = resp.read()
                status = resp.status
                resp_headers = list(resp.headers.items())
        except urllib.error.HTTPError as e:
            resp_body = e.read()
            status = e.code
            resp_headers = list(e.headers.items())
        except Exception as exc:
            _log_proxy(f"PROXY ERROR: {exc}")
            error_body = json.dumps({"error": {"type": "proxy_error", "message": str(exc)}}).encode()
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(error_body)))
            self.end_headers()
            self.wfile.write(error_body)
            return

        _log_proxy(f"← {status} ({len(resp_body)}B)")

        # Decompress for usage extraction (forward original compressed body)
        content_enc = next((v for k, v in resp_headers if k.lower() == "content-encoding"), "")
        parse_body = resp_body
        if "gzip" in content_enc.lower() and resp_body[:2] == b"\x1f\x8b":
            try:
                parse_body = gzip.decompress(resp_body)
            except Exception:
                pass

        # Extract and log usage
        usage = _extract_usage_from_sse(parse_body)
        if usage.get("input_tokens") or usage.get("output_tokens"):
            _log_usage(usage)
            _log_proxy(f"  usage: in={usage.get('input_tokens',0)} out={usage.get('output_tokens',0)} "
                       f"cr={usage.get('cache_read_input_tokens',0)} cost=${_cost(usage):.4f}")
        else:
            _log_proxy(f"  no usage extracted from response")

        self.send_response(status)
        skip_headers = {"transfer-encoding", "content-length", "connection", "keep-alive"}
        for k, v in resp_headers:
            if k.lower() not in skip_headers:
                self.send_header(k, v)
        self.send_header("Content-Length", str(len(resp_body)))
        self.end_headers()
        self.wfile.write(resp_body)


def query_and_print(port: int = DEFAULT_PORT, days: int | None = None) -> None:
    """Query a running proxy and print usage summary."""
    url = f"http://localhost:{port}/usage"
    if days:
        url += f"?days={days}"
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.loads(resp.read())
        s = data["session"]
        w = data["window"]
        print(f"Session ({data['session_id']}):")
        print(f"  {s['calls']} calls | {s['input_tokens']:,} in | {s['output_tokens']:,} out | "
              f"{s['cache_read_tokens']:,} cache-read | ${s['cost_usd']:.4f}")
        print(f"Window ({w['calls']} calls total):")
        print(f"  {w['input_tokens']:,} in | {w['output_tokens']:,} out | "
              f"{w['cache_read_tokens']:,} cache-read | ${w['cost_usd']:.4f}")
    except Exception as e:
        print(f"Proxy not running or unreachable: {e}")
        print("Falling back to log file...")
        records = _read_log_lines(days or 1)
        agg = _aggregate(records)
        print(f"Last {days or 1} day(s): {agg['calls']} calls | "
              f"{agg['input_tokens']:,} in | {agg['output_tokens']:,} out | ${agg['cost_usd']:.4f}")


def main(port: int = DEFAULT_PORT) -> None:
    server = HTTPServer(("127.0.0.1", port), ProxyHandler)
    print(f"[token-proxy] Listening on http://localhost:{port} — session {_session_id}", flush=True)
    print(f"[token-proxy] Set ANTHROPIC_BASE_URL=http://localhost:{port} to track usage", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("[token-proxy] Stopped")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--query", action="store_true", help="query running proxy and exit")
    parser.add_argument("--days", type=int, default=None)
    args = parser.parse_args()
    if args.query:
        query_and_print(args.port, args.days)
    else:
        main(args.port)
