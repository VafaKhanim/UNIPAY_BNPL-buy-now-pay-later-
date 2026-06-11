from datetime import date

from dateutil.relativedelta import relativedelta


def calculate_monthly_payment(
    principal: float, monthly_rate: float, n: int
) -> float:
    if monthly_rate == 0:
        return principal / n
    return principal * monthly_rate / (1 - (1 + monthly_rate) ** -n)


def build_installment_schedule(
    loan_id: str, principal: float, rate: float, term: int
) -> list[dict]:
    monthly_payment = calculate_monthly_payment(principal, rate, term)
    schedule = []
    remaining = principal

    for i in range(1, term + 1):
        interest = round(remaining * rate, 2)
        principal_portion = round(monthly_payment - interest, 2)
        remaining -= principal_portion

        schedule.append({
            "loan_id": loan_id,
            "installment_number": i,
            "due_date": date.today() + relativedelta(months=i),
            "principal_portion": principal_portion,
            "interest_portion": interest,
            "total_amount": round(monthly_payment, 2),
        })

    return schedule