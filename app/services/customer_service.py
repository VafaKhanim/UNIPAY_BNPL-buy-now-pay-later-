from sqlalchemy.orm import Session

from app.core.enums import KYCStatus
from app.core.exceptions import NotFoundError
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerKYCUpdate
from app.utils.customer_validators import assert_unique_customer_fields


class CustomerService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: CustomerCreate) -> Customer:
        assert_unique_customer_fields(
            self.db, data.national_id, data.phone, data.email
        )
        customer = Customer(
            full_name=data.full_name,
            national_id=data.national_id,
            phone=data.phone,
            email=data.email,
        )
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def get_by_id(self, customer_id: str) -> Customer:
        customer = self.db.get(Customer, customer_id)
        if not customer:
            raise NotFoundError("Customer", customer_id)
        return customer

    def update_kyc(self, customer_id: str, data: CustomerKYCUpdate) -> Customer:
        customer = self.get_by_id(customer_id)
        customer.kyc_status = data.kyc_status
        if data.credit_score is not None:
            customer.credit_score = data.credit_score
        self.db.commit()
        self.db.refresh(customer)
        return customer


