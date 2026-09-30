"""Reusable login-popup behavior."""

from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class LoginPopupComponent(BasePage):
    CLOSE_BUTTON_LOCATORS = [
        (By.XPATH, "//*[self::button or self::span][normalize-space()='✕']"),
        (By.XPATH, "//*[self::button or self::span][normalize-space()='×']"),
    ]

    def close_if_present(self):
        """Close the optional login popup without failing when it is absent."""
        for locator in self.CLOSE_BUTTON_LOCATORS:
            for button in self.driver.find_elements(*locator):
                if button.is_displayed() and button.is_enabled():
                    try:
                        button.click()
                    except Exception:
                        self.driver.execute_script("arguments[0].click();", button)
                    self.logger.info("Closed the login popup.")
                    return True

        self.logger.info("Login popup was not displayed.")
        return False
