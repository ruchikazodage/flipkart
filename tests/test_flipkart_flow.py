import re

from config.settings import environment_config, test_data
from selenium.webdriver.support.ui import WebDriverWait

from pages.home_page import HomePage
from pages.search_results_page import SearchResultsPage
from pages.comparison_page import ComparisonPage
from pages.product_page import ProductPage
from pages.cart_page import CartPage
from utils.logger import get_logger

logger = get_logger(__name__)


def test_verify_mobile_search_result_message(driver):

    base_url = environment_config["base_url"]
    keyword = test_data["search"]["keyword"]

    home_page = HomePage(driver)
    search_results_page = SearchResultsPage(driver)
    

    # Step 1: Open Flipkart
    home_page.open(base_url)

    # Step 2: Close login popup if displayed
    home_page.close_login_popup_if_present()

    # Step 3: Search for mobile
    home_page.search(keyword)

    # Step 4: Verify search result message
    actual_message = (
        search_results_page
        .verify_search_result_message(keyword)
    )

    logger.info(
        "TEST CASE: test_verify_mobile_search_result_message | "
        "VERIFIED SEARCH RESULTS: %s",
        actual_message,
    )


def test_verify_compare_10th_and_11th_mobile(driver):

    home_page = HomePage(driver)
    search_results_page = SearchResultsPage(driver)
    comparison_page = ComparisonPage(driver)

    # Open Flipkart
    home_page.open(
        environment_config["base_url"]
    )

    # Close login popup if displayed
    home_page.close_login_popup_if_present()

    # Get test data
    keyword = test_data["search"]["keyword"]
    compare_indices = test_data["search"]["compare_indices"]

    # Search for mobile
    home_page.search(keyword)

    # Select products and capture their names
    selected_product_names = []

    for index in compare_indices:

        product_name = (
            search_results_page
            .select_compare_checkbox(index)
        )

        selected_product_names.append(product_name)

    # Verify compare tray
    search_results_page.verify_compare_tray_items(
    selected_product_names
    )

    # Open comparison page
    search_results_page.click_compare_button()

    # Verify selected products on comparison page
    actual_product_names = (
    comparison_page.verify_product_names_for_flipkart(
        selected_product_names
    )
)

    print("\nSelected products:")

    for product_name in selected_product_names:
        print(f"  - {product_name}")

    print("\nComparison page products:")

    for product_name in actual_product_names:
        print(f"  - {product_name}")


def test_verify_product_add_to_cart_and_total_amount(driver):

    home_page = HomePage(driver)
    search_results_page = SearchResultsPage(driver)
    product_page = ProductPage(driver)
    cart_page = CartPage(driver)
    base_url = environment_config["base_url"]

    # Ensure previous executions do not affect the product and total assertions.
    cart_page.clear_cart_items(base_url)

    # Open Flipkart
    home_page.open(base_url)

    # Close login popup if displayed
    home_page.close_login_popup_if_present()

    # Get search keyword
    keyword = test_data["search"]["keyword"]

    # Search for mobile
    home_page.search(keyword)

    # Get 10th product details
    product_index = 10

    product_name = (
        search_results_page
        .get_product_name_by_index(product_index)
    )

    product_price = (
        search_results_page
        .get_product_price_by_index(product_index)
    )
    product_price_digits = re.sub(r"[^0-9]", "", product_price)
    assert product_price_digits, (
        f"Could not extract a numeric amount from product price: {product_price}"
    )
    product_price_amount = int(product_price_digits)

    print(f"\n10th Product: {product_name}")
    print(f"Product List Price: {product_price}")

    # Click 10th phone name
    handles_before = driver.window_handles[:]
    search_results_page.click_product_by_index(
        product_index
    )

    # Product pages open in a new tab on Flipkart; switch before looking for
    # product-page controls such as Add to Cart.
    WebDriverWait(driver, 10).until(
        lambda browser: len(browser.window_handles) > len(handles_before)
    )
    product_handle = next(
        handle
        for handle in driver.window_handles
        if handle not in handles_before
    )
    driver.switch_to.window(product_handle)

    # Some product pages use an alternate "Add 1 Item to Cart" action.
    if product_page.is_add_to_cart_available():
        logger.info("Using standard Add to Cart action.")
        product_page.click_add_to_cart()
    else:
        logger.info("Using alternate Add 1 Item to Cart action.")
        product_page.add_one_item_to_cart()

    # Verify Add to Cart changed to Going to Cart
    product_page.verify_going_to_cart()

    # Verify item is added to cart
    product_page.click_going_to_cart()

    cart_page.verify_product_in_cart(
        product_name
    )

    # The list-page price is the selling price. Include the platform fee only
    # when Flipkart applies a non-zero fee to the cart.
    platform_fee_labels = [
        label
        for label in driver.find_elements(*cart_page.PLATFORM_FEE_LABEL)
        if label.is_displayed()
    ]
    platform_fee = (
        cart_page._amount_for_label(cart_page.PLATFORM_FEE_LABEL, "Platform Fee")
        if platform_fee_labels
        else 0
    )
    expected_total_amount = product_price_amount + platform_fee
    cart_total = cart_page._amount_for_label(
        cart_page.TOTAL_AMOUNT_LABEL,
        "Total Amount",
    )

    logger.info(
        "Product price: %s | Platform fee: %s | Expected total: %s | Cart total: %s",
        product_price_amount,
        platform_fee,
        expected_total_amount,
        cart_total,
    )

    assert cart_total == expected_total_amount, (
        f"Total Amount mismatch.\n"
        f"Product list price: {product_price_amount}\n"
        f"Platform fee: {platform_fee}\n"
        f"Expected Total Amount: {expected_total_amount}\n"
        f"Cart Total Amount: {cart_total}"
    )
