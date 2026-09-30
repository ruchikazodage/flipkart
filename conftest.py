'''import pytest

from drivers.driver_factory import DriverFactory


def pytest_addoption(parser):
    parser.addoption(
        "--browser",
        action="store",
        default=None,
        help="Browser to execute tests: chrome, firefox, edge"
    )


@pytest.fixture
def driver(request):

    browser = request.config.getoption("--browser")

    if browser is None:
        browser = "chrome"

    driver = DriverFactory.get_driver(browser=browser)

    yield driver

    driver.quit()'''

""" import logging
import re
from datetime import datetime
from pathlib import Path

import pytest

from drivers.driver_factory import DriverFactory
from config.settings import environment_config
from utils.logger import get_logger

logger = get_logger(__name__)

def pytest_addoption(parser):

    parser.addoption(
        "--browser",
        action="store",
        default=None,
        help="Browser: chrome, firefox, edge"
    )


@pytest.fixture
def driver(request):

    browser = request.config.getoption("--browser")

    if browser is None:
        browser = environment_config["browser"]

    headless = environment_config.get("headless", False)

    logger.info("Starting browser: %s", browser)
    logger.info("Headless mode: %s", headless)

    driver = DriverFactory.get_driver(
        browser=browser,
        headless=headless
    )
    logger.info("Browser started successfully")


    yield driver

    logger.info("Closing browser")
    driver.quit()
    logger.info("Browser closed")"""



import logging
import re
from hashlib import sha1
from datetime import datetime
from pathlib import Path

import pytest
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

from drivers.driver_factory import DriverFactory
from config.settings import environment_config


# ============================================================
# PROJECT / EXECUTION DIRECTORIES
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent

execution_time = datetime.now()

EXECUTION_DATE = execution_time.strftime("%Y-%m-%d")
EXECUTION_TIMESTAMP = execution_time.strftime("%Y%m%d_%H%M%S_%f")
EXECUTION_TIME = execution_time.strftime("%H:%M:%S")
EXECUTION_STARTED = execution_time.strftime("%Y-%m-%d %H:%M:%S")

RUN_DIR = (
    PROJECT_ROOT
    / "test_results"
    / EXECUTION_DATE
    / f"execution_{EXECUTION_TIMESTAMP}"
)

REPORT_DIR = RUN_DIR / "reports"
LOG_DIR = RUN_DIR / "logs"
SCREENSHOT_DIR = RUN_DIR / "screenshots"


# Create directories
REPORT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOGGING CONFIGURATION
# ============================================================

LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)s | "
    "%(name)s | "
    "%(message)s"
)

LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

formatter = logging.Formatter(
    LOG_FORMAT,
    datefmt=LOG_DATE_FORMAT
)


def get_safe_test_name(nodeid):
    """
    Converts pytest node ID into a safe filename.

    Example:
    tests/test_flipkart.py::test_search
    becomes:
    tests_test_flipkart.py_test_search
    """

    safe_name = re.sub(
        r"[^A-Za-z0-9_.-]+",
        "_",
        nodeid
    )

    return safe_name.strip("_")


# ============================================================
# PYTEST CONFIGURATION
# ============================================================

def pytest_configure(config):
    """
    Configure execution-level directories and logging.
    """

    # Store paths on pytest config object
    config.run_dir = RUN_DIR
    config.report_dir = REPORT_DIR
    config.log_dir = LOG_DIR
    config.screenshot_dir = SCREENSHOT_DIR
    config.excel_results = {}
    config.collected_test_ids = []

    # --------------------------------------------------------
    # Root logger
    # --------------------------------------------------------

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # --------------------------------------------------------
    # Console handler
    # --------------------------------------------------------

    console_handler_exists = any(
        getattr(handler, "_qa_console_handler", False)
        for handler in root_logger.handlers
    )

    if not console_handler_exists:

        console_handler = logging.StreamHandler()

        console_handler.setFormatter(formatter)

        console_handler._qa_console_handler = True

        root_logger.addHandler(console_handler)

    # --------------------------------------------------------
    # Dynamic pytest-html report location
    # --------------------------------------------------------

    if hasattr(config.option, "htmlpath"):

        config.option.htmlpath = str(
            REPORT_DIR / "execution_report.html"
        )

        config.option.self_contained_html = True


# ============================================================
# CSV EXECUTION SUMMARY
# ============================================================

def pytest_collection_finish(session):
    """Remember every selected test so tests that never start are reported."""
    session.config.collected_test_ids = [item.nodeid for item in session.items]


def _record_excel_result(item, report):
    """Store the final result for one test, including setup/teardown failures."""
    if report.when == "call" and report.passed:
        status = "Passed"
    elif report.when == "call" and report.failed:
        status = "Failed"
    elif report.when in {"setup", "call"} and report.skipped:
        status = "Skipped"
    elif report.when in {"setup", "teardown"} and report.failed:
        status = "Failed"
    else:
        return

    existing = item.config.excel_results.get(item.nodeid)
    # A teardown failure must replace an earlier passed call result.
    if existing and existing["status"] == "Failed":
        return

    item.config.excel_results[item.nodeid] = {
        "status": status,
        "duration_seconds": round(report.duration, 3),
        "failure_reason": (
            (getattr(report, "longreprtext", "") or str(getattr(report, "longrepr", "")))
            if status == "Failed"
            else ""
        )[:32767],
    }


def pytest_sessionfinish(session, exitstatus):
    """Write an Excel summary and per-test results for every pytest run."""
    config = session.config
    results = config.excel_results
    test_ids = config.collected_test_ids
    xlsx_path = REPORT_DIR / f"test_execution_summary_{EXECUTION_TIMESTAMP}.xlsx"

    passed = sum(result["status"] == "Passed" for result in results.values())
    failed = sum(result["status"] == "Failed" for result in results.values())
    skipped = sum(result["status"] == "Skipped" for result in results.values())
    not_run = len(test_ids) - len(results)
    executed = passed + failed

    workbook = Workbook()
    summary_sheet = workbook.active
    summary_sheet.title = "Execution Summary"
    results_sheet = workbook.create_sheet("Test Results")

    header_fill = PatternFill("solid", fgColor="1F4E78")
    header_font = Font(color="FFFFFF", bold=True)

    summary_rows = [
        ["Test Execution Summary", ""],
        ["Execution Date", EXECUTION_DATE],
        ["Execution Time", EXECUTION_TIME],
        ["Execution Started", EXECUTION_STARTED],
        ["", ""],
        ["Metric", "Count"],
        ["Total test cases", len(test_ids)],
        ["Executed", executed],
        ["Passed", passed],
        ["Failed", failed],
        ["Not Run", skipped + not_run],
    ]
    for row in summary_rows:
        summary_sheet.append(row)
    summary_sheet.merge_cells("A1:B1")
    summary_sheet["A1"].font = Font(bold=True, size=14)
    for cell in summary_sheet[6]:
        cell.fill = header_fill
        cell.font = header_font
    summary_sheet.column_dimensions["A"].width = 24
    summary_sheet.column_dimensions["B"].width = 24

    headers = [
        "Test Case",
        "Status",
        "Duration (seconds)",
        "Execution Date",
        "Execution Time",
        "Execution Started",
        "Failure Reason",
    ]
    results_sheet.append(headers)
    for cell in results_sheet[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")
    results_sheet.freeze_panes = "A2"
    results_sheet.auto_filter.ref = "A1:G1"

    for nodeid in test_ids:
        result = results.get(nodeid)
        if result is None:
            row = [nodeid, "Not Run", "", EXECUTION_DATE, EXECUTION_TIME, EXECUTION_STARTED, ""]
        else:
            row = [
                nodeid,
                "Not Run" if result["status"] == "Skipped" else result["status"],
                result["duration_seconds"],
                EXECUTION_DATE,
                EXECUTION_TIME,
                EXECUTION_STARTED,
                result["failure_reason"],
            ]
        results_sheet.append(row)

    for row in results_sheet.iter_rows(min_row=2):
        row[6].alignment = Alignment(wrap_text=True, vertical="top")
    for column, width in {"A": 70, "B": 14, "C": 18, "D": 16, "E": 16, "F": 24, "G": 80}.items():
        results_sheet.column_dimensions[column].width = width

    workbook.save(xlsx_path)
    logging.getLogger(__name__).info("Excel execution summary saved: %s", xlsx_path)


# ============================================================
# SEPARATE LOG FILE FOR EACH TEST
# ============================================================

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):
    """
    Creates a separate log file for every test case.

    Example:

    test_results/
        2026-09-17/
            execution_20260917_013500_123456/
                logs/
                    tests_test_flipkart_test_search.log
                    tests_test_flipkart_test_login.log
    """

    test_name = get_safe_test_name(item.nodeid)

    test_log_file = LOG_DIR / f"{test_name}.log"

    root_logger = logging.getLogger()

    file_handler = logging.FileHandler(
        test_log_file,
        mode="w",
        encoding="utf-8"
    )

    file_handler.setFormatter(formatter)

    # Mark handler so we can identify it later
    file_handler._qa_test_handler = True

    # Add test-specific handler
    root_logger.addHandler(file_handler)

    try:

        yield

    finally:

        # Remove test-specific handler
        root_logger.removeHandler(file_handler)

        file_handler.close()


# ============================================================
# BROWSER CLI OPTION
# ============================================================

def pytest_addoption(parser):

    parser.addoption(
        "--browser",
        action="store",
        default=None,
        help="Browser: chrome, firefox, edge"
    )


# ============================================================
# DRIVER FIXTURE
# ============================================================

@pytest.fixture
def driver(request):

    logger = logging.getLogger(__name__)

    # --------------------------------------------------------
    # Browser selection
    # --------------------------------------------------------

    browser = request.config.getoption("--browser")

    if browser is None:
        browser = environment_config["browser"]

    headless = environment_config.get(
        "headless",
        False
    )

    logger.info(
        "Starting browser: %s",
        browser
    )

    logger.info(
        "Headless mode: %s",
        headless
    )

    # --------------------------------------------------------
    # Create driver
    # --------------------------------------------------------

    driver = DriverFactory.get_driver(
        browser=browser,
        headless=headless
    )

    logger.info(
        "Browser started successfully"
    )

    try:

        yield driver

    finally:

        # ----------------------------------------------------
        # Close browser
        # ----------------------------------------------------

        logger.info(
            "Closing browser"
        )

        driver.quit()

        logger.info(
            "Browser closed"
        )


# ============================================================
# SCREENSHOT ON FAILURE
# ============================================================

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):

    outcome = yield
    report = outcome.get_result()

    setattr(
        item,
        f"rep_{report.when}",
        report
    )

    _record_excel_result(item, report)

    # Take screenshot when test fails
    if report.when == "call" and report.failed:

        driver = item.funcargs.get("driver")

        if driver is not None:

            test_name = get_safe_test_name(
                item.nodeid
            )

            # Parameterized node IDs can make a Windows path exceed its legacy
            # 260-character boundary. Retain a readable prefix and a stable
            # hash so every failure screenshot remains uniquely identifiable.
            screenshot_name = (
                f"{test_name[:80]}_{sha1(item.nodeid.encode('utf-8')).hexdigest()[:10]}.png"
            )
            screenshot_file = SCREENSHOT_DIR / screenshot_name

            try:
                screenshot_file.parent.mkdir(parents=True, exist_ok=True)
                screenshot_bytes = driver.get_screenshot_as_png()
                screenshot_file.write_bytes(screenshot_bytes)

                if not screenshot_bytes or not screenshot_file.is_file():
                    raise RuntimeError("WebDriver returned an empty screenshot.")

                logging.getLogger(__name__).info(
                    "Failure screenshot saved: %s",
                    screenshot_file
                )

            except Exception as screenshot_error:

                logging.getLogger(__name__).error(
                    "Failed to capture screenshot: %s",
                    screenshot_error
                )
