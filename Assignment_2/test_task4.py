import pytest

import air_traffic_control

def test_activeClausesFirstPredicate(capsys):
    #all needed true
    inputs = [True, True, 100.0, False, 10.0, 1000, 2, False]
    assert air_traffic_control.air_traffic_control(inputs[0],inputs[1],inputs[2],inputs[3],inputs[4],inputs[5],
                                                   inputs[6],inputs[7])=="Landing Allowed"
    captured = capsys.readouterr()
    assert "All conditions met for landing." in captured.out
    #set speed to false (too high)
    inputs = [True, True, 150.0, False, 10.0, 1000, 2, False]
    assert air_traffic_control.air_traffic_control(inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], inputs[5],
                                                   inputs[6], inputs[7]) == "Landing Denied"
    captured = capsys.readouterr()
    assert "Conditions not met for safe landing." in captured.out

    #all needed true
    inputs = [False, True, 100.0, False, 10.0, 1000, 2, False]
    assert air_traffic_control.air_traffic_control(inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], inputs[5],
                                                   inputs[6], inputs[7]) == "Landing Allowed"
    captured = capsys.readouterr()
    assert "All conditions met for landing." in captured.out
    #set wind speed false (too high9
    inputs = [False, True, 100.0, False, 50.0, 1000, 2, False]
    assert air_traffic_control.air_traffic_control(inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], inputs[5],
                                                   inputs[6], inputs[7]) == "Landing Denied"
    captured = capsys.readouterr()
    assert "Conditions not met for safe landing." in captured.out
    #all neded true
    inputs = [True, False, 100.0, False, 10.0, 1000, 2, False]
    assert air_traffic_control.air_traffic_control(inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], inputs[5],
                                                   inputs[6], inputs[7]) == "Landing Allowed"
    captured = capsys.readouterr()
    assert "All conditions met for landing." in captured.out
    #set traffic false (too high)
    inputs = [True, False, 100.0, False, 10.0, 1000, 6, False]
    assert air_traffic_control.air_traffic_control(inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], inputs[5],
                                                   inputs[6], inputs[7]) == "Landing Denied"
    captured = capsys.readouterr()
    assert "Conditions not met for safe landing." in captured.out

def test_activeClausesSecondPredicate(capsys):
    #only with priority possible (visibility low)
    inputs = [True, True, 100.0, False, 10.0, 800, 2, True]
    assert air_traffic_control.air_traffic_control(inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], inputs[5],
                                                   inputs[6], inputs[7]) == "Landing Allowed"
    captured = capsys.readouterr()
    assert "Landing allowed with priority overrides." in captured.out
    #landing still allowed but predicate set to false, different reasoning for allowance
    inputs = [True, True, 100.0, True, 10.0, 800, 2, True]
    assert air_traffic_control.air_traffic_control(inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], inputs[5],
                                                   inputs[6], inputs[7]) == "Landing Allowed"
    captured = capsys.readouterr()
    assert "Emergency landing with priority clearance." in captured.out
    # only with priority possible (visibility low)
    inputs = [False, True, 100.0, False, 10.0, 800, 2, True]
    assert air_traffic_control.air_traffic_control(inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], inputs[5],
                                                   inputs[6], inputs[7]) == "Landing Allowed"
    captured = capsys.readouterr()
    assert "Landing allowed with priority overrides." in captured.out
    #speed to false (too high)
    inputs = [False, True, 150.0, False, 10.0, 800, 2, True]
    assert air_traffic_control.air_traffic_control(inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], inputs[5],
                                                   inputs[6], inputs[7]) == "Landing Denied"
    captured = capsys.readouterr()
    assert "Conditions not met for safe landing." in captured.out
    # only with priority possible (visibility low)
    inputs = [True, False, 100.0, False, 10.0, 800, 2, True]
    assert air_traffic_control.air_traffic_control(inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], inputs[5],
                                                   inputs[6], inputs[7]) == "Landing Allowed"
    captured = capsys.readouterr()
    assert "Landing allowed with priority overrides." in captured.out
    #no runway available
    inputs = [False, False, 100.0, False, 10.0, 800, 6, True]
    assert air_traffic_control.air_traffic_control(inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], inputs[5],
                                                   inputs[6], inputs[7]) == "Landing Denied"
    captured = capsys.readouterr()
    assert "Conditions not met for safe landing." in captured.out


def test_activeClausesThirdPredicate(capsys):
    #both true, no other allowance possbile
    inputs = [False, False, 100.0, True, 10.0, 1000, 2, True]
    assert air_traffic_control.air_traffic_control(inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], inputs[5],
                                                   inputs[6], inputs[7]) == "Landing Allowed"
    captured = capsys.readouterr()
    assert "Emergency landing with priority clearance." in captured.out
    #no priority
    inputs = [False, False, 100.0, True, 10.0, 1000, 2, False]
    assert air_traffic_control.air_traffic_control(inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], inputs[5],
                                                   inputs[6], inputs[7]) == "Landing Denied"
    captured = capsys.readouterr()
    assert "Conditions not met for safe landing." in captured.out
    #no emergency
    inputs = [False, False, 100.0, False, 10.0, 1000, 2, True]
    assert air_traffic_control.air_traffic_control(inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], inputs[5],
                                                   inputs[6], inputs[7]) == "Landing Denied"
    captured = capsys.readouterr()
    assert "Conditions not met for safe landing." in captured.out

def test_inactiveClausesFirstPredicate(capsys):
    #landing denied anyways
    inputs = [True, True, 100.0, False, 10.0, 1000, 6, False]
    assert air_traffic_control.air_traffic_control(inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], inputs[5],
                                                   inputs[6], inputs[7]) == "Landing Denied"
    captured = capsys.readouterr()
    assert "Conditions not met for safe landing." in captured.out
    #giving emergency yields no change in predicate result
    inputs = [True, True, 100.0, True, 10.0, 1000, 6, False]
    assert air_traffic_control.air_traffic_control(inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], inputs[5],
                                                   inputs[6], inputs[7]) == "Landing Denied"
    captured = capsys.readouterr()
    assert "Conditions not met for safe landing." in captured.out
    #landing allowed (both runway and alternative)
    inputs = [True, True, 100.0, False, 10.0, 1000, 2, False]
    assert air_traffic_control.air_traffic_control(inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], inputs[5],
                                                   inputs[6], inputs[7]) == "Landing Allowed"
    captured = capsys.readouterr()
    assert "All conditions met for landing." in captured.out
    #alternative not available doesnt change result
    inputs = [True, False, 100.0, False, 10.0, 1000, 2, False]
    assert air_traffic_control.air_traffic_control(inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], inputs[5],
                                                   inputs[6], inputs[7]) == "Landing Allowed"
    captured = capsys.readouterr()
    assert "All conditions met for landing." in captured.out


def test_inactiveClausesSecondPredicate(capsys):
    #priority allowed
    inputs = [True, True, 100.0, False, 10.0, 800, 5, True]
    assert air_traffic_control.air_traffic_control(inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], inputs[5],
                                                   inputs[6], inputs[7]) == "Landing Allowed"
    captured = capsys.readouterr()
    assert "Landing allowed with priority overrides." in captured.out
    #set traffic too false, but maxtraffic still true (with priority)
    inputs = [True, True, 100.0, False, 10.0, 800, 6, True]
    assert air_traffic_control.air_traffic_control(inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], inputs[5],
                                                   inputs[6], inputs[7]) == "Landing Allowed"
    captured = capsys.readouterr()
    assert "Landing allowed with priority overrides." in captured.out
    #priority allowed
    inputs = [True, True, 100.0, False, 10.0, 100, 6, True]
    assert air_traffic_control.air_traffic_control(inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], inputs[5],
                                                   inputs[6], inputs[7]) == "Landing Allowed"
    captured = capsys.readouterr()
    assert "Landing allowed with priority overrides." in captured.out
    #wind speed to false, but still true (with priority)
    inputs = [True, True, 100.0, False, 100.0, 100, 6, True]
    assert air_traffic_control.air_traffic_control(inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], inputs[5],
                                                   inputs[6], inputs[7]) == "Landing Allowed"
    captured = capsys.readouterr()
    assert "Landing allowed with priority overrides." in captured.out



def test_inactiveClausesThirdPredicate(capsys):
    #denied because emergency false
    inputs = [False, False, 100.0, False, 10.0, 1000, 6, True]
    assert air_traffic_control.air_traffic_control(inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], inputs[5],
                                                   inputs[6], inputs[7]) == "Landing Denied"
    captured = capsys.readouterr()
    assert "Conditions not met for safe landing." in captured.out
    #priority to false does not affect
    inputs = [False, False, 100.0, False, 10.0, 1000, 6, False]
    assert air_traffic_control.air_traffic_control(inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], inputs[5],
                                                   inputs[6], inputs[7]) == "Landing Denied"
    captured = capsys.readouterr()
    assert "Conditions not met for safe landing." in captured.out
    #denied because priority false
    inputs = [False, False, 100.0, True, 10.0, 1000, 6, False]
    assert air_traffic_control.air_traffic_control(inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], inputs[5],
                                                   inputs[6], inputs[7]) == "Landing Denied"
    captured = capsys.readouterr()
    assert "Conditions not met for safe landing." in captured.out
    #emergency false does not affect
    inputs = [False, False, 100.0, False, 10.0, 1000, 6, False]
    assert air_traffic_control.air_traffic_control(inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], inputs[5],
                                                   inputs[6], inputs[7]) == "Landing Denied"
    captured = capsys.readouterr()
    assert "Conditions not met for safe landing." in captured.out