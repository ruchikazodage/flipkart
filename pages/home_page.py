from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from pages.base_page import BasePage


class HomePage(BasePage):

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