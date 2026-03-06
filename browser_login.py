import asyncio
from playwright.async_api import async_playwright

SESSION_FILE = ".pw-session.json"

async def login_and_save_session():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://www.linkedin.com/login")

        print("👉 Log into LinkedIn in the opened browser.")
        input("👉 After LinkedIn home loads, press ENTER here...")

        await context.storage_state(path=SESSION_FILE)
        await browser.close()
        print("✅ Session saved.")

asyncio.run(login_and_save_session())