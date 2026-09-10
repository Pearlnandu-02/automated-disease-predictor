import subprocess
import time
import json
import urllib.request
import os
import websocket
import base64

def test_scanner_contrast():
    print("============================================================")
    print("TESTING SCANNER HERO CONTRAST & RESPONSIVENESS VIA CDP")
    print("============================================================")

    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    tmp_dir = os.path.join(os.environ.get("TEMP", "C:\\temp"), "edge_cdp_scanner_contrast")
    os.makedirs(tmp_dir, exist_ok=True)

    port = 9230
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
        "http://127.0.0.1:8000/image_scanner.php"
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
                resp = json.loads(ws.recv())
                if resp.get("method") == "Runtime.consoleAPICalled":
                    args_val = [a.get("value", "") for a in resp.get("params", {}).get("args", [])]
                    if resp.get("params", {}).get("type") == "error":
                        console_errors.append(" ".join(str(v) for v in args_val))
                if resp.get("id") == msg_id:
                    return resp.get("result", {})

        send_cdp("Runtime.enable")
        send_cdp("Page.enable")

        # Wait for page load
        time.sleep(1.5)

        def eval_js(expression):
            res = send_cdp("Runtime.evaluate", {"expression": expression, "returnByValue": True})
            return res.get("result", {}).get("value")

        def take_screenshot(filename, clip_rect=None):
            params = {"format": "png"}
            if clip_rect:
                params["clip"] = clip_rect
            res = send_cdp("Page.captureScreenshot", params)
            data = base64.b64decode(res["data"])
            artifact_dir = r"C:\Users\Pearl\.gemini\antigravity-ide\brain\293bb488-1883-4cab-8067-3cfa9f62fc24"
            out_path = os.path.join(artifact_dir, filename)
            with open(out_path, "wb") as f:
                f.write(data)
            print(f"  [SAVED SCREENSHOT] {filename} -> {out_path}")

        # -------------------------------------------------------------
        # STEP 1: TEST IN LIGHT MODE
        # -------------------------------------------------------------
        print("\n--- 1. Testing Light Mode ---")
        eval_js("""
            document.documentElement.setAttribute('data-theme', 'light');
            document.documentElement.setAttribute('data-bs-theme', 'light');
            localStorage.setItem('theme', 'light');
        """)
        time.sleep(0.5)

        light_metrics = eval_js("""
            (() => {
                const hero = document.querySelector('.scanner-hero-banner');
                const heading = document.querySelector('.scanner-hero-banner h1');
                const subtitle = document.querySelector('.scanner-hero-banner .hero-lead');
                const badge = document.querySelector('.scanner-hero-banner .hero-badge');
                const notice = document.querySelector('.disclaimer-banner');
                const noticeTitle = document.querySelector('.disclaimer-banner strong, .disclaimer-banner .disclaimer-title');
                const noticeIcon = document.querySelector('.disclaimer-banner .bi-exclamation-triangle-fill');
                
                const getProps = (el) => {
                    if (!el) return null;
                    const cs = window.getComputedStyle(el);
                    return {
                        color: cs.color,
                        background: cs.background,
                        backgroundColor: cs.backgroundColor,
                        fontWeight: cs.fontWeight,
                        fontSize: cs.fontSize,
                        border: cs.border,
                        borderLeftColor: cs.borderLeftColor,
                        borderTopWidth: cs.borderTopWidth
                    };
                };

                return {
                    hero: getProps(hero),
                    heading: getProps(heading),
                    subtitle: getProps(subtitle),
                    badge: getProps(badge),
                    notice: getProps(notice),
                    noticeTitle: getProps(noticeTitle),
                    noticeIcon: getProps(noticeIcon),
                    theme: document.documentElement.getAttribute('data-theme')
                };
            })()
        """)

        print(f"  Light Mode Theme: {light_metrics['theme']}")
        print(f"  Hero Heading Color: {light_metrics['heading']['color']} (Font Weight: {light_metrics['heading']['fontWeight']})")
        print(f"  Hero Subtitle Color: {light_metrics['subtitle']['color']}")
        print(f"  Hero Badge Color: {light_metrics['badge']['color']}, BG: {light_metrics['badge']['backgroundColor']}")
        print(f"  Notice Text Color: {light_metrics['notice']['color']}, Border-Left: {light_metrics['notice']['borderLeftColor']}")
        print(f"  Notice Title Color: {light_metrics['noticeTitle']['color']}")

        # Validate heading is pure white
        assert light_metrics['heading']['color'] == 'rgb(255, 255, 255)', f"Heading must be white in light mode, got {light_metrics['heading']['color']}"
        assert int(light_metrics['heading']['fontWeight']) >= 700, "Heading must be bold"

        # Validate subtitle is light text
        sub_color = light_metrics['subtitle']['color']
        assert "255, 255, 255" in sub_color or "226, 232, 240" in sub_color, f"Subtitle must be light text, got {sub_color}"

        # Capture Light Mode screenshot
        take_screenshot("scanner_hero_light.png")

        # -------------------------------------------------------------
        # STEP 2: TEST IN DARK MODE
        # -------------------------------------------------------------
        print("\n--- 2. Testing Dark Mode ---")
        eval_js("""
            document.documentElement.setAttribute('data-theme', 'dark');
            document.documentElement.setAttribute('data-bs-theme', 'dark');
            localStorage.setItem('theme', 'dark');
        """)
        time.sleep(0.5)

        dark_metrics = eval_js("""
            (() => {
                const heading = document.querySelector('.scanner-hero-banner h1');
                const subtitle = document.querySelector('.scanner-hero-banner .hero-lead');
                const badge = document.querySelector('.scanner-hero-badge, .scanner-hero-banner .hero-badge');
                const notice = document.querySelector('.disclaimer-banner');
                const noticeTitle = document.querySelector('.disclaimer-banner strong, .disclaimer-banner .disclaimer-title');
                
                const getProps = (el) => {
                    if (!el) return null;
                    const cs = window.getComputedStyle(el);
                    return {
                        color: cs.color,
                        background: cs.background,
                        backgroundColor: cs.backgroundColor,
                        fontWeight: cs.fontWeight
                    };
                };

                return {
                    heading: getProps(heading),
                    subtitle: getProps(subtitle),
                    badge: getProps(badge),
                    notice: getProps(notice),
                    noticeTitle: getProps(noticeTitle),
                    theme: document.documentElement.getAttribute('data-theme')
                };
            })()
        """)

        print(f"  Dark Mode Theme: {dark_metrics['theme']}")
        print(f"  Hero Heading Color: {dark_metrics['heading']['color']}")
        print(f"  Hero Subtitle Color: {dark_metrics['subtitle']['color']}")
        print(f"  Hero Badge Color: {dark_metrics['badge']['color']}")
        print(f"  Notice Text Color: {dark_metrics['notice']['color']}")
        print(f"  Notice Title Color: {dark_metrics['noticeTitle']['color']}")

        assert dark_metrics['heading']['color'] == 'rgb(255, 255, 255)', f"Heading must be white in dark mode, got {dark_metrics['heading']['color']}"

        take_screenshot("scanner_hero_dark.png")

        # -------------------------------------------------------------
        # STEP 3: RESPONSIVE CHECKS
        # -------------------------------------------------------------
        print("\n--- 3. Testing Responsive Viewports ---")
        viewports = [
            (1920, 1080, "Desktop 1920px"),
            (1366, 768, "Laptop 1366px"),
            (768, 1024, "Tablet 768px"),
            (480, 800, "Mobile 480px"),
            (375, 667, "Small Mobile 375px")
        ]

        for w, h, label in viewports:
            send_cdp("Emulation.setDeviceMetricsOverride", {
                "width": w,
                "height": h,
                "deviceScaleFactor": 1,
                "mobile": (w < 768)
            })
            time.sleep(0.3)

            resp_info = eval_js(f"""
                (() => {{
                    const h1 = document.querySelector('.scanner-hero-banner h1');
                    const hero = document.querySelector('.scanner-hero-banner');
                    const body = document.body;
                    return {{
                        h1FontSize: window.getComputedStyle(h1).fontSize,
                        h1OffsetWidth: h1.offsetWidth,
                        heroOffsetWidth: hero.offsetWidth,
                        windowInnerWidth: window.innerWidth,
                        hasHorizontalOverflow: body.scrollWidth > window.innerWidth + 1
                    }};
                }})()
            """)

            print(f"  [{label}] innerWidth: {resp_info['windowInnerWidth']}px | H1 font: {resp_info['h1FontSize']} | H1 width: {resp_info['h1OffsetWidth']}px | Hero width: {resp_info['heroOffsetWidth']}px | Overflow: {resp_info['hasHorizontalOverflow']}")
            assert not resp_info['hasHorizontalOverflow'], f"Horizontal overflow detected at {label}"

            if w == 375:
                # Switch back to light mode to capture mobile in light mode
                eval_js("document.documentElement.setAttribute('data-theme', 'light'); document.documentElement.setAttribute('data-bs-theme', 'light');")
                time.sleep(0.3)
                take_screenshot("scanner_mobile_375.png")

        # Check console errors
        print(f"\n--- 4. Console Log Audit ---")
        print(f"  Console errors detected: {len(console_errors)}")
        for err in console_errors:
            print(f"    ERROR: {err}")
        assert len(console_errors) == 0, f"Found console errors: {console_errors}"

        print("\nALL SCANNER HERO CONTRAST & RESPONSIVENESS TESTS PASSED SUCCESSFULLY!")

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()

if __name__ == "__main__":
    test_scanner_contrast()
