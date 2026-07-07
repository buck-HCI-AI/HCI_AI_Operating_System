"""
One-time (periodic) manual login capture for Houzz Pro.

Houzz throws a CAPTCHA on any unattended login attempt (confirmed live
2026-07-07) - fully automated username/password login is not viable and
won't be attempted again. This script opens a real, visible browser window
so Buck can log in himself (including the CAPTCHA), then saves the
authenticated session (cookies, including HttpOnly auth cookies which are
invisible to page JavaScript) to disk. houzz_pull.py reuses that saved
session for scheduled read-only extraction until it naturally expires,
at which point this script needs to be run again.

Run manually: python3 capture_session.py
"""
import asyncio
import os
from playwright.async_api import async_playwright

STATE_PATH = os.path.join(os.path.dirname(__file__), "houzz_session.json")
LOGIN_URL = "https://pro.houzz.com/"
LOGGED_IN_URL_MARKER = "/manage/projects"
TIMEOUT_SECONDS = 600  # 10 minutes to complete login + any CAPTCHA


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            viewport={"width": 1440, "height": 900},
        )
        page = await context.new_page()
        await page.goto(LOGIN_URL, wait_until="domcontentloaded")

        print(f"\n{'='*60}\nBrowser window is open. Please log into Houzz Pro yourself.\n"
              f"Waiting up to {TIMEOUT_SECONDS//60} minutes for you to reach {LOGGED_IN_URL_MARKER}...\n{'='*60}\n")

        elapsed = 0
        poll_interval = 3
        while elapsed < TIMEOUT_SECONDS:
            if LOGGED_IN_URL_MARKER in page.url:
                print(f"Detected logged-in state at {page.url}")
                break
            await page.wait_for_timeout(poll_interval * 1000)
            elapsed += poll_interval
        else:
            print("Timed out waiting for login. No session saved. Run again when ready.")
            await browser.close()
            return

        await context.storage_state(path=STATE_PATH)
        print(f"Session saved to {STATE_PATH}")
        await browser.close()

asyncio.run(main())
