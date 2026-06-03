# main.py
from contextlib import asynccontextmanager

import httpx
from config import get_settings
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from models import AuthURLResponse, ErrorResponse, StatusResponse, UserInfo, VacancySearchParams
from oauth_hh import auth_client

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Startup
    print("Starting up...")
    yield
    # Shutdown
    print("Shutting down...")
    await auth_client.close()


# Создаем приложение
app = FastAPI(
    title="HH.ru OAuth Client",
    description="Клиент для авторизации и работы с API HH.ru",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# Обработчики ошибок
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(error="http_exception", detail=str(exc.detail), status_code=exc.status_code).model_dump(),
    )


# Auth endpoints
@app.get("/auth/login", response_model=AuthURLResponse, tags=["Authentication"])
async def login():
    """
    Шаг 1: Получить URL для авторизации.

    Откройте полученную ссылку в браузере, авторизуйтесь на HH.ru и разрешите доступ.
    После авторизации вы будете перенаправлены на /auth/callback
    """
    auth_url = auth_client.get_authorization_url()
    return AuthURLResponse(auth_url=auth_url, redirect_uri=settings.hh_redirect_uri)


@app.get("/auth/callback", tags=["Authentication"])
async def oauth_callback(code: str, request: Request):
    """
    Шаг 2: Обработка callback от HH.ru.

    Этот эндпоинт вызывается автоматически после авторизации пользователя.
    Полученный code обменивается на токены, которые сохраняются для дальнейшего использования.
    """
    error = request.query_params.get("error")
    if error:
        error_description = request.query_params.get("error_description", "Неизвестная ошибка")
        raise HTTPException(status_code=400, detail=f"Ошибка авторизации: {error} - {error_description}")

    if not code:
        raise HTTPException(status_code=400, detail="Не передан параметр code")

    try:
        tokens = await auth_client.exchange_code_for_tokens(code)
        return {
            "message": "Авторизация успешна! Токены сохранены.",
            "expires_in": tokens.expires_in_seconds,
            "expires_at": tokens.expires_at.isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обмене кода: {str(e)}")


@app.get("/auth/status", response_model=StatusResponse, tags=["Authentication"])
async def auth_status():
    """Проверка статуса токенов"""
    return StatusResponse(**auth_client.get_status())


@app.post("/auth/logout", tags=["Authentication"])
async def logout():
    """Удаляет сохраненные токены"""
    auth_client.logout()
    return {"message": "Токены удалены. При следующем использовании выполните /auth/login"}


# API endpoints (требуют валидный токен)
@app.get("/api/me", response_model=UserInfo, tags=["API"])
async def get_current_user():
    """Получить информацию о текущем пользователе (себе)"""
    access_token = await auth_client.get_valid_access_token()

    headers = {"Authorization": f"Bearer {access_token}", "User-Agent": f"{settings.hh_client_id}/1.0"}

    async with httpx.AsyncClient(timeout=settings.http_timeout) as client:
        response = await client.get(settings.api_me_url, headers=headers)

    if response.status_code == 401:
        raise HTTPException(status_code=401, detail="Токены истекли. Выполните повторную авторизацию через /auth/login")

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=f"Ошибка API HH.ru: {response.text}")

    return UserInfo(**response.json())


@app.get("/api/resumes", tags=["API"])
async def get_resumes():
    """Получить список резюме пользователя"""
    access_token = await auth_client.get_valid_access_token()

    headers = {"Authorization": f"Bearer {access_token}", "User-Agent": f"{settings.hh_client_id}/1.0"}

    async with httpx.AsyncClient(timeout=settings.http_timeout) as client:
        response = await client.get(settings.api_resumes_url, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=f"Ошибка получения резюме: {response.text}")

    return response.json()


@app.get("/api/vacancies", tags=["API"])
async def search_vacancies(params: VacancySearchParams = Depends()):
    """Поиск вакансий с параметрами фильтрации"""
    access_token = await auth_client.get_valid_access_token()

    headers = {"Authorization": f"Bearer {access_token}", "User-Agent": f"{settings.hh_client_id}/1.0"}

    async with httpx.AsyncClient(timeout=settings.http_timeout) as client:
        response = await client.get(
            settings.api_vacancies_url, headers=headers, params=params.model_dump(exclude_none=True),
        )

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=f"Ошибка поиска вакансий: {response.text}")

    return response.json()


@app.get("/health", tags=["System"])
async def health_check():
    """Проверка работоспособности сервиса"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "oauth_configured": bool(settings.hh_client_id and settings.hh_client_secret),
        "tokens_exist": auth_client.get_status()["status"] != "no_tokens",
    }


if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("HH.ru OAuth Client v2.0")
    print("=" * 60)
    print(f"Документация API: http://localhost:8080/docs")
    print(f"Health check: http://localhost:8080/health")
    print(f"\nДля авторизации:")
    print(f"1. Откройте http://localhost:8080/auth/login")
    print(f"2. Перейдите по ссылке в браузер")
    print(f"3. Разрешите доступ в HH.ru")
    print("=" * 60)

    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True, reload_delay=0.5, log_level=settings.log_level.lower())
