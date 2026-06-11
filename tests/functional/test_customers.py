import pytest


class TestCreateCustomer:

    def test_success(self, client, customer_payload):
        res = client.post("/api/v1/customers", json=customer_payload)
        assert res.status_code == 201

        body = res.json()
        assert body["full_name"] == customer_payload["full_name"]
        assert body["phone"] == customer_payload["phone"]
        assert body["email"] == customer_payload["email"]
        assert body["kyc_status"] == "PENDING"
        assert body["credit_score"] is None

    def test_duplicate_national_id_rejected(self, client, customer_payload):
        client.post("/api/v1/customers", json=customer_payload)

        duplicate = customer_payload | {
            "phone": "+994509999999",
            "email": "other@example.com",
        }
        res = client.post("/api/v1/customers", json=duplicate)
        assert res.status_code == 409

    def test_duplicate_phone_rejected(self, client, customer_payload):
        client.post("/api/v1/customers", json=customer_payload)

        duplicate = customer_payload | {
            "national_id": "AZE999999",
            "email": "other@example.com",
        }
        res = client.post("/api/v1/customers", json=duplicate)
        assert res.status_code == 409

    def test_duplicate_email_rejected(self, client, customer_payload):
        client.post("/api/v1/customers", json=customer_payload)

        duplicate = customer_payload | {
            "national_id": "AZE999999",
            "phone": "+994509999999",
        }
        res = client.post("/api/v1/customers", json=duplicate)
        assert res.status_code == 409

    def test_invalid_phone_format_rejected(self, client, customer_payload):
        customer_payload["phone"] = "not-a-phone"
        res = client.post("/api/v1/customers", json=customer_payload)
        assert res.status_code == 422

    def test_missing_required_field_rejected(self, client):
        res = client.post(
            "/api/v1/customers",
            json={"full_name": "Əli"},  # phone, email, national_id yoxdur
        )
        assert res.status_code == 422


class TestGetCustomer:

    def test_success(self, client, customer_payload):
        created = client.post(
            "/api/v1/customers", json=customer_payload
        ).json()

        res = client.get(f"/api/v1/customers/{created['id']}")
        assert res.status_code == 200
        assert res.json()["id"] == created["id"]

    def test_not_found(self, client):
        res = client.get("/api/v1/customers/00000000-0000-0000-0000-000000000000")
        assert res.status_code == 404
        assert "detail" in res.json()


class TestKYCUpdate:

    def test_verified_with_credit_score(self, client, customer_payload):
        created = client.post(
            "/api/v1/customers", json=customer_payload
        ).json()

        res = client.patch(
            f"/api/v1/customers/{created['id']}/kyc",
            json={"kyc_status": "VERIFIED", "credit_score": 720},
        )
        assert res.status_code == 200

        body = res.json()
        assert body["kyc_status"] == "VERIFIED"
        assert body["credit_score"] == 720

    def test_rejected_without_score(self, client, customer_payload):
        created = client.post(
            "/api/v1/customers", json=customer_payload
        ).json()

        res = client.patch(
            f"/api/v1/customers/{created['id']}/kyc",
            json={"kyc_status": "REJECTED"},
        )
        assert res.status_code == 200
        assert res.json()["kyc_status"] == "REJECTED"

    def test_invalid_kyc_status_rejected(self, client, customer_payload):
        created = client.post(
            "/api/v1/customers", json=customer_payload
        ).json()

        res = client.patch(
            f"/api/v1/customers/{created['id']}/kyc",
            json={"kyc_status": "UNKNOWN_STATUS"},
        )
        assert res.status_code == 422

    def test_credit_score_out_of_range_rejected(self, client, customer_payload):
        created = client.post(
            "/api/v1/customers", json=customer_payload
        ).json()

        res = client.patch(
            f"/api/v1/customers/{created['id']}/kyc",
            json={"kyc_status": "VERIFIED", "credit_score": 9999},
        )
        assert res.status_code == 422