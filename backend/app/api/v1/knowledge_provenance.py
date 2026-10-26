from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.models.user import User
from app.schemas.knowledge_provenance import (
    KnowledgeFactAuditResponse,
    KnowledgeFactCreateRequest,
    KnowledgeFactResponse,
    KnowledgeFactUpdateRequest,
    KnowledgeSourceCreateRequest,
    KnowledgeSourceResponse,
    KnowledgeSourceUpdateRequest,
)
from app.services.knowledge_provenance_service import KnowledgeProvenanceService, is_fact_fresh


router = APIRouter(prefix="/admin", tags=["knowledge provenance"])


def _fact_response(fact) -> KnowledgeFactResponse:
    source = fact.source
    is_fresh = is_fact_fresh(fact, source)
    return KnowledgeFactResponse(
        id=fact.id,
        source_id=fact.source_id,
        source_name=source.name,
        source_url=source.source_url,
        attribution_text=source.attribution_text,
        subject_type=fact.subject_type,
        subject_id=fact.subject_id,
        country_code=fact.country_code,
        fact_type=fact.fact_type,
        value=fact.value,
        source_record_id=fact.source_record_id,
        source_record_url=fact.source_record_url,
        checked_at=fact.checked_at,
        freshness_days=fact.freshness_days or source.freshness_days,
        status="stale" if fact.status == "approved" and not is_fresh else fact.status,
        review_notes=fact.review_notes,
        reviewed_by=fact.reviewed_by,
        reviewed_at=fact.reviewed_at,
        created_at=fact.created_at,
        updated_at=fact.updated_at,
    )


@router.get("/knowledge-sources", response_model=list[KnowledgeSourceResponse])
def list_knowledge_sources(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[KnowledgeSourceResponse]:
    return [
        KnowledgeSourceResponse.model_validate(source)
        for source in KnowledgeProvenanceService(db).list_sources()
    ]


@router.post(
    "/knowledge-sources",
    response_model=KnowledgeSourceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_knowledge_source(
    payload: KnowledgeSourceCreateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> KnowledgeSourceResponse:
    source = KnowledgeProvenanceService(db).create_source(
        actor_id=admin.id, **payload.model_dump()
    )
    return KnowledgeSourceResponse.model_validate(source)


@router.patch("/knowledge-sources/{source_id}", response_model=KnowledgeSourceResponse)
def update_knowledge_source(
    source_id: int,
    payload: KnowledgeSourceUpdateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> KnowledgeSourceResponse:
    source = KnowledgeProvenanceService(db).update_source(
        source_id,
        actor_id=admin.id,
        **payload.model_dump(exclude_unset=True),
    )
    return KnowledgeSourceResponse.model_validate(source)


@router.get("/knowledge-facts", response_model=list[KnowledgeFactResponse])
def list_knowledge_facts(
    fact_status: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[KnowledgeFactResponse]:
    allowed = {"pending", "approved", "rejected", "withdrawn", "stale"}
    if fact_status is not None and fact_status not in allowed:
        raise HTTPException(status_code=422, detail="Unsupported knowledge fact status")
    return [
        _fact_response(fact)
        for fact in KnowledgeProvenanceService(db).list_facts(status=fact_status)
    ]


@router.post(
    "/knowledge-facts",
    response_model=KnowledgeFactResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_knowledge_fact(
    payload: KnowledgeFactCreateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> KnowledgeFactResponse:
    fact = KnowledgeProvenanceService(db).create_fact(
        actor_id=admin.id, **payload.model_dump()
    )
    return _fact_response(fact)


@router.patch("/knowledge-facts/{fact_id}", response_model=KnowledgeFactResponse)
def update_knowledge_fact(
    fact_id: int,
    payload: KnowledgeFactUpdateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> KnowledgeFactResponse:
    fact = KnowledgeProvenanceService(db).update_fact(
        fact_id,
        actor_id=admin.id,
        **payload.model_dump(exclude_unset=True),
    )
    return _fact_response(fact)


@router.get(
    "/knowledge-facts/{fact_id}/audit",
    response_model=list[KnowledgeFactAuditResponse],
)
def get_knowledge_fact_audit(
    fact_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[KnowledgeFactAuditResponse]:
    return [
        KnowledgeFactAuditResponse.model_validate(event)
        for event in KnowledgeProvenanceService(db).list_audit(fact_id)
    ]
