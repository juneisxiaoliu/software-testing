import pytest
from air_traffic_control import air_traffic_control


# Test Case 1: Predicate P1 = True

def test_predicate_P1_true(capsys):
    result = air_traffic_control(
        runway_clear = True,
        alternate_runway_available = False,
        plane_speed = 120,
        emergency = False,
        wind_speed = 20,
        visibility = 2000,
        airport_traffic = 2,
        priority_status = False
    )

    assert result == "Landing Allowed"

    captured = capsys.readouterr().out
    assert "All conditions met for landing." in captured


# Test Case 2: Predicate P2 = True
def test_predicate_P2_true(capsys):
    result = air_traffic_control(
        runway_clear = False,
        alternate_runway_available = True,
        plane_speed = 140,
        emergency = False,
        wind_speed = 50,  # unsafe weather
        visibility = 500,
        airport_traffic = 7,  # requires override
        priority_status = True
    )

    assert result == "Landing Allowed"

    captured = capsys.readouterr().out
    assert "Landing allowed with priority overrides." in captured


# Test Case 3: Predicate P3 = True
def test_predicate_P3_true(capsys):
    result = air_traffic_control(
        runway_clear = False,
        alternate_runway_available = False,
        plane_speed = 200,
        emergency = True,
        wind_speed = 60,
        visibility = 300,
        airport_traffic = 10,
        priority_status = True
    )

    assert result == "Landing Allowed"

    captured = capsys.readouterr().out
    assert "Emergency landing with priority clearance." in captured


# Test Case 4: All predicates False → else branch
def test_predicate_all_false(capsys):
    result = air_traffic_control(
        runway_clear = False,
        alternate_runway_available = False,
        plane_speed = 180,
        emergency = False,
        wind_speed = 60,
        visibility = 300,
        airport_traffic = 10,
        priority_status = False
    )

    assert result == "Landing Denied"

    captured = capsys.readouterr().out
    assert "Conditions not met for safe landing." in captured
