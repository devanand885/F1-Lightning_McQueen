from app.models.season import Season


def test_list_seasons_returns_years_descending(client, db_session):
    db_session.add_all([Season(year=2025), Season(year=2026)])
    db_session.commit()

    resp = client.get("/api/v1/seasons")

    assert resp.status_code == 200
    body = resp.json()
    assert body["count"] == 2
    assert body["items"] == [2026, 2025]


def test_list_seasons_empty(client):
    resp = client.get("/api/v1/seasons")
    assert resp.status_code == 200
    assert resp.json() == {"count": 0, "items": []}
