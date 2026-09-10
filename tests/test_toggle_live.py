import subprocess
import time
import json
import urllib.request
import os
import websocket

def run_toggle_test():
    print("=== LIVE BROWSER THEME TOGGLE TEST VIA CDP ===")
    
    # 1. Launch Headless Edge with Remote Debugging
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    tmp_dir = os.path.join(os.environ.get("TEMP", "C:\\temp"), "edge_cdp_test")
    os.makedirs(tmp_dir, exist_ok=True)
    
    port = 9222
    args = [
        edge_path,
        "--headless",
        "--disable-gpu",
        f"--remote-debugging-port={port}",
        "--remote-allow-origins=*",
        f"--user-data-dir={tmp_dir}",
        "http://127.0.0.1:8000/index.php"
    ]
    
    proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    
    try:
        # Get target tab websocket URL
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/json") as resp:
            tabs = json.loads(resp.read().decode('utf-8'))
            target_tab = None
            for t in tabs:
                if "127.0.0.1:8000" in t.get("url", ""):
                    target_tab = t
                    break
            if not target_tab:
                target_tab = tabs[0]
            ws_url = target_tab["webSocketDebuggerUrl"]
            print(f"Connected to Edge tab: {target_tab.get('title')} ({target_tab.get('url')})")
        
        ws = websocket.create_connection(ws_url)
        msg_id = 0
        exceptions_logged = []
        
        def send_cdp(method, params=None):
            nonlocal msg_id
            msg_id += 1
            payload = {"id": msg_id, "method": method, "params": params or {}}
            ws.send(json.dumps(payload))
            while True:
                res = json.loads(ws.recv())
                if res.get("method") == "Runtime.exceptionThrown":
                    exceptions_logged.append(res.get("params", {}))
                if res.get("id") == msg_id:
                    return res.get("result", {})
        
        # Enable Runtime to capture any JS errors
        send_cdp("Runtime.enable")
        
        def eval_js(expression):
            res = send_cdp("Runtime.evaluate", {"expression": expression, "returnByValue": True})
            return res.get("result", {}).get("value")

        # Wait for page to be ready
        time.sleep(1)
        
        # Test 1: Start in Light Mode
        print("\n--- Setup: Initializing to Light Mode ---")
        eval_js("applyTheme('light');")
        initial_theme = eval_js("document.documentElement.getAttribute('data-theme')")
        initial_label = eval_js("document.querySelector('#themeToggleBtn .theme-text').textContent")
        print(f"Initial theme: {initial_theme} | Button label: {initial_label}")
        assert initial_theme == "light", f"Expected light, got {initial_theme}"
        assert initial_label == "Light", f"Expected 'Light', got {initial_label}"
        
        # Test 2: Real Click on #themeToggleBtn to switch to Dark Mode
        print("\n--- TEST 1: Clicking #themeToggleBtn (Light -> Dark) ---")
        eval_js("document.getElementById('themeToggleBtn').click()")
        time.sleep(0.5)
        new_theme = eval_js("document.documentElement.getAttribute('data-theme')")
        new_bs_theme = eval_js("document.documentElement.getAttribute('data-bs-theme')")
        new_storage = eval_js("localStorage.getItem('ai_healthcare_theme')")
        new_label = eval_js("document.querySelector('#themeToggleBtn .theme-text').textContent")
        print(f"After click: data-theme={new_theme} | data-bs-theme={new_bs_theme} | localStorage={new_storage} | label={new_label}")
        assert new_theme == "dark", f"TEST 1 FAILED: Expected dark, got {new_theme}"
        assert new_bs_theme == "dark", f"TEST 1 FAILED: Expected bs-theme dark, got {new_bs_theme}"
        assert new_storage == "dark", f"TEST 1 FAILED: Expected localStorage dark, got {new_storage}"
        assert new_label == "Dark", f"TEST 1 FAILED: Expected button label 'Dark', got {new_label}"
        print("-> TEST 1 PASSED: Successfully toggled from Light to Dark!")

        # Test 3: Real Click on #themeToggleBtn to switch to Light Mode
        print("\n--- TEST 2: Clicking #themeToggleBtn (Dark -> Light) ---")
        eval_js("document.getElementById('themeToggleBtn').click()")
        time.sleep(0.5)
        new_theme2 = eval_js("document.documentElement.getAttribute('data-theme')")
        new_bs_theme2 = eval_js("document.documentElement.getAttribute('data-bs-theme')")
        new_storage2 = eval_js("localStorage.getItem('ai_healthcare_theme')")
        new_label2 = eval_js("document.querySelector('#themeToggleBtn .theme-text').textContent")
        print(f"After click 2: data-theme={new_theme2} | data-bs-theme={new_bs_theme2} | localStorage={new_storage2} | label={new_label2}")
        assert new_theme2 == "light", f"TEST 2 FAILED: Expected light, got {new_theme2}"
        assert new_bs_theme2 == "light", f"TEST 2 FAILED: Expected bs-theme light, got {new_bs_theme2}"
        assert new_storage2 == "light", f"TEST 2 FAILED: Expected localStorage light, got {new_storage2}"
        assert new_label2 == "Light", f"TEST 2 FAILED: Expected button label 'Light', got {new_label2}"
        print("-> TEST 2 PASSED: Successfully toggled from Dark to Light!")

        # Test 4: Toggle to Dark, then reload page to verify persistence
        print("\n--- TEST 3: Persistence after Reload (Dark Mode) ---")
        eval_js("document.getElementById('themeToggleBtn').click()") # to Dark
        time.sleep(0.5)
        assert eval_js("document.documentElement.getAttribute('data-theme')") == "dark"
        # Reload
        send_cdp("Page.reload")
        time.sleep(2)
        reloaded_theme = eval_js("document.documentElement.getAttribute('data-theme')")
        reloaded_label = eval_js("document.querySelector('#themeToggleBtn .theme-text').textContent")
        print(f"After reload: data-theme={reloaded_theme} | label={reloaded_label}")
        assert reloaded_theme == "dark", f"TEST 3 FAILED: Expected dark after reload, got {reloaded_theme}"
        assert reloaded_label == "Dark", f"TEST 3 FAILED: Expected 'Dark' after reload, got {reloaded_label}"
        print("-> TEST 3 PASSED: Dark Mode persisted across page reload!")

        # Test 5: Toggle to Light, then reload page to verify persistence
        print("\n--- TEST 4: Persistence after Reload (Light Mode) ---")
        eval_js("document.getElementById('themeToggleBtn').click()") # to Light
        time.sleep(0.5)
        assert eval_js("document.documentElement.getAttribute('data-theme')") == "light"
        # Reload
        send_cdp("Page.reload")
        time.sleep(2)
        reloaded_theme_light = eval_js("document.documentElement.getAttribute('data-theme')")
        reloaded_label_light = eval_js("document.querySelector('#themeToggleBtn .theme-text').textContent")
        print(f"After reload: data-theme={reloaded_theme_light} | label={reloaded_label_light}")
        assert reloaded_theme_light == "light", f"TEST 4 FAILED: Expected light after reload, got {reloaded_theme_light}"
        assert reloaded_label_light == "Light", f"TEST 4 FAILED: Expected 'Light' after reload, got {reloaded_label_light}"
        print("-> TEST 4 PASSED: Light Mode persisted across page reload!")

        # Test 6: Cross-page navigation
        print("\n--- TEST 5: Cross-page Theme Persistence ---")
        eval_js("window.location.href = 'http://127.0.0.1:8000/prediction.php'")
        time.sleep(2)
        nav_theme = eval_js("document.documentElement.getAttribute('data-theme')")
        nav_label = eval_js("document.querySelector('#themeToggleBtn .theme-text').textContent")
        print(f"Navigated to prediction.php: data-theme={nav_theme} | label={nav_label}")
        assert nav_theme == "light", f"TEST 5 FAILED: Expected light on prediction.php, got {nav_theme}"
        assert nav_label == "Light", f"TEST 5 FAILED: Expected 'Light' on prediction.php, got {nav_label}"
        print("-> TEST 5 PASSED: Theme persisted across navigation to prediction.php!")

        # Test 7: Toggle on prediction.php to Dark, then navigate to image_scanner.php
        eval_js("document.getElementById('themeToggleBtn').click()")
        time.sleep(0.5)
        assert eval_js("document.documentElement.getAttribute('data-theme')") == "dark"
        eval_js("window.location.href = 'http://127.0.0.1:8000/image_scanner.php'")
        time.sleep(2)
        nav_theme2 = eval_js("document.documentElement.getAttribute('data-theme')")
        nav_label2 = eval_js("document.querySelector('#themeToggleBtn .theme-text').textContent")
        print(f"Navigated to image_scanner.php: data-theme={nav_theme2} | label={nav_label2}")
        assert nav_theme2 == "dark", f"TEST 5b FAILED: Expected dark on image_scanner.php, got {nav_theme2}"
        assert nav_label2 == "Dark", f"TEST 5b FAILED: Expected 'Dark' on image_scanner.php, got {nav_label2}"
        print("-> TEST 5b PASSED: Dark theme persisted across navigation to image_scanner.php!")

        print(f"\n--- TEST 6: JavaScript Console Errors Check ---")
        print(f"Total JavaScript exceptions caught: {len(exceptions_logged)}")
        assert len(exceptions_logged) == 0, f"Detected JS exceptions: {exceptions_logged}"
        print("-> TEST 6 PASSED: ZERO JavaScript console errors or exceptions detected!")

        ws.close()
        print("\n==================================================")
        print("ALL BROWSER THEME TOGGLE TESTS PASSED WITH 100% SUCCESS!")
        print("==================================================")
        
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()

if __name__ == '__main__':
    run_toggle_test()
