import re

from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class SearchResultsPage(BasePage):

    RESULT_SUMMARY = (
        By.XPATH,
        "//*[contains(normalize-space(), 'results for')]"
    )

    def get_result_summary(self):

        return self.get_text(
            self.RESULT_SUMMARY
        )

    def verify_search_result_message(self, keyword):

        actual_message = self.get_result_summary()

        print(
            f"\nActual search result message: "
            f"{actual_message}"
        )

        pattern = (
            r"Showing\s+1\s*[–-]\s*24\s+of\s+"
            r"([\d,]+)\s+results\s+for\s+"
            r"[\"']?"
            + re.escape(keyword)
            + r"[\"']?"
        )

        match = re.search(
            pattern,
            actual_message,
            re.IGNORECASE
        )

        assert match is not None, (
            f"\nSearch result message format "
            f"is incorrect.\n"
            f"Expected keyword: {keyword}\n"
            f"Actual message: {actual_message}"
        )

        result_count = int(
            match.group(1).replace(",", "")
        )

        assert result_count > 0, (
            f"Result count should be greater than 0, "
            f"but found {result_count}"
        )

        return actual_message

    def select_compare_checkbox(self, product_index):
        """
        Select compare checkbox for the product at the given
        1-based position and return the product name.
        """

        product = self.get_product_card(product_index)

        product_name = self.get_product_name(product)

        compare_checkbox = self.get_compare_checkbox(product)

        compare_checkbox.click()

        return product_name