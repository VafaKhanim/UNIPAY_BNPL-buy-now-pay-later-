from fastapi import APIRouter

from app.api.deps import DB
from app.schemas.installment import LoanScheduleResponse
from app.schemas.loan import LoanResponse
from app.services.loan_service import LoanService

router = APIRouter(tags=["Loans"])


@router.get("/loans/{loan_id}", response_model=LoanResponse)
def get_loan(loan_id: str, db: DB):
    return LoanService(db).get_by_id(loan_id)


@router.get("/loans/{loan_id}/schedule", response_model=LoanScheduleResponse)
def get_loan_schedule(loan_id: str, db: DB):
    return LoanService(db).get_schedule(loan_id)


@router.get(
    "/customers/{customer_id}/loans", response_model=list[LoanResponse]
)
def get_customer_loans(customer_id: str, db: DB):
    return LoanService(db).get_customer_loans(customer_id)