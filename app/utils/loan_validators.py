from sqlalchemy.orm import Session

from app.core.enums import ApplicationStatus, LoanStatus
from app.core.exceptions import BusinessRuleError
from app.models.loan import Loan, LoanApplication


def assert_no_active_loan(db: Session, customer_id: str) -> None:
    active = (
        db.query(Loan)
        .filter_by(customer_id=customer_id, status=LoanStatus.ACTIVE)
        .first()
    )
    if active:
        raise BusinessRuleError("Customer already has an active loan")


def assert_application_is_pending(application: LoanApplication) -> None:
    if application.status != ApplicationStatus.PENDING:
        raise BusinessRuleError(
            f"Application is already {application.status}"
        )