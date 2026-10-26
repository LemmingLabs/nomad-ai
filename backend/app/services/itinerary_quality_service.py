"""Warnings for itinerary details that are incomplete or may not fit a day."""

import re
import math


_TIME_WINDOW_PATTERN = re.compile(r"^(\d{1,2}):(\d{2})\s*[-–]\s*(\d{1,2}):(\d{2})$")


def _distance_km(first: dict, second: dict) -> float | None:
    try:
        lat1, lon1 = float(first["lat"]), float(first["lng"])
        lat2, lon2 = float(second["lat"]), float(second["lng"])
    except (KeyError, TypeError, ValueError):
        return None
    if not (-90 <= lat1 <= 90 and -90 <= lat2 <= 90 and -180 <= lon1 <= 180 and -180 <= lon2 <= 180):
        return None
    lat1, lat2 = math.radians(lat1), math.radians(lat2)
    delta_lat = lat2 - lat1
    delta_lon = math.radians(lon2 - lon1)
    value = math.sin(delta_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
    return 6371 * 2 * math.atan2(math.sqrt(value), math.sqrt(1 - value))


def validate_itinerary_quality(itinerary: dict, country_code: str) -> list[dict[str, str | int]]:
    warnings: list[dict[str, str | int]] = []
    days = itinerary.get("days")
    if not isinstance(days, list):
        return warnings

    for index, day in enumerate(days):
        if not isinstance(day, dict):
            continue
        day_number = day.get("day", index + 1)
        if not str(day.get("city") or "").strip() or not str(day.get("location") or "").strip():
            warnings.append({
                "code": "location_details_missing",
                "day": day_number,
                "message": f"A city or primary location is missing for day {day_number}.",
            })
        activities = day.get("activities")
        if not isinstance(activities, list):
            activities = []

        total_duration = 0
        has_unknown_duration = False
        overlap_detected = False
        order_conflict = False
        boundary_conflict = False
        previous_start: int | None = None
        windows: list[tuple[int, int]] = []
        for activity in activities:
            if not isinstance(activity, dict):
                continue
            duration = activity.get("duration_minutes")
            if isinstance(duration, int) and not isinstance(duration, bool) and duration > 0:
                total_duration += duration
            else:
                has_unknown_duration = True

            match = _TIME_WINDOW_PATTERN.fullmatch(str(activity.get("time_window") or "").strip())
            if match:
                start_hour, start_minute, end_hour, end_minute = map(int, match.groups())
                if start_hour < 24 and end_hour < 24 and start_minute < 60 and end_minute < 60:
                    start = start_hour * 60 + start_minute
                    end = end_hour * 60 + end_minute
                    if end > start:
                        if start < 6 * 60 or end > 23 * 60:
                            boundary_conflict = True
                        if previous_start is not None and start < previous_start:
                            order_conflict = True
                        previous_start = start
                        if any(start < prior_end and end > prior_start for prior_start, prior_end in windows):
                            overlap_detected = True
                        windows.append((start, end))

        if overlap_detected:
            warnings.append({
                "code": "overlapping_activity_times",
                "day": day_number,
                "message": f"Some estimated activity times overlap on day {day_number}.",
            })
        if order_conflict:
            warnings.append({
                "code": "activity_order_conflict",
                "day": day_number,
                "message": f"Estimated activity times are not in chronological order on day {day_number}.",
            })
        if boundary_conflict:
            warnings.append({
                "code": "activity_outside_day_window",
                "day": day_number,
                "message": f"An estimated activity time falls outside the suggested 6 AM to 11 PM day window for day {day_number}.",
            })
        if has_unknown_duration and activities:
            warnings.append({
                "code": "activity_duration_unknown",
                "day": day_number,
                "message": f"One or more activity durations are unknown for day {day_number}.",
            })
        if total_duration > 12 * 60:
            warnings.append({
                "code": "schedule_overloaded",
                "day": day_number,
                "message": f"The estimated activities exceed 12 hours on day {day_number}; review the pace.",
            })

        if index > 0:
            route = day.get("route_from_previous")
            route_unavailable = (
                not isinstance(route, dict)
                or route.get("status") in {"unavailable", "stale"}
                or route.get("distance_km") is None
                or route.get("duration_mins") is None
            )
            if route_unavailable:
                warnings.append({
                    "code": "route_details_unavailable",
                    "day": day_number,
                    "message": f"Transfer details for day {day_number} are unavailable or stale.",
                })
            elif total_duration and route.get("duration_mins"):
                try:
                    route_duration = int(route["duration_mins"])
                except (TypeError, ValueError):
                    route_duration = 0
                if route_duration > 0 and total_duration + route_duration > 14 * 60:
                    warnings.append({
                        "code": "travel_day_overloaded",
                        "day": day_number,
                        "message": f"Activities plus the transfer may make day {day_number} too long.",
                    })

            previous_candidate = days[index - 1].get("place_candidate") if isinstance(days[index - 1], dict) else None
            current_candidate = day.get("place_candidate")
            if isinstance(route, dict) and isinstance(previous_candidate, dict) and isinstance(current_candidate, dict):
                straight_distance = _distance_km(previous_candidate, current_candidate)
                route_distance = route.get("distance_km")
                if (
                    straight_distance is not None
                    and isinstance(route_distance, (int, float))
                    and route_distance > max(200, straight_distance * 4, straight_distance + 100)
                ):
                    warnings.append({
                        "code": "route_may_backtrack",
                        "day": day_number,
                        "message": f"The transfer to day {day_number} may be unusually indirect; review the route.",
                    })

        place_candidate = day.get("place_candidate")
        if isinstance(place_candidate, dict):
            candidate_country = place_candidate.get("country_code")
            if candidate_country and str(candidate_country).upper() != country_code.upper():
                warnings.append({
                    "code": "stop_outside_destination",
                    "day": day_number,
                    "message": f"The suggested place for day {day_number} is outside the selected country.",
                })

    itinerary["quality_warnings"] = warnings
    return warnings
