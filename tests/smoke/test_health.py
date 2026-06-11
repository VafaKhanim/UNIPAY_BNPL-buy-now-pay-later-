import pytest


class TestApiAlive:
    """Server ayaq üstədir?"""

    def test_docs_accessible(self, client):
        """Swagger UI yüklənir."""
        res = client.get("/docs")
        assert res.status_code == 200

    def test_redoc_accessible(self, client):
        """ReDoc UI yüklənir."""
        res = client.get("/redoc")
        assert res.status_code == 200

    def test_openapi_schema_exists(self, client):
        """OpenAPI JSON schema mövcuddur."""
        res = client.get("/openapi.json")
        assert res.status_code == 200

        schema = res.json()
        assert schema["info"]["title"] == "UniPay BNPL API"
        assert "paths" in schema


class TestCustomerSmoke:
    """Customer endpoint ayaq üstədir?"""

    def test_create_customer_returns_201(self, client, customer_payload):
        res = client.post("/api/v1/customers", json=customer_payload)
        assert res.status_code == 201

    def test_create_customer_response_has_id(self, client, customer_payload):
        res = client.post("/api/v1/customers", json=customer_payload)
        body = res.json()
        assert "id" in body
        assert len(body["id"]) > 0

    def test_get_nonexistent_customer_returns_404(self, client):
        res = client.get("/api/v1/customers/nonexistent-id")
        assert res.status_code == 404


class TestMerchantSmoke:
    """Merchant endpoint ayaq üstədir?"""

    def test_create_merchant_returns_201(self, client, merchant_payload):
        res = client.post("/api/v1/merchants", json=merchant_payload)
        assert res.status_code == 201

    def test_create_merchant_response_has_id(self, client, merchant_payload):
        res = client.post("/api/v1/merchants", json=merchant_payload)
        body = res.json()
        assert "id" in body
        assert len(body["id"]) > 0

    def test_get_nonexistent_merchant_returns_404(self, client):
        res = client.get("/api/v1/merchants/nonexistent-id")
        assert res.status_code == 404


class TestApplicationSmoke:
    """Application endpoint mövcuddur?"""

    def test_get_nonexistent_application_returns_404(self, client):
        res = client.get("/api/v1/applications/nonexistent-id")
        assert res.status_code == 404