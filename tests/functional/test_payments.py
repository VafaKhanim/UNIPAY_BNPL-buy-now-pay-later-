import pytest
from datetime import date, timedelta


class TestPayInstallment:

    def _get_first_installment(self, client, loan_id: str) -> dict:
        res = client.get(f"/api/v1/loans/{loan_id}/schedule")
        return res.json()["installments"][0]

    def test_pay_installment_success(self, client, approved_loan):
        installment = self._get_first_installment(
            client, approved_loan["id"]
        )

        res = client.post(
            f"/api/v1/installments/{installment['id']}/pay",
            json={
                "payment_method": "CARD",
                "provider_transaction_id": "TXN-001",
            },
        )
        assert res.status_code == 201

        body = res.json()
        assert body["status"] == "SUCCESS"
        assert body["installment_id"] == installment["id"]
        assert body["payment_method"] == "CARD"

    def test_installment_status_becomes_paid(self, client, approved_loan):
        """Ödəniş sonrası installment PAID olmalıdır."""
        installment = self._get_first_installment(
            client, approved_loan["id"]
        )

        client.post(
            f"/api/v1/installments/{installment['id']}/pay",
            json={"payment_method": "BANK_TRANSFER"},
        )

        res = client.get(f"/api/v1/installments/{installment['id']}")
        assert res.status_code == 200
        assert res.json()["status"] == "PAID"
        assert res.json()["paid_at"] is not None

    def test_pay_already_paid_installment_blocked(
        self, client, approved_loan
    ):
        """PAID installment-i yenidən ödəmək mümkün deyil."""
        installment = self._get_first_installment(
            client, approved_loan["id"]
        )

        # Birinci ödəniş
        client.post(
            f"/api/v1/installments/{installment['id']}/pay",
            json={"payment_method": "CARD"},
        )

        # İkinci ödəniş cəhdi
        res = client.post(
            f"/api/v1/installments/{installment['id']}/pay",
            json={"payment_method": "CARD"},
        )
        assert res.status_code == 422
        assert "cannot be paid" in res.json()["detail"].lower()

    def test_payment_history_recorded(self, client, approved_loan):
        """Ödəniş payments tarixinə yazılmalıdır."""
        installment = self._get_first_installment(
            client, approved_loan["id"]
        )

        client.post(
            f"/api/v1/installments/{installment['id']}/pay",
            json={
                "payment_method": "AUTO_DEBIT",
                "provider_transaction_id": "TXN-AUTO-001",
            },
        )

        res = client.get(
            f"/api/v1/installments/{installment['id']}/payments"
        )
        assert res.status_code == 200

        payments = res.json()
        assert len(payments) == 1
        assert payments[0]["status"] == "SUCCESS"
        assert payments[0]["provider_transaction_id"] == "TXN-AUTO-001"

    def test_pay_nonexistent_installment(self, client):
        res = client.post(
            "/api/v1/installments/00000000-0000-0000-0000-000000000000/pay",
            json={"payment_method": "CARD"},
        )
        assert res.status_code == 404


class TestOverdueProcessing:

    def test_overdue_process_marks_due_installments(
        self, client, db, approved_loan
    ):
        """Due date keçmiş installment-lər OVERDUE olmalıdır."""
        from app.models.installment import Installment

        # DB-də installment-lərin due_date-ini keçmişə çək
        installments = (
            db.query(Installment)
            .filter_by(loan_id=approved_loan["id"])
            .all()
        )
        for inst in installments:
            inst.due_date = date.today() - timedelta(days=5)
        db.commit()

        res = client.post("/api/v1/admin/overdue/process")
        assert res.status_code == 200
        assert res.json()["processed"] >= 1

        # İlk installment-i yoxla
        check = client.get(f"/api/v1/installments/{installments[0].id}")
        assert check.json()["status"] == "OVERDUE"
        assert check.json()["overdue_days"] >= 5

    def test_paid_installments_not_affected_by_overdue(
        self, client, db, approved_loan
    ):
        """PAID installment-lər overdue process-dən təsirlənməməlidir."""
        from app.models.installment import Installment

        installments = (
            db.query(Installment)
            .filter_by(loan_id=approved_loan["id"])
            .all()
        )

        # Birinci installment-i əvvəlcə ödə
        client.post(
            f"/api/v1/installments/{installments[0].id}/pay",
            json={"payment_method": "CARD"},
        )

        # Hamısının due_date-ini keçmişə çək
        for inst in installments:
            inst.due_date = date.today() - timedelta(days=10)
        db.commit()

        client.post("/api/v1/admin/overdue/process")

        # PAID olan dəyişməməlidir
        check = client.get(f"/api/v1/installments/{installments[0].id}")
        assert check.json()["status"] == "PAID"


class TestBadDebtProcessing:

    def test_bad_debt_marks_long_overdue(
        self, client, db, approved_loan
    ):
        """30+ gün overdue → BAD_DEBT."""
        from app.models.installment import Installment

        installments = (
            db.query(Installment)
            .filter_by(loan_id=approved_loan["id"])
            .all()
        )

        # 35 gün overdue simulasiya et
        for inst in installments:
            inst.due_date = date.today() - timedelta(days=35)
        db.commit()

        # Əvvəlcə overdue process
        client.post("/api/v1/admin/overdue/process")

        # Sonra bad debt process
        res = client.post("/api/v1/admin/bad-debt/process")
        assert res.status_code == 200
        assert res.json()["marked_bad_debt"] >= 1

        # Status yoxla
        check = client.get(f"/api/v1/installments/{installments[0].id}")
        assert check.json()["status"] == "BAD_DEBT"

    def test_recent_overdue_not_marked_bad_debt(
        self, client, db, approved_loan
    ):
        """Yeni overdue (< 30 gün) BAD_DEBT olmamalıdır."""
        from app.models.installment import Installment

        installments = (
            db.query(Installment)
            .filter_by(loan_id=approved_loan["id"])
            .all()
        )

        # Yalnız 10 gün overdue
        for inst in installments:
            inst.due_date = date.today() - timedelta(days=10)
        db.commit()

        client.post("/api/v1/admin/overdue/process")

        res = client.post("/api/v1/admin/bad-debt/process")
        assert res.json()["marked_bad_debt"] == 0