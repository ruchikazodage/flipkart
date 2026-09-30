from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from utils.logger import get_logger


logger = get_logger(__name__)


class ComparisonPage:

    def __init__(self, driver):
        self.driver = driver

        # Keep an optional explicit locator if someone sets it later.
        self.comparison_product_names = (
            By.CSS_SELECTOR,
            "YOUR_PRODUCT_NAME_LOCATOR"
        )

    def _is_candidate_title(self, text: str) -> bool:
        if not text:
            return False
        t = text.strip()
        if len(t) < 5 or len(t) > 120:
            return False
        # must contain at least one space (multi-word product names)
        if " " not in t:
            return False
        # exclude obvious page chrome words
        exclude_words = [
            "ratings", "reviews", "price", "off", "bank", "offer",
            "sort", "relevance", "results", "add to compare", "compare"
        ]
        low = t.lower()
        for w in exclude_words:
            if w in low:
                return False
        # require at least one alpha character
        if not any(ch.isalpha() for ch in t):
            return False
        return True

    def get_product_names(self, timeout=6):
        """
        Dynamically discover product names on the comparison page using
        multiple heuristics and a short wait for the page to render.
        """

        # Poll for up to `timeout` seconds, attempting discovery each iteration.
        end = time.time() + timeout

        # 1) If an explicit locator has been updated from the placeholder,
        # try it first (quick path).
        locator_value = self.comparison_product_names[1]
        if locator_value and "YOUR_PRODUCT_NAME_LOCATOR" not in locator_value:
            try:
                WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_all_elements_located(self.comparison_product_names)
                )
                elems = self.driver.find_elements(*self.comparison_product_names)
                names = [e.text.strip() for e in elems if e.text.strip()]
                if names:
                    logger.info("Products displayed on comparison page (by explicit locator): %s", names)
                    return names
            except TimeoutException:
                pass

        # 2) Look for containers with 'compare' or 'comparison' in id/class
        try:
            containers = self.driver.find_elements(By.XPATH,
                "//*[contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'compare') or contains(translate(@id,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'compare') or contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'comparison') or contains(translate(@id,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'comparison')]")
        except Exception:
            containers = []

        # Repeatedly attempt discovery until timeout
        while time.time() < end:
            found = []
            for c in containers:
                try:
                    cand = c.find_elements(By.XPATH, ".//h1|.//h2|.//h3|.//h4|.//div|.//span|.//a")
                except Exception:
                    cand = []
                for el in cand:
                    txt = el.text.strip()
                    if self._is_candidate_title(txt) and txt not in found:
                        found.append(txt)
                if len(found) >= 2:
                    logger.info("Products displayed on comparison page (in compare containers): %s", found)
                    return found

            # 3) Broad scan: look at headline and link elements across the page
            try:
                candidates = self.driver.find_elements(By.XPATH, "//h1|//h2|//h3|//h4|//a|//div|//span")
            except Exception:
                candidates = []

            for el in candidates:
                try:
                    txt = el.text.strip()
                except Exception:
                    txt = ""
                if self._is_candidate_title(txt) and txt not in found:
                    found.append(txt)
                if len(found) >= 2:
                    logger.info("Products displayed on comparison page (broad scan): %s", found)
                    return found

            # small pause before next attempt
            time.sleep(0.5)

        # 4) Timeout reached: return whatever was found (possibly empty)
        logger.info("Products displayed on comparison page (after polling): %s", found)
        return found

    def verify_product_names(self, expected_product_names):
        """
        Verifies that all selected products are present
        on the comparison page.
        """

        actual_product_names = self.get_product_names()

        found = set(name.strip().lower() for name in actual_product_names)
        missing = []

        for expected in expected_product_names:
            expected_norm = expected.strip().lower()
            if expected_norm in found:
                continue

            xpath = (
                "//*[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '"
                + expected_norm.replace("'", "")
                + "')]"
            )

            try:
                elems = self.driver.find_elements(By.XPATH, xpath)
            except Exception:
                elems = []

            if elems:
                txt = elems[0].text.strip()
                if txt:
                    found.add(txt.lower())
            else:
                missing.append(expected)

        if missing:
            logger.error(
                "Comparison verification failed. Missing products: %s",
                missing
            )
            raise AssertionError(
                "Selected product(s) not found on comparison page: "
                f"{set(missing)}"
            )

        logger.info(
            "Comparison verification successful. All selected products are present on comparison page."
        )

        return list(found)

    def verify_product_names_for_flipkart(self, expected_product_names):
        """Verifies product names on the Flipkart comparison page using the actual product-name locator."""

        product_locator = (
            By.CSS_SELECTOR,
            "a._vlotY"
        )

        products = WebDriverWait(
            self.driver,
            20
        ).until(
            EC.visibility_of_all_elements_located(
                product_locator
            )
        )

        actual_product_names = [
            product.text.strip()
            for product in products
            if product.text.strip()
        ]

        logger.info(
            "Flipkart comparison products: %s",
            actual_product_names
        )

        for expected_name in expected_product_names:
            assert expected_name in actual_product_names, (
                f"Product '{expected_name}' was not found "
                f"on comparison page. "
                f"Actual products: {actual_product_names}"
            )

        logger.info(
            "Flipkart comparison verification successful."
        )
        return actual_product_names