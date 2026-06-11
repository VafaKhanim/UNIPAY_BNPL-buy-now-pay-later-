from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import BusinessRuleError, DuplicateError, NotFoundError


def _json_error(status_code: int, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"detail": str(exc)})


def register_exception_handlers(app) -> None:
    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError):
        return _json_error(404, exc)

    @app.exception_handler(BusinessRuleError)
    async def business_rule_handler(request: Request, exc: BusinessRuleError):
        return _json_error(422, exc)

    @app.exception_handler(DuplicateError)
    async def duplicate_handler(request: Request, exc: DuplicateError):
        return _json_error(409, exc)