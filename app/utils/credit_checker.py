from app.core.exceptions import BusinessRuleError


def assert_sufficient_credit_score(score: int | None, min_score: int) -> None:
    actual = score or 0
    if actual < min_score:
        raise BusinessRuleError(
            f"Credit score {actual} below minimum {min_score}"
        )