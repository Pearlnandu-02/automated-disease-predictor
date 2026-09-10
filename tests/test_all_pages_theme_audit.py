import subprocess
import time
import json
import urllib.request
import os
import websocket

def run_multipage_and_responsive_audit():
    print("============================================================")
    print("STARTING MULTI-PAGE & RESPONSIVE THEME CONTRAST AUDIT")
    print("============================================================")
    
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    tmp_dir = os.path.join(os.environ.get("TEMP", "C:\\temp"), "edge_cdp_multipage")
    os.makedirs(tmp_dir, exist_ok=True)
    
    port = 9224
    args = [
        edge_path,
        "--headless",
        "--disable-gpu",
        f"--remote-debugging-port={port}",
        "--remote-allow-origins=*",
        f"--user-data-dir={tmp_dir}",
        "--window-size=1280,900",
        "http://127.0.0.1:8000/symptoms_guide.php"
    ]
    
    proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/json") as resp:
            tabs = json.loads(resp.read().decode('utf-8'))
            ws_url = tabs[0]["webSocketDebuggerUrl"]
        
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
            time.sleep(1.2)
            
        def set_viewport(width, height):
            send_cdp("Emulation.setDeviceMetricsOverride", {
                "width": width,
                "height": height,
                "deviceScaleFactor": 1,
                "mobile": (width < 768)
            })
            time.sleep(0.3)

        # 1. Responsive Viewport Check on Symptoms Guide
        print("\n--- 1. Testing Symptoms Guide Responsiveness ---")
        for width, device in [(1280, "Desktop"), (768, "Tablet"), (375, "Mobile")]:
            set_viewport(width, 800)
            overflow_issues = eval_js("""
            (() => {
                const boxes = document.querySelectorAll('.symptom-relation-box');
                let overflowing = 0;
                boxes.forEach(b => {
                    if (b.scrollWidth > b.clientWidth + 2) {
                        overflowing++;
                    }
                });
                return { count: boxes.length, overflowing };
            })()
            """)
            print(f"  [{device} - {width}px] Symptom boxes: {overflow_issues['count']}, Horizontal overflow: {overflow_issues['overflowing']}")
            assert overflow_issues['overflowing'] == 0, f"Horizontal overflow detected on {device} ({width}px)!"

        # Reset viewport
        set_viewport(1280, 900)

        # 2. Check Other Pages in LIGHT MODE for Black Boxes or Dark Bg + Dark Text
        pages = [
            ("symptoms_guide.php", "Symptoms Guide"),
            ("prevention.php", "Prevention"),
            ("diseases.php", "Diseases Library"),
            ("disease_detail.php?id=1", "Disease Detail (Diabetes)"),
            ("assessment.php", "Clinical Risk Assessment"),
            ("simulator.php", "Health Simulator"),
            ("prediction.php", "AI Prediction"),
            ("image_scanner.php", "Image Scanner"),
            ("dashboard.php", "Dashboard")
        ]

        print("\n--- 2. Auditing Other Pages in LIGHT MODE ---")
        eval_js("applyTheme('light');")
        
        for page_file, page_name in pages:
            url = f"http://127.0.0.1:8000/{page_file}"
            navigate(url)
            eval_js("applyTheme('light');")
            time.sleep(0.5)
            
            # Inspect all cards, boxes, badges, callouts for black box in light mode
            dark_boxes = eval_js("""
            (() => {
                const elements = document.querySelectorAll('.card-custom, .symptom-relation-box, .bg-card-subtle, .alert, .badge, div[class*="card"], div[class*="box"]');
                const darkOnes = [];
                elements.forEach(el => {
                    const comp = window.getComputedStyle(el);
                    const bg = comp.backgroundColor;
                    // Check if background is black or very dark (r < 50, g < 50, b < 50, a > 0.8)
                    const match = bg.match(/rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)(?:,\\s*([\\d.]+))?\\)/);
                    if (match) {
                        const r = parseInt(match[1]);
                        const g = parseInt(match[2]);
                        const b = parseInt(match[3]);
                        const a = match[4] !== undefined ? parseFloat(match[4]) : 1.0;
                        if (r < 40 && g < 40 && b < 40 && a > 0.8) {
                            darkOnes.push({
                                tag: el.tagName,
                                class: el.className,
                                text: el.innerText ? el.innerText.slice(0, 30) : '',
                                bg: bg,
                                color: comp.color
                            });
                        }
                    }
                });
                return darkOnes;
            })()
            """)
            print(f"  Page '{page_name}' ({page_file}): {len(dark_boxes)} dark-box elements found")
            if dark_boxes:
                for db in dark_boxes:
                    print(f"    WARNING: Dark box: <{db['tag']} class='{db['class']}'> bg={db['bg']} color={db['color']}")
            assert len(dark_boxes) == 0, f"Found unexpected dark box on page {page_name} in Light Mode!"

        # 3. Check Pages in DARK MODE for High Contrast and Dark Surfaces
        print("\n--- 3. Auditing Pages in DARK MODE ---")
        for page_file, page_name in [("symptoms_guide.php", "Symptoms Guide"), ("prevention.php", "Prevention"), ("diseases.php", "Diseases")]:
            url = f"http://127.0.0.1:8000/{page_file}"
            navigate(url)
            eval_js("applyTheme('dark');")
            time.sleep(0.5)
            
            theme = eval_js("document.documentElement.getAttribute('data-theme')")
            assert theme == "dark"
            
            # Check that text is readable light
            text_color = eval_js("window.getComputedStyle(document.body).color")
            bg_color = eval_js("window.getComputedStyle(document.body).backgroundColor")
            print(f"  Dark Mode '{page_name}': body bg={bg_color}, body text={text_color}")
            assert bg_color in ["rgb(11, 22, 36)", "rgb(7, 14, 23)"], f"Unexpected body bg in dark mode: {bg_color}"

        print("\n============================================================")
        print("ALL MULTI-PAGE & RESPONSIVE THEME AUDITS PASSED 100%!")
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
    run_multipage_and_responsive_audit()
