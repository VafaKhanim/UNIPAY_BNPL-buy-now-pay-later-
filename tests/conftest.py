"""
SQLite in-memory DB qurur,
hər test üçün ayrı transaction açır, test bitəndə rollback edir.
Yəni testlər bir-birini çirkləndirmir.
verified_customer, active_merchant, approved_loan kimi
hazır fixture-lar var — hər dəfə sıfırdan yaratmırıq.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.deps import get_db
from app.main import create_app
from app.models.base import Base

# --- Engine: in-memory SQLite (test üçün) ---
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(
    bind=engine, autocommit=False, autoflush=False
)


# --- Fixtures ---

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Bütün testlər üçün bir dəfə: cədvəlləri yarat."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    """Hər test üçün təmiz session — test sonrası rollback."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db):
    """FastAPI TestClient — db session override edilib."""
    app = create_app()

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c


# --- Helper fixtures ---

@pytest.fixture
def customer_payload():
    return {
        "full_name": "Əli Həsənov",
        "national_id": "AZE123456",
        "phone": "+994501234567",
        "email": "ali@example.com",
    }


@pytest.fixture
def merchant_payload():
    return {
        "business_name": "TechStore MMC",
        "tax_id": "AZ1234567890",
        "settlement_iban": "AZ21NABZ00000000137010001944",
    }


@pytest.fixture
def verified_customer(client, customer_payload):
    """KYC-si VERIFIED olan hazır customer."""
    res = client.post("/api/v1/customers", json=customer_payload)
    assert res.status_code == 201
    customer_id = res.json()["id"]

    client.patch(
        f"/api/v1/customers/{customer_id}/kyc",
        json={"kyc_status": "VERIFIED", "credit_score": 650},
    )
    return res.json() | {"id": customer_id}


@pytest.fixture
def active_merchant(client, merchant_payload):
    """Aktiv merchant."""
    res = client.post("/api/v1/merchants", json=merchant_payload)
    assert res.status_code == 201
    return res.json()


@pytest.fixture
def approved_loan(client, verified_customer, active_merchant):
    """
    Full flow: application → approve → loan.
    Loan + installment-lər hazırdır.
    """
    app_res = client.post(
        "/api/v1/applications",
        json={
            "customer_id": verified_customer["id"],
            "merchant_id": active_merchant["id"],
            "amount": 600.00,
            "term_months": 3,
        },
    )
    assert app_res.status_code == 201
    application_id = app_res.json()["id"]

    decision_res = client.patch(
        f"/api/v1/applications/{application_id}/decision",
        json={"status": "APPROVED"},
    )
    assert decision_res.status_code == 200

    # Loan-u customer loans-dan al
    loans_res = client.get(
        f"/api/v1/customers/{verified_customer['id']}/loans"
    )
    assert loans_res.status_code == 200
    loan = loans_res.json()[0]
    return loan