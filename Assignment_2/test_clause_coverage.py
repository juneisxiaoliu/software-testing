import pytest
from air_traffic_control import air_traffic_control


def run_test(capsys, **kwargs):
    """Helper to run function + capture printed output"""
    result = air_traffic_control(**kwargs)
    out = capsys.readouterr().out
    return result, out


# TC1: Baseline safe case
# Covers TRUE: runway_available, safe_speed, safe_weather,
#              acceptable_traffic
def test_TC1_all_safe(capsys):
    result, out = run_test(
        capsys,
        runway_clear=True,
        alternate_runway_available=False,
        plane_speed=120,
        emergency=False,
        wind_speed=20,
        visibility=2000,
        airport_traffic=2,
        priority_status=False
    )

    assert result == "Landing Allowed"
    assert "All conditions met for landing." in out


# TC2: traffic_override = TRUE
# Covers TRUE: traffic_override
# Covers FALSE: safe_weather, acceptable_traffic
def test_TC2_traffic_override_true(capsys):
    result, out = run_test(
        capsys,
        runway_clear=True,
        alternate_runway_available=False,
        plane_speed=120,
        emergency=False,
        wind_speed=60,      # unsafe weather
        visibility=500,
        airport_traffic=7,  # requires override
        priority_status=True
    )

    assert result == "Landing Allowed"
    assert "Landing allowed with priority overrides." in out


# TC3: weather_override = TRUE, emergency TRUE
# Covers TRUE: weather_override, emergency
def test_TC3_weather_override_true(capsys):
    result, out = run_test(
        capsys,
        runway_clear=True,
        alternate_runway_available=False,
        plane_speed=120,
        emergency=True,     # emergency true
        wind_speed=70,      # unsafe weather
        visibility=300,
        airport_traffic=2,
        priority_status=True
    )

    # Emergency + priority => P3
    assert result == "Landing Allowed"
    assert "Emergency landing with priority clearance." in out


# TC4: safe_speed = FALSE
# Covers FALSE: safe_speed
def test_TC4_speed_false(capsys):
    result, out = run_test(
        capsys,
        runway_clear=True,
        alternate_runway_available=False,
        plane_speed=200,  # unsafe speed
        emergency=False,
        wind_speed=20,
        visibility=2000,
        airport_traffic=2,
        priority_status=False
    )

    assert result == "Landing Denied"
    assert "Conditions not met for safe landing." in out


# TC5: runway_available = FALSE
# Covers FALSE: runway_available
def test_TC5_runway_unavailable(capsys):
    result, out = run_test(
        capsys,
        runway_clear=False,
        alternate_runway_available=False,
        plane_speed=120,
        emergency=False,
        wind_speed=20,
        visibility=2000,
        airport_traffic=2,
        priority_status=False
    )

    assert result == "Landing Denied"
    assert "Conditions not met for safe landing." in out


# TC6: acceptable_traffic = FALSE (but emergency TRUE)
# Covers FALSE: acceptable_traffic
def test_TC6_traffic_false_under_emergency(capsys):
    result, out = run_test(
        capsys,
        runway_clear=False,
        alternate_runway_available=False,
        plane_speed=200,
        emergency=True,       # TRUE → P3
        wind_speed=20,
        visibility=2000,
        airport_traffic=10,   # unacceptable traffic
        priority_status=True
    )

    assert result == "Landing Allowed"
    assert "Emergency landing with priority clearance." in out


# TC7: all core clauses FALSE
# Covers FALSE: safe_weather, runway_available, safe_speed,
#               acceptable_traffic, traffic_override, weather_override
def test_TC7_all_false(capsys):
    result, out = run_test(
        capsys,
        runway_clear=False,
        alternate_runway_available=False,
        plane_speed=200,
        emergency=False,
        wind_speed=70,
        visibility=300,
        airport_traffic=10,
        priority_status=False
    )

    assert result == "Landing Denied"
    assert "Conditions not met for safe landing." in out
