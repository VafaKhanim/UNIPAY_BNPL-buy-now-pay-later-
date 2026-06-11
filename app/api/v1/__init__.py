from fastapi import APIRouter

from app.api.v1 import admin, applications, customers, loans, merchants, payments

router = APIRouter(prefix="/api/v1")

router.include_router(customers.router)
router.include_router(merchants.router)
router.include_router(applications.router)
router.include_router(loans.router)
router.include_router(payments.router)
router.include_router(admin.router)