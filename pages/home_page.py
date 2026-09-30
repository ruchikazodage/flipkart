from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage


class HomePage(BasePage):

    BRAND_FILTER_HEADING = (
        By.CSS_SELECTOR,
        "div._6odwB.UHMz4K",
    )
    BRAND_SEARCH_FIELD = (
        By.CSS_SELECTOR,
        "input.MocAag[placeholder='Search Brand']",
    )
    NOKIA_BRAND_OPTION = (
        By.XPATH,
        "//div[normalize-space()='Nokia']",
    )
    NOKIA_BRAND_CHECKBOX = (
        By.XPATH,
        "//div[normalize-space()='Nokia']"
        "/ancestor::div[.//div[contains(concat(' ', normalize-space(@class), ' '), "
        "' ybaCDx ')]]"
        "[1]//div[contains(concat(' ', normalize-space(@class), ' '), ' ybaCDx ')]",
    )
    SEARCH_RESULTS_READY = (
        By.XPATH,
        "//*[starts-with(normalize-space(), 'Showing 1') "
        "and contains(normalize-space(), 'results for')]",
    )

    SEARCH_BOX = (
        By.NAME,
        "q"
    )

    LOGIN_CLOSE_BUTTON = (
        By.XPATH,
        "//span[text()='✕']"
    )

    def open(self, url):

        self.driver.get(url)

    def close_login_popup_if_present(self):

        if self.is_element_present(
            self.LOGIN_CLOSE_BUTTON
        ):
            self.click(
                self.LOGIN_CLOSE_BUTTON
            )

    def search(self, keyword):

        search_box = self.wait.until(
            lambda driver:
            driver.find_element(*self.SEARCH_BOX)
        )

        search_box.clear()
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.ENTER)

    def select_nokia_brand_filter(self, timeout=15):
        """Select Nokia under the Brand filter on a search-results page."""
        wait = WebDriverWait(self.driver, timeout)
        wait.until(EC.visibility_of_element_located(self.SEARCH_RESULTS_READY))
        expanded_search_fields = [
            field
            for field in self.driver.find_elements(*self.BRAND_SEARCH_FIELD)
            if field.is_displayed()
        ]
        if not expanded_search_fields:
            wait.until(
                EC.element_to_be_clickable(self.BRAND_FILTER_HEADING)
            ).click()
        brand_search = wait.until(
            EC.visibility_of_element_located(self.BRAND_SEARCH_FIELD)
        )
        brand_search.clear()
        brand_search.send_keys("Nokia")

        wait.until(EC.visibility_of_element_located(self.NOKIA_BRAND_OPTION))
        result_summary = wait.until(
            EC.visibility_of_element_located(self.SEARCH_RESULTS_READY)
        )
        previous_summary = result_summary.text
        checkbox = wait.until(
            EC.element_to_be_clickable(self.NOKIA_BRAND_CHECKBOX)
        )
        checkbox.click()
        wait.until(
            lambda browser: browser.find_element(
                *self.SEARCH_RESULTS_READY
            ).text != previous_summary
        )
        self.logger.info("Applied the Nokia brand filter.")
