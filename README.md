# Udemy → LinkedIn Rotation Bot

A production-oriented starter repo for rotating through multiple Udemy courses, creating discount coupons, and publishing one LinkedIn post per run.

## What this repo does

- rotates through a list of courses from `config/courses.json`
- enforces a **hard monthly limit** per course (`monthly_coupon_limit`, default `3`)
- creates at most **one coupon + one LinkedIn post per run**
- stores runtime state in `state/runtime_state.json`
- can run on a daily GitHub Actions schedule or manually with `workflow_dispatch`
- supports Playwright `storage_state` authentication for Udemy and LinkedIn
- supports dry-run mode for safe testing

## Important reality check

This repo is deliberately built as a **production starter**, not a magic one-click bot:

- Udemy does not expose a public coupon-creation API for this flow, so this repo automates the website through Playwright.
- LinkedIn posting through browser automation may trigger anti-automation checks.
- UI selectors change over time. You will likely need to re-record or adjust selectors.

Because of that, the project isolates selectors in one place so future fixes are quick.

---

## Repository structure

```text
.
├── .github/workflows/daily-bot.yml
├── config/
│   └── courses.json
├── scripts/
│   └── bootstrap_auth.py
├── src/udemy_bot/
│   ├── __init__.py
│   ├── bot.py
│   ├── config.py
│   ├── exceptions.py
│   ├── linkedin_client.py
│   ├── models.py
│   ├── selectors.py
│   ├── state_store.py
│   ├── text_renderer.py
│   └── udemy_client.py
├── state/
│   └── runtime_state.json
├── .env.example
├── .gitignore
├── requirements.txt
└── run_bot.py
```

---

## 1) Put your courses and messages into JSON

Edit `config/courses.json`.

Example:

```json
[
  {
    "course_id": "embedded-c-interviews",
    "course_label": "Embedded C Interview Prep",
    "udemy_promotions_url": "https://www.udemy.com/instructor/course/YOUR_COURSE/manage/promotions/",
    "coupon_prefix": "EMBC",
    "coupon_price": "9.99",
    "monthly_coupon_limit": 3,
    "max_redemptions": 1000,
    "linkedin_message_template": "🚀 New discount for my {course_label} course!\n\nUse this link: {coupon_url}\n\nLearn practical embedded concepts with hands-on examples.\n\n#embedded #cprogramming #udemy"
  }
]
```

You can add all 11 courses here.

---

## 2) Authentication approach

This starter uses **Playwright storage state** rather than raw passwords.

Why this is better:

- more stable than logging in every run
- easier to use when MFA or extra checks appear
- better for CI

### Generate storage state locally

Run on your own machine first:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install --with-deps chromium
python scripts/bootstrap_auth.py --target udemy
python scripts/bootstrap_auth.py --target linkedin
```

This opens a browser. Log in manually, then press Enter in the terminal when the account is fully logged in.

It will create:

- `.auth/udemy.json`
- `.auth/linkedin.json`

### Save them in GitHub secrets

Encode them:

```bash
base64 -w 0 .auth/udemy.json > /tmp/udemy.b64
base64 -w 0 .auth/linkedin.json > /tmp/linkedin.b64
```

Create these GitHub Actions secrets:

- `UDEMY_STORAGE_STATE_B64`
- `LINKEDIN_STORAGE_STATE_B64`

---

## 3) Optional environment variables

Copy `.env.example` to `.env` for local testing.

Key variables:

- `BOT_TIMEZONE=Europe/Berlin`
- `CONFIG_PATH=config/courses.json`
- `STATE_PATH=state/runtime_state.json`
- `DRY_RUN=true` for safe testing
- `HEADLESS=true`
- `COURSE_OVERRIDE=` to force one course by `course_id`

---

## 4) Daily run locally

```bash
python run_bot.py
```

---

## 5) GitHub Actions schedule

The workflow already includes:

- `schedule` for automatic daily runs
- `workflow_dispatch` for manual test runs

If you want Berlin 10:00, remember GitHub scheduled workflows use **UTC** and run on the latest commit of the default branch.
Adjust the cron expression accordingly.

---

## 6) Runtime state

The bot persists:

- rotation index
- monthly counts per course
- last coupon code and URL
- last run outcome

The workflow commits the updated `state/runtime_state.json` back to the repository automatically.

---

## 7) Selector setup

Before production, record selectors with Playwright codegen or browser inspector and update:

- `src/udemy_bot/selectors.py`

This is the only file you should usually need to touch when Udemy or LinkedIn changes UI.

---

## 8) Safe rollout plan

1. Run with `DRY_RUN=true`
2. Verify course rotation and state updates
3. Test Udemy only
4. Test LinkedIn only
5. Enable full production mode

---

## 9) Recommended operational notes

- Keep posting frequency realistic.
- Recreate storage state if sessions expire.
- Expect occasional selector maintenance.
- Never commit raw auth files to git.

