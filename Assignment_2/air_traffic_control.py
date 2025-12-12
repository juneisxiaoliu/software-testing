def air_traffic_control(
    runway_clear, 
    alternate_runway_available, 
    plane_speed, 
    emergency, 
    wind_speed, 
    visibility, 
    airport_traffic, 
    priority_status
):
    """
    Determines whether a plane can land safely based on multiple conditions.

    :param runway_clear: Boolean, whether the primary runway is clear.
    :param alternate_runway_available: Boolean, whether an alternate runway is available.
    :param plane_speed: Float, current speed of the plane in knots.
    :param emergency: Boolean, whether the plane is in an emergency.
    :param wind_speed: Float, current wind speed in knots.
    :param visibility: Float, visibility in meters.
    :param airport_traffic: Integer, current number of planes in the airport's airspace.
    :param priority_status: Boolean, whether the plane has priority clearance.
    :return: String, indicating the landing decision ("Landing Allowed" or "Landing Denied").
    """
    # Thresholds
    landing_speed_threshold = 150  # Maximum speed for safe landing in knots
    max_wind_speed = 40            # Maximum wind speed for safe landing in knots
    min_visibility = 1000          # Minimum visibility for safe landing in meters
    max_air_traffic = 5            # Maximum allowable traffic in airport airspace

    # derived conditions
    runway_available = runway_clear or alternate_runway_available
    safe_speed = plane_speed < landing_speed_threshold
    safe_weather = wind_speed <= max_wind_speed and visibility >= min_visibility
    acceptable_traffic = airport_traffic <= max_air_traffic
    traffic_override = priority_status and airport_traffic <= max_air_traffic + 3
    weather_override = priority_status and not safe_weather

    # Decision-making
    if runway_available and safe_speed and not emergency and safe_weather and acceptable_traffic:
        decision = "Landing Allowed"
        reason = "All conditions met for landing."
    elif runway_available and safe_speed and not emergency and \
            (acceptable_traffic or traffic_override) and (safe_weather or weather_override):
        decision = "Landing Allowed"
        reason = "Landing allowed with priority overrides."
    elif emergency and priority_status:
        decision = "Landing Allowed"
        reason = "Emergency landing with priority clearance."
    else:
        decision = "Landing Denied"
        reason = "Conditions not met for safe landing."

    # Debugging output
    print(f"Debug Info:\n{reason}\n")

    return decision
