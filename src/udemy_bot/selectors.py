from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UdemySelectors:
    create_coupon_button: str = "button:has-text('Create coupon')"
    generated_coupon_link: str = "a:has-text('Share coupon')"


@dataclass(frozen=True)
class LinkedInSelectors:
    start_post_button: str = "button:has-text('Start a post'), div[role='button']:has-text('Start a post')"
    post_editor: str = "div[role='textbox'], div[contenteditable='true']"
    submit_post_button: str = "button:has-text('Post')"


UDEMY_SELECTORS = UdemySelectors()
LINKEDIN_SELECTORS = LinkedInSelectors()


def validate_selectors() -> None:
    pass