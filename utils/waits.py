from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Waits:

    def __init__(self, driver, timeout=20):
        self.driver = driver
        self.timeout = timeout

    def visible(self, locator):
        return WebDriverWait(self.driver, self.timeout).until(
            EC.visibility_of_element_located(locator)
        )

    def clickable(self, locator):
        return WebDriverWait(self.driver, self.timeout).until(
            EC.element_to_be_clickable(locator)
        )