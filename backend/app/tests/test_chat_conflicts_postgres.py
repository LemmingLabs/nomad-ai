"""Concurrency tests run against an isolated schema when TEST_POSTGRES_URL is supplied."""
import os
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Event
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.models.trip import Trip
from app.models.trip_message import TripMessage
from app.models.user import User
from app.models.user_usage_stat import UserUsageStat
from app.services.trip_message_service import TripMessageService


@pytest.fixture
def sessions(monkeypatch):
    url = os.environ.get("TEST_POSTGRES_URL")
    if not url:
        pytest.skip("TEST_POSTGRES_URL not configured")
    schema = "chat_test_" + uuid4().hex
    admin = create_engine(url)
    with admin.begin() as connection:
        connection.execute(text(f'CREATE SCHEMA "{schema}"'))
    engine = create_engine(url, connect_args={"options": f"-csearch_path={schema}"})
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    with factory() as db:
        user = User(email="owner@example.test", password_hash="test")
        db.add(user)
        db.flush()
        trip = Trip(user_id=user.id, title="Trip", budget="100", days=1, interests=[], travel_style="balanced",
                    itinerary_json={"days": [{"day": 1, "location": "Bishkek", "city": "Bishkek",
                                              "place_candidate": {"place_id": "one"}, "images": {"hero": {"photo_id": "one"}}}]})
        db.add(trip)
        db.commit()
        trip_id, user_id = trip.id, user.id
    monkeypatch.setattr("app.services.trip_message_service.LimitService.can_edit_chat", lambda *_: True)
    monkeypatch.setattr("app.services.trip_message_service.CatalogService.enrich_itinerary_with_catalog", lambda self, value, *a, **kw: value)
    monkeypatch.setattr("app.services.trip_message_service.SponsoredInjectionService.inject_sponsored_places", lambda self, value, **kw: value)
    monkeypatch.setattr("app.services.knowledge_provenance_service.KnowledgeProvenanceService.attach_facts_to_itinerary", lambda self, value, *a: value)
    monkeypatch.setattr("app.services.trip_message_service.validate_itinerary_quality", lambda *a: None)
    try:
        yield factory, trip_id, user_id
    finally:
        engine.dispose()
        with admin.begin() as connection:
            connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        admin.dispose()


def test_overlapping_edits_conflict_without_losing_messages_or_charging_twice(sessions):
    factory, trip_id, user_id = sessions
    barrier = Barrier(2, timeout=10)
    winner_done = Event()
    first_key, second_key = str(uuid4()), str(uuid4())

    class AI:
        def __init__(self, winner):
            self.winner = winner

        def continue_trip(self, **kwargs):
            barrier.wait()
            if not self.winner:
                assert winner_done.wait(10)
            day = dict(kwargs["current_itinerary"]["days"][0])
            day["title"] = "winner" if self.winner else "loser"
            return "saved", {"days": [day]}

    def run(winner, key):
        with factory() as db:
            trip = db.get(Trip, trip_id)
            try:
                response = TripMessageService(db, ai_service=AI(winner)).continue_trip(trip, "first" if winner else "second", key)
                if winner:
                    winner_done.set()
                return response
            except HTTPException as error:
                return error

    with ThreadPoolExecutor(max_workers=2) as executor:
        first = executor.submit(run, True, first_key)
        second = executor.submit(run, False, second_key)
        assert first.result(timeout=20)[0].content == "saved"
        error = second.result(timeout=20)
    assert isinstance(error, HTTPException) and error.status_code == 409
    with factory() as db:
        trip = db.get(Trip, trip_id)
        assert trip.itinerary_json["days"][0]["title"] == "winner"
        assert trip.chat_revision == 1
        assert db.query(TripMessage).count() == 2
        assert db.query(UserUsageStat).filter_by(user_id=user_id).one().chat_edits_count == 1
        class RetryAI:
            def continue_trip(self, **kwargs):
                day = dict(kwargs["current_itinerary"]["days"][0])
                day["title"] = "retry"
                return "retried", {"days": [day]}
        service = TripMessageService(db, ai_service=RetryAI())
        assert service.continue_trip(trip, "second", second_key)[0].content == "retried"
        assert service.continue_trip(trip, "second", second_key)[0].content == "retried"
        original_reply, current_itinerary = service.continue_trip(trip, "first", first_key)
        assert original_reply.content == "saved"
        assert current_itinerary["days"][0]["title"] == "retry"
        with pytest.raises(HTTPException) as mismatch:
            service.continue_trip(trip, "different content", second_key)
        assert mismatch.value.status_code == 409
        assert db.get(Trip, trip_id).itinerary_json["days"][0]["title"] == "retry"
        assert db.query(TripMessage).count() == 4
        assert db.query(UserUsageStat).filter_by(user_id=user_id).one().chat_edits_count == 2


def test_provider_failure_rolls_back_messages_revision_and_usage(sessions):
    factory, trip_id, user_id = sessions
    class FailedAI:
        def continue_trip(self, **kwargs):
            raise RuntimeError("provider failed")
    with factory() as db:
        trip = db.get(Trip, trip_id)
        with pytest.raises(RuntimeError):
            TripMessageService(db, ai_service=FailedAI()).continue_trip(trip, "edit", str(uuid4()))
        assert db.get(Trip, trip_id).chat_revision == 0
        assert db.query(TripMessage).count() == 0
        assert db.query(UserUsageStat).filter_by(user_id=user_id).count() == 0


def test_concurrent_retries_with_same_request_id_are_charged_once(sessions):
    factory, trip_id, user_id = sessions
    barrier = Barrier(2, timeout=10)
    winner_done = Event()
    key = str(uuid4())

    class AI:
        def __init__(self, winner):
            self.winner = winner

        def continue_trip(self, **kwargs):
            barrier.wait()
            if not self.winner:
                assert winner_done.wait(10)
            return "same answer", None

    def run(winner):
        with factory() as db:
            trip = db.get(Trip, trip_id)
            response = TripMessageService(db, ai_service=AI(winner)).continue_trip(trip, "same edit", key)
            if winner:
                winner_done.set()
            return response[0].id

    with ThreadPoolExecutor(max_workers=2) as executor:
        first = executor.submit(run, True)
        second = executor.submit(run, False)
        assert first.result(timeout=20) == second.result(timeout=20)
    with factory() as db:
        assert db.get(Trip, trip_id).chat_revision == 1
        assert db.query(TripMessage).count() == 2
        assert db.query(UserUsageStat).filter_by(user_id=user_id).one().chat_edits_count == 1
