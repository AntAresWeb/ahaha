from httpx import AsyncClient

from src.vacancy_analizer.share.config import get_settings

settings = get_settings()


class VacancyFetcher:
    def __init__(
        self,
        per_page: int = 10,
    ) -> None:
        self.base_url = settings.hh_api_base_url
        self.per_page = per_page
        self.user_agent = settings.hh_app_name


    async def fetch(self, key: str) -> list:
        url = f"{self.base_url}/vacancies"
        params = {"text": key, "per_page": self.per_page}
        headers = {"HH-User-Agent": self.user_agent}

        async with AsyncClient() as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            return {
                "items": data.get("items", []),
                "found": data.get("found", 0),
                "pages": data.get("pages", 0),
                "page": data.get("page", 0),
                "per_page": self.per_page,
            }
