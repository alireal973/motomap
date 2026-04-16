from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    
    # We want a detailed error trace
    page.on('pageerror', lambda exc: print(f'[PAGE ERROR] {exc}'))
    
    def handle_console(msg):
        print(f'[CONSOLE {msg.type}] {msg.text} at {msg.location}')
    
    page.on('console', handle_console)
    
    page.goto('file:///C:/Users/lenovo/Desktop/motomap/docs/index.html')
    
    browser.close()
