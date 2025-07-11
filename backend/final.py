import time
import cv2
import pytesseract
import numpy as np
import re
import os
from PIL import Image

# ====== CONFIG ======
FRONT_IMAGE_PATH = r"C:\Viresh\Projects\Web-Apps\adhaar-ocr-app\assets\front.jpg"
BACK_IMAGE_PATH = r"C:\Viresh\Projects\Web-Apps\adhaar-ocr-app\assets\back.jpg"
MAX_WIDTH = 500


# ====== DISPLAY HELPERS ======
def resize_for_display(image):
    h, w = image.shape[:2]
    if w > MAX_WIDTH:
        scale = MAX_WIDTH / w
        return cv2.resize(image, (int(w * scale), int(h * scale)))
    return image


# ====== UTILITY FUNCTIONS ======
def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def four_point_transform(image, pts):
    rect = order_points(pts)
    (tl, tr, br, bl) = rect
    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxWidth = max(int(widthA), int(widthB))
    maxHeight = max(int(heightA), int(heightB))
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]
    ], dtype="float32")
    M = cv2.getPerspectiveTransform(rect, dst)
    return cv2.warpPerspective(image, M, (maxWidth, maxHeight))

def detect_orientation(image):
    try:
        osd = pytesseract.image_to_osd(image)
        rotation = int(re.search(r'Rotate: (\d+)', osd).group(1))
        return rotation
    except:
        return 0

def rotate_image(image, angle):
    if angle == 90:
        return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    elif angle == 180:
        return cv2.rotate(image, cv2.ROTATE_180)
    elif angle == 270:
        return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return image


# ====== FRONT SIDE PROCESSING ======
def preprocess_image_full(image_stream):
    image = Image.open(image_stream).convert('RGB')
    image_np = np.array(image)
    gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    return cv2.bilateralFilter(gray, 9, 75, 75)

def preprocess_image_for_aadhaar(image_stream):
    image = Image.open(image_stream).convert('RGB')
    image_np = np.array(image)
    gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh

def extract_text_with_boxes(image):
    raw_text = pytesseract.image_to_string(image, config='--oem 3 --psm 6', lang='eng')
    ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    return raw_text, ocr_data

def extract_raw_text_only(image):
    return pytesseract.image_to_string(image)

def extract_aadhaar_number(text):
    aadhaar_raw_matches = re.findall(r'(\d[\d\s\-]{10,})', text)
    for match in aadhaar_raw_matches:
        digits = re.sub(r'\D', '', match)
        if len(digits) == 12:
            return ' '.join([digits[i:i+4] for i in range(0, 12, 4)])
    return None

def extract_remaining_fields(text, ocr_data):
    data = {}
    clean_text = text.lower()
    if m := re.search(r'\d{2}/\d{2}/\d{4}', text):
        data['dob'] = m.group()
    if 'female' in clean_text:
        data['gender'] = 'Female'
    elif 'male' in clean_text:
        data['gender'] = 'Male'
    elif 'other' in clean_text:
        data['gender'] = 'Other'

    ignore_words = {'dob', 'india', 'government', 'female', 'male', 'aadhaar'}
    for i in range(len(ocr_data['text']) - 1):
        w1 = ocr_data['text'][i].strip()
        w2 = ocr_data['text'][i + 1].strip()
        c1 = int(ocr_data['conf'][i])
        c2 = int(ocr_data['conf'][i + 1])
        if all(word.isalpha() for word in [w1, w2]) and c1 > 60 and c2 > 60:
            full_name = f"{w1} {w2}"
            if not any(kw in full_name.lower() for kw in ignore_words):
                data['name'] = full_name
                break
    return data

def extract_front_fields(image_path):
    time.sleep(1)
    with open(image_path, 'rb') as f1:
        print("🔍 Preprocessing image for name/dob/gender...")
        processed_main = preprocess_image_full(f1)
    print("🧠 Running OCR for fields...")
    raw_text_main, ocr_data_main = extract_text_with_boxes(processed_main)
    with open(image_path, 'rb') as f2:
        print("🔢 Preprocessing image for Aadhaar number...")
        processed_aadhaar = preprocess_image_for_aadhaar(f2)
    raw_text_aadhaar = extract_raw_text_only(processed_aadhaar)
    aadhaar_number = extract_aadhaar_number(raw_text_aadhaar)
    fields = extract_remaining_fields(raw_text_main, ocr_data_main)
    if aadhaar_number:
        fields['aadhaar_number'] = aadhaar_number
    return fields


# ====== BACK SIDE PROCESSING ======
def extract_address_and_pincode(text):
    lines = text.splitlines()
    capture = False
    address_lines = []
    pincode = None
    for line in lines:
        clean = line.strip()
        if not clean:
            continue
        if not capture and 'address' in clean.lower():
            capture = True
            continue
        if capture:
            if re.search(r'\b\d{6}\b', clean):
                pincode = re.search(r'\b\d{6}\b', clean).group()
                break
            address_lines.append(clean)
    return ' '.join(address_lines).strip(), pincode

def extract_back_address(image_path):
    time.sleep(1)
    img = cv2.imread(image_path)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_white = np.array([0, 0, 188])
    upper_white = np.array([180, 60, 255])
    mask = cv2.inRange(hsv, lower_white, upper_white)
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    card_contour = max(contours, key=cv2.contourArea)
    peri = cv2.arcLength(card_contour, True)
    approx = cv2.approxPolyDP(card_contour, 0.02 * peri, True)
    try:
        if approx.shape[0] != 4:
            print(f"⚠️ Detected contour with shape {approx.shape}, using bounding rectangle fallback")
            x, y, w, h = cv2.boundingRect(approx)
            box = np.array([
                [x, y],
                [x + w, y],
                [x + w, y + h],
                [x, y + h]
            ], dtype=np.float32)
        else:
            box = approx.reshape(4, 2)

        warped = four_point_transform(img, box)
    except Exception as e:
        print(f"❌ Contour transform failed: {e}")
        return None, None
    h, w = warped.shape[:2]
    print(f"📐 Warped image size: {w}x{h}")
    if w >= h:
        selected = warped[:, w//2:]
        print("📊 Orientation: Landscape → Selected Right Half")
    else:
        selected = warped[h//2:, :]
        print("📊 Orientation: Portrait → Selected Bottom Half")
    print("🧭 Detecting orientation...")
    rotation = detect_orientation(cv2.cvtColor(selected, cv2.COLOR_BGR2GRAY))
    rotated = rotate_image(selected, rotation)
    print(f"🔄 Detected rotation: {rotation}° → Image rotated.")
    print("🧠 Running OCR...")
    text = pytesseract.image_to_string(
        cv2.cvtColor(rotated, cv2.COLOR_BGR2GRAY),
        config='--oem 3 --psm 6',
        lang='eng'
    )
    print("\n===== RAW OCR TEXT =====")
    print(text)
    print("\n📦 Extracting structured address...")
    return extract_address_and_pincode(text)


# ====== MAIN ======
if __name__ == "__main__":
    print("📄 Running OCR for FRONT...")
    front_fields = extract_front_fields(FRONT_IMAGE_PATH)

    print("\n🏠 Running OCR for BACK...")
    address, pincode = extract_back_address(BACK_IMAGE_PATH)

    print("\n======= FINAL OUTPUT =======")
    for k, v in front_fields.items():
        print(f"{k}: {v}")
    print(f"english_address: {address}")
    print(f"pincode: {pincode}")

    cv2.waitKey(0)
    cv2.destroyAllWindows()
