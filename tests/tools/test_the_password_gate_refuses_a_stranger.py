"""The site's password gate (`functions/_middleware.js`), driven by node against the real file.

Director ruling 19 Nov, addendum 20 Nov 07:00: every route behind a password, robots open, the
deploy check reading through the gate, fail closed with no secret. Each assertion names the
defect it catches. The first control asserts the gate CAN let a reader in, because a gate that
refuses everything passes every refusal test.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
GATE = ROOT / "functions" / "_middleware.js"

DRIVER = r"""
import fs from "node:fs";
const src = fs.readFileSync(process.argv[2], "utf8");
const mod = await import("data:text/javascript;base64," + Buffer.from(src).toString("base64"));
const cases = JSON.parse(process.argv[3]);
const out = [];
for (const c of cases) {
  let served = false;
  const init = { method: c.method || "GET", headers: c.headers || {} };
  if (c.form) init.body = new URLSearchParams(c.form);
  const request = new Request("https://poesys.net" + c.path, init);
  const next = async () => { served = true; return new Response("CONTENT", { status: 200 }); };
  const resp = await mod.onRequest({ request, env: c.env, next });
  out.push({ status: resp.status, served, location: resp.headers.get("Location"),
             cookie: resp.headers.get("Set-Cookie"), robots: resp.headers.get("X-Robots-Tag"),
             body: served ? "" : await resp.text() });
}
console.log(JSON.stringify(out));
"""

PW = "test-only-password-not-the-real-one"
ENV = {"SITE_PASSWORD": PW}


def _drive(tmp_path: Path, cases: list[dict]) -> list[dict]:
    node = shutil.which("node")
    if node is None:
        pytest.fail("node is not installed, so the gate cannot be driven")
    drv = tmp_path / "drive.mjs"
    drv.write_text(DRIVER)
    out = subprocess.run([node, str(drv), str(GATE), json.dumps(cases)],
                         capture_output=True, text=True, timeout=60)
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


def test_the_gate_can_open_and_refuses_everyone_else(tmp_path):
    login = _drive(tmp_path, [{"path": "/__gate", "method": "POST", "env": ENV,
                               "form": {"password": PW, "next": "/proof/"}}])[0]
    # Defect: a gate that never opens (wrong token, wrong redirect).
    assert login["status"] == 303 and login["location"] == "/proof/"
    token = login["cookie"].split(";")[0]
    assert PW not in login["cookie"], "the cookie must not carry the password itself"

    stranger, cookie, header, bad_cookie, bad_header, robots, wrong_pw = _drive(tmp_path, [
        {"path": "/", "env": ENV},
        {"path": "/data/dashboard.json", "env": ENV, "headers": {"Cookie": token}},
        {"path": "/", "env": ENV, "headers": {"X-Poesys-Gate": PW}},
        {"path": "/", "env": ENV, "headers": {"Cookie": "poesys_gate=deadbeef"}},
        {"path": "/", "env": ENV, "headers": {"X-Poesys-Gate": "guess"}},
        {"path": "/robots.txt", "env": ENV},
        {"path": "/__gate", "method": "POST", "env": ENV, "form": {"password": "guess"}},
    ])
    # The partition: each branch is taken at least once.
    assert cookie["served"] and header["served"] and robots["served"]
    for refused in (stranger, bad_cookie, bad_header, wrong_pw):
        assert refused["status"] == 401 and not refused["served"]
        assert refused["robots"] == "noindex, nofollow"
        assert "CONTENT" not in refused["body"]


def test_no_secret_fails_closed(tmp_path):
    # Defect: an unset secret serving the site open. It must serve nothing, even with a
    # header that would match an empty password.
    for env in ({}, {"SITE_PASSWORD": "  "}):
        r1, r2 = _drive(tmp_path, [{"path": "/", "env": env},
                                   {"path": "/", "env": env, "headers": {"X-Poesys-Gate": ""}}])
        assert r1["status"] == 503 and not r1["served"]
        assert r2["status"] == 503 and not r2["served"]


def test_the_login_is_not_an_open_redirect(tmp_path):
    for target in ("//evil.example/", "https://evil.example/", "/\\evil.example"):
        r = _drive(tmp_path, [{"path": "/__gate", "method": "POST", "env": ENV,
                               "form": {"password": PW, "next": target}}])[0]
        assert r["status"] == 303 and r["location"] == "/", target
