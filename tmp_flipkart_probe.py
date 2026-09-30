from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time

options = webdriver.ChromeOptions()
options.add_argument('--disable-notifications')
options.add_argument('--disable-popup-blocking')
options.add_argument('--start-maximized')

d = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
try:
    d.get('https://www.flipkart.com')
    time.sleep(2)
    try:
        close = d.find_element(By.XPATH, "//span[text()='✕']")
        close.click()
        time.sleep(1)
    except Exception:
        pass

    s = d.find_element(By.NAME, 'q')
    s.send_keys('mobile')
    s.send_keys(Keys.ENTER)
    time.sleep(6)

    cards = d.find_elements(By.CSS_SELECTOR, 'a.k7wcnx')
    print('cards', len(cards))
    if len(cards) >= 10:
        prod = cards[9]
        d.execute_script('arguments[0].click();', prod)
        time.sleep(4)
        if len(d.window_handles) > 1:
            d.switch_to.window(d.window_handles[-1])
        print('current_url', d.current_url)
        print('title', d.title)
        for xp in [
            "//button[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'add to cart')]",
            "//button[contains(text(),'Add to cart')]",
            "//*[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'buy now')]",
            "//*[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'go to cart')]",
            "//button",
            "//*[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'cart')]",
        ]:
            els = d.find_elements(By.XPATH, xp)
            print('XP', xp, 'count=', len(els))
            for i, el in enumerate(els[:20]):
                txt = (el.text or '').strip()
                if txt:
                    print(' ', i, repr(txt[:120]))
        print('body contains add to cart', 'add to cart' in d.page_source.lower())
        print('body contains go to cart', 'go to cart' in d.page_source.lower())
finally:
    d.quit()
