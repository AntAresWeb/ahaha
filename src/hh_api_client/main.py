# main.py

import asyncio
import logging

from pydantic_settings import SettingsConfigDict # Для явной загрузки (опционально)
from hh_api_client.config import HHApiSettings
from hh_api_client.client import HHApiClient

async def main():
    logging.basicConfig(level=logging.INFO)
    
    # 1. Загружаем настройки из .env файла и переменных окружения
    settings = HHApiSettings() 
    
    # 2. Инициализируем клиент с этими настройками
    api_client = HHApiClient(settings=settings)
    
    try:
        params = {
            "text": "Python разработчик",
            "area": "1",  # Москва
            "per_page": 2,
        }
        
        result = await api_client.search_vacancies(params)
        
        for item in result.get("items", []):
            print(f"Вакансия: {item.get('name')}")
    
    finally:
        await api_client.close()
        
if __name__ == "__main__":
    asyncio.run(main())