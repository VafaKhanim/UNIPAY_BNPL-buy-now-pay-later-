class TestGetLoan:

    def test_get_loan_after_approval(self, client, approved_loan):
        res = client.get(f"/api/v1/loans/{approved_loan['id']}")
        assert res.status_code == 200

        body = res.json()
        assert body["id"] == approved_loan["id"]
        assert body["status"] == "ACTIVE"
        assert body["principal_amount"] == 600.00

    def test_get_nonexistent_loan_returns_404(self, client):
        res = client.get(
            "/api/v1/loans/00000000-0000-0000-0000-000000000000"
        )
        assert res.status_code == 404


class TestLoanSchedule:

    def test_schedule_installment_count_matches_term(
        self, client, approved_loan
    ):
        """Installment sayı term_months-a bərabər olmalıdır."""
        res = client.get(f"/api/v1/loans/{approved_loan['id']}/schedule")
        assert res.status_code == 200

        body = res.json()
        assert len(body["installments"]) == 3  # fixture: term_months=3

    def test_schedule_total_exceeds_principal(
        self, client, approved_loan
    ):
        """Faiz olduğu üçün total_payable > principal_amount."""
        res = client.get(f"/api/v1/loans/{approved_loan['id']}/schedule")
        body = res.json()

        assert body["total_payable"] > body["principal_amount"]

    def test_schedule_installment_numbers_sequential(
        self, client, approved_loan
    ):
        """Installment-lər 1-dən başlayaraq ardıcıl nömrələnib."""
        res = client.get(f"/api/v1/loans/{approved_loan['id']}/schedule")
        installments = res.json()["installments"]

        numbers = [i["installment_number"] for i in installments]
        assert numbers == list(range(1, len(numbers) + 1))

    def test_schedule_all_initially_scheduled(
        self, client, approved_loan
    ):
        """Yeni loan-da bütün installment-lər SCHEDULED statusunda olmalıdır."""
        res = client.get(f"/api/v1/loans/{approved_loan['id']}/schedule")
        installments = res.json()["installments"]

        statuses = {i["status"] for i in installments}
        assert statuses == {"SCHEDULED"}

    def test_schedule_amounts_sum_to_total(
        self, client, approved_loan
    ):
        """Hər installment-in total_amount cəmi = loan total_payable."""
        res = client.get(f"/api/v1/loans/{approved_loan['id']}/schedule")
        body = res.json()

        installment_sum = sum(
            i["total_amount"] for i in body["installments"]
        )
        assert abs(installment_sum - body["total_payable"]) < 0.02  # rounding

    def test_schedule_due_dates_monthly(self, client, approved_loan):
        """Hər installment bir ay arayla due_date-ə malikdir."""
        from datetime import date

        res = client.get(f"/api/v1/loans/{approved_loan['id']}/schedule")
        installments = res.json()["installments"]

        dates = [
            date.fromisoformat(i["due_date"]) for i in installments
        ]
        for i in range(1, len(dates)):
            diff_days = (dates[i] - dates[i - 1]).days
            assert 28 <= diff_days <= 31  # aylıq interval


class TestCustomerLoans:

    def test_get_customer_loans(
        self, client, approved_loan, verified_customer
    ):
        res = client.get(
            f"/api/v1/customers/{verified_customer['id']}/loans"
        )
        assert res.status_code == 200

        loans = res.json()
        assert len(loans) >= 1
        assert loans[0]["customer_id"] == verified_customer["id"]

    def test_customer_with_no_loans_returns_empty(self, client, customer_payload):
        """Loan-u olmayan customer üçün boş list qayıtmalıdır."""
        new_customer = client.post(
            "/api/v1/customers",
            json=customer_payload | {
                "national_id": "AZE888888",
                "phone": "+994508888888",
                "email": "noloan@example.com",
            },
        ).json()

        res = client.get(f"/api/v1/customers/{new_customer['id']}/loans")
        assert res.status_code == 200
        assert res.json() == []