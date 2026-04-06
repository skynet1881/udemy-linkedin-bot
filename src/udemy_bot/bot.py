from __future__ import annotations

import json
from pathlib import Path

from playwright.sync_api import sync_playwright

from .config import Settings, find_course_by_id, load_courses
from .selectors import validate_selectors
from .linkedin_client import LinkedInClient
from .state_store import RuntimeStateStore
from .text_renderer import build_coupon_code, render_linkedin_message
from .udemy_client import UdemyClient


def _load_settings() -> Settings:
    return Settings()


def _write_secret_file_if_needed(path: Path, secret_name: str) -> None:
    import base64
    import os

    encoded = os.getenv(secret_name, "").strip()
    if not encoded:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(base64.b64decode(encoded))


def run() -> int:
    settings = _load_settings()
    _write_secret_file_if_needed(settings.udemy_storage_state_path, "UDEMY_STORAGE_STATE_B64")
    _write_secret_file_if_needed(settings.linkedin_storage_state_path, "LINKEDIN_STORAGE_STATE_B64")

    courses = load_courses(settings.config_path)
    state_store = RuntimeStateStore(settings.state_path, settings.bot_timezone)
    state = state_store.load()

    if not settings.dry_run:
        validate_selectors()

    selected_course = None
    try:
        if settings.course_override:
            selected_course = find_course_by_id(courses, settings.course_override)
            if selected_course is None:
                raise ValueError(f"Course override not found: {settings.course_override}")
        else:
            selected_course = state_store.choose_next_course(state, courses)

        if selected_course is None:
            state_store.mark_skipped(state, "All courses have reached their monthly coupon limit.")
            state_store.save(state)
            print(json.dumps(state["last_run"], indent=2))
            return 0

        current_bucket = state.setdefault("courses", {}).setdefault(selected_course.course_id, {})
        serial = int(current_bucket.get("count", 0)) + 1
        coupon_code = build_coupon_code(selected_course, serial)

        with sync_playwright() as playwright:
            with UdemyClient(playwright, settings) as udemy_client:
                coupon = udemy_client.create_coupon(selected_course, coupon_code)
            message = render_linkedin_message(selected_course, coupon.coupon_url)
            with LinkedInClient(playwright, settings) as linkedin_client:
                linkedin_client.publish_post(message)

        state_store.mark_success(state, selected_course, coupon.coupon_code, coupon.coupon_url)
        state_store.save(state)
        print(json.dumps(state["last_run"], indent=2))
        return 0
    except Exception as exc:
        state_store.mark_failed(state, selected_course, str(exc))
        state_store.save(state)
        print(json.dumps(state["last_run"], indent=2))
        return 1
