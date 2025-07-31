import os
import sys
import time
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright, Error as PlaywrightError


def create_screenshot_filename(url: str, label: str = "text") -> str:
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.replace("www.", "").replace(".", "_")
    path = parsed_url.path.strip("/").replace("/", "_") or "home"
    timestamp = int(time.time())
    return f"{domain}_{path}_{label}_{timestamp}.png"


def test_text_present(url: str, expected_text: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        print(f"🔍 Navigating to {url}")
        screenshot_name = create_screenshot_filename(url)

        try:
            response = page.goto(url, timeout=15000)
            if not response or response.status >= 400:
                print(f"❌ Page returned HTTP {response.status if response else 'no response'}")
                try:
                    page.screenshot(path=screenshot_name, full_page=True)
                    print(f"📷 Screenshot saved to '{screenshot_name}'")
                except Exception as screenshot_error:
                    print(f"⚠️ Could not capture screenshot: {screenshot_error}")
                browser.close()
                sys.exit(1)
        except PlaywrightError as e:
            print(f"❌ Navigation failed: {e}")
            try:
                page.screenshot(path=screenshot_name, full_page=True)
                print(f"📷 Screenshot saved to '{screenshot_name}'")
            except Exception as screenshot_error:
                print(f"⚠️ Could not capture screenshot: {screenshot_error}")
            browser.close()
            sys.exit(1)

        try:
            page.wait_for_selector("body", timeout=5000)
            body_text = page.inner_text("body")
            assert expected_text in body_text, f"Text '{expected_text}' not found"
        except Exception as e:
            print(f"❌ Text presence check failed: {e}")
            try:
                page.screenshot(path=screenshot_name, full_page=True)
                print(f"📷 Screenshot saved to '{screenshot_name}'")
            except Exception as screenshot_error:
                print(f"⚠️ Could not capture screenshot: {screenshot_error}")
            browser.close()
            sys.exit(1)

        page.screenshot(path=screenshot_name, full_page=True)
        print(f"✅ Text '{expected_text}' found on page")
        print(f"📷 Screenshot saved to '{screenshot_name}'")

        browser.close()


if __name__ == "__main__":
    url = os.getenv("SMOKETEST_URL")
    expected_text = os.getenv("EXPECTED_TEXT")

    if not url and len(sys.argv) > 1:
        url = sys.argv[1]
    if not expected_text and len(sys.argv) > 2:
        expected_text = sys.argv[2]

    if not url or not expected_text:
        print("❌ Missing URL or expected text. Set SMOKETEST_URL and EXPECTED_TEXT or pass as arguments.")
        sys.exit(1)

    test_text_present(url, expected_text)
