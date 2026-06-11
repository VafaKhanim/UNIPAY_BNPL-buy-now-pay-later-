from sqlalchemy.orm import Session

from app.core.enums import InstallmentStatus
from app.core.exceptions import BusinessRuleError, NotFoundError
from app.models.installment import Installment

PAYABLE_STATUSES = {
    InstallmentStatus.SCHEDULED,
    InstallmentStatus.DUE,
    InstallmentStatus.OVERDUE,
}


def get_installment_or_404(db: Session, installment_id: str) -> Installment:
    installment = db.get(Installment, installment_id)
    if not installment:
        raise NotFoundError("Installment", installment_id)
    return installment


def assert_installment_is_payable(installment: Installment) -> None:
    if installment.status not in PAYABLE_STATUSES:
        raise BusinessRuleError(
            f"Installment cannot be paid. Status: {installment.status}"
        )
