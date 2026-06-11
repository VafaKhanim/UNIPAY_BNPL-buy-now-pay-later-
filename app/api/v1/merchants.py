from fastapi import APIRouter

from app.api.deps import DB
from app.schemas.merchant import MerchantCreate, MerchantResponse, MerchantStatusUpdate
from app.services.merchant_service import MerchantService

router = APIRouter(prefix="/merchants", tags=["Merchants"])


@router.post("", response_model=MerchantResponse, status_code=201)
def create_merchant(data: MerchantCreate, db: DB):
    return MerchantService(db).create(data)


@router.get("/{merchant_id}", response_model=MerchantResponse)
def get_merchant(merchant_id: str, db: DB):
    return MerchantService(db).get_by_id(merchant_id)


@router.patch("/{merchant_id}/status", response_model=MerchantResponse)
def update_merchant_status(
    merchant_id: str, data: MerchantStatusUpdate, db: DB
):
    return MerchantService(db).update_status(merchant_id, data)