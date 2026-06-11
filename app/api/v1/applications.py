from fastapi import APIRouter

from app.api.deps import DB
from app.schemas.application import (
    ApplicationCreate,
    ApplicationDecision,
    ApplicationResponse,
)
from app.services.application_service import ApplicationService

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.post("", response_model=ApplicationResponse, status_code=201)
def create_application(data: ApplicationCreate, db: DB):
    return ApplicationService(db).create(data)


@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(application_id: str, db: DB):
    return ApplicationService(db).get_by_id(application_id)


@router.patch("/{application_id}/decision", response_model=ApplicationResponse)
def process_decision(
    application_id: str, data: ApplicationDecision, db: DB
):
    return ApplicationService(db).process_decision(application_id, data)