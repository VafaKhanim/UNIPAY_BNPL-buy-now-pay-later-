from fastapi import APIRouter

from app.api.deps import DB
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/overdue/process")
def process_overdue(db: DB):
    processed = AdminService(db).process_overdue()
    return {"processed": processed}


@router.post("/bad-debt/process")
def process_bad_debt(db: DB, threshold_days: int = 30):
    marked = AdminService(db).process_bad_debt(threshold_days)
    return {"marked_bad_debt": marked}
