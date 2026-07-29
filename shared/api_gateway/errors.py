from http import HTTPStatus

import httpx

from shared.api_gateway.exceptions import (
    APIGatewayError,
    APIResponseError,
    AuthenticationError,
    RateLimitError,
    ResourceNotFoundError,
)

ERROR_MAPPING: dict[int, type[APIGatewayError]] = {
    HTTPStatus.UNAUTHORIZED: AuthenticationError,
    HTTPStatus.FORBIDDEN: AuthenticationError,
    HTTPStatus.NOT_FOUND: ResourceNotFoundError,
    HTTPStatus.TOO_MANY_REQUESTS: RateLimitError,
}


def extract_error_message(error: httpx.HTTPStatusError) -> str:
    try:
        data = error.response.json()
        for key in ("message", "error", "description", "detail", "errors"):
            if key in data:
                value = data[key]
                if isinstance(value, str):
                    return value
                if isinstance(value, dict) and "message" in value:
                    return str(value["message"])
                return str(value)
        return str(data)
    except Exception:
        return str(error)


def handle_http_error(error: httpx.HTTPStatusError) -> APIGatewayError:
    """
    Преобразует HTTP ошибку в соответствующее исключение API Gateway.
    """
    status = error.response.status_code
    message = extract_error_message(error)

    error_class = ERROR_MAPPING.get(status)
    if error_class:
        return error_class(f"{error_class.__name__}: {message}")

    return APIResponseError(f"API error {status}: {message}")
