import os
import sys
import time
from urllib.parse import urlparse
from playwright.sync_api import (
    sync_playwright,
    Error as PlaywrightError,
    TimeoutError as PlaywrightTimeoutError,
)

def create_screenshot_filename(url: str, suffix: str | None = None) -> str:
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.replace("www.", "").replace(".", "_")
    path = parsed_url.path.strip("/").replace("/", "_") or "home"
    timestamp = int(time.time())
    parts = [domain, path, str(timestamp)]
    if suffix:
        parts.append(suffix)
    return "_".join(parts) + ".png"

def test_page_loads(url: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.set_default_navigation_timeout(65000)

        print(f"🔍 Navigating to {url}")

        try:
            start_time = time.perf_counter()
            response = page.goto(url, timeout=65000, wait_until="domcontentloaded")
            time.sleep(2)

            # Screenshot before scroll
            pre_scroll_name = create_screenshot_filename(url, "pre_scroll")
            page.screenshot(path=pre_scroll_name, full_page=True)
            print(f"📷 Pre-scroll screenshot saved to '{pre_scroll_name}'")

            # Scroll incrementally
            scroll_steps = 4
            for step in range(1, scroll_steps + 1):
                scroll_position = f"document.body.scrollHeight * {step / scroll_steps}"
                page.evaluate(f"window.scrollTo(0, {scroll_position})")
                time.sleep(1)

            # Final scroll to bottom
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)

            # Screenshot after scroll
            post_scroll_name = create_screenshot_filename(url, "post_scroll")
            page.screenshot(path=post_scroll_name, full_page=True)
            print(f"📷 Post-scroll screenshot saved to '{post_scroll_name}'")

            # Wait for specific content to appear
            selector = os.getenv("TEST_SELECTOR", "h1")
            try:
                page.wait_for_selector(selector, timeout=10000)
                print(f"✅ Selector '{selector}' detected, page likely rendered.")
            except PlaywrightTimeoutError as e:
                print(f"⚠️ Selector '{selector}' not found: {e}")
                raise

            load_time = time.perf_counter() - start_time

            if not response or response.status >= 400:
                print(f"❌ Page returned HTTP {response.status if response else 'no response'}")
                screenshot_name = create_screenshot_filename(url)
                try:
                    page.screenshot(path=screenshot_name, full_page=True)
                    print(f"📷 Screenshot saved to '{screenshot_name}'")
                except Exception as screenshot_error:
                    print(f"⚠️ Could not capture screenshot: {screenshot_error}")
                browser.close()
                sys.exit(1)
        except PlaywrightError as e:
            print(f"❌ Navigation failed: {e}")
            screenshot_name = create_screenshot_filename(url)
            try:
                page.screenshot(path=screenshot_name, full_page=True)
                print(f"📷 Screenshot saved to '{screenshot_name}'")
            except Exception as screenshot_error:
                print(f"⚠️ Could not capture screenshot: {screenshot_error}")
            browser.close()
            sys.exit(1)

        try:
            page.wait_for_selector("body", timeout=5000)
        except PlaywrightError as e:
            print(f"❌ Page body did not load: {e}")
            screenshot_name = create_screenshot_filename(url)
            try:
                page.screenshot(path=screenshot_name, full_page=True)
                print(f"📷 Screenshot saved to '{screenshot_name}'")
            except Exception as screenshot_error:
                print(f"⚠️ Could not capture screenshot: {screenshot_error}")
            browser.close()
            sys.exit(1)

        try:
            title = page.title()
            assert title.strip(), "Page title is empty"
        except Exception as e:
            print(f"❌ Title check failed: {e}")
            screenshot_name = create_screenshot_filename(url)
            try:
                page.screenshot(path=screenshot_name, full_page=True)
                print(f"📷 Screenshot saved to '{screenshot_name}'")
            except Exception as screenshot_error:
                print(f"⚠️ Could not capture screenshot: {screenshot_error}")
            browser.close()
            sys.exit(1)

        screenshot_name = create_screenshot_filename(url, "final")
        page.screenshot(path=screenshot_name, full_page=True)
        print(f"✅ Page loaded. Title: {title}")
        print(f"⏱ Load time: {load_time:.2f} seconds")
        print(f"📷 Screenshot saved to '{screenshot_name}'")

        browser.close()

if __name__ == "__main__":
    url = os.getenv("SMOKETEST_URL")
    if not url and len(sys.argv) > 1:
        url = sys.argv[1]
    if not url:
        print("❌ No URL provided. Set SMOKETEST_URL or pass as argument.")
        sys.exit(1)

    test_page_loads(url)
