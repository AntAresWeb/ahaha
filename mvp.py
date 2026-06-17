import asyncio
import logging
import sys

from httpx import AsyncClient, HTTPError, Response

ACCESS_TOKEN = "APPLGK1QBEQNHBE0E4TFPF4SCQHAJCA8FKR9VVJJHL95G8LRLORILCHJ1CC6VFVC"
HEADER = {
    "HH-User-Agent": "antares_hh/1.0 (davydov.a@mail.ru))",
    "Authorization": f"Bearer {ACCESS_TOKEN}",
}


logger = logging.getLogger(__name__)
logger.setLevel("INFO")
console_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(console_handler)


async def log_response(response: Response) -> None:
    logger.info("Получены данные")
    logger.info(f"Статус: {response.status_code} {response.reason_phrase}")
    data = response.json()
    logger.info(f"Данные: {data}")


async def get_area() -> None:
    async with AsyncClient() as client:
        response = await client.get(
            url="https://api.hh.ru/areas/113", headers=HEADER, params={"locale": "RU"})
        try:
            response.raise_for_status()
            await log_response(response)
        except HTTPError:
            await log_response(response)


async def get_vacancy() -> None:
    async with AsyncClient() as client:
        response = await client.get(
            url="https://api.hh.ru/vacancies",
            headers=HEADER,
            params={"page": 1, "per_page": 1, "area": "2", "text": "Python разработчик"},
        )
        try:
            response.raise_for_status()
            await log_response(response)
        except HTTPError:
            await log_response(response)

asyncio.run(get_vacancy())
