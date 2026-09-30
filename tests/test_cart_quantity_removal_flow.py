"""Data-driven cart quantity and removal checks using hybrid page objects."""

import pytest
from selenium.webdriver.support.ui import WebDriverWait

from config.settings import cart_test_data, environment_config
from pages.cart_page import CartPage
from pages.components.cart_summary_component import CartSummaryComponent
from pages.components.header_component import HeaderComponent
from pages.components.login_popup_component import LoginPopupComponent
from pages.product_page import ProductPage
from pages.search_results_page import SearchResultsPage
from utils.logger import get_logger


logger = get_logger(__name__)


@pytest.mark.regression
@pytest.mark.parametrize(
    "scenario",
    cart_test_data["cart_quantity_removal"],
    ids=lambda scenario: scenario["id"],
)
def test_increase_product_quantity_and_remove_from_cart(driver, scenario):
    """Increase a cart item to two, validate messages, then remove it."""
    header = HeaderComponent(driver)
    login_popup = LoginPopupComponent(driver)
    cart_summary = CartSummaryComponent(driver)
    search_results_page = SearchResultsPage(driver)
    product_page = ProductPage(driver)
    cart_page = CartPage(driver)

    base_url = environment_config["base_url"]
    keyword = scenario["keyword"]
    product_index = scenario["product_index"]
    expected_quantity = scenario["expected_quantity"]

    logger.info("Starting cart quantity and removal flow.")
    logger.info("Clearing cart so the test starts with exactly one product.")
    cart_page.clear_cart_items(base_url)

    logger.info("Opening Flipkart: %s", base_url)
    driver.get(base_url)
    logger.info("Closing the login popup when it is displayed.")
    login_popup.close_if_present()

    logger.info("Searching for product keyword: %s", keyword)
    header.search(keyword)
    product_name = search_results_page.get_product_name_by_index(product_index)
    logger.info("Selected product %s: %s", product_index, product_name)

    handles_before = driver.window_handles[:]
    logger.info("Opening selected product details.")
    search_results_page.click_product_by_index(product_index)
    WebDriverWait(driver, 10).until(
        lambda browser: len(browser.window_handles) > len(handles_before)
    )
    product_handle = next(
        handle for handle in driver.window_handles if handle not in handles_before
    )
    driver.switch_to.window(product_handle)
    logger.info("Switched to the product-details tab.")

    if product_page.is_add_to_cart_available():
        logger.info("Adding product using the standard Add to Cart control.")
        product_page.add_to_cart()
    else:
        logger.info("Adding product using the viewport-lazy Add 1 Item to Cart control.")
        product_page.add_one_item_to_cart()

    logger.info("Opening the cart to verify the product was added.")
    cart_page.open_cart(base_url)
    logger.info("Verifying the selected product is present in the cart.")
    cart_page.verify_product_in_cart(product_name)
    logger.info("Verifying the reusable cart summary component is visible.")
    cart_summary.wait_until_visible()

    logger.info("Increasing '%s' quantity using the Qty dropdown.", product_name)
    quantity = cart_page.set_quantity(expected_quantity)
    assert quantity == expected_quantity, (
        f"Expected quantity {expected_quantity} after increment, got {quantity}."
    )
    logger.info("Verified the product quantity is now %s.", quantity)

    logger.info("Verifying the quantity-change popup message.")
    cart_page.verify_quantity_change_message(product_name, quantity)

    logger.info("Clicking the Remove option.")
    cart_page.click_remove_option()
    logger.info("Verifying the remove confirmation dialog buttons.")
    cart_page.verify_remove_confirmation_dialog()

    logger.info("Clicking Remove in the confirmation dialog.")
    cart_page.confirm_remove()
    logger.info("Verifying the '%s' from your cart message.", product_name)
    cart_page.verify_removal_message(product_name)

    logger.info("Verifying the empty-cart screen message.")
    cart_page.verify_empty_cart_message()
    logger.info("Cart quantity and removal flow completed successfully.")
