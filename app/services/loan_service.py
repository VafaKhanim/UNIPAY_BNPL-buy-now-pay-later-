#BU OKAYDIMII CHECK EDERSEN
from sqlalchemy.orm import Session

from app.core.enums import InstallmentStatus
from app.core.exceptions import NotFoundError
from app.models.base import utcnow
from app.models.installment import Installment
from app.models.loan import Loan, LoanApplication
from app.schemas.installment import LoanScheduleResponse
from app.utils.installment_calculator import build_installment_schedule

MONTHLY_INTEREST_RATE = 0.0199


class LoanService:
    def __init__(self, db: Session):
        self.db = db

    def create_from_application(self, application: LoanApplication) -> Loan:
        loan = self._build_loan(application)
        self.db.add(loan)
        self.db.flush()
        self._save_installments(loan)
        return loan

    def _build_loan(self, application: LoanApplication) -> Loan:
        return Loan(
            application_id=application.id,
            customer_id=application.customer_id,
            merchant_id=application.merchant_id,
            principal_amount=application.requested_amount,
            interest_rate=MONTHLY_INTEREST_RATE,
            term_months=application.requested_term_months,
            disbursed_at=utcnow(),
        )

    def get_by_id(self, loan_id: str) -> Loan:
        loan = self.db.get(Loan, loan_id)
        if not loan:
            raise NotFoundError("Loan", loan_id)
        return loan

    def get_schedule(self, loan_id: str) -> LoanScheduleResponse:
        loan = self.get_by_id(loan_id)
        total_payable = sum(float(i.total_amount) for i in loan.installments)
        return LoanScheduleResponse(
            loan_id=loan.id,
            principal_amount=float(loan.principal_amount),
            total_payable=round(total_payable, 2),
            installments=loan.installments,
        )

    def get_customer_loans(self, customer_id: str) -> list[Loan]:
        return (
            self.db.query(Loan)
            .filter_by(customer_id=customer_id)
            .order_by(Loan.created_at.desc())
            .all()
        )

    def _save_installments(self, loan: Loan) -> None:
        schedule = build_installment_schedule(
            loan_id=loan.id,
            principal=float(loan.principal_amount),
            rate=float(loan.interest_rate),
            term=loan.term_months,
        )
        for item in schedule:
            self.db.add(Installment(
                loan_id=item["loan_id"],
                installment_number=item["installment_number"],
                due_date=item["due_date"],
                principal_portion=item["principal_portion"],
                interest_portion=item["interest_portion"],
                total_amount=item["total_amount"],
                status=InstallmentStatus.SCHEDULED,
            ))