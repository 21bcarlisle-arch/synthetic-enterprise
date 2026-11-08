# ARCHIVED LEGS of tests/company/billing/test_collections.py (archive increment 4). The tests here reach a module
# under archive/unhooked_supplier/; the live legs stay at tests/company/billing/test_collections.py.
from datetime import date
from pathlib import Path
from company.billing.collections import (
    _aging_tier, get_overdue_invoices, get_collections_queue
)
from company.billing.invoice import create_invoice, create_schema
from starlette.testclient import TestClient
from company.portal.app import app


client = TestClient(app, raise_server_exceptions=True)


def test_admin_collections_route_returns_200():
    r = client.get("/admin/collections")
    assert r.status_code == 200


def test_admin_collections_shows_clear_state_or_table():
    r = client.get("/admin/collections")
    assert "Collections" in r.text


def test_admin_collections_content_type_is_html():
    r = client.get("/admin/collections")
    assert "text/html" in r.headers.get("content-type", "")

