from dataclasses import dataclass
from datetime import datetime


@dataclass
class Vacancy:
    external_id: str                   # "133473143"
    name: str                          # "Python-разработчик (Django)"
    employer_id: str                   # "123123"
    employer_name: str                 # "Shtab"
    requirement: str                   # HTML-фрагмент требований
    responsibility: str                # HTML-фрагмент обязанностей
    published_at: datetime             # Дата публикации
    url: str                           # "https://hh.ru/vacancy/133473143"
    alternate_url: str                 # для API
    work_format: str = "REMOTE"        # ON_SITE, REMOTE, MIXE (удалёнка/офис)
    salary_from: int | None = None     # 150000
    salary_to: int | None = None       # 180000
    currency: str = "RUR"              # "RUR"
    gross: bool = True                 # True = до налогов, False = на руки
    city: str | None = None            # "Санкт-Петербург"
    area_id: str | None =  None        # ID региона
    experience_id: str | None = None   # "between1And3"
    experience_name: str | None = None # "От 1 года до 3 лет"
    company_logo_url: str | None = None
