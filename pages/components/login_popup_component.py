"""Reusable login-popup behavior."""

from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class LoginPopupComponent(BasePage):
    CLOSE_BUTTON_LOCATORS = [
        (By.CSS_SELECTOR, "span._30XB9F"),
        (By.CSS_SELECTOR, "[aria-label='Close'], [aria-label='close'], [title='Close']"),
        (
            By.XPATH,
            "//*[self::button or @role='button' or self::span or self::div]"
            "[normalize-space()='\u00d7' or normalize-space()='\u2715' "
            "or normalize-space()='X']",
        ),
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
