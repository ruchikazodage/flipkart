import re
from urllib.parse import urljoin

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select

from pages.base_page import BasePage


class CartPage(BasePage):
    QUANTITY_DROPDOWN = (By.XPATH, "//select[option[normalize-space()='1']]")
    REMOVE_BUTTONS = (
        By.XPATH,
        "//*[self::button or @role='button'][normalize-space()='Remove']",
    )

    def open_cart(self, base_url):
        """Open the cart directly so pre-existing items can be removed."""
        cart_url = urljoin(base_url, "viewcart?exploreMode=true&preference=FLIPKART")
        self.driver.get(cart_url)
        WebDriverWait(self.driver, 20).until(
            lambda browser: browser.execute_script("return document.readyState") == "complete"
        )

    def is_empty(self):
        page_text = (self.driver.find_element(By.TAG_NAME, "body").text or "").lower()
        return "missing cart items" in page_text or "your cart is empty" in page_text

    def _visible_remove_buttons(self):
        return [
            button
            for button in self.driver.find_elements(*self.REMOVE_BUTTONS)
            if button.is_displayed() and button.is_enabled()
        ]

    def _wait_for_cart_state(self):
        """Wait for Flipkart's asynchronously rendered empty or populated cart."""
        WebDriverWait(self.driver, 15).until(
            lambda _: self.is_empty() or bool(self._visible_remove_buttons())
        )

    def _confirm_removal(self):
        """Confirm Flipkart's remove dialog when the cart uses one."""
        dialog_remove = (
            By.XPATH,
            "//*[(@role='dialog' or @aria-modal='true')]"
            "//*[self::button or @role='button'][normalize-space()='Remove']",
        )
        try:
            confirm_button = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable(dialog_remove)
            )
            confirm_button.click()
        except Exception:
            # Some cart versions remove the item immediately and show no dialog.
            pass

    def clear_cart_items(self, base_url):
        """Remove every existing cart item; do nothing when the cart is empty."""
        self.open_cart(base_url)
        self._wait_for_cart_state()

        if self.is_empty():
            self.logger.info("Cart is already empty; no cleanup is required.")
            return

        for _ in range(20):
            remove_buttons = self._visible_remove_buttons()
            if not remove_buttons:
                break

            remove_buttons[0].click()
            self._confirm_removal()

            try:
                WebDriverWait(self.driver, 5).until(
                    lambda _: self.is_empty()
                    or len(self._visible_remove_buttons()) < len(remove_buttons)
                )
            except Exception:
                # The next loop checks the page again and either continues or fails clearly.
                pass

            if self.is_empty():
                self.logger.info("Removed all existing cart items.")
                return

        assert self.is_empty(), "Unable to clear all existing cart items before the test."

    @staticmethod
    def _extract_amount(text):
        """Return a positive rupee amount from a cart summary line, if present."""
        match = re.search(r"(?:\u20b9|rs\.?)[\s]*([0-9][0-9,]*)", text, re.IGNORECASE)
        return int(match.group(1).replace(",", "")) if match else None

    def _summary_amount(self, label_pattern):
        """Find an amount in Flipkart's rendered price-summary text."""
        body_text = self.driver.find_element(By.TAG_NAME, "body").text or ""
        lines = [" ".join(line.split()) for line in body_text.splitlines() if line.strip()]

        for index in range(len(lines) - 1, -1, -1):
            if not re.search(label_pattern, lines[index], re.IGNORECASE):
                continue

            inline_amount = self._extract_amount(lines[index])
            if inline_amount is not None:
                return inline_amount

            for following_line in lines[index + 1:index + 4]:
                amount = self._extract_amount(following_line)
                if amount is not None:
                    return amount

        return None

    def get_price_breakdown(self):
        """Return the visible Price Details values used to calculate the payable total."""
        WebDriverWait(self.driver, 20).until(
            lambda _: self._summary_amount(r"^total amount$") is not None
        )

        breakdown = {
            "price": self._summary_amount(r"^price(?:\s*\([^)]*\))?$"),
            "discount": self._summary_amount(r"^discount$"),
            "platform_fee": self._summary_amount(r"^platform fee$"),
            "total_amount": self._summary_amount(r"^total amount$"),
        }
        missing = [name for name, amount in breakdown.items() if amount is None]
        assert not missing, f"Cart price details missing fields: {', '.join(missing)}"

        self.logger.info("Cart price breakdown: %s", breakdown)
        return breakdown

    def verify_product_in_cart(self, product_name):
        expected_name = " ".join(product_name.lower().split())
        WebDriverWait(self.driver, 15).until(
            lambda browser: expected_name
            in " ".join((browser.find_element(By.TAG_NAME, "body").text or "").lower().split())
        )

    def set_quantity(self, quantity):
        """Choose an item quantity from the cart's Qty dropdown."""
        native_dropdowns = self.driver.find_elements(*self.QUANTITY_DROPDOWN)
        if native_dropdowns:
            dropdown = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable(self.QUANTITY_DROPDOWN)
            )
            Select(dropdown).select_by_value(str(quantity))
            WebDriverWait(self.driver, 10).until(
                lambda _: Select(self.driver.find_element(*self.QUANTITY_DROPDOWN))
                .first_selected_option.text.strip() == str(quantity)
            )
            return int(quantity)

        dropdown_locator = (
            By.XPATH,
            "//*[self::button or @role='button' or self::div]"
            "[normalize-space()='Qty: 1']",
        )
        WebDriverWait(self.driver, 15).until(
            EC.element_to_be_clickable(dropdown_locator)
        ).click()
        option_locator = (
            By.XPATH,
            f"//*[self::button or @role='option' or self::div]"
            f"[normalize-space()='{quantity}']",
        )
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(option_locator)
        ).click()
        selected_locator = (
            By.XPATH,
            f"//*[self::button or @role='button' or self::div]"
            f"[normalize-space()='Qty: {quantity}']",
        )
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(selected_locator)
        )
        return int(quantity)

    def get_total_amount(self):
        return str(self.get_price_breakdown()["total_amount"])

    def remove_item(self):
        remove_buttons = self._visible_remove_buttons()
        assert remove_buttons, "No Remove button is available for the cart item."
        remove_buttons[0].click()
        self._confirm_removal()
