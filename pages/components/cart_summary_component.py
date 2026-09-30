"""Reusable cart-summary region assertions."""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage


class CartSummaryComponent(BasePage):
    PRICE_LABEL = (By.XPATH, "//div[starts-with(normalize-space(.), 'Price (')]")
    TOTAL_AMOUNT_LABEL = (
        By.XPATH,
        "//*[self::div or self::span][normalize-space()='Total Amount']",
    )

    def wait_until_visible(self, timeout=20):
        """Wait until the cart's price summary is rendered."""
        WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(self.PRICE_LABEL)
        )
        WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(self.TOTAL_AMOUNT_LABEL)
        )
        self.logger.info("Cart summary is visible.")
