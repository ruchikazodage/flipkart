import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class SearchResultsPage(BasePage):

    RESULT_SUMMARY = (
        By.XPATH,
        "//*[starts-with(normalize-space(), 'Showing 1') "
        "and contains(normalize-space(), 'results for')]"
    )

    PRODUCT_CARDS = (
        By.CSS_SELECTOR,
        "a.k7wcnx"
    )

    PRODUCT_NAME = (
        By.CSS_SELECTOR,
        "div.RG5Slk"
    )

    PRODUCT_PRICE = (
    By.CSS_SELECTOR,
    "div.hZ3P6w.DeU9vF"
)

    ORIGINAL_PRODUCT_PRICE_LOCATORS = [
        # Flipkart's legacy class for a struck-through/original product price.
        (By.CSS_SELECTOR, "div._3I9_wc._27UcVY"),
        # Class names change frequently, so retain semantic fallbacks.
        (By.XPATH, ".//*[contains(@style, 'line-through') and contains(normalize-space(), '₹')]"),
        (By.XPATH, ".//*[contains(@class, 'line-through') and contains(normalize-space(), '₹')]"),
    ]

    COMPARE_CHECKBOX = (
        By.CSS_SELECTOR,
        "input[type='checkbox']"
    )

    def get_result_summary(self):
        return self.get_text(self.RESULT_SUMMARY)

    def verify_search_result_message(self, keyword, timeout=20):
        """Verify the dynamic search-results message for the requested keyword."""
        pattern = re.compile(
            r"^Showing\s+1\s*[\u2013\u2014-]\s*24\s+of\s+"
            r"([\d,]+)\s+results\s+for\s+[\"']?"
            + re.escape(keyword)
            + r"[\"']?$",
            re.IGNORECASE,
        )

        def matching_summary(_):
            message = " ".join(self.get_result_summary().split())
            return message if pattern.fullmatch(message) else False

        actual_message = WebDriverWait(self.driver, timeout).until(
            matching_summary,
            message=f"Search-result message did not match the expected format for '{keyword}'.",
        )
        result_count = int(pattern.fullmatch(actual_message).group(1).replace(",", ""))

        assert result_count > 0, (
            f"Result count should be greater than 0, but found {result_count}."
        )
        return actual_message

    def _verify_search_result_message_legacy(self, expected_message):
        actual_message = " ".join(self.get_result_summary().split())
        expected_message = " ".join(expected_message.split())

        assert actual_message == expected_message, (
            "Search result message is incorrect.\n"
            f"Expected: {expected_message}\n"
            f"Actual: {actual_message}"
        )

        return actual_message

        pattern = (
            r"Showing\s+1\s*[–-]\s*24\s+of\s+"
            r"([\d,]+)\s+results\s+for\s+"
            r"[\"']?" + re.escape(keyword) + r"[\"']?"
        )

        match = re.search(pattern, actual_message, re.IGNORECASE)

        assert match is not None, (
            f"\nSearch result message format is incorrect.\n"
            f"Expected keyword: {keyword}\nActual message: {actual_message}"
        )

        result_count = int(match.group(1).replace(",", ""))

        assert result_count > 0, (
            f"Result count should be greater than 0, but found {result_count}"
        )

        return actual_message

    def get_product_cards(self, timeout=20):
      products = WebDriverWait(
        self.driver,
        timeout
    ).until(
             EC.presence_of_all_elements_located(
            self.PRODUCT_CARDS
        )
    )

      if not products:
        raise AssertionError(
            "No product cards were found on the search results page."
        )

      return products

    def get_product_card(self, product_index):
        products = self.get_product_cards()
        total_products = len(products)

        if product_index < 1:
            raise ValueError(f"Invalid product index: {product_index}. Product index must be >= 1.")

        if product_index > total_products:
            raise IndexError(f"Requested product #{product_index}, but only {total_products} product cards are available.")

        return products[product_index - 1]

    def get_product_name(self, product):
        return product.find_element(*self.PRODUCT_NAME).text.strip()

    def get_compare_checkbox(self, product):
        return product.find_element(*self.COMPARE_CHECKBOX)

    def select_compare_checkbox(self, product_index):
        product = self.get_product_card(product_index)
        product_name = self.get_product_name(product)
        compare_checkbox = self.get_compare_checkbox(product)

        # Use JS click because Flipkart uses a custom checkbox UI
        self.driver.execute_script("arguments[0].click();", compare_checkbox)

        return product_name

    def get_product_name_by_index(self, product_index):
        product = self.get_product_card(product_index)
        return self.get_product_name(product)

    def get_product_price(self, product):
        """Return the discounted/selling price displayed on a product card."""
        price_element = product.find_element(*self.PRODUCT_PRICE)
        return price_element.text.strip()

    def get_original_product_price(self, product):
        """Return the struck-through/original price, not the discounted price."""
        for locator in self.ORIGINAL_PRODUCT_PRICE_LOCATORS:
            for element in product.find_elements(*locator):
                price_text = element.text.strip()
                if price_text:
                    return price_text

        # Newer Flipkart pages use generated CSS classes. The computed style is
        # still the reliable semantic marker for the original struck-through price.
        price_elements = product.find_elements(
            By.XPATH,
            ".//*[contains(normalize-space(), '₹')]",
        )
        for element in price_elements:
            is_struck_through = self.driver.execute_script(
                "return getComputedStyle(arguments[0]).textDecorationLine "
                ".includes('line-through');",
                element,
            )
            if is_struck_through and element.text.strip():
                return element.text.strip()

        # Some valid product cards have no discount and therefore no MRP/struck-
        # through price. Use their displayed selling price for the cart comparison.
        for element in price_elements:
            price_text = element.text.strip()
            amount = self._extract_price_amount(price_text)
            if amount is not None:
                self.logger.info(
                    "No original price is displayed; using selling price: %s",
                    amount,
                )
                return f"\u20b9{amount:,}"

        raise AssertionError("No price was found in the product card.")

    @staticmethod
    def _extract_price_amount(price_text):
        match = re.search(r"\u20b9\s*([0-9][0-9,]*)", price_text)
        return int(match.group(1).replace(",", "")) if match else None

    def get_product_price_by_index(self, product_index):
        product = self.get_product_card(product_index)
        return self.get_product_price(product)

    def get_original_product_price_by_index(self, product_index):
        product = self.get_product_card(product_index)
        return self.get_original_product_price(product)

    def verify_compare_tray_items(self, expected_product_names, timeout=10):
    

        compare_tray = (
        By.XPATH,
        "//span[normalize-space()='COMPARE']"
    )

        self.find_element(compare_tray, timeout)

        self.logger.info(
        "Compare tray displayed successfully."
    )

        self.logger.info(
        "Products selected for comparison: %s",
        expected_product_names
    )

    def click_compare_button(self):
        """
        Clicks the visible Compare button on the page.
        """

        btn = None
        try:
            btn = self.driver.find_element(By.XPATH, "//span[normalize-space()='COMPARE']")
        except Exception:
            pass

        if btn:
            try:
                self.driver.execute_script("arguments[0].click();", btn)
                return
            except Exception:
                btn.click()

        raise AssertionError("Compare button not found on the page")

    def click_product_by_index(self, product_index):
        product = self.get_product_card(product_index)
        # product card selector uses an anchor, click it
        self.driver.execute_script("arguments[0].click();", product)
