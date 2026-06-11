from datetime import date

from sqlalchemy.orm import Session

from app.core.enums import InstallmentStatus
from app.models.installment import Installment


class AdminService:
    def __init__(self, db: Session):
        self.db = db

    def process_overdue(self) -> int:
        candidates = self._fetch_overdue_candidates()
        for inst in candidates:
            self._mark_overdue(inst)
        self.db.commit()
        return len(candidates)

    def process_bad_debt(self, threshold_days: int = 30) -> int:
        candidates = self._fetch_bad_debt_candidates(threshold_days)
        for inst in candidates:
            inst.status = InstallmentStatus.BAD_DEBT
        self.db.commit()
        return len(candidates)

    def _fetch_overdue_candidates(self) -> list[Installment]:
        return (
            self.db.query(Installment)
            .filter(
                Installment.due_date < date.today(),
                Installment.status.in_([
                    InstallmentStatus.SCHEDULED,
                    InstallmentStatus.DUE,
                ]),
            )
            .all()
        )

    def _fetch_bad_debt_candidates(self, threshold_days: int) -> list[Installment]:
        return (
            self.db.query(Installment)
            .filter(
                Installment.status == InstallmentStatus.OVERDUE,
                Installment.overdue_days >= threshold_days,
            )
            .all()
        )

    def _mark_overdue(self, inst: Installment) -> None:
        inst.status = InstallmentStatus.OVERDUE
        inst.overdue_days = (date.today() - inst.due_date).days

