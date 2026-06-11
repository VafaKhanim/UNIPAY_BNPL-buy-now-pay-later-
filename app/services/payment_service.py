from sqlalchemy.orm import Session

from app.core.enums import InstallmentStatus, PaymentStatus
from app.models.base import utcnow
from app.models.installment import Installment
from app.models.payment import Payment
from app.schemas.payment import PaymentCreate
from app.utils.payment_validators import (
    assert_installment_is_payable,
    get_installment_or_404,
)


class PaymentService:
    def __init__(self, db: Session):
        self.db = db

    def pay_installment(
        self, installment_id: str, data: PaymentCreate
    ) -> Payment:
        installment = get_installment_or_404(self.db, installment_id)
        assert_installment_is_payable(installment)

        payment = self._create_payment(installment, data)
        self._mark_paid(payment, installment)

        self.db.commit()
        self.db.refresh(payment)
        return payment

    def get_installment(self, installment_id: str) -> Installment:
        return get_installment_or_404(self.db, installment_id)

    def get_installment_payments(self, installment_id: str) -> list[Payment]:
        return (
            self.db.query(Payment)
            .filter_by(installment_id=installment_id)
            .order_by(Payment.created_at.desc())
            .all()
        )

    def _create_payment(
        self, installment: Installment, data: PaymentCreate
    ) -> Payment:
        payment = Payment(
            installment_id=installment.id,
            amount=installment.total_amount,
            status=PaymentStatus.PENDING,
            payment_method=data.payment_method,
            provider_transaction_id=data.provider_transaction_id,
        )
        self.db.add(payment)
        self.db.flush()
        return payment

    def _mark_paid(self, payment: Payment, installment: Installment) -> None:
        payment.status = PaymentStatus.SUCCESS
        installment.status = InstallmentStatus.PAID
        installment.paid_at = utcnow()
