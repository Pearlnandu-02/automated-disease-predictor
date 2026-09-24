import urllib.request
import io
import uuid
import os
import json
from PIL import Image

def test_reference_image():
    ref_path = r"C:\Users\Pearl\Downloads\WhatsApp Image 2026-09-10 at 10.43.37 AM.jpeg"
    if not os.path.exists(ref_path):
        print(f"Reference image not found at {ref_path}")
        return

    with open(ref_path, 'rb') as f:
        img_bytes = f.read()

    boundary = '----WebKitFormBoundary' + uuid.uuid4().hex
    header_part = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="image"; filename="reference_lesion_test.jpeg"\r\n'
        f'Content-Type: image/jpeg\r\n\r\n'
    ).encode('utf-8')
    footer_part = f'\r\n--{boundary}--\r\n'.encode('utf-8')
    body = header_part + img_bytes + footer_part

    headers = {
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'X-Requested-With': 'XMLHttpRequest'
    }

    req = urllib.request.Request('http://127.0.0.1:8000/image_scanner.php?action=scan', data=body, headers=headers)
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode('utf-8'))

    print("=== Reference Lesion Test Results ===")
    print(f"Success: {res.get('success')}")
    print(f"Status: {res.get('status')}")
    print(f"Category: {res.get('category')}")
    print(f"Is Unsupported Lesion: {res.get('is_unsupported_lesion')}")
    print(f"Confidence Score: {res.get('confidence_score')}")
    print(f"Findings: {res.get('findings')}")
    print(f"What Detected: {res.get('what_detected')}")
    print(f"Technical Features: {res.get('technical_image_features')}")
    print(f"Recommended Next Step: {res.get('recommended_next_step')}")

    # Assertions based on User Prompt requirements:
    assert res.get('success') is True, "Expected success: True"
    assert res.get('is_unsupported_lesion') is True, "Expected is_unsupported_lesion: True"
    assert res.get('status') == 'unsupported_lesion', "Expected status: unsupported_lesion"
    assert res.get('category') == 'Unable to Assess', "Expected category: Unable to Assess"
    assert res.get('confidence_score') is None or res.get('confidence_score') == 0.0, "Score must not be fake 76.8%"
    
    # Must NOT classify as Rash/Skin Irritation
    assert 'Rash' not in res.get('category'), "Must NOT misclassify as Rash"
    
    # Check educational warning
    rec = res.get('recommended_next_step', '')
    assert 'dermatologist' in rec.lower() or 'healthcare professional' in rec.lower(), "Must advise seeking professional care"
    
    findings_text = " ".join(res.get('findings', []))
    assert 'does not support reliable classification' in findings_text, "Must clearly state scanner does not support this type of skin lesion"

    print("\nSUCCESS: Reference test case correctly recognized as unsupported skin lesion, safely rejected, and directed to dermatological care without fake classification!")

if __name__ == '__main__':
    test_reference_image()
