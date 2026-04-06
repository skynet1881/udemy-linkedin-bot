from __future__ import annotations

import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright

TARGET_URLS = {
    "udemy": "https://www.udemy.com/",
    "linkedin": "https://www.linkedin.com/",
}

OUTPUT_PATHS = {
    "udemy": Path(".auth/udemy.json"),
    "linkedin": Path(".auth/linkedin.json"),
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", choices=["udemy", "linkedin"], required=True)
    args = parser.parse_args()

    output_path = OUTPUT_PATHS[args.target]
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="chromium", headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(TARGET_URLS[args.target], wait_until="domcontentloaded")
        input(f"Log in to {args.target}, then press Enter here to save storage state... ")
        context.storage_state(path=str(output_path))
        browser.close()

    print(f"Saved auth state to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
