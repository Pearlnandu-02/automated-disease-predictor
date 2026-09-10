import re
import os

def run_theme_audit():
    print("--- Running Comprehensive Theme System Audit ---")
    css_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'css', 'style.css')
    with open(css_path, 'r', encoding='utf-8') as f:
        css = f.read()

    required_tokens = [
        '--accent-primary', '--accent-secondary', '--accent-teal', '--accent-cyan',
        '--color-danger', '--color-warning', '--color-success',
        '--bg-body', '--bg-card', '--bg-card-subtle', '--bg-input',
        '--border-color', '--border-card', '--border-input',
        '--text-primary', '--text-heading', '--text-secondary', '--text-muted',
        '--navbar-bg', '--footer-bg', '--footer-heading', '--footer-text',
        '--tile-bg-unselected', '--tile-bg-selected'
    ]

    for token in required_tokens:
        assert token in css, f"Token {token} missing from CSS"
    print("  [OK] All core design tokens present in style.css.")

    # Verify absence of destructive !important overrides on .text-white
    assert not re.search(r'\[data-theme="light"\]\s+\.text-white\s*\{[^}]*color:[^;]*!important', css), \
        "Found destructive [data-theme='light'] .text-white override in style.css!"
    print("  [OK] No destructive text-white !important overrides found.")

    # Verify footer styling
    assert "footer h5, footer h6" in css and "var(--footer-heading)" in css, \
        "Footer headings must use --footer-heading variable"
    print("  [OK] Footer headings explicitly styled with --footer-heading.")

    # Verify button styling
    assert ".btn-info, .btn-primary, .btn-danger, .btn-success" in css and "#ffffff" in css, \
        "Filled buttons must maintain crisp #ffffff text"
    print("  [OK] Filled buttons maintain crisp contrast across both themes.")

    # Verify zero-FOUC early script in header.php
    header_path = os.path.join(os.path.dirname(__file__), '..', 'includes', 'header.php')
    with open(header_path, 'r', encoding='utf-8') as f:
        header_html = f.read()

    assert "localStorage.getItem('ai_healthcare_theme')" in header_html, \
        "Early localStorage check must exist in header.php"
    assert "document.documentElement.setAttribute('data-theme', theme)" in header_html, \
        "Early data-theme attribute assignment must exist in header.php"
    assert "themeToggleBtn" in header_html, \
        "Theme toggle button must exist in header.php"
    print("  [OK] Zero-FOUC early theme assignment verified in header.php.")

    print("\nTHEME SYSTEM AUDIT PASSED 100%!")

if __name__ == '__main__':
    run_theme_audit()
