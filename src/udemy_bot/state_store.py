from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from .models import CourseConfig


@dataclass
class RuntimeStateStore:
    path: Path
    timezone_name: str

    def _default(self) -> dict:
        return {"rotation_index": 0, "courses": {}, "last_run": None}

    def load(self) -> dict:
        if not self.path.exists():
            state = self._default()
            self.save(state)
            return state
        return json.loads(self.path.read_text(encoding="utf-8"))

    def save(self, state: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def now(self) -> datetime:
        return datetime.now(ZoneInfo(self.timezone_name))

    def _course_bucket(self, state: dict, course: CourseConfig) -> dict:
        courses = state.setdefault("courses", {})
        return courses.setdefault(
            course.course_id,
            {
                "year_month": None,
                "count": 0,
                "last_coupon_code": None,
                "last_coupon_url": None,
                "last_posted_at": None,
            },
        )

    def _reset_month_if_needed(self, bucket: dict, current_year_month: str) -> None:
        if bucket.get("year_month") != current_year_month:
            bucket["year_month"] = current_year_month
            bucket["count"] = 0

    def choose_next_course(self, state: dict, courses: list[CourseConfig]) -> CourseConfig | None:
        if not courses:
            return None
        now = self.now()
        current_year_month = f"{now.year:04d}-{now.month:02d}"
        start_index = int(state.get("rotation_index", 0)) % len(courses)

        for offset in range(len(courses)):
            idx = (start_index + offset) % len(courses)
            course = courses[idx]
            bucket = self._course_bucket(state, course)
            self._reset_month_if_needed(bucket, current_year_month)
            if int(bucket.get("count", 0)) < course.monthly_coupon_limit:
                state["rotation_index"] = (idx + 1) % len(courses)
                return course

        return None

    def mark_success(self, state: dict, course: CourseConfig, coupon_code: str, coupon_url: str) -> None:
        now = self.now().isoformat()
        bucket = self._course_bucket(state, course)
        bucket["count"] = int(bucket.get("count", 0)) + 1
        bucket["last_coupon_code"] = coupon_code
        bucket["last_coupon_url"] = coupon_url
        bucket["last_posted_at"] = now
        state["last_run"] = {
            "status": "success",
            "course_id": course.course_id,
            "course_label": course.course_label,
            "coupon_code": coupon_code,
            "coupon_url": coupon_url,
            "timestamp": now,
        }

    def mark_skipped(self, state: dict, reason: str) -> None:
        state["last_run"] = {
            "status": "skipped",
            "reason": reason,
            "timestamp": self.now().isoformat(),
        }

    def mark_failed(self, state: dict, course: CourseConfig | None, error: str) -> None:
        state["last_run"] = {
            "status": "failed",
            "course_id": None if course is None else course.course_id,
            "course_label": None if course is None else course.course_label,
            "error": error,
            "timestamp": self.now().isoformat(),
        }

    def snapshot(self, state: dict) -> dict:
        return deepcopy(state)
