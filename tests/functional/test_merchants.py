import pytest


class TestCreateMerchant:

    def test_success(self, client, merchant_payload):
        res = client.post("/api/v1/merchants", json=merchant_payload)
        assert res.status_code == 201

        body = res.json()
        assert body["business_name"] == merchant_payload["business_name"]
        assert body["tax_id"] == merchant_payload["tax_id"]
        assert body["is_active"] is True

    def test_duplicate_tax_id_rejected(self, client, merchant_payload):
        client.post("/api/v1/merchants", json=merchant_payload)

        duplicate = merchant_payload | {"business_name": "Digər Şirkət"}
        res = client.post("/api/v1/merchants", json=duplicate)
        assert res.status_code == 409

    def test_missing_required_field_rejected(self, client):
        res = client.post(
            "/api/v1/merchants",
            json={"business_name": "Test"},  # tax_id, iban yoxdur
        )
        assert res.status_code == 422

    def test_short_business_name_rejected(self, client, merchant_payload):
        merchant_payload["business_name"] = "X"  # min_length=2
        res = client.post("/api/v1/merchants", json=merchant_payload)
        assert res.status_code == 422


class TestGetMerchant:

    def test_success(self, client, merchant_payload):
        created = client.post(
            "/api/v1/merchants", json=merchant_payload
        ).json()

        res = client.get(f"/api/v1/merchants/{created['id']}")
        assert res.status_code == 200
        assert res.json()["id"] == created["id"]

    def test_not_found(self, client):
        res = client.get(
            "/api/v1/merchants/00000000-0000-0000-0000-000000000000"
        )
        assert res.status_code == 404


class TestMerchantStatus:

    def test_deactivate_merchant(self, client, merchant_payload):
        created = client.post(
            "/api/v1/merchants", json=merchant_payload
        ).json()

        res = client.patch(
            f"/api/v1/merchants/{created['id']}/status",
            json={"is_active": False},
        )
        assert res.status_code == 200
        assert res.json()["is_active"] is False

    def test_reactivate_merchant(self, client, merchant_payload):
        created = client.post(
            "/api/v1/merchants", json=merchant_payload
        ).json()

        # Əvvəl deaktiv et
        client.patch(
            f"/api/v1/merchants/{created['id']}/status",
            json={"is_active": False},
        )

        # Sonra aktiv et
        res = client.patch(
            f"/api/v1/merchants/{created['id']}/status",
            json={"is_active": True},
        )
        assert res.status_code == 200
        assert res.json()["is_active"] is True

    def test_inactive_merchant_blocks_application(
        self, client, verified_customer, merchant_payload
    ):
        """Deaktiv merchant-ə application yaratmaq mümkün deyil."""
        merchant = client.post(
            "/api/v1/merchants", json=merchant_payload
        ).json()

        client.patch(
            f"/api/v1/merchants/{merchant['id']}/status",
            json={"is_active": False},
        )

        res = client.post(
            "/api/v1/applications",
            json={
                "customer_id": verified_customer["id"],
                "merchant_id": merchant["id"],
                "amount": 300.00,
                "term_months": 3,
            },
        )
        assert res.status_code == 422
        assert "not active" in res.json()["detail"].lower()