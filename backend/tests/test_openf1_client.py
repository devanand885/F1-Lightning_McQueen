from datetime import datetime, timezone

import httpx
import pytest
import respx

from app.core.config import Settings
from app.integrations.openf1.client import OpenF1Client
from app.integrations.openf1.exceptions import OpenF1RequestError, OpenF1ValidationError

BASE_URL = "https://fake-openf1.test/v1"


def _settings(**overrides) -> Settings:
    values = {
        "openf1_base_url": BASE_URL,
        "openf1_timeout_seconds": 1.0,
        "openf1_max_retries": 3,
        "openf1_max_requests_per_second": 100.0,
        "openf1_max_requests_per_minute": 1000.0,
    }
    values.update(overrides)
    return Settings(**values)


@respx.mock
def test_get_meetings_parses_response_and_keeps_raw():
    respx.get(f"{BASE_URL}/meetings").mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "meeting_key": 1,
                    "meeting_name": "Test GP",
                    "circuit_key": 1,
                    "circuit_short_name": "Test",
                    "date_start": "2025-01-01T00:00:00Z",
                    "year": 2025,
                    "some_future_field": "ignored",
                }
            ],
        )
    )

    with OpenF1Client(_settings()) as client:
        results = client.get_meetings(year=2025)

    assert len(results) == 1
    record, raw = results[0]
    assert record.meeting_key == 1
    assert record.meeting_name == "Test GP"
    assert raw["some_future_field"] == "ignored"


@respx.mock
def test_retries_on_server_error_then_succeeds():
    route = respx.get(f"{BASE_URL}/drivers")
    route.side_effect = [httpx.Response(500), httpx.Response(200, json=[])]

    with OpenF1Client(_settings(openf1_max_retries=3)) as client:
        result = client.get_drivers(session_key=1)

    assert result == []
    assert route.call_count == 2


@respx.mock
def test_gives_up_after_max_retries():
    respx.get(f"{BASE_URL}/drivers").mock(return_value=httpx.Response(500))

    with OpenF1Client(_settings(openf1_max_retries=2)) as client, pytest.raises(OpenF1RequestError):
        client.get_drivers(session_key=1)


@respx.mock
def test_retries_on_429_then_succeeds():
    route = respx.get(f"{BASE_URL}/laps")
    route.side_effect = [httpx.Response(429, headers={"Retry-After": "0"}), httpx.Response(200, json=[])]

    with OpenF1Client(_settings(openf1_max_retries=3)) as client:
        result = client.get_laps(session_key=1)

    assert result == []
    assert route.call_count == 2


@respx.mock
def test_400_does_not_retry():
    route = respx.get(f"{BASE_URL}/meetings").mock(return_value=httpx.Response(400))

    with OpenF1Client(_settings(openf1_max_retries=3)) as client, pytest.raises(OpenF1RequestError):
        client.get_meetings(year=2025)

    assert route.call_count == 1


@respx.mock
def test_404_is_treated_as_empty_result_not_an_error():
    respx.get(f"{BASE_URL}/intervals").mock(return_value=httpx.Response(404))

    with OpenF1Client(_settings()) as client:
        result = client.get_intervals(session_key=1)

    assert result == []


@respx.mock
def test_get_location_uses_strict_inequality_date_filters():
    """OpenF1's range filter is a strict `date>`/`date<` appended to the
    field name - `date>=` silently matches nothing (confirmed against the
    live API). This pins that exact query-string shape so a refactor can't
    quietly reintroduce the `>=` mistake."""
    route = respx.get(f"{BASE_URL}/location").mock(return_value=httpx.Response(200, json=[]))

    with OpenF1Client(_settings()) as client:
        client.get_location(
            session_key=9693,
            date_from=datetime(2025, 3, 16, 4, 18, 22, tzinfo=timezone.utc),
            date_to=datetime(2025, 3, 16, 4, 19, 22, tzinfo=timezone.utc),
        )

    sent = route.calls.last.request.url
    assert "date%3E=2025-03-16T04%3A18%3A22" in str(sent)
    assert "date%3C=2025-03-16T04%3A19%3A22" in str(sent)


@respx.mock
def test_get_car_data_all_drivers_in_one_call():
    route = respx.get(f"{BASE_URL}/car_data").mock(return_value=httpx.Response(200, json=[{"speed": 300}]))

    with OpenF1Client(_settings()) as client:
        result = client.get_car_data(
            session_key=9693,
            date_from=datetime(2025, 3, 16, 4, 18, 22, tzinfo=timezone.utc),
            date_to=datetime(2025, 3, 16, 4, 19, 22, tzinfo=timezone.utc),
        )

    assert result == [{"speed": 300}]
    assert "driver_number" not in str(route.calls.last.request.url)


@respx.mock
def test_validation_error_on_malformed_response():
    respx.get(f"{BASE_URL}/meetings").mock(return_value=httpx.Response(200, json=[{"meeting_name": "Missing keys"}]))

    with OpenF1Client(_settings()) as client, pytest.raises(OpenF1ValidationError):
        client.get_meetings(year=2025)
