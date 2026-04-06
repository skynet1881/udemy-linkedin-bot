from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Iterable

from dotenv import load_dotenv

from .models import CourseConfig


load_dotenv()


class Settings:
    def __init__(self) -> None:
        self.bot_timezone = os.getenv("BOT_TIMEZONE", "Europe/Berlin")
        self.config_path = Path(os.getenv("CONFIG_PATH", "config/courses.json"))
        self.state_path = Path(os.getenv("STATE_PATH", "state/runtime_state.json"))
        self.headless = os.getenv("HEADLESS", "true").lower() == "true"
        self.dry_run = os.getenv("DRY_RUN", "true").lower() == "true"
        self.course_override = os.getenv("COURSE_OVERRIDE", "").strip() or None
        self.timeout_ms = int(os.getenv("PLAYWRIGHT_TIMEOUT_MS", "30000"))
        self.udemy_storage_state_path = Path(
            os.getenv("UDEMY_STORAGE_STATE_PATH", ".auth/udemy.json")
        )
        self.linkedin_storage_state_path = Path(
            os.getenv("LINKEDIN_STORAGE_STATE_PATH", ".auth/linkedin.json")
        )


def load_courses(path: Path) -> list[CourseConfig]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("Course config must be a JSON array.")
    return [CourseConfig.from_dict(item) for item in raw]


def find_course_by_id(courses: Iterable[CourseConfig], course_id: str) -> CourseConfig | None:
    for course in courses:
        if course.course_id == course_id:
            return course
    return None
