from fastapi import APIRouter

from app.api.deps import DB
from app.schemas.customer import CustomerCreate, CustomerKYCUpdate, CustomerResponse
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.post("", response_model=CustomerResponse, status_code=201)
def create_customer(data: CustomerCreate, db: DB):
    return CustomerService(db).create(data)


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: str, db: DB):
    return CustomerService(db).get_by_id(customer_id)


@router.patch("/{customer_id}/kyc", response_model=CustomerResponse)
def update_kyc(customer_id: str, data: CustomerKYCUpdate, db: DB):
    return CustomerService(db).update_kyc(customer_id, data)