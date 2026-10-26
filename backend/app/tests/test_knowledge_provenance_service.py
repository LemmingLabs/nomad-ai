from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException

from app.models.user import User
from app.models.knowledge_fact import KnowledgeFact
from app.services.knowledge_provenance_service import (
    KnowledgeProvenanceService,
    route_subject_id,
)


def _actor(db_session):
    actor = User(email="reviewer@example.com", password_hash="hashed")
    db_session.add(actor)
    db_session.commit()
    return actor


def _source(service, actor_id):
    return service.create_source(
        actor_id=actor_id,
        name="Local park register",
        owner="Park authority",
        source_url="https://example.org/routes",
        terms_url="https://example.org/terms",
        license_basis="Written permission",
        allowed_use="Display attributed place and access facts",
        attribution_text="Source: Local park register",
        geographic_scope=["KG"],
        freshness_days=30,
        approval_evidence="Permission reference CASE-123",
    )


def _fact(service, actor_id, source_id, **overrides):
    values = {
        "source_id": source_id,
        "subject_type": "place",
        "subject_id": "google_places:place-123",
        "country_code": "KG",
        "fact_type": "permit_required",
        "value": "Permit required for entry.",
        "source_record_id": "record-123",
        "source_record_url": "https://example.org/routes/record-123",
        "checked_at": datetime.now(timezone.utc),
        "freshness_days": 30,
    }
    values.update(overrides)
    return service.create_fact(actor_id=actor_id, **values)


def test_fact_requires_approved_source_and_source_record_before_publication(db_session):
    actor = _actor(db_session)
    service = KnowledgeProvenanceService(db_session)
    source = _source(service, actor.id)
    fact = _fact(service, actor.id, source.id)

    with pytest.raises(HTTPException, match="Approve source terms"):
        service.update_fact(fact.id, actor_id=actor.id, status="approved")

    service.update_source(source.id, actor_id=actor.id, status="approved")
    with pytest.raises(HTTPException, match="source record ID or URL"):
        service.update_fact(
            fact.id,
            actor_id=actor.id,
            source_record_id=None,
            source_record_url=None,
            status="approved",
        )


def test_public_facts_include_fresh_reviewed_claims_with_attribution(db_session):
    actor = _actor(db_session)
    service = KnowledgeProvenanceService(db_session)
    source = _source(service, actor.id)
    service.update_source(source.id, actor_id=actor.id, status="approved")
    fact = _fact(service, actor.id, source.id)
    service.update_fact(fact.id, actor_id=actor.id, status="approved")

    result = service.list_public_facts(
        subject_type="place",
        subject_id="google_places:place-123",
        country_code="kg",
    )

    assert len(result) == 1
    assert result[0]["verification_status"] == "reviewed"
    assert result[0]["attribution_text"] == "Source: Local park register"
    assert service.list_public_facts(
        subject_type="place", subject_id="google_places:place-123", country_code="KZ"
    ) == []


def test_stale_or_withdrawn_facts_are_not_public_and_edits_return_to_review(db_session):
    actor = _actor(db_session)
    service = KnowledgeProvenanceService(db_session)
    source = _source(service, actor.id)
    service.update_source(source.id, actor_id=actor.id, status="approved")
    stale = _fact(
        service,
        actor.id,
        source.id,
        checked_at=datetime.now(timezone.utc) - timedelta(days=60),
    )
    db_session.query(KnowledgeFact).filter(KnowledgeFact.id == stale.id).update(
        {"status": "approved"}
    )
    db_session.commit()

    assert service.list_facts(status="stale")[0].id == stale.id
    assert service.list_public_facts(
        subject_type="place", subject_id="google_places:place-123", country_code="KG"
    ) == []

    fresh = _fact(service, actor.id, source.id)
    service.update_fact(fresh.id, actor_id=actor.id, status="approved")
    updated = service.update_fact(fresh.id, actor_id=actor.id, value="Updated access detail")
    assert updated.status == "pending"
    assert [event.action for event in service.list_audit(fresh.id)] == ["updated", "approved", "created"]

    service.update_fact(fresh.id, actor_id=actor.id, status="withdrawn")
    assert service.list_public_facts(
        subject_type="place", subject_id="google_places:place-123", country_code="KG"
    ) == []


def test_route_subject_id_is_stable_for_case_and_whitespace():
    assert route_subject_id("kg", "Bishkek   ", "Karakol") == "KG:bishkek->karakol"
