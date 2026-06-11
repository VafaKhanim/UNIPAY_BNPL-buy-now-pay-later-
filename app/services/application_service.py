#BUNA BAXARSAN DAHA DA NECE SIMPLE ETMEK OLAR DEYE

from sqlalchemy.orm import Session

from app.config import settings
from app.core.enums import ApplicationStatus
from app.core.exceptions import BusinessRuleError
from app.models.loan import LoanApplication
from app.schemas.application import ApplicationCreate, ApplicationDecision
from app.services.loan_service import LoanService
from app.utils.credit_checker import assert_sufficient_credit_score
from app.utils.customer_validators import get_verified_customer
from app.utils.loan_validators import assert_no_active_loan, assert_application_is_pending
from app.utils.merchant_validators import get_active_merchant
from app.core.exceptions import NotFoundError


class ApplicationService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: ApplicationCreate) -> LoanApplication:
        customer = get_verified_customer(self.db, data.customer_id)
        get_active_merchant(self.db, data.merchant_id)
        assert_no_active_loan(self.db, data.customer_id)
        application = self._build_application(data, customer.credit_score)
        self.db.add(application)
        self.db.commit()
        self.db.refresh(application)
        return application

    def get_by_id(self, application_id: str) -> LoanApplication:
        application = self.db.get(LoanApplication, application_id)
        if not application:
            raise NotFoundError("LoanApplication", application_id)
        return application

    def process_decision(
        self, application_id: str, decision: ApplicationDecision
    ) -> LoanApplication:
        application = self.get_by_id(application_id)
        assert_application_is_pending(application)
        self._assert_valid_decision(decision.status)

        if decision.status == ApplicationStatus.REJECTED:
            return self._reject(application, decision.rejection_reason)
        return self._approve(application)

    # --- private ---

    def _build_application(
        self, data: ApplicationCreate, credit_score: int | None
    ) -> LoanApplication:
        return LoanApplication(
            customer_id=data.customer_id,
            merchant_id=data.merchant_id,
            requested_amount=data.amount,
            requested_term_months=data.term_months,
            credit_score_at_application=credit_score,
        )

    def _approve(self, application: LoanApplication) -> LoanApplication:
        assert_sufficient_credit_score(
            application.credit_score_at_application,
            settings.min_credit_score,
        )
        self._set_status(application, ApplicationStatus.APPROVED)
        LoanService(self.db).create_from_application(application)
        self.db.commit()
        self.db.refresh(application)
        return application

    def _reject(
        self, application: LoanApplication, reason: str | None
    ) -> LoanApplication:
        self._set_status(application, ApplicationStatus.REJECTED)
        application.rejection_reason = reason
        self.db.commit()
        self.db.refresh(application)
        return application

    def _set_status(
        self, application: LoanApplication, status: ApplicationStatus
    ) -> None:
        application.status = status
        self.db.flush()

    def _assert_valid_decision(self, status: ApplicationStatus) -> None:
        allowed = {ApplicationStatus.APPROVED, ApplicationStatus.REJECTED}
        if status not in allowed:
            raise BusinessRuleError("Decision must be APPROVED or REJECTED")

