import asyncio
import os
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        # Point to the pre-installed system browsers
        browser_path = "/ms-playwright"
        
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Capture console messages from ALL frames
        page.on("console", lambda msg: print(f"CONSOLE [{msg.type}] ({msg.location.get('url', 'unknown')}): {msg.text}"))
        page.on("pageerror", lambda err: print(f"PAGE_ERROR: {err}"))
        page.on("requestfailed", lambda req: print(f"REQ_FAILED: {req.method} {req.url} - {req.failure.error_text}"))
        
        print("🔍 Navigating to https://dash.bitmango.win...")
        try:
            # Go to page and wait for everything to load
            await page.goto("https://dash.bitmango.win", wait_until="networkidle", timeout=30000)
            await asyncio.sleep(5)  # Wait for async JS / frames
            
            print("\n🖼️ Frame Analysis:")
            for i, frame in enumerate(page.frames):
                print(f"  Frame {i}: {frame.url}")
                try:
                    # Check visibility of key elements in the frame
                    is_visible = await frame.is_visible("body")
                    print(f"    - Body visible: {is_visible}")
                    
                    if "login_frame" in frame.url:
                        login_card = await frame.is_visible(".login-card")
                        opacity = await frame.evaluate("getComputedStyle(document.body).opacity")
                        print(f"    - Login Card visible: {login_card}")
                        print(f"    - Body Opacity: {opacity}")
                except Exception as fe:
                    print(f"    - Frame check error: {fe}")

            # Check if main app shell is hidden
            header_hidden = await page.evaluate("document.getElementById('app-header').classList.contains('hidden')")
            overlay_hidden = await page.evaluate("document.getElementById('auth-overlay').classList.contains('hidden')")
            print(f"\n🏠 Main Shell Status:")
            print(f"  - App Header hidden: {header_hidden}")
            print(f"  - Auth Overlay hidden: {overlay_hidden}")

        except Exception as e:
            print(f"🛑 Error during navigation: {e}")
            
        await browser.close()

if __name__ == "__main__":
    # Ensure Playwright knows where browsers are if needed
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "/ms-playwright"
    asyncio.run(main())
