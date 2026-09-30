from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
    ElementClickInterceptedException,
    ElementNotInteractableException
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.logger import get_logger


class BasePage:

    def __init__(self, driver):
        self.driver = driver
        self.logger = get_logger(self.__class__.__name__)

        self.wait = WebDriverWait(
            driver,
            20
        )

    def find_element(
        self,
        locator,
        timeout=20
    ):
        """
        Finds an element with explicit wait and
        centralized exception handling.
        """

        try:

            return WebDriverWait(
                self.driver,
                timeout
            ).until(
                EC.presence_of_element_located(locator)
            )

        except TimeoutException as e:

            self.logger.error(
                "Timeout waiting for element: %s",
                locator
            )

            raise TimeoutException(
                f"Element not found within {timeout} seconds: "
                f"{locator}"
            ) from e

        except NoSuchElementException as e:

            self.logger.error(
                "Element not found: %s",
                locator
            )

            raise

        except StaleElementReferenceException as e:

            self.logger.warning(
                "Stale element encountered: %s",
                locator
            )

            raise    

    def click(self, locator):

        element = self.wait.until(
            EC.element_to_be_clickable(locator)
        )

        element.click()

    def type(self, locator, text):

        element = self.wait.until(
            EC.visibility_of_element_located(locator)
        )

        element.clear()
        element.send_keys(text)

    def get_text(self, locator):

        element = self.wait.until(
            EC.visibility_of_element_located(locator)
        )

        return element.text

    def is_element_present(self, locator, timeout=3):

        try:

            WebDriverWait(
                self.driver,
                timeout
            ).until(
                EC.presence_of_element_located(locator)
            )

            return True

        except Exception:
            return False