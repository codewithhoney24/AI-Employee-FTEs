def send_to_whatsapp_visual(platform, content, filename):

    print(f"\n[APPROVAL] Triggering WhatsApp for: {filename}")

    try:
        with sync_playwright() as p:

            browser = p.chromium.launch_persistent_context(
                user_data_dir=SESSION_PATH,
                headless=False,
                slow_mo=400,
                no_viewport=True,
                args=["--start-maximized"]
            )

            # 🔥 FIX: use existing page (NOT new_page)
            page = browser.pages[0] if browser.pages else browser.new_page()

            print(">>> WhatsApp Opened")

            # OPEN CHAT DIRECTLY (SAFE METHOD)
            page.goto("https://web.whatsapp.com")

            page.wait_for_selector('div[contenteditable="true"]', timeout=60000)

            message = (
                f"🚀 KE AI EMPLOYEE: DRAFT READY\n\n"
                f"PLATFORM: {platform}\n"
                f"CONTENT: {content}\n\n"
                f"Reply: YES {filename} / NO / EDIT"
            )

            # paste message
            box = page.locator('div[contenteditable="true"]').last
            box.click()

            page.keyboard.insert_text(message)
            page.keyboard.press("Enter")

            print("✅ Message sent to WhatsApp")

            print("\n" + "="*60)
            print("✋ WAITING FOR HUMAN APPROVAL")
            print("="*60)

            # 🔥 KEEP SESSION ALIVE (IMPORTANT FIX)
            while True:
                time.sleep(10)

    except Exception as e:
        print("🔥 WhatsApp Error:", e)