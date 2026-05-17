from playwright.sync_api import sync_playwright
import time
with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context('D:/AI-Employee-FTEs/KE_AI_Vault/.sessions/linkedin', headless=False)
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto('https://www.linkedin.com/in/digital-dreamers-9a15bb3b4/recent-activity/all/', timeout=30000, wait_until='domcontentloaded')
    page.wait_for_timeout(5000)
    
    links = page.evaluate("() => Array.from(document.querySelectorAll('a')).map(a => a.href)")
    print('Total links:', len(links))
    for l in links:
        if 'urn:li:activity' in l or 'posts' in l or 'update' in l:
            print('Post link:', l)
            
    print(page.evaluate("() => document.body.innerText")[:500])
    ctx.close()