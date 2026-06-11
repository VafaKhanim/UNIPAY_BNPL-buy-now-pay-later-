class TestCreateApplication:

    def test_success(self, client, verified_customer, active_merchant):
        res = client.post(
            "/api/v1/applications",
            json={
                "customer_id": verified_customer["id"],
                "merchant_id": active_merchant["id"],
                "amount": 500.00,
                "term_months": 6,
            },
        )
        assert res.status_code == 201

        body = res.json()
        assert body["status"] == "PENDING"
        assert body["customer_id"] == verified_customer["id"]
        assert body["merchant_id"] == active_merchant["id"]
        assert body["requested_amount"] == 500.00
        assert body["credit_score_at_application"] == 650  # fixture-dan

    def test_unverified_customer_blocked(
        self, client, customer_payload, active_merchant
    ):
        """KYC=PENDING olan customer apply edə bilməz."""
        unverified = client.post(
            "/api/v1/customers", json=customer_payload
        ).json()

        res = client.post(
            "/api/v1/applications",
            json={
                "customer_id": unverified["id"],
                "merchant_id": active_merchant["id"],
                "amount": 300.00,
                "term_months": 3,
            },
        )
        assert res.status_code == 422
        assert "kyc" in res.json()["detail"].lower()

    def test_inactive_merchant_blocked(
        self, client, verified_customer, active_merchant
    ):
        """Deaktiv merchant-ə apply etmək olmaz."""
        client.patch(
            f"/api/v1/merchants/{active_merchant['id']}/status",
            json={"is_active": False},
        )

        res = client.post(
            "/api/v1/applications",
            json={
                "customer_id": verified_customer["id"],
                "merchant_id": active_merchant["id"],
                "amount": 300.00,
                "term_months": 3,
            },
        )
        assert res.status_code == 422

    def test_amount_exceeds_limit_rejected(
        self, client, verified_customer, active_merchant
    ):
        """Schema limit: amount <= 50_000."""
        res = client.post(
            "/api/v1/applications",
            json={
                "customer_id": verified_customer["id"],
                "merchant_id": active_merchant["id"],
                "amount": 99_999.00,
                "term_months": 6,
            },
        )
        assert res.status_code == 422

    def test_zero_amount_rejected(
        self, client, verified_customer, active_merchant
    ):
        res = client.post(
            "/api/v1/applications",
            json={
                "customer_id": verified_customer["id"],
                "merchant_id": active_merchant["id"],
                "amount": 0,
                "term_months": 3,
            },
        )
        assert res.status_code == 422

    def test_term_out_of_range_rejected(
        self, client, verified_customer, active_merchant
    ):
        """term_months: 1-36 arasında olmalıdır."""
        res = client.post(
            "/api/v1/applications",
            json={
                "customer_id": verified_customer["id"],
                "merchant_id": active_merchant["id"],
                "amount": 300.00,
                "term_months": 99,
            },
        )
        assert res.status_code == 422

    def test_active_loan_blocks_new_application(
        self, client, approved_loan, verified_customer, active_merchant
    ):
        """Aktiv loan olan customer yeni apply edə bilməz."""
        res = client.post(
            "/api/v1/applications",
            json={
                "customer_id": verified_customer["id"],
                "merchant_id": active_merchant["id"],
                "amount": 200.00,
                "term_months": 3,
            },
        )
        assert res.status_code == 422
        assert "active loan" in res.json()["detail"].lower()


class TestApplicationDecision:

    def _create_application(
        self, client, verified_customer, active_merchant, amount=400.00
    ) -> str:
        res = client.post(
            "/api/v1/applications",
            json={
                "customer_id": verified_customer["id"],
                "merchant_id": active_merchant["id"],
                "amount": amount,
                "term_months": 4,
            },
        )
        assert res.status_code == 201
        return res.json()["id"]

    def test_approve_success(
        self, client, verified_customer, active_merchant
    ):
        app_id = self._create_application(
            client, verified_customer, active_merchant
        )

        res = client.patch(
            f"/api/v1/applications/{app_id}/decision",
            json={"status": "APPROVED"},
        )
        assert res.status_code == 200
        assert res.json()["status"] == "APPROVED"

    def test_approve_creates_loan(
        self, client, verified_customer, active_merchant
    ):
        """Approval sonrası customer-in aktiv loanu olmalıdır."""
        app_id = self._create_application(
            client, verified_customer, active_merchant
        )

        client.patch(
            f"/api/v1/applications/{app_id}/decision",
            json={"status": "APPROVED"},
        )

        loans_res = client.get(
            f"/api/v1/customers/{verified_customer['id']}/loans"
        )
        assert loans_res.status_code == 200
        loans = loans_res.json()
        assert len(loans) == 1
        assert loans[0]["status"] == "ACTIVE"

    def test_reject_with_reason(
        self, client, verified_customer, active_merchant
    ):
        app_id = self._create_application(
            client, verified_customer, active_merchant
        )

        res = client.patch(
            f"/api/v1/applications/{app_id}/decision",
            json={
                "status": "REJECTED",
                "rejection_reason": "Kredit tarixi qeyri-kafi",
            },
        )
        assert res.status_code == 200

        body = res.json()
        assert body["status"] == "REJECTED"
        assert body["rejection_reason"] == "Kredit tarixi qeyri-kafi"

    def test_double_decision_blocked(
        self, client, verified_customer, active_merchant
    ):
        """Artıq qərar verilmiş application-a ikinci qərar verilə bilməz."""
        app_id = self._create_application(
            client, verified_customer, active_merchant
        )

        client.patch(
            f"/api/v1/applications/{app_id}/decision",
            json={"status": "APPROVED"},
        )

        res = client.patch(
            f"/api/v1/applications/{app_id}/decision",
            json={"status": "REJECTED"},
        )
        assert res.status_code == 422
        assert "already" in res.json()["detail"].lower()

    def test_low_credit_score_blocks_approval(
        self, client, customer_payload, active_merchant
    ):
        """Credit score < 500 olan customer approve edilə bilməz."""
        # Aşağı score ilə verified customer yarat
        low_score_customer = client.post(
            "/api/v1/customers",
            json=customer_payload | {
                "national_id": "AZE777777",
                "phone": "+994507777777",
                "email": "lowscore@example.com",
            },
        ).json()

        client.patch(
            f"/api/v1/customers/{low_score_customer['id']}/kyc",
            json={"kyc_status": "VERIFIED", "credit_score": 350},
        )

        app_res = client.post(
            "/api/v1/applications",
            json={
                "customer_id": low_score_customer["id"],
                "merchant_id": active_merchant["id"],
                "amount": 300.00,
                "term_months": 3,
            },
        )
        assert app_res.status_code == 201

        res = client.patch(
            f"/api/v1/applications/{app_res.json()['id']}/decision",
            json={"status": "APPROVED"},
        )
        assert res.status_code == 422
        assert "credit score" in res.json()["detail"].lower()

    def test_get_application_not_found(self, client):
        res = client.get(
            "/api/v1/applications/00000000-0000-0000-0000-000000000000"
        )
        assert res.status_code == 404