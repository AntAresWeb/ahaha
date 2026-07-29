class APIGatewayError(Exception):
    """Базовое исключение для API Gateway."""


class AuthenticationError(APIGatewayError):
    """Ошибка аутентификации (невалидный токен)."""


class RateLimitError(APIGatewayError):
    """Превышен лимит запросов (429)."""


class ResourceNotFoundError(APIGatewayError):
    """Ресурс не найден (404)."""


class APIResponseError(APIGatewayError):
    """Ошибка в ответе API (невалидный JSON, ошибка валидации)."""


class NetworkError(APIGatewayError):
    """Сетевая ошибка."""
