from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from shared.infrastructure.models.base import Base


class ResumeORM(Base):
    """ORM-модель для таблицы резюме."""

    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    hh_resume_id: Mapped[str | None] = mapped_column(String(50), nullable=True, unique=True)
    profession: Mapped[str] = mapped_column(String(100), nullable=False)
    skills: Mapped[str] = mapped_column(Text, default="")
    full_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self) -> str:
        return f"<ResumeORM(id={self.id}, profession={self.profession})>"
