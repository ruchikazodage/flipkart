from selenium.webdriver.support.ui import WebDriverWait

from config.settings import environment_config, test_data
from pages.home_page import HomePage
from pages.search_results_page import SearchResultsPage
from pages.product_page import ProductPage
from pages.cart_page import CartPage
from utils.logger import get_logger

import re
import time

logger = get_logger(__name__)


def _parse_price(text: str) -> int:
    if not text:
        return 0
    # Remove non-digit characters
    digits = re.sub(r"[^0-9]", "", text)
    return int(digits) if digits else 0


def test_add_10th_product_to_cart_and_verify_flow(driver):
    """
    Full flow:
    - Clear any existing cart items, then search for the keyword
    - From results take 10th product: capture name and price
    - Open product, Add to cart, verify 'Going to cart'
    - Go to cart, verify the product and its price/discount/platform-fee calculation
    - Increase qty to 2, verify quantity changed and confirmation appears
    - Remove item and verify removal confirmation and empty-cart message
    """

    home_page = HomePage(driver)
    search_results_page = SearchResultsPage(driver)
    product_page = ProductPage(driver)
    cart_page = CartPage(driver)

    base_url = environment_config["base_url"]
    keyword = test_data["search"]["keyword"]

    # Start from an empty cart so previous runs do not affect the total.
    cart_page.clear_cart_items(base_url)

    # Open site and search
    home_page.open(base_url)
    home_page.close_login_popup_if_present()
    home_page.search(keyword)

    product_index = 10

    # Capture the product's selling price from the search results.
    product_name = search_results_page.get_product_name_by_index(product_index)
    product_price_text = search_results_page.get_product_price_by_index(product_index)
    product_price = _parse_price(product_price_text)

    logger.info("10th product name: %s", product_name)
    logger.info("10th product selling price: %s -> %s", product_price_text, product_price)

    # Click product (may open new tab)
    handles_before = driver.window_handles[:]
    search_results_page.click_product_by_index(product_index)

    # If new window opened, switch
    time.sleep(1)
    handles_after = driver.window_handles
    if len(handles_after) > len(handles_before):
        new = [h for h in handles_after if h not in handles_before][0]
        driver.switch_to.window(new)

    # Lower-priced products commonly expose Add to Cart directly. Some
    # higher-priced/EMI product layouts expose the lower-page Add 1 Item to
    # Cart CTA instead, so select the applicable product-add journey.
    if product_page.is_add_to_cart_available():
        logger.info("Using standard Add to Cart action.")
        product_page.click_add_to_cart()
    else:
        logger.info("Using alternate Add 1 Item to Cart action.")
        product_page.add_one_item_to_cart()

    # Verify button changed after the applicable add-to-cart action.
    product_page.verify_going_to_cart()

    # Click Going to Cart to go to cart page
    product_page.click_going_to_cart()

    # Verify the selected product and compare the selling price plus platform fee
    # with the cart's Total Amount.
    cart_page.verify_product_in_cart(product_name)
    price_breakdown = cart_page.get_price_breakdown()
    platform_fee = price_breakdown["platform_fee"]
    expected_total = product_price + platform_fee
    cart_total = price_breakdown["total_amount"]

    logger.info(
        "Product selling price: %s | Platform fee: %s | "
        "Expected total: %s | Cart total: %s",
        product_price,
        platform_fee,
        expected_total,
        cart_total,
    )
    assert price_breakdown["price"] - price_breakdown["discount"] == product_price, (
        "Cart selling price does not match the search-results selling price.\n"
        f"Cart price: {price_breakdown['price']}\n"
        f"Cart discount: {price_breakdown['discount']}\n"
        f"Search-results selling price: {product_price}"
    )
    assert cart_total == expected_total, (
        "Cart Total Amount does not match selling price plus platform fee.\n"
        f"Product selling price: {product_price}\n"
        f"Platform fee: {platform_fee}\n"
        f"Expected Total Amount: {expected_total}\n"
        f"Cart Total Amount: {cart_total}"
    )

    # Flipkart presents quantity as a Qty dropdown, not a plus button.
    cart_page.set_quantity(2)

    # Remove the product; CartPage also confirms the dialog when Flipkart shows one.
    cart_page.remove_item()

    WebDriverWait(driver, 10).until(lambda _: cart_page.is_empty())
