import cv2
import numpy as np
import pytesseract
import re
import os

IMAGE_PATH = r"C:\Viresh\Projects\Web-Apps\adhaar-ocr-app\assets\back.jpg"
MAX_WIDTH = 500

def resize_for_display(image):
    h, w = image.shape[:2]
    if w > MAX_WIDTH:
        scale = MAX_WIDTH / w
        return cv2.resize(image, (int(w * scale), int(h * scale)))
    return image

def show(title, img):
    cv2.imshow(title, resize_for_display(img))

def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]  # top-left
    rect[2] = pts[np.argmax(s)]  # bottom-right
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # top-right
    rect[3] = pts[np.argmax(diff)]  # bottom-left
    return rect

def four_point_transform(image, pts):
    rect = order_points(pts)
    (tl, tr, br, bl) = rect
    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    maxWidth = max(int(widthA), int(widthB))
    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
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

def detect_and_extract_address(image_path):
    img = cv2.imread(image_path)
    if img is None:
        print("❌ Could not load image.")
        return

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_white = np.array([0, 0, 188])
    upper_white = np.array([180, 60, 255])
    mask = cv2.inRange(hsv, lower_white, upper_white)

    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        print("⚠️ No contours found.")
        return

    card_contour = max(contours, key=cv2.contourArea)
    peri = cv2.arcLength(card_contour, True)
    approx = cv2.approxPolyDP(card_contour, 0.02 * peri, True)

    if len(approx) != 4:
        print("⚠️ Detected contour is not rectangular.")
        return

    warped = four_point_transform(img, approx.reshape(4, 2))
    h, w = warped.shape[:2]
    print(f"📐 Warped image size: {w}x{h}")

    if w >= h:
        selected = warped[:, w//2:]
        print("📊 Orientation: Landscape → Selected Right Half")
    else:
        selected = warped[h//2:, :]
        print("📊 Orientation: Portrait → Selected Bottom Half")

    show("Selected English Half", selected)

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
    address, pincode = extract_address_and_pincode(text)

    print("\n===== EXTRACTED ADDRESS FIELDS =====")
    print(f"english_address: {address}")
    print(f"pincode: {pincode}")

    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    detect_and_extract_address(IMAGE_PATH)
