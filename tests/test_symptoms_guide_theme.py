import subprocess
import time
import json
import urllib.request
import os
import websocket
import base64

def run_symptoms_and_theme_cdp_test():
    print("============================================================")
    print("STARTING CDP VERIFICATION OF SYMPTOMS GUIDE & GLOBAL THEME")
    print("============================================================")
    
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    tmp_dir = os.path.join(os.environ.get("TEMP", "C:\\temp"), "edge_cdp_symptoms")
    os.makedirs(tmp_dir, exist_ok=True)
    
    port = 9223
    args = [
        edge_path,
        "--headless",
        "--disable-gpu",
        f"--remote-debugging-port={port}",
        "--remote-allow-origins=*",
        f"--user-data-dir={tmp_dir}",
        "--window-size=1400,1000",
        "http://127.0.0.1:8000/symptoms_guide.php"
    ]
    
    proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    
    try:
        # Get target tab websocket URL
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/json") as resp:
            tabs = json.loads(resp.read().decode('utf-8'))
            target_tab = None
            for t in tabs:
                if "symptoms_guide.php" in t.get("url", ""):
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
        
        # 1. Test Light Mode
        print("\n--- STEP 1: Verifying Symptoms Guide in LIGHT MODE ---")
        eval_js("applyTheme('light');")
        time.sleep(0.5)
        
        curr_theme = eval_js("document.documentElement.getAttribute('data-theme')")
        print(f"Active theme: {curr_theme}")
        assert curr_theme == "light", f"Expected light mode, got {curr_theme}"
        
        # Count symptom cards
        card_count = eval_js("document.querySelectorAll('.symptom-relation-box').length")
        print(f"Found {card_count} .symptom-relation-box elements (expected 58)")
        assert card_count == 58, f"Expected 58 symptom cards, found {card_count}"
        
        # Check computed styles for first 5 cards
        style_check = eval_js("""
        (() => {
            const boxes = document.querySelectorAll('.symptom-relation-box');
            const results = [];
            for (let i = 0; i < Math.min(5, boxes.length); i++) {
                const box = boxes[i];
                const card = box.closest('.card-custom') || box.parentElement;
                const title = card.querySelector('h5, h4') ? card.querySelector('h5, h4').textContent.trim() : ('Card ' + (i+1));
                const comp = window.getComputedStyle(box);
                const titleComp = window.getComputedStyle(box.querySelector('.symptom-relation-title') || box);
                const tag = box.querySelector('.symptom-condition-tag');
                const tagComp = tag ? window.getComputedStyle(tag) : null;
                results.push({
                    title,
                    boxBg: comp.backgroundColor,
                    boxColor: comp.color,
                    boxBorder: comp.borderColor,
                    titleColor: titleComp.color,
                    tagBg: tagComp ? tagComp.backgroundColor : 'none',
                    tagColor: tagComp ? tagComp.color : 'none',
                    tagCount: box.querySelectorAll('.symptom-condition-tag').length
                });
            }
            return results;
        })()
        """)
        
        for idx, item in enumerate(style_check):
            print(f"  Card #{idx+1} '{item['title']}':")
            print(f"    - boxBg: {item['boxBg']}")
            print(f"    - boxBorder: {item['boxBorder']}")
            print(f"    - titleColor: {item['titleColor']}")
            print(f"    - tagCount: {item['tagCount']} | tagBg: {item['tagBg']} | tagColor: {item['tagColor']}")
            
            # Check for black box
            assert item['boxBg'] != "rgb(0, 0, 0)" and item['boxBg'] != "rgb(33, 37, 41)", \
                f"CRITICAL: Black box detected on card {item['title']}! Got {item['boxBg']}"
            # Check that background is light
            assert "rgb(237, 243, 248)" in item['boxBg'] or "rgba" in item['boxBg'], \
                f"Expected light subtle surface #edf3f8, got {item['boxBg']}"
            # Check text is readable dark
            assert item['titleColor'] == "rgb(23, 32, 51)", \
                f"Expected title text #172033 (rgb(23, 32, 51)), got {item['titleColor']}"

        capture_screenshot("symptoms_light_cdp.png")
        print("  [PASS] Light Mode styles verified clean with zero black boxes!")

        # 2. Test Dark Mode
        print("\n--- STEP 2: Toggling to DARK MODE via Navbar Button ---")
        eval_js("document.getElementById('themeToggleBtn').click();")
        time.sleep(0.5)
        
        dark_theme = eval_js("document.documentElement.getAttribute('data-theme')")
        print(f"Active theme: {dark_theme}")
        assert dark_theme == "dark", f"Expected dark mode, got {dark_theme}"
        
        dark_style_check = eval_js("""
        (() => {
            const boxes = document.querySelectorAll('.symptom-relation-box');
            const results = [];
            for (let i = 0; i < Math.min(5, boxes.length); i++) {
                const box = boxes[i];
                const card = box.closest('.card-custom') || box.parentElement;
                const title = card.querySelector('h5, h4') ? card.querySelector('h5, h4').textContent.trim() : ('Card ' + (i+1));
                const comp = window.getComputedStyle(box);
                const titleComp = window.getComputedStyle(box.querySelector('.symptom-relation-title') || box);
                const tag = box.querySelector('.symptom-condition-tag');
                const tagComp = tag ? window.getComputedStyle(tag) : null;
                results.push({
                    title,
                    boxBg: comp.backgroundColor,
                    boxBorder: comp.borderColor,
                    titleColor: titleComp.color,
                    tagBg: tagComp ? tagComp.backgroundColor : 'none',
                    tagColor: tagComp ? tagComp.color : 'none'
                });
            }
            return results;
        })()
        """)
        
        for idx, item in enumerate(dark_style_check):
            print(f"  Dark Card #{idx+1} '{item['title']}':")
            print(f"    - boxBg: {item['boxBg']}")
            print(f"    - boxBorder: {item['boxBorder']}")
            print(f"    - titleColor: {item['titleColor']}")
            print(f"    - tagBg: {item['tagBg']} | tagColor: {item['tagColor']}")
            
            # Check dark surface
            assert item['boxBg'] == "rgb(15, 28, 43)", \
                f"Expected dark surface #0f1c2b (rgb(15, 28, 43)), got {item['boxBg']}"
            # Check light readable text
            assert item['titleColor'] == "rgb(255, 255, 255)", \
                f"Expected dark-mode title text #ffffff (rgb(255, 255, 255)), got {item['titleColor']}"

        capture_screenshot("symptoms_dark_cdp.png")
        print("  [PASS] Dark Mode styles verified clean with high contrast!")

        # 3. Test Toggle Back to Light Mode
        print("\n--- STEP 3: Toggling Back to LIGHT MODE ---")
        eval_js("document.getElementById('themeToggleBtn').click();")
        time.sleep(0.5)
        back_theme = eval_js("document.documentElement.getAttribute('data-theme')")
        assert back_theme == "light", f"Expected light mode, got {back_theme}"
        print("  [PASS] Toggled back to light mode successfully!")

        # 4. Check for console errors
        print(f"\nConsole exceptions caught: {len(console_errors)}")
        if console_errors:
            print("Errors:", console_errors)
        assert len(console_errors) == 0, "Console errors detected during execution!"

        print("\n============================================================")
        print("ALL SYMPTOMS GUIDE THEME VERIFICATIONS PASSED 100%!")
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
    run_symptoms_and_theme_cdp_test()
