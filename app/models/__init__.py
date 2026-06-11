# Single import point — Alembic autogenerate üçün vacibdir
from app.models.base import Base, BaseModel
from app.models.customer import Customer
from app.models.installment import Installment
from app.models.loan import Loan, LoanApplication
from app.models.merchant import Merchant
from app.models.payment import Payment

__all__ = [
    "Base",
    "BaseModel",
    "Customer",
    "Merchant",
    "LoanApplication",
    "Loan",
    "Installment",
    "Payment",
]