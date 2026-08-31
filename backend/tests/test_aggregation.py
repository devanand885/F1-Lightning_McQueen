from app.repositories.aggregation import aggregate_results


def test_aggregate_results_computes_points_wins_podiums_from_race_sessions_only():
    rows = [
        # (entity_id, session_type, position, points, dnf)
        (1, "Qualifying", 1, 0.0, False),  # pole - shouldn't count as a "win"
        (1, "Race", 1, 25.0, False),
        (1, "Race", 3, 15.0, False),
        (1, "Race", None, 0.0, True),  # DNF
        (2, "Race", 2, 18.0, False),
    ]

    result = aggregate_results(rows)

    assert result[1]["points"] == 40.0
    assert result[1]["wins"] == 1
    assert result[1]["podiums"] == 2
    assert result[1]["avg_finish"] == 2.0  # (1 + 3) / 2, DNF has no position
    assert result[1]["dnf_rate"] == 1 / 3

    assert result[2]["points"] == 18.0
    assert result[2]["wins"] == 0
    assert result[2]["podiums"] == 1
    assert result[2]["dnf_rate"] == 0.0


def test_aggregate_results_handles_entity_with_no_race_sessions():
    rows = [(1, "Practice", 5, 0.0, False)]

    result = aggregate_results(rows)

    assert result[1]["points"] == 0.0
    assert result[1]["wins"] == 0
    assert result[1]["podiums"] == 0
    assert result[1]["avg_finish"] is None
    assert result[1]["dnf_rate"] is None


def test_aggregate_results_with_no_rows_returns_empty():
    assert aggregate_results([]) == {}
