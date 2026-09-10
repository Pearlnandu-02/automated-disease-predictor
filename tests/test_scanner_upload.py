import urllib.request
import io
import uuid
from PIL import Image
import numpy as np
import json

def upload_synthetic_image(arr, filename="test.jpg"):
    img = Image.fromarray(arr)
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    img_bytes = buf.getvalue()

    boundary = '----WebKitFormBoundary' + uuid.uuid4().hex
    header_part = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="image"; filename="{filename}"\r\n'
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
        return json.loads(resp.read().decode('utf-8'))

def run_tests():
    print("Test 1: Valid erythema / wound pattern...")
    arr_wound = np.full((160, 160, 3), [220, 60, 60], dtype=np.uint8)
    arr_wound[40:80, 40:80] = [80, 20, 20]
    res1 = upload_synthetic_image(arr_wound, "wound.jpg")
    print(f"  Category: {res1.get('category')} | Score: {res1.get('confidence_score')}%")
    assert res1.get('success') is True
    assert res1.get('category') != 'Unable to Assess'

    print("Test 2: Underexposed / black image (Quality Gate)...")
    arr_dark = np.full((120, 120, 3), 10, dtype=np.uint8)
    res2 = upload_synthetic_image(arr_dark, "dark.jpg")
    print(f"  Category: {res2.get('category')} | Findings: {res2.get('findings')}")
    assert res2.get('category') == 'Unable to Assess'
    assert 'underexposed' in res2.get('findings')[0].lower()

    print("Test 3: Overexposed / washed out image (Quality Gate)...")
    arr_bright = np.full((120, 120, 3), 250, dtype=np.uint8)
    res3 = upload_synthetic_image(arr_bright, "bright.jpg")
    print(f"  Category: {res3.get('category')} | Findings: {res3.get('findings')}")
    assert res3.get('category') == 'Unable to Assess'
    assert 'overexposed' in res3.get('findings')[0].lower()

    print("Test 4: High surface roughness / laceration...")
    arr_cut = np.full((160, 160, 3), [180, 120, 100], dtype=np.uint8)
    # Add sharp cut line
    arr_cut[20:140, 78:82] = [30, 10, 10]
    res4 = upload_synthetic_image(arr_cut, "cut.jpg")
    print(f"  Category: {res4.get('category')} | Score: {res4.get('confidence_score')}%")
    assert res4.get('success') is True

    print("\nALL SCANNER UNIT TESTS PASSED!")

if __name__ == '__main__':
    run_tests()
