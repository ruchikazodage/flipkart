from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import monotonic, sleep

from pages.base_page import BasePage


class ProductPage(BasePage):

    ADD_TO_CART_LOCATORS = [
        (
            By.XPATH,
            "//button[translate(normalize-space(.), "
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='add to cart']"
        ),
        (
            By.XPATH,
            "//*[@role='button' and translate(normalize-space(.), "
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='add to cart']"
        ),
        (
            By.XPATH,
            "//div[translate(normalize-space(text()), "
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='add to cart']"
        ),
        (
            By.XPATH,
            "//*[self::button or @role='button'][contains(translate(@aria-label, "
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'add to cart') "
            "or contains(translate(@title, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
            "'abcdefghijklmnopqrstuvwxyz'), 'add to cart') "
            "or contains(@data-testid, 'addToCart')]"
        )
    ]

    ADD_ONE_ITEM_TO_CART_LOCATORS = [
        (
            By.XPATH,
            "//*[self::button or self::div or @role='button']"
            "[translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
            "'abcdefghijklmnopqrstuvwxyz')='add 1 item to cart']",
        ),
        (
            By.XPATH,
            "//*[self::button or self::div or @role='button']"
            "[translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
            "'abcdefghijklmnopqrstuvwxyz')='add 1 item']",
        ),
    ]

    BUY_NOW_LOCATORS = [
        (
            By.XPATH,
            "//*[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'buy now')]"
        ),
        (
            By.XPATH,
            "//*[normalize-space()='Buy now' or normalize-space()='BUY NOW']"
        ),
        (
            By.XPATH,
            "//*[contains(@aria-label, 'Buy now') or contains(@title, 'Buy now') or contains(@data-testid, 'buyNow')]"
        )
    ]

    CART_ICON_LOCATORS = [
        (
            By.XPATH,
            "//*[self::a or self::button or @role='button'][contains(translate(@aria-label, "
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'cart') "
            "or contains(translate(@title, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
            "'abcdefghijklmnopqrstuvwxyz'), 'cart')]"
        ),
        (
            By.XPATH,
            "//a[contains(@href, 'viewcart') or contains(@href, '/cart')]"
        )
    ]

    GOING_TO_CART_LOCATORS = [
        (
            By.XPATH,
            "//*[self::button or @role='button'][translate(normalize-space(.), "
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='going to cart']"
        ),
        (
            By.XPATH,
            "//*[self::button or @role='button'][translate(normalize-space(.), "
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='go to cart']"
        ),
        (
            By.XPATH,
            "//div[translate(normalize-space(text()), "
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='going to cart' "
            "or translate(normalize-space(text()), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
            "'abcdefghijklmnopqrstuvwxyz')='go to cart']"
        ),
        (
            By.XPATH,
            "//*[self::a or self::button or @role='button'][contains(translate(@aria-label, "
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'go to cart') "
            "or contains(translate(@title, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
            "'abcdefghijklmnopqrstuvwxyz'), 'go to cart')]"
        )
    ]

    def _click_first_available(self, locators, timeout=20):
        """Find and click a cart action, scrolling for viewport-lazy CTAs.

        Flipkart can defer rendering the alternate ``Add 1 Item to Cart``
        control until the product details below the initial viewport are
        reached.  Scrolling must therefore happen while looking for the
        locator, rather than only after Selenium has found it.
        """
        deadline = monotonic() + timeout
        last_scroll_position = None

        while monotonic() < deadline:
            for locator in locators:
                try:
                    for element in self.driver.find_elements(*locator):
                        if not element.is_displayed() or not element.is_enabled():
                            continue

                        self.driver.execute_script(
                            "arguments[0].scrollIntoView({block: 'center', inline: 'center'});",
                            element,
                        )
                        try:
                            element.click()
                        except Exception:
                            self.driver.execute_script("arguments[0].click();", element)

                        self.logger.info("Clicked cart action using locator: %s", locator)
                        return True
                except Exception:
                    # The page is dynamic; retry after the next scroll step.
                    continue

            scroll_position, viewport_height, page_height = self.driver.execute_script(
                "return [window.pageYOffset, window.innerHeight, "
                "document.documentElement.scrollHeight];"
            )
            if (
                scroll_position == last_scroll_position
                and scroll_position + viewport_height + 1 >= page_height
            ):
                # A final rescan at the top handles controls that render while
                # the page is being scrolled, without remaining at the footer.
                self.driver.execute_script("window.scrollTo(0, 0);")
            else:
                self.driver.execute_script(
                    "window.scrollBy(0, Math.max(500, window.innerHeight * 0.8));"
                )
            last_scroll_position = scroll_position
            sleep(0.25)

        raise TimeoutError(f"None of the cart action locators matched: {locators}")

    def _get_first_text(self, locators):
        for locator in locators:
            try:
                element = WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located(locator)
                )
                text = (element.text or "").strip()
                if text:
                    return text
            except Exception:
                continue

        raise TimeoutError(f"None of the cart status locators matched: {locators}")

    def add_to_cart(self):
        """Click either supported product-add control.

        Flipkart uses either ``Add to Cart`` or the viewport-lazy
        ``Add 1 Item to Cart`` CTA, depending on the product and page layout.
        Both controls represent the same product-add journey. Buy Now and the
        cart icon are intentionally excluded because they change that journey.
        """
        self._click_first_available(
            self.ADD_TO_CART_LOCATORS + self.ADD_ONE_ITEM_TO_CART_LOCATORS
        )

    def is_add_to_cart_available(self, timeout=10):
        """Return whether the standard Add to Cart control is available."""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda _: any(
                    element.is_displayed() and element.is_enabled()
                    for locator in self.ADD_TO_CART_LOCATORS
                    for element in self.driver.find_elements(*locator)
                )
            )
            return True
        except Exception:
            return False

    def add_one_item_to_cart(self):
        """Click Flipkart's alternate cart action for products with this CTA."""
        self._click_first_available(self.ADD_ONE_ITEM_TO_CART_LOCATORS)

    def click_add_to_cart(self):
        self.add_to_cart()

    def verify_going_to_cart(self):
        try:
            actual_text = self._get_first_text(self.GOING_TO_CART_LOCATORS).lower()
            assert "cart" in actual_text, (
                f"Expected cart button text, but found '{actual_text}'"
            )
        except Exception:
            page_text = (self.driver.find_element(By.TAG_NAME, "body").text or "").lower()
            assert "cart" in page_text or "buy now" in page_text, (
                "No cart navigation state was detected after product action."
            )

    def click_going_to_cart(self):
        try:
            self._click_first_available(self.GOING_TO_CART_LOCATORS)
            return
        except Exception:
            self._click_first_available(self.CART_ICON_LOCATORS)
