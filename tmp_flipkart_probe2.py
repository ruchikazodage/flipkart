from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time, re

out = []

def log(msg):
    out.append(str(msg))

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
        close.click(); time.sleep(1)
    except Exception:
        pass

    s = d.find_element(By.NAME, 'q')
    s.send_keys('mobile'); s.send_keys(Keys.ENTER)
    time.sleep(6)
    cards = d.find_elements(By.CSS_SELECTOR, 'a.k7wcnx')
    log(f'cards={len(cards)}')
    if len(cards) >= 10:
        prod = cards[9]
        d.execute_script('arguments[0].click();', prod)
        time.sleep(4)
        if len(d.window_handles) > 1:
            d.switch_to.window(d.window_handles[-1])
        log('current_url=' + d.current_url)
        log('title=' + d.title)
        # collect visible button/link texts
        texts = []
        for tag in ['button', 'a', 'span', 'div']:
            for el in d.find_elements(By.TAG_NAME, tag):
                txt = (el.text or '').strip()
                if txt and len(txt) < 120:
                    texts.append(txt)
        uniq = []
        seen = set()
        for txt in texts:
            if txt not in seen:
                uniq.append(txt)
                seen.add(txt)
        log('VISIBLE_TEXT_COUNT=' + str(len(uniq)))
        for txt in uniq[:200]:
            if any(k in txt.lower() for k in ['cart','buy','add','mobile','iphone','save','go to']):
                log('TEXT=' + txt)
        body_text = d.execute_script("return document.body.innerText || ''")
        for kw in ['Add to cart', 'Buy Now', 'Go to cart', 'add to cart', 'go to cart', 'buy now', 'cart']:
            log(f'KW_{kw}={kw.lower() in body_text.lower()}')
        snippet = body_text.lower()
        for kw in ['add to cart', 'go to cart', 'buy now', 'add to']:
            idx = snippet.find(kw)
            log(f'IDX_{kw}={idx}')
            if idx != -1:
                log(snippet[max(0, idx-200): idx+300])
        # DOM match counts
        xpaths = [
            "//button[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'add to cart')]",
            "//button[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'go to cart')]",
            "//button[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'buy now')]",
            "//*[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'add to cart')]",
            "//*[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'go to cart')]",
        ]
        for xp in xpaths:
            els = d.find_elements(By.XPATH, xp)
            log(f'XP {xp} count={len(els)}')
        with open('probe2_output.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(out))
finally:
    d.quit()
