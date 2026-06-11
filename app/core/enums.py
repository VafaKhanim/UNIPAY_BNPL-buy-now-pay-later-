from enum import Enum


class KYCStatus(str, Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class ApplicationStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class LoanStatus(str, Enum):
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    DEFAULTED = "DEFAULTED"


class InstallmentStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    DUE = "DUE"
    PAID = "PAID"
    OVERDUE = "OVERDUE"
    BAD_DEBT = "BAD_DEBT"
    COLLECTION = "COLLECTION"
    WRITTEN_OFF = "WRITTEN_OFF"


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class PaymentMethod(str, Enum):
    CARD = "CARD"
    BANK_TRANSFER = "BANK_TRANSFER"
    AUTO_DEBIT = "AUTO_DEBIT"