import json
import logging

from app.core.logging import ApplicationFormatter


def test_application_formatter_emits_generation_context_as_json():
    record = logging.LogRecord(
        name="app.services.trip_service",
        level=logging.WARNING,
        pathname=__file__,
        lineno=1,
        msg="trip_generation_stage_failed",
        args=(),
        exc_info=None,
    )
    record.event = "trip_generation_stage_failed"
    record.stage = "place_enrichment"
    record.country_code = "KG"
    record.error_type = "TimeoutError"

    payload = json.loads(ApplicationFormatter().format(record))

    assert payload["event"] == "trip_generation_stage_failed"
    assert payload["stage"] == "place_enrichment"
    assert payload["country_code"] == "KG"
    assert payload["error_type"] == "TimeoutError"
