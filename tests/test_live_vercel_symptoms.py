import subprocess
import time
import json
import urllib.request
import os
import websocket
import base64

def test_live_vercel_symptoms():
    print("============================================================")
    print("TESTING LIVE VERCEL DEPLOYMENT OF SYMPTOMS GUIDE VIA CDP")
    print("URL: https://automated-disease-predictor-mvhc.vercel.app/symptoms")
    print("============================================================")
    
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    tmp_dir = os.path.join(os.environ.get("TEMP", "C:\\temp"), "edge_cdp_vercel_symptoms")
    os.makedirs(tmp_dir, exist_ok=True)
    
    port = 9225
    args = [
        edge_path,
        "--headless",
        "--disable-gpu",
        f"--remote-debugging-port={port}",
        "--remote-allow-origins=*",
        f"--user-data-dir={tmp_dir}",
        "--window-size=1400,1000",
        "https://automated-disease-predictor-mvhc.vercel.app/symptoms"
    ]
    
    proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3)
    
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/json") as resp:
            tabs = json.loads(resp.read().decode('utf-8'))
            ws_url = tabs[0]["webSocketDebuggerUrl"]
            print(f"Connected to Edge tab: {tabs[0].get('title')} ({tabs[0].get('url')})")
            
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

        # Wait for page to finish loading
        time.sleep(2)
        
        # Check if the deployment is updated by checking for .symptom-relation-box
        retry_count = 0
        while retry_count < 10:
            box_count = eval_js("document.querySelectorAll('.symptom-relation-box').length")
            if box_count and box_count > 0:
                print(f"Live deployment updated! Found {box_count} .symptom-relation-box elements.")
                break
            print(f"Waiting for Vercel deployment to propagate... attempt {retry_count+1}/10")
            time.sleep(4)
            send_cdp("Page.reload", {"ignoreCache": True})
            time.sleep(2)
            retry_count += 1
            
        assert box_count > 0, "Failed to detect .symptom-relation-box on live Vercel deployment after retries"
        
        # 1. Test Light Mode
        print("\n--- STEP 1: Verifying Live Symptoms Guide in LIGHT MODE ---")
        eval_js("applyTheme('light');")
        time.sleep(0.5)
        
        light_check = eval_js("""
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
                    tagColor: tagComp ? tagComp.color : 'none',
                    tagCount: box.querySelectorAll('.symptom-condition-tag').length
                });
            }
            return results;
        })()
        """)
        
        for idx, item in enumerate(light_check):
            print(f"  Live Card #{idx+1} '{item['title']}':")
            print(f"    - boxBg: {item['boxBg']}")
            print(f"    - boxBorder: {item['boxBorder']}")
            print(f"    - titleColor: {item['titleColor']}")
            print(f"    - tagCount: {item['tagCount']} | tagBg: {item['tagBg']} | tagColor: {item['tagColor']}")
            assert item['boxBg'] != "rgb(0, 0, 0)" and item['boxBg'] != "rgb(33, 37, 41)", \
                f"CRITICAL: Black box detected on live card {item['title']}! Got {item['boxBg']}"
            assert "rgb(237, 243, 248)" in item['boxBg'] or "rgba" in item['boxBg'], \
                f"Expected light subtle surface #edf3f8, got {item['boxBg']}"
            assert item['titleColor'] == "rgb(23, 32, 51)", \
                f"Expected title text #172033, got {item['titleColor']}"

        capture_screenshot("vercel_symptoms_light.png")
        print("  [PASS] Live Light Mode verified clean with zero black boxes!")

        # 2. Test Dark Mode
        print("\n--- STEP 2: Toggling Live Symptoms Guide to DARK MODE ---")
        eval_js("document.getElementById('themeToggleBtn').click();")
        time.sleep(0.5)
        
        dark_check = eval_js("""
        (() => {
            const boxes = document.querySelectorAll('.symptom-relation-box');
            const results = [];
            for (let i = 0; i < Math.min(5, boxes.length); i++) {
                const box = boxes[i];
                const card = box.closest('.card-custom') || box.parentElement;
                const title = card.querySelector('h5, h4') ? card.querySelector('h5, h4').textContent.trim() : ('Card ' + (i+1));
                const comp = window.getComputedStyle(box);
                const titleComp = window.getComputedStyle(box.querySelector('.symptom-relation-title') || box);
                results.push({
                    title,
                    boxBg: comp.backgroundColor,
                    boxBorder: comp.borderColor,
                    titleColor: titleComp.color
                });
            }
            return results;
        })()
        """)
        
        for idx, item in enumerate(dark_check):
            print(f"  Live Dark Card #{idx+1} '{item['title']}':")
            print(f"    - boxBg: {item['boxBg']}")
            print(f"    - boxBorder: {item['boxBorder']}")
            print(f"    - titleColor: {item['titleColor']}")
            assert item['boxBg'] == "rgb(15, 28, 43)", \
                f"Expected dark surface #0f1c2b (rgb(15, 28, 43)), got {item['boxBg']}"
            assert item['titleColor'] == "rgb(255, 255, 255)", \
                f"Expected dark-mode title text #ffffff (rgb(255, 255, 255)), got {item['titleColor']}"

        capture_screenshot("vercel_symptoms_dark.png")
        print("  [PASS] Live Dark Mode verified clean with high contrast!")

        # 3. Test Toggle Back to Light
        print("\n--- STEP 3: Toggling Back to Light Mode on Vercel ---")
        eval_js("document.getElementById('themeToggleBtn').click();")
        time.sleep(0.5)
        back_theme = eval_js("document.documentElement.getAttribute('data-theme')")
        assert back_theme == "light", f"Expected light mode, got {back_theme}"
        print("  [PASS] Live toggle back to light mode verified!")

        # 4. Search Filter Test
        print("\n--- STEP 4: Testing Client-Side Symptom Search on Vercel ---")
        eval_js("""
        const input = document.getElementById('symptomSearchInput');
        input.value = 'cough';
        input.dispatchEvent(new Event('input'));
        """)
        time.sleep(0.5)
        visible_cards = eval_js("""
        (() => {
            const cards = document.querySelectorAll('.symptom-guide-card');
            let visible = 0;
            cards.forEach(c => {
                if (c.style.display !== 'none') visible++;
            });
            return visible;
        })()
        """)
        print(f"  Filtered 'cough': {visible_cards} matching symptom cards visible")
        assert visible_cards > 0 and visible_cards < 58, f"Unexpected search filter results: {visible_cards}"
        print("  [PASS] Interactive search filtering works seamlessly!")

        # 5. Check Console Errors
        print(f"\nConsole exceptions on Vercel: {len(console_errors)}")
        assert len(console_errors) == 0, f"Console errors on Vercel: {console_errors}"

        print("\n============================================================")
        print("LIVE VERCEL SYMPTOMS GUIDE VERIFICATIONS PASSED 100%!")
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
    test_live_vercel_symptoms()
