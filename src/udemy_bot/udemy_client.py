from __future__ import annotations

from pathlib import Path

from playwright.sync_api import Browser, BrowserContext, Page, Playwright

from .config import Settings
from .exceptions import AuthStateMissingError
from .models import CouponResult, CourseConfig
from .selectors import UDEMY_SELECTORS


class UdemyClient:
    def __init__(self, playwright: Playwright, settings: Settings) -> None:
        self._playwright = playwright
        self._settings = settings
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None

    def __enter__(self) -> "UdemyClient":
        auth_path = self._settings.udemy_storage_state_path
        if not auth_path.exists():
            raise AuthStateMissingError(f"Udemy auth state file is missing: {auth_path}")

        self._browser = self._playwright.chromium.launch(
            channel="chromium",
            headless=False,
            slow_mo=500,
        )
        self._context = self._browser.new_context(storage_state=str(auth_path))
        self._page = self._context.new_page()
        self._page.set_default_timeout(self._settings.timeout_ms)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._context is not None:
            self._context.close()
        if self._browser is not None:
            self._browser.close()

    @property
    def page(self) -> Page:
        assert self._page is not None
        return self._page

    def create_coupon(self) -> str:
        if self._page is None:
            raise RuntimeError("Browser page is not initialized.")

        page = self._page

        page.wait_for_selector("button:has-text('Create coupon')")
        page.click("button:has-text('Create coupon')")

        page.wait_for_selector("a:has-text('Share coupon')")
        page.locator("a:has-text('Share coupon')").last.click()

        page.wait_for_selector("input")
        coupon_link = page.locator("input").first.input_value()

        return coupon_link