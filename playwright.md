# Automate your browser with Playwright

Playwright is a tool for automating browsers. It's similar to Selenium, but it's more modern and has
a better API. It's also cross-platform, so you can use it on Windows, Mac, and Linux.

## Installation


## Interactive usage

### Start Playwright and Launch a new Browser

```python
from playwright.sync_api import sync_playwright
playwright = sync_playwright().start()
browser = playwright.chromium.launch(headless=False)
page = browser.new_page()
```

### Connect to an existing browser


