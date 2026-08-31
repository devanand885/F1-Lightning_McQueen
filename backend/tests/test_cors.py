"""Regression test: the frontend calls this API from the browser, so without
CORS headers every request is silently blocked client-side (curl/TestClient
don't enforce CORS, so this was missed until manual browser testing)."""


def test_allowed_origin_gets_cors_header(client):
    resp = client.get("/health", headers={"Origin": "http://localhost:3000"})
    assert resp.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_disallowed_origin_has_no_cors_header(client):
    resp = client.get("/health", headers={"Origin": "http://evil.example.com"})
    assert "access-control-allow-origin" not in resp.headers
