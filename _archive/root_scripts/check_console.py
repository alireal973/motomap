from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    messages = []
    page.on('console', lambda msg: messages.append(f'[{msg.type}] {msg.text}'))
    page.on('pageerror', lambda exc: messages.append(f'[error] {exc}'))
    
    page.goto('file:///C:/Users/lenovo/Desktop/motomap/docs/index.html')
    
    print('Console Messages:')
    for msg in messages:
        print(msg)
    browser.close()
