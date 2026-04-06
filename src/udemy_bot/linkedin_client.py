from __future__ import annotations

from playwright.sync_api import Browser, BrowserContext, Page, Playwright

from .config import Settings
from .exceptions import AuthStateMissingError
from .selectors import LINKEDIN_SELECTORS


class LinkedInClient:
    def __init__(self, playwright: Playwright, settings: Settings) -> None:
        self._playwright = playwright
        self._settings = settings
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None

    def __enter__(self) -> "LinkedInClient":
        auth_path = self._settings.linkedin_storage_state_path
        if not auth_path.exists():
            raise AuthStateMissingError(f"LinkedIn auth state file is missing: {auth_path}")
        self._browser = self._playwright.chromium.launch(
            channel="chromium",
            headless=self._settings.headless,
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

    def publish_post(self, message: str) -> None:
        page = self.page
        page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded")

        if self._settings.dry_run:
            return

        page.locator(LINKEDIN_SELECTORS.start_post_button).click()
        page.locator(LINKEDIN_SELECTORS.post_editor).fill(message)
        page.locator(LINKEDIN_SELECTORS.submit_post_button).click()
