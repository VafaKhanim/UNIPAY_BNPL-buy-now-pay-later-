from fastapi import APIRouter

from app.api.deps import DB
from app.schemas.installment import InstallmentResponse
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.services.payment_service import PaymentService

router = APIRouter(tags=["Payments"])


@router.get(
    "/installments/{installment_id}", response_model=InstallmentResponse
)
def get_installment(installment_id: str, db: DB):
    return PaymentService(db).get_installment(installment_id)


@router.post(
    "/installments/{installment_id}/pay",
    response_model=PaymentResponse,
    status_code=201,
)
def pay_installment(
    installment_id: str, data: PaymentCreate, db: DB
):
    return PaymentService(db).pay_installment(installment_id, data)


@router.get(
    "/installments/{installment_id}/payments",
    response_model=list[PaymentResponse],
)
def get_installment_payments(installment_id: str, db: DB):
    return PaymentService(db).get_installment_payments(installment_id)