import subprocess
import time
import json
import urllib.request
import os
import websocket
import base64

def run_navbar_and_theme_audit():
    print("============================================================")
    print("STARTING COMPREHENSIVE NAVBAR, DROPDOWN & RESPONSIVE AUDIT")
    print("============================================================")
    
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    tmp_dir = os.path.join(os.environ.get("TEMP", "C:\\temp"), "edge_cdp_navbar_audit")
    os.makedirs(tmp_dir, exist_ok=True)
    
    port = 9227
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
            print(f"Connected to Edge tab: {target_tab.get('title')} ({target_tab.get('url')})")
        
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

        time.sleep(1)

        # -------------------------------------------------------------
        # STEP 1: Verify Dataset & AI is NOT present in Navbar or Footer
        # -------------------------------------------------------------
        print("\n--- STEP 1: Verifying Complete Absence of 'Dataset & AI' ---")
        dataset_in_nav = eval_js("""
        (() => {
            const nav = document.querySelector('nav');
            return nav ? nav.innerText.includes('Dataset') : false;
        })()
        """)
        print(f"  Dataset in navbar: {dataset_in_nav} (must be False)")
        assert not dataset_in_nav, "ERROR: 'Dataset' still found in navbar!"

        dataset_in_footer = eval_js("""
        (() => {
            const footer = document.querySelector('footer');
            return footer ? footer.innerText.includes('Dataset & AI') : false;
        })()
        """)
        print(f"  Dataset & AI in footer: {dataset_in_footer} (must be False)")
        assert not dataset_in_footer, "ERROR: 'Dataset & AI' found in footer!"
        print("  [PASS] 'Dataset & AI' successfully removed from navigation!")

        # -------------------------------------------------------------
        # STEP 2: Verify Desktop Navbar Structure & Dimensions
        # -------------------------------------------------------------
        print("\n--- STEP 2: Verifying Desktop Navbar Structure (1400px) ---")
        eval_js("applyTheme('light');")
        time.sleep(0.3)

        nav_height = eval_js("document.querySelector('.navbar-custom').offsetHeight")
        print(f"  Navbar height: {nav_height}px (target ~70-80px)")
        assert 68 <= nav_height <= 85, f"Unexpected navbar height: {nav_height}px"

        # Check top-level center links
        top_links = eval_js("""
        (() => {
            const links = Array.from(document.querySelectorAll('#navbarMain > ul > li > a'));
            return links.map(a => a.innerText.trim().replace(/\\n/g, ' '));
        })()
        """)
        print(f"  Top-level nav links found: {top_links}")
        expected_links = ['Home', 'About', 'AI Prediction', 'Injury Scanner', 'Clinical Tools', 'Health Library']
        for el in expected_links:
            assert any(el in tl for tl in top_links), f"Expected '{el}' in top links, got {top_links}"

        # Check that top links do NOT wrap onto multiple lines
        wraps = eval_js("""
        (() => {
            const links = document.querySelectorAll('#navbarMain > ul > li > a');
            let wrappedCount = 0;
            links.forEach(l => {
                if (l.offsetHeight > 45) wrappedCount++;
            });
            return wrappedCount;
        })()
        """)
        print(f"  Multi-line wrapped top links: {wraps} (must be 0)")
        assert wraps == 0, f"Found {wraps} top links wrapping into multiple lines!"

        capture_screenshot("navbar_desktop_light.png")

        # -------------------------------------------------------------
        # STEP 3: Verify Clinical Tools Dropdown Interaction & Contrast
        # -------------------------------------------------------------
        print("\n--- STEP 3: Testing Clinical Tools Dropdown Interaction ---")
        eval_js("document.getElementById('clinicalToolsDropdown').click();")
        time.sleep(0.4)

        clin_open = eval_js("document.getElementById('clinicalToolsDropdown').classList.contains('show') || document.querySelector('#clinicalToolsDropdown + .dropdown-menu').classList.contains('show')")
        print(f"  Clinical Tools dropdown opened: {clin_open}")
        assert clin_open, "Clinical Tools dropdown failed to open on click"

        clin_items = eval_js("""
        (() => {
            const items = Array.from(document.querySelectorAll('#clinicalToolsDropdown + .dropdown-menu .dropdown-item'));
            return items.map(it => ({
                title: it.querySelector('.dropdown-item-title').textContent.trim(),
                desc: it.querySelector('.dropdown-item-desc').textContent.trim(),
                href: it.getAttribute('href'),
                bg: window.getComputedStyle(it).backgroundColor,
                titleColor: window.getComputedStyle(it.querySelector('.dropdown-item-title')).color
            }));
        })()
        """)
        print(f"  Found {len(clin_items)} Clinical Tools items:")
        for it in clin_items:
            print(f"    - {it['title']} ({it['href']}): {it['desc']} | text-color: {it['titleColor']}")
            assert it['titleColor'] == "rgb(23, 32, 51)", f"Expected readable dark title in light mode, got {it['titleColor']}"

        assert len(clin_items) == 3, f"Expected 3 clinical tools, found {len(clin_items)}"
        assert any("Clinical Risk" in it['title'] for it in clin_items)
        assert any("Simulator" in it['title'] for it in clin_items)
        assert any("Diabetes" in it['title'] for it in clin_items)

        capture_screenshot("navbar_clinical_dropdown_light.png")

        # -------------------------------------------------------------
        # STEP 4: Verify Dark Mode Dropdown & Contrast
        # -------------------------------------------------------------
        print("\n--- STEP 4: Testing Dark Mode Dropdown & Contrast ---")
        eval_js("applyTheme('dark');")
        time.sleep(0.4)

        # Open Health Library dropdown
        eval_js("document.getElementById('healthLibraryDropdown').click();")
        time.sleep(0.4)

        lib_open = eval_js("document.getElementById('healthLibraryDropdown').classList.contains('show') || document.querySelector('#healthLibraryDropdown + .dropdown-menu').classList.contains('show')")
        print(f"  Health Library dropdown opened: {lib_open}")
        assert lib_open, "Health Library dropdown failed to open on click"

        lib_items = eval_js("""
        (() => {
            const items = Array.from(document.querySelectorAll('#healthLibraryDropdown + .dropdown-menu .dropdown-item'));
            return items.map(it => ({
                title: it.querySelector('.dropdown-item-title').textContent.trim(),
                desc: it.querySelector('.dropdown-item-desc').textContent.trim(),
                href: it.getAttribute('href'),
                titleColor: window.getComputedStyle(it.querySelector('.dropdown-item-title')).color
            }));
        })()
        """)
        print(f"  Found {len(lib_items)} Health Library items in Dark Mode:")
        for it in lib_items:
            print(f"    - {it['title']} ({it['href']}): {it['desc']} | text-color: {it['titleColor']}")
            assert it['titleColor'] == "rgb(255, 255, 255)", f"Expected readable white title in dark mode, got {it['titleColor']}"

        assert len(lib_items) == 3, f"Expected 3 health library items, found {len(lib_items)}"
        assert any("Diseases" in it['title'] for it in lib_items)
        assert any("Symptoms" in it['title'] for it in lib_items)
        assert any("Prevention" in it['title'] for it in lib_items)

        capture_screenshot("navbar_health_dropdown_dark.png")

        # -------------------------------------------------------------
        # STEP 5: Active Page States
        # -------------------------------------------------------------
        print("\n--- STEP 5: Verifying Active Page States ---")
        # 1. Prediction page -> AI Prediction active
        navigate("http://127.0.0.1:8000/prediction.php")
        pred_active = eval_js("document.querySelector('a[href=\"prediction.php\"]').classList.contains('active')")
        print(f"  On prediction.php: AI Prediction link active = {pred_active}")
        assert pred_active, "AI Prediction should be active on prediction.php"

        # 2. Symptoms Guide page -> Health Library dropdown active
        navigate("http://127.0.0.1:8000/symptoms_guide.php")
        lib_active = eval_js("document.getElementById('healthLibraryDropdown').classList.contains('active')")
        print(f"  On symptoms_guide.php: Health Library dropdown active = {lib_active}")
        assert lib_active, "Health Library dropdown should be active on symptoms_guide.php"

        # 3. Diseases page -> Health Library dropdown active
        navigate("http://127.0.0.1:8000/diseases.php")
        dis_active = eval_js("document.getElementById('healthLibraryDropdown').classList.contains('active')")
        print(f"  On diseases.php: Health Library dropdown active = {dis_active}")
        assert dis_active, "Health Library dropdown should be active on diseases.php"

        # 4. Login and verify Assessment page -> Clinical Tools dropdown active
        navigate("http://127.0.0.1:8000/login.php")
        eval_js("""
        (() => {
            document.querySelector('input[name="email"]').value = 'student@college.edu';
            document.querySelector('input[name="password"]').value = 'password123';
            document.querySelector('form').submit();
        })()
        """)
        time.sleep(1.0)
        navigate("http://127.0.0.1:8000/assessment.php")
        clin_active = eval_js("document.getElementById('clinicalToolsDropdown').classList.contains('active')")
        print(f"  On assessment.php (authenticated): Clinical Tools dropdown active = {clin_active}")
        assert clin_active, "Clinical Tools dropdown should be active on assessment.php"

        # -------------------------------------------------------------
        # STEP 6: Multi-Screen Desktop & Tablet Responsiveness
        # -------------------------------------------------------------
        print("\n--- STEP 6: Multi-Screen Desktop Responsiveness (1920, 1440, 1366, 1280) ---")
        for width in [1920, 1440, 1366, 1280]:
            set_viewport(width, 800)
            wraps = eval_js("""
            (() => {
                const links = document.querySelectorAll('#navbarMain > ul > li > a');
                let count = 0;
                links.forEach(l => { if (l.offsetHeight > 45) count++; });
                return count;
            })()
            """)
            print(f"  [{width}px] Top-level links multi-line wraps: {wraps}")
            assert wraps == 0, f"Links wrap at {width}px!"

        # -------------------------------------------------------------
        # STEP 7: Mobile Navigation (768px, 480px, 375px)
        # -------------------------------------------------------------
        print("\n--- STEP 7: Testing Mobile Navigation & Hamburger Menu ---")
        for width in [768, 480, 375]:
            set_viewport(width, 750)
            eval_js("applyTheme('light');")
            time.sleep(0.3)

            # Check toggler is visible
            toggler_visible = eval_js("""
            (() => {
                const btn = document.querySelector('.navbar-toggler');
                const comp = window.getComputedStyle(btn);
                return comp.display !== 'none';
            })()
            """)
            print(f"  [{width}px] Mobile toggler visible: {toggler_visible}")
            assert toggler_visible, f"Navbar toggler not visible at {width}px"

            # Click hamburger to open
            eval_js("document.querySelector('.navbar-toggler').click();")
            time.sleep(0.5)

            menu_open = eval_js("document.getElementById('navbarMain').classList.contains('show')")
            print(f"  [{width}px] Mobile menu opened on click: {menu_open}")
            assert menu_open, f"Mobile menu failed to open at {width}px"

            # Check horizontal overflow
            overflow = eval_js("document.body.scrollWidth > window.innerWidth + 2")
            print(f"  [{width}px] Horizontal page overflow: {overflow}")
            assert not overflow, f"Horizontal page overflow detected at {width}px"

            if width == 375:
                capture_screenshot("navbar_mobile_375_light.png")

            # Close hamburger
            eval_js("document.querySelector('.navbar-toggler').click();")
            time.sleep(0.4)

        # -------------------------------------------------------------
        # STEP 8: Footer Architecture Check
        # -------------------------------------------------------------
        print("\n--- STEP 8: Verifying Organized Footer Architecture ---")
        footer_sections = eval_js("""
        (() => {
            const headings = Array.from(document.querySelectorAll('footer h6'));
            return headings.map(h => h.textContent.trim());
        })()
        """)
        print(f"  Footer categories: {footer_sections}")
        assert "Explore" in footer_sections, "Missing 'Explore' in footer"
        assert "Clinical Tools" in footer_sections, "Missing 'Clinical Tools' in footer"
        assert "Health Library" in footer_sections, "Missing 'Health Library' in footer"

        # Check console errors
        print(f"\nConsole exceptions caught: {len(console_errors)}")
        if console_errors:
            print("Errors:", console_errors)
        assert len(console_errors) == 0, "Console errors detected!"

        print("\n============================================================")
        print("ALL NAVBAR & RESPONSIVE THEME AUDITS PASSED 100%!")
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
    run_navbar_and_theme_audit()
