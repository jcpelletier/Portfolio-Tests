import os
import pytest


@pytest.fixture
def url():
    value = os.getenv("SMOKETEST_URL")
    if not value:
        pytest.skip("SMOKETEST_URL not provided")
    return value


@pytest.fixture
def expected_text():
    value = os.getenv("EXPECTED_TEXT")
    if not value:
        pytest.skip("EXPECTED_TEXT not provided")
    return value
