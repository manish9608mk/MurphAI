import asyncio
from types import SimpleNamespace

from fastapi.responses import JSONResponse

from backend.app.core.exception_handlers import (
    unexpected_exception_handler,
)


def test_unexpected_exception_includes_request_id():
    request = SimpleNamespace(
        state=SimpleNamespace(
            request_id="test-request-id",
        ),
    )

    response = asyncio.run(
        unexpected_exception_handler(
            request,
            RuntimeError("test failure"),
        )
    )

    assert isinstance(response, JSONResponse)
    assert response.status_code == 500
    assert response.headers["X-Request-ID"] == "test-request-id"
