import os
import sys
import time
from playwright.sync_api import sync_playwright

def test_page_loads(url: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        print(f"🔍 Navigating to {url}")
        page.goto(url, timeout=15000)

        # 🔄 Wait for visible content
        try:
            page.wait_for_selector("body", timeout=5000)
        except Exception:
            print("❌ Page body did not load in time")
            browser.close()
            sys.exit(1)

        # ✅ Check title
        title = page.title()
        assert title.strip(), "Page title is empty"

        # 🕓 Timestamped screenshot filename
        timestamp = int(time.time())
        screenshot_path = f"screenshot_{timestamp}.png"
        page.screenshot(path=screenshot_path, full_page=True)

        print(f"✅ Page loaded. Title: {title}")
        print(f"📷 Screenshot saved to '{screenshot_path}'")

        browser.close()

if __name__ == "__main__":
    url = os.getenv("SMOKETEST_URL")

    if not url and len(sys.argv) > 1:
        url = sys.argv[1]

    if not url:
        print("❌ No URL provided. Set SMOKETEST_URL or pass as argument.")
        sys.exit(1)

    test_page_loads(url)
