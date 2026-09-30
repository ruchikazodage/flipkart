from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService

from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager


class DriverFactory:

    @staticmethod
    def get_driver(browser="chrome", headless=False):

        browser = browser.lower()

        if browser == "chrome":
            driver = DriverFactory._create_chrome_driver(headless)

        elif browser == "firefox":
            driver = DriverFactory._create_firefox_driver(headless)

        elif browser == "edge":
            driver = DriverFactory._create_edge_driver(headless)

        else:
            raise ValueError(
                f"Unsupported browser: {browser}. "
                f"Supported browsers: chrome, firefox, edge"
            )

        driver.maximize_window()
        driver.implicitly_wait(0)

        return driver

    @staticmethod
    def _create_chrome_driver(headless=False):

        options = webdriver.ChromeOptions()

        if headless:
            options.add_argument("--headless=new")

        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")

        return webdriver.Chrome(
            service=ChromeService(
                ChromeDriverManager().install()
            ),
            options=options
        )

    @staticmethod
    def _create_firefox_driver(headless=False):

        options = webdriver.FirefoxOptions()

        if headless:
            options.add_argument("--headless")

        return webdriver.Firefox(
            service=FirefoxService(
                GeckoDriverManager().install()
            ),
            options=options
        )

    @staticmethod
    def _create_edge_driver(headless=False):

        options = webdriver.EdgeOptions()

        if headless:
            options.add_argument("--headless=new")

        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")

        return webdriver.Edge(
            service=EdgeService(
                EdgeChromiumDriverManager().install()
            ),
            options=options
        )