import subprocess
import time
import json
import urllib.request
import os
import websocket
import base64

def test_navbar_actions():
    print("============================================================")
    print("TESTING REDESIGNED NAVBAR ACTION AREA (THEME, LOGIN, REGISTER)")
    print("============================================================")

    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    tmp_dir = os.path.join(os.environ.get("TEMP", "C:\\temp"), "edge_cdp_actions_audit")
    os.makedirs(tmp_dir, exist_ok=True)

    port = 9228
    args = [
        edge_path,
        "--headless",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check",
        f"--remote-debugging-port={port}",
        "--remote-allow-origins=*",
        f"--user-data-dir={tmp_dir}",
        "--window-size=1400,900",
        "http://127.0.0.1:8000/index.php"
    ]

    proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2.5)

    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/json") as resp:
            tabs = json.loads(resp.read().decode('utf-8'))
            target_tab = None
            for t in tabs:
                if "127.0.0.1:8000" in t.get("url", ""):
                    target_tab = t
                    break
            if not target_tab:
                for t in tabs:
                    if t.get("type") == "page":
                        target_tab = t
                        break
            if not target_tab:
                target_tab = tabs[0]
            ws_url = target_tab["webSocketDebuggerUrl"]
            print(f"Connected to tab: {target_tab.get('title')}")

        ws = websocket.create_connection(ws_url)
        msg_id = 0
        console_errors = []

        def send_cdp(method, params=None):
            nonlocal msg_id
            msg_id += 1
            payload = {"id": msg_id, "method": method, "params": params or {}}
            ws.send(json.dumps(payload))
            while True:
                res = json.loads(ws.recv())
                if res.get("method") == "Runtime.exceptionThrown":
                    console_errors.append(res.get("params", {}))
                if res.get("id") == msg_id:
                    return res.get("result", {})

        send_cdp("Runtime.enable")
        send_cdp("Page.enable")

        def eval_js(expression):
            res = send_cdp("Runtime.evaluate", {"expression": expression, "returnByValue": True})
            return res.get("result", {}).get("value")

        def navigate(url):
            send_cdp("Page.navigate", {"url": url})
            time.sleep(1.0)

        def set_viewport(width, height):
            send_cdp("Emulation.setDeviceMetricsOverride", {
                "width": width,
                "height": height,
                "deviceScaleFactor": 1,
                "mobile": (width < 768)
            })
            time.sleep(0.3)

        def capture_screenshot(filename):
            res = send_cdp("Page.captureScreenshot", {"format": "png"})
            b64data = res.get("data", "")
            if b64data:
                save_dir = r"C:\Users\Pearl\.gemini\antigravity-ide\brain\293bb488-1883-4cab-8067-3cfa9f62fc24"
                save_path = os.path.join(save_dir, filename)
                with open(save_path, "wb") as f:
                    f.write(base64.b64decode(b64data))
                print(f"  [SCREENSHOT] Saved {filename}")

        # -------------------------------------------------------------
        # STEP 1: Light Mode Actions Inspection (Desktop 1400px)
        # -------------------------------------------------------------
        print("\n--- STEP 1: Inspecting Action Area in Light Mode ---")
        eval_js("applyTheme('light');")
        time.sleep(0.4)

        theme_btn_info = eval_js("""
        (() => {
            const btn = document.getElementById('themeToggleBtn');
            const style = window.getComputedStyle(btn);
            const darkIcon = btn.querySelector('.theme-icon-dark');
            const lightIcon = btn.querySelector('.theme-icon-light');
            const textSpan = btn.querySelector('.theme-text');
            const rect = btn.getBoundingClientRect();
            return {
                width: rect.width,
                height: rect.height,
                title: btn.getAttribute('title'),
                ariaLabel: btn.getAttribute('aria-label'),
                darkIconVisible: darkIcon ? !darkIcon.classList.contains('d-none') : false,
                lightIconVisible: lightIcon ? !lightIcon.classList.contains('d-none') : false,
                textVisible: textSpan ? (window.getComputedStyle(textSpan).display !== 'none') : false,
                displayedText: textSpan ? textSpan.innerText.trim() : ""
            };
        })()
        """)
        print(f"  Theme button dimensions: {theme_btn_info['width']}px x {theme_btn_info['height']}px")
        print(f"  Theme button tooltip: '{theme_btn_info['title']}' | aria-label: '{theme_btn_info['ariaLabel']}'")
        print(f"  Sun icon visible: {theme_btn_info['lightIconVisible']} | Moon icon visible: {theme_btn_info['darkIconVisible']}")
        print(f"  Text visible on desktop: {theme_btn_info['textVisible']}")

        assert 38 <= theme_btn_info['width'] <= 46, f"Theme button width should be ~42px, got {theme_btn_info['width']}px"
        assert 38 <= theme_btn_info['height'] <= 46, f"Theme button height should be ~42px, got {theme_btn_info['height']}px"
        assert theme_btn_info['lightIconVisible'] and not theme_btn_info['darkIconVisible'], "Sun icon must be visible in light mode"
        assert not theme_btn_info['textVisible'], "The text 'Light' or 'Dark' must NOT be visible on desktop"
        assert "dark" in theme_btn_info['title'].lower(), f"Expected dark mode prompt in tooltip, got {theme_btn_info['title']}"

        # Login and Register buttons inspection
        actions_info = eval_js("""
        (() => {
            const container = document.querySelector('.navbar-actions');
            const gap = window.getComputedStyle(container).gap;
            const login = document.querySelector('.btn-nav-login');
            const register = document.querySelector('.btn-nav-register');
            const loginRect = login.getBoundingClientRect();
            const regRect = register.getBoundingClientRect();
            const loginStyle = window.getComputedStyle(login);
            const regStyle = window.getComputedStyle(register);
            return {
                gap: gap,
                loginHeight: loginRect.height,
                loginBorderRadius: loginStyle.borderRadius,
                loginBg: loginStyle.backgroundColor,
                loginColor: loginStyle.color,
                regHeight: regRect.height,
                regBorderRadius: regStyle.borderRadius,
                regBg: regStyle.backgroundColor,
                regColor: regStyle.color
            };
        })()
        """)
        print(f"  Actions gap: {actions_info['gap']}")
        print(f"  Login button: height={actions_info['loginHeight']}px, radius={actions_info['loginBorderRadius']}, bg={actions_info['loginBg']}, color={actions_info['loginColor']}")
        print(f"  Register button: height={actions_info['regHeight']}px, radius={actions_info['regBorderRadius']}, bg={actions_info['regBg']}, color={actions_info['regColor']}")

        assert 40 <= actions_info['loginHeight'] <= 46, f"Login height should be 42-44px, got {actions_info['loginHeight']}"
        assert 40 <= actions_info['regHeight'] <= 46, f"Register height should be 42-44px, got {actions_info['regHeight']}"

        capture_screenshot("actions_desktop_light.png")

        # -------------------------------------------------------------
        # STEP 2: Theme Switch to Dark Mode
        # -------------------------------------------------------------
        print("\n--- STEP 2: Clicking Theme Toggle Button to Switch to Dark Mode ---")
        eval_js("document.getElementById('themeToggleBtn').click();")
        time.sleep(0.5)

        dark_active = eval_js("document.documentElement.getAttribute('data-theme')")
        print(f"  data-theme after click: {dark_active}")
        assert dark_active == "dark", f"Expected dark theme, got {dark_active}"

        dark_btn_info = eval_js("""
        (() => {
            const btn = document.getElementById('themeToggleBtn');
            const darkIcon = btn.querySelector('.theme-icon-dark');
            const lightIcon = btn.querySelector('.theme-icon-light');
            return {
                title: btn.getAttribute('title'),
                ariaLabel: btn.getAttribute('aria-label'),
                darkIconVisible: darkIcon ? !darkIcon.classList.contains('d-none') : false,
                lightIconVisible: lightIcon ? !lightIcon.classList.contains('d-none') : false
            };
        })()
        """)
        print(f"  Dark mode tooltip: '{dark_btn_info['title']}' | Moon icon visible: {dark_btn_info['darkIconVisible']} | Sun icon visible: {dark_btn_info['lightIconVisible']}")
        assert dark_btn_info['darkIconVisible'] and not dark_btn_info['lightIconVisible'], "Moon icon must be visible in dark mode"
        assert "light" in dark_btn_info['title'].lower(), f"Expected light mode prompt in tooltip, got {dark_btn_info['title']}"

        capture_screenshot("actions_desktop_dark.png")

        # -------------------------------------------------------------
        # STEP 3: Refresh & Theme Persistence
        # -------------------------------------------------------------
        print("\n--- STEP 3: Testing Theme Persistence Across Page Refresh ---")
        send_cdp("Page.reload")
        time.sleep(1.0)
        persisted_theme = eval_js("document.documentElement.getAttribute('data-theme')")
        print(f"  Persisted theme after reload: {persisted_theme}")
        assert persisted_theme == "dark", "Theme failed to persist in localStorage"

        # Switch back to light mode
        eval_js("document.getElementById('themeToggleBtn').click();")
        time.sleep(0.4)
        assert eval_js("document.documentElement.getAttribute('data-theme')") == "light", "Failed to switch back to light mode"

        # -------------------------------------------------------------
        # STEP 4: Flexbox Alignment & Spacing Verification
        # -------------------------------------------------------------
        print("\n--- STEP 4: Verifying Flexbox Alignment & Elimination of Awkward Empty Space ---")
        layout_metrics = eval_js("""
        (() => {
            const brand = document.querySelector('.navbar-brand').getBoundingClientRect();
            const navUl = document.querySelector('.navbar-nav');
            const healthLink = document.getElementById('healthLibraryDropdown').getBoundingClientRect();
            const actions = document.querySelector('.navbar-actions').getBoundingClientRect();
            const navContainer = document.querySelector('.navbar-custom .container').getBoundingClientRect();
            return {
                brandRight: brand.right,
                navLeft: navUl.getBoundingClientRect().left,
                healthLinkRight: healthLink.right,
                actionsLeft: actions.left,
                actionsRight: actions.right,
                containerRight: navContainer.right,
                distBrandToNav: navUl.getBoundingClientRect().left - brand.right,
                distNavToActions: actions.left - healthLink.right
            };
        })()
        """)
        print(f"  Layout metrics raw: {layout_metrics}")
        print(f"  Distance from Brand to Navigation: {layout_metrics['distBrandToNav']:.1f}px (clean adjacent spacing)")
        print(f"  Distance from Health Library to Actions: {layout_metrics['distNavToActions']:.1f}px (flex free-space)")
        print(f"  Actions right aligned in container: {layout_metrics['containerRight'] - layout_metrics['actionsRight']:.1f}px margin to edge")
        assert layout_metrics['distBrandToNav'] < 50, "Navigation should sit adjacent to brand, not pushed away"
        assert layout_metrics['actionsRight'] <= layout_metrics['containerRight'] + 15, "Actions should sit cleanly on the right of the container"

        # -------------------------------------------------------------
        # STEP 5: Mobile Navigation (768px, 480px, 375px)
        # -------------------------------------------------------------
        print("\n--- STEP 5: Verifying Mobile Navigation Action Area ---")
        for width in [768, 480, 375]:
            set_viewport(width, 750)
            time.sleep(0.3)

            # Open hamburger
            eval_js("document.querySelector('.navbar-toggler').click();")
            time.sleep(0.4)

            mob_actions = eval_js("""
            (() => {
                const actions = document.querySelector('.navbar-actions');
                const themeBtn = document.getElementById('themeToggleBtn');
                const login = document.querySelector('.btn-nav-login');
                const register = document.querySelector('.btn-nav-register');
                const rectA = actions.getBoundingClientRect();
                const rectT = themeBtn.getBoundingClientRect();
                const rectL = login.getBoundingClientRect();
                const rectR = register.getBoundingClientRect();
                const overflow = document.body.scrollWidth > window.innerWidth + 2;
                return {
                    themeWidth: rectT.width,
                    themeHeight: rectT.height,
                    loginWidth: rectL.width,
                    loginHeight: rectL.height,
                    regWidth: rectR.width,
                    regHeight: rectR.height,
                    overflow: overflow
                };
            })()
            """)
            print(f"  [{width}px] Theme btn: {mob_actions['themeWidth']:.1f}px x {mob_actions['themeHeight']:.1f}px | Login: {mob_actions['loginWidth']:.1f}px | Register: {mob_actions['regWidth']:.1f}px")
            print(f"  [{width}px] Page overflow: {mob_actions['overflow']}")
            assert not mob_actions['overflow'], f"Overflow detected at {width}px"
            assert mob_actions['themeHeight'] >= 42, "Mobile theme button should have >=42px touch height"
            assert mob_actions['loginHeight'] >= 42, "Mobile login button should have >=42px touch height"

            if width == 375:
                capture_screenshot("actions_mobile_375.png")

            # Close hamburger
            eval_js("document.querySelector('.navbar-toggler').click();")
            time.sleep(0.3)

        print(f"\nConsole exceptions caught: {len(console_errors)}")
        assert len(console_errors) == 0, f"Console errors: {console_errors}"
        print("\n============================================================")
        print("ALL NAVBAR ACTION AREA TESTS PASSED 100%!")
        print("============================================================")

    finally:
        try:
            ws.close()
        except:
            pass
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except:
            proc.kill()

if __name__ == '__main__':
    test_navbar_actions()
