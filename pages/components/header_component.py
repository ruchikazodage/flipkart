"""Reusable header controls shared across Flipkart pages."""

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from pages.base_page import BasePage


class HeaderComponent(BasePage):
    SEARCH_BOX = (By.NAME, "q")

    def search(self, keyword):
        """Search from the global Flipkart header."""
        search_box = self.wait.until(
            lambda browser: browser.find_element(*self.SEARCH_BOX)
        )
        search_box.clear()
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.ENTER)
        self.logger.info("Searched from header for: %s", keyword)
