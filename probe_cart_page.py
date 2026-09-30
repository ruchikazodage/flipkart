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
        d.find_element(By.XPATH, "//span[text()='✕']").click()
    except Exception:
        pass
    s = d.find_element(By.NAME, 'q')
    s.send_keys('mobile')
    s.send_keys(Keys.ENTER)
    time.sleep(6)
    cards = d.find_elements(By.CSS_SELECTOR, 'a.k7wcnx')
    print('CARD_COUNT', len(cards))
    if len(cards) >= 10:
        d.execute_script('arguments[0].click();', cards[9])
        time.sleep(4)
        if len(d.window_handles) > 1:
            d.switch_to.window(d.window_handles[-1])
        print('URL', d.current_url)
        print('TITLE', d.title)
        print('BODY_START')
        page_text = (d.find_element(By.TAG_NAME, 'body').text or '').strip()
        print(page_text[:4000])
        print('BODY_END')
        print('BUTTONS')
        for b in d.find_elements(By.TAG_NAME, 'button'):
            txt = (b.text or '').strip()
            if txt:
                print('BUTTON:', repr(txt))
        print('LINKS')
        for a in d.find_elements(By.TAG_NAME, 'a'):
            txt = (a.text or '').strip()
            if txt:
                print('LINK:', repr(txt))
finally:
    d.quit()
