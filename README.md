# PortfolioTests
A collection of Playwright tests used to confirm my portfolio site is running correctly.

## Running the tests

Each test script can be run directly with Python and is configured using environment variables.

### `test_page_loads.py`
Checks that a page loads successfully and saves a screenshot. Set `SMOKETEST_URL` to the URL to test or pass it as the first argument.

```bash
SMOKETEST_URL="https://example.com" python Tests/test_page_loads.py
```

### `test_text_presence.py`
Verifies that a specific piece of text is present on the page. Set `SMOKETEST_URL` and `EXPECTED_TEXT` or provide them as arguments.

```bash
SMOKETEST_URL="https://example.com" EXPECTED_TEXT="Hello World" \
    python Tests/test_text_presence.py
```


## Additional test ideas
- Verify that all images have an `alt` attribute to improve accessibility.
- Crawl internal links and ensure none return an HTTP error status.
- Check that a footer or navigation element is present on every page.
