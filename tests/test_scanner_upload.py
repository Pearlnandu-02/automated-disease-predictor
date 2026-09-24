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

def upload_file_path(file_path, filename=None):
    if filename is None:
        filename = os.path.basename(file_path)
    with open(file_path, 'rb') as f:
        img_bytes = f.read()

    mime = 'image/jpeg'
    if filename.lower().endswith('.avif'):
        mime = 'image/avif'
    elif filename.lower().endswith('.png'):
        mime = 'image/png'
    elif filename.lower().endswith('.webp'):
        mime = 'image/webp'

    boundary = '----WebKitFormBoundary' + uuid.uuid4().hex
    header_part = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="image"; filename="{filename}"\r\n'
        f'Content-Type: {mime}\r\n\r\n'
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
    print(f"  Category: {res1.get('category')} | Model Conf: {res1.get('model_confidence')}")
    assert res1.get('success') is True
    assert 'Unable' not in res1.get('category')

    print("Test 2: Underexposed / black image (Quality Gate)...")
    arr_dark = np.full((120, 120, 3), 10, dtype=np.uint8)
    res2 = upload_synthetic_image(arr_dark, "dark.jpg")
    print(f"  Category: {res2.get('category')} | Findings: {res2.get('findings')}")
    assert 'Unable' in res2.get('category')
    assert any('underexposed' in f.lower() for f in res2.get('findings', []))

    print("Test 3: Overexposed / washed out image (Quality Gate)...")
    arr_bright = np.full((120, 120, 3), 250, dtype=np.uint8)
    res3 = upload_synthetic_image(arr_bright, "bright.jpg")
    print(f"  Category: {res3.get('category')} | Findings: {res3.get('findings')}")
    assert 'Unable' in res3.get('category')
    assert any('overexposed' in f.lower() for f in res3.get('findings', []))

    print("Test 4: High surface roughness / laceration...")
    arr_cut = np.full((160, 160, 3), [180, 120, 100], dtype=np.uint8)
    arr_cut[20:140, 78:82] = [30, 10, 10]
    res4 = upload_synthetic_image(arr_cut, "cut.jpg")
    print(f"  Category: {res4.get('category')} | Model Conf: {res4.get('model_confidence')}")
    assert res4.get('success') is True

    print("\nTest 5: Testing 4 distinct image fixtures for dynamic metrics...")
    fixtures = [
        'tests/fixtures/infection_wound.jpg',
        'tests/fixtures/minor_abrasion.jpg',
        'tests/fixtures/rash_irritation.jpg',
        'tests/fixtures/swelling_bruise.jpg'
    ]
    seen_categories = set()
    for fix in fixtures:
        with open(fix, 'rb') as f:
            arr = np.array(Image.open(f))
        res = upload_synthetic_image(arr, fix.split('/')[-1])
        cat = res.get('category')
        seen_categories.add(cat)
        print(f"  Fixture {fix.split('/')[-1]}: {cat} | Conf: {res.get('model_confidence')} | EI: {res.get('metrics', {}).get('erythema_index')} | Roughness: {res.get('metrics', {}).get('surface_roughness')}")
        assert res.get('success') is True
        assert 'Unable' not in cat
        assert res.get('model_confidence') is not None
        assert res.get('metrics', {}).get('surface_roughness') is not None
        assert res.get('metrics', {}).get('erythema_index') is not None

    print(f"  Distinct categories observed: {seen_categories}")

    # Test 6: Cancer reference image (if exists)
    cancer_path = r"C:\Users\Pearl\Downloads\cancer.avif"
    if os.path.exists(cancer_path):
        print("\nTest 6: Testing cancer reference image (cancer.avif)...")
        res_cancer = upload_file_path(cancer_path)
        cat_cancer = res_cancer.get('category')
        pred_cancer = res_cancer.get('prediction')
        conf_cancer = res_cancer.get('confidence_score')
        model_conf_cancer = res_cancer.get('model_confidence')
        print(f"  Result Category: {cat_cancer}")
        print(f"  Prediction: {pred_cancer}")
        print(f"  Confidence Score: {conf_cancer}")
        print(f"  Model Confidence: {model_conf_cancer}")
        print(f"  Is Concerning Lesion: {res_cancer.get('is_concerning_lesion')}")
        print(f"  Findings: {res_cancer.get('findings')}")
        assert cat_cancer == "Potentially Concerning Skin Lesion"
        assert pred_cancer == "Potentially Concerning Skin Lesion"
        assert conf_cancer is None, "Confidence score must be None (no fake percentages)"
        assert res_cancer.get('is_concerning_lesion') is True
        print("  PASS: Cancer reference image correctly identified as Potentially Concerning Skin Lesion with NO fake confidence!")

    print("\nALL SCANNER UNIT TESTS PASSED!")

if __name__ == '__main__':
    import os
    run_tests()

