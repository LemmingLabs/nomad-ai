from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user_usage_stat import UserUsageStat


class UsageService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _today() -> date:
        return datetime.now(timezone.utc).date()

    def _get_row(self, user_id: int, day: date) -> UserUsageStat | None:
        statement = select(UserUsageStat).where(
            UserUsageStat.user_id == user_id,
            UserUsageStat.date == day,
        )
        return self.db.execute(statement).scalar_one_or_none()

    def _get_or_create_row(self, user_id: int, day: date) -> UserUsageStat:
        row = self._get_row(user_id=user_id, day=day)
        if row is not None:
            return row

        row = UserUsageStat(
            user_id=user_id,
            date=day,
            trip_generations_count=0,
            chat_edits_count=0,
        )

        try:
            with self.db.begin_nested():
                self.db.add(row)
                self.db.flush()
            return row
        except IntegrityError:
            try:
                self.db.expunge(row)
            except Exception:
                pass
            existing = self._get_row(user_id=user_id, day=day)
            if existing is None:
                raise
            return existing

    def get_or_create_today_usage(self, user_id: int) -> UserUsageStat:
        return self._get_or_create_row(user_id=user_id, day=self._today())

    def get_today_usage(self, user_id: int) -> UserUsageStat | None:
        return self._get_row(user_id=user_id, day=self._today())

    def increment_trip_generation(self, user_id: int) -> UserUsageStat:
        row = self.get_or_create_today_usage(user_id)
        row.trip_generations_count += 1
        self.db.add(row)
        self.db.flush()
        return row

    def increment_chat_edit(self, user_id: int) -> UserUsageStat:
        row = self.get_or_create_today_usage(user_id)
        row.chat_edits_count += 1
        self.db.add(row)
        self.db.flush()
        return row
