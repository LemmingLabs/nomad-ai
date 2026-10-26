import re
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.knowledge_fact import KnowledgeFact, KnowledgeFactAudit
from app.models.knowledge_source import KnowledgeSource


SOURCE_METADATA_FIELDS = {
    "name", "owner", "source_url", "terms_url", "license_basis", "allowed_use",
    "attribution_text", "geographic_scope", "freshness_days", "approval_evidence",
}
FACT_CONTENT_FIELDS = {
    "source_id", "subject_type", "subject_id", "country_code", "fact_type", "value",
    "source_record_id", "source_record_url", "checked_at", "freshness_days",
}
FACT_MUTABLE_FIELDS = FACT_CONTENT_FIELDS | {"review_notes"}


def is_fact_fresh(fact: KnowledgeFact, source: KnowledgeSource, *, now: datetime | None = None) -> bool:
    checked_at = fact.checked_at
    if checked_at.tzinfo is None:
        checked_at = checked_at.replace(tzinfo=timezone.utc)
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    freshness_days = fact.freshness_days or source.freshness_days
    return current <= checked_at + timedelta(days=freshness_days)


def route_subject_id(country_code: str, origin: str, destination: str) -> str:
    def normalize(value: str) -> str:
        return re.sub(r"\s+", " ", value.strip().casefold())

    return f"{country_code.strip().upper()}:{normalize(origin)}->{normalize(destination)}"


class KnowledgeProvenanceService:
    def __init__(self, db: Session):
        self.db = db

    def list_sources(self) -> list[KnowledgeSource]:
        return list(self.db.execute(
            select(KnowledgeSource).order_by(KnowledgeSource.updated_at.desc())
        ).scalars().all())

    def get_source(self, source_id: int) -> KnowledgeSource:
        source = self.db.get(KnowledgeSource, source_id)
        if source is None:
            raise HTTPException(status_code=404, detail="Knowledge source not found")
        return source

    def create_source(self, *, actor_id: int, **values) -> KnowledgeSource:
        values["source_url"] = str(values["source_url"])
        values["terms_url"] = str(values["terms_url"])
        values["geographic_scope"] = [code.upper() for code in values["geographic_scope"]]
        source = KnowledgeSource(**values, status="pending", created_by=actor_id)
        self.db.add(source)
        self.db.commit()
        self.db.refresh(source)
        return source

    def update_source(self, source_id: int, *, actor_id: int, **updates) -> KnowledgeSource:
        source = self.get_source(source_id)
        metadata_changed = any(key in SOURCE_METADATA_FIELDS for key in updates)
        requested_status = updates.pop("status", None)
        if metadata_changed and source.status == "approved":
            if requested_status == "approved":
                raise HTTPException(
                    status_code=422,
                    detail="Save source-term changes as pending, then review and approve them separately",
                )
            source.status = "pending"
            source.approved_by = None
            source.approved_at = None

        for key, value in updates.items():
            if key in {"source_url", "terms_url"} and value is not None:
                value = str(value)
            if key == "geographic_scope" and value is not None:
                value = [code.strip().upper() for code in value]
            setattr(source, key, value)

        if requested_status is not None:
            if requested_status == "approved":
                required = (
                    source.license_basis,
                    source.allowed_use,
                    source.terms_url,
                    source.attribution_text,
                    source.approval_evidence,
                )
                if any(not str(item or "").strip() for item in required):
                    raise HTTPException(
                        status_code=422,
                        detail="Terms, allowed use, attribution, and approval evidence are required",
                    )
                source.approved_by = actor_id
                source.approved_at = datetime.now(timezone.utc)
            else:
                source.approved_by = None
                source.approved_at = None
            source.status = requested_status

        self.db.commit()
        self.db.refresh(source)
        return source

    def list_facts(self, *, status: str | None = None) -> list[KnowledgeFact]:
        statement = select(KnowledgeFact).options(selectinload(KnowledgeFact.source)).order_by(
            KnowledgeFact.updated_at.desc()
        )
        if status and status != "stale":
            statement = statement.where(KnowledgeFact.status == status)
        facts = list(self.db.execute(statement).scalars().all())
        if status == "stale":
            return [
                fact for fact in facts
                if fact.status == "approved" and not is_fact_fresh(fact, fact.source)
            ]
        return facts

    def get_fact(self, fact_id: int) -> KnowledgeFact:
        fact = self.db.execute(
            select(KnowledgeFact)
            .where(KnowledgeFact.id == fact_id)
            .options(selectinload(KnowledgeFact.source))
        ).scalar_one_or_none()
        if fact is None:
            raise HTTPException(status_code=404, detail="Knowledge fact not found")
        return fact

    @staticmethod
    def _snapshot(fact: KnowledgeFact) -> dict:
        return {
            "source_id": fact.source_id,
            "subject_type": fact.subject_type,
            "subject_id": fact.subject_id,
            "country_code": fact.country_code,
            "fact_type": fact.fact_type,
            "value": fact.value,
            "source_record_id": fact.source_record_id,
            "source_record_url": fact.source_record_url,
            "checked_at": fact.checked_at.isoformat() if fact.checked_at else None,
            "freshness_days": fact.freshness_days,
            "status": fact.status,
            "review_notes": fact.review_notes,
        }

    def _validate_fact(self, fact: KnowledgeFact, source: KnowledgeSource, status: str) -> None:
        if fact.country_code.upper() not in source.geographic_scope and "*" not in source.geographic_scope:
            raise HTTPException(status_code=422, detail="The source is not approved for this country")
        if status == "approved":
            if source.status != "approved":
                raise HTTPException(status_code=422, detail="Approve source terms before publishing facts")
            if not (fact.source_record_id or fact.source_record_url):
                raise HTTPException(status_code=422, detail="A source record ID or URL is required before publishing")
            if not is_fact_fresh(fact, source):
                raise HTTPException(status_code=422, detail="Refresh this fact before publishing it")

    def create_fact(self, *, actor_id: int, **values) -> KnowledgeFact:
        values["country_code"] = values["country_code"].strip().upper()
        if values.get("source_record_url") is not None:
            values["source_record_url"] = str(values["source_record_url"])
        source = self.get_source(values["source_id"])
        fact = KnowledgeFact(**values, status="pending", created_by=actor_id)
        self._validate_fact(fact, source, "pending")
        self.db.add(fact)
        self.db.flush()
        self.db.add(KnowledgeFactAudit(
            fact_id=fact.id,
            actor_id=actor_id,
            action="created",
            after_state=self._snapshot(fact),
        ))
        self.db.commit()
        return self.get_fact(fact.id)

    def update_fact(self, fact_id: int, *, actor_id: int, **updates) -> KnowledgeFact:
        fact = self.get_fact(fact_id)
        before = self._snapshot(fact)
        requested_status = updates.pop("status", None)
        content_changed = bool(set(updates) & FACT_CONTENT_FIELDS)
        for key, value in updates.items():
            if key not in FACT_MUTABLE_FIELDS:
                continue
            if key == "source_record_url" and value is not None:
                value = str(value)
            if key == "country_code" and value is not None:
                value = value.strip().upper()
            setattr(fact, key, value)
        source = self.get_source(fact.source_id)
        self._validate_fact(
            fact,
            source,
            "pending" if content_changed and requested_status is None else (requested_status or "pending"),
        )
        if requested_status is not None:
            self._validate_fact(fact, source, requested_status)
            fact.status = requested_status
            fact.reviewed_by = actor_id if requested_status in {"approved", "rejected", "withdrawn"} else None
            fact.reviewed_at = datetime.now(timezone.utc) if fact.reviewed_by else None
        elif content_changed and fact.status == "approved":
            # Content edits always return a claim to the review queue.
            fact.status = "pending"
            fact.reviewed_by = None
            fact.reviewed_at = None

        self.db.flush()
        action = requested_status or "updated"
        self.db.add(KnowledgeFactAudit(
            fact_id=fact.id,
            actor_id=actor_id,
            action=action,
            note=fact.review_notes,
            before_state=before,
            after_state=self._snapshot(fact),
        ))
        self.db.commit()
        return self.get_fact(fact.id)

    def list_public_facts(self, *, subject_type: str, subject_id: str, country_code: str) -> list[dict]:
        facts = self.db.execute(
            select(KnowledgeFact)
            .join(KnowledgeSource, KnowledgeSource.id == KnowledgeFact.source_id)
            .where(
                KnowledgeFact.subject_type == subject_type,
                KnowledgeFact.subject_id == subject_id,
                KnowledgeFact.country_code == country_code.upper(),
                KnowledgeFact.status == "approved",
                KnowledgeSource.status == "approved",
            )
            .options(selectinload(KnowledgeFact.source))
            .order_by(KnowledgeFact.fact_type.asc(), KnowledgeFact.id.asc())
        ).scalars().all()
        result = []
        for fact in facts:
            if not is_fact_fresh(fact, fact.source):
                continue
            result.append({
                "subject_type": fact.subject_type,
                "fact_type": fact.fact_type,
                "value": fact.value,
                "source_name": fact.source.name,
                "source_url": fact.source.source_url,
                "attribution_text": fact.source.attribution_text,
                "checked_at": fact.checked_at,
                "verification_status": "reviewed",
            })
        return result

    def attach_facts_to_itinerary(self, itinerary: dict, country_code: str) -> dict:
        days = itinerary.get("days")
        if not isinstance(days, list):
            return itinerary
        for day in days:
            if not isinstance(day, dict):
                continue
            facts = []
            candidate = day.get("place_candidate")
            if isinstance(candidate, dict) and candidate.get("place_id"):
                provider = str(candidate.get("provider") or "unknown")
                subject_id = f"{provider}:{candidate['place_id']}"
                facts.extend(self.list_public_facts(
                    subject_type="place", subject_id=subject_id, country_code=country_code
                ))
            route = day.get("route_from_previous")
            if isinstance(route, dict) and route.get("origin") and route.get("destination"):
                subject_id = route_subject_id(country_code, str(route["origin"]), str(route["destination"]))
                facts.extend(self.list_public_facts(
                    subject_type="route", subject_id=subject_id, country_code=country_code
                ))
            if facts:
                day["reviewed_facts"] = facts
            else:
                day.pop("reviewed_facts", None)
        return itinerary

    def list_audit(self, fact_id: int) -> list[KnowledgeFactAudit]:
        self.get_fact(fact_id)
        return list(self.db.execute(
            select(KnowledgeFactAudit)
            .where(KnowledgeFactAudit.fact_id == fact_id)
            .order_by(KnowledgeFactAudit.created_at.desc(), KnowledgeFactAudit.id.desc())
        ).scalars().all())
