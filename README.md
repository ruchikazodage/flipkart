# Flipkart QA Automation Framework

UI automation framework created for the Unbox QA Automation Lead assignment. It uses Python, pytest, Selenium WebDriver, and the Page Object Model to automate core Flipkart search, comparison, and shopping-cart journeys.

## Scope

The framework currently covers:

- Searching for mobile products and validating the result summary.
- Selecting the 10th and 11th search results and validating the comparison flow.
- Opening the 10th search result, adding it to the cart, and validating the cart total against the captured list price.
- Increasing quantity, removing the item, and validating the empty-cart state.
- Running against Chrome, Firefox, or Edge through a common driver factory.
- Creating timestamped test-result folders with HTML reports and per-test log files.

## Technology Stack

- Python 3.10+ recommended
- pytest
- Selenium WebDriver
- pytest-html
- webdriver-manager
- PyYAML
- python-dotenv
- requests and SQLAlchemy are listed as extension dependencies

## Project Structure

```text
.
|-- api/                  API client extension point
|-- config/
|   |-- environments/     dev, qa, uat, and prod YAML configuration
|   `-- settings.py       Loads ENV and test data
|-- data/
|   `-- test_data.yaml    Search keyword and product indexes
|-- drivers/
|   `-- driver_factory.py Browser creation and options
|-- pages/                Page Object Model classes
|   |-- base_page.py      Shared waits, actions, and element helpers
|   |-- home_page.py
|   |-- search_results_page.py
|   |-- comparison_page.py
|   |-- product_page.py
|   `-- cart_page.py
|-- tests/                pytest test cases
|-- utils/                Logging and utility extension points
|-- conftest.py           Fixtures, CLI options, logging, and reports
|-- pytest.ini             pytest discovery and markers
`-- requirements.txt      Python dependencies
```

## Setup

From the repository root, create and activate a virtual environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
```

The project also supports a `.env` file. Set `ENV` to select a configuration file; when it is omitted, `qa` is used:

```text
ENV=qa
```

The selected file is loaded from `config/environments/<ENV>.yaml`. The QA configuration points to `https://www.flipkart.com/` and runs Chrome in non-headless mode by default.

## Running Tests

Run the complete suite:

```powershell
py -m pytest
```

Run with a specific browser:

```powershell
py -m pytest --browser chrome
py -m pytest --browser firefox
py -m pytest --browser edge
```

List tests without starting a browser:

```powershell
py -m pytest --collect-only -q
```

The browser driver is downloaded and managed by `webdriver-manager`. A network connection is therefore required on the first browser run. Flipkart is a live site, so tests can also be affected by changes to the site DOM, login popups, product availability, price changes, or regional behavior.

## Test Coverage

| Test module | Coverage |
| --- | --- |
| `tests/test_flipkart_flow.py` | Search result message; comparison of products 10 and 11; add-to-cart and total validation |
| `tests/test_cart_flow.py` | End-to-end cart flow for product 10, quantity update, removal, and empty-cart validation |
| `tests/test_flipkart_mobile_flow.py` | Legacy flow retained for reference; it is collected but uses older page-object method names and should be aligned before treating it as a maintained test |

The current suite collects five tests: four maintained scenarios in the two primary modules and one legacy scenario.

## Reporting and Diagnostics

`conftest.py` creates a unique execution directory under `test_results/<date>/execution_<timestamp>/` containing:

- `reports/execution_report.html`: pytest-html report when HTML reporting is enabled.
- `reports/test_execution_summary_<timestamp>.xlsx`: Excel workbook containing an execution summary and per-test results, including execution date/time and failure reason.
- `logs/`: a separate log file for each test.
- `screenshots/`: reserved for execution screenshots.

Example:

```text
test_results/
`-- 2026-09-17/
	`-- execution_20260917_153557_414801/
		|-- logs/
		|-- reports/
		`-- screenshots/
```

## Design Decisions

- Page objects keep browser locators and user actions out of the test cases.
- `BasePage` centralizes explicit waits and common Selenium operations.
- `DriverFactory` provides browser-independent setup and supports headless execution through environment configuration.
- Test data and environment values are externalized in YAML files rather than hard-coded in test logic.
- Product name and price are captured from the search result before navigation so the cart assertions compare the same product selected by the test.
- The fixture always closes the browser after the test, including after failures.

## Current Limitations and Next Improvements

These are known items to address before presenting the framework as production-ready:

1. Implement `CartPage.verify_product_in_cart()`. The maintained cart test currently performs this assertion through page-source inspection instead.
2. Update or remove `tests/test_flipkart_mobile_flow.py`; its calls do not match the current `HomePage` API.
3. Replace fragile, live-site CSS/XPath selectors with stable application test IDs where available.
4. Add failure screenshots through a pytest hook and attach them to the HTML report.
5. Remove duplicate or unused scaffolding in `api/`, `db/`, and `utils/` until those extension points are implemented.
6. Add API, unit, and negative tests so the suite is not dependent only on live UI behavior.
7. Add CI execution with browser setup, artifact retention, and a controlled test environment.

## Recruiter Presentation Summary

This is a maintainable Selenium framework rather than a collection of recorded scripts. The key engineering points are separation of concerns, reusable page objects, externalized configuration, cross-browser support, explicit waits, data-driven product selection, and diagnostic artifacts for each execution. During a live demo, explain the current limitations honestly and describe the next improvements as part of the engineering roadmap.
