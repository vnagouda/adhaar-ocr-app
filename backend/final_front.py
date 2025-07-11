import cv2
import pytesseract
from PIL import Image
import re
import numpy as np

IMAGE_PATH = r"C:\Viresh\Projects\Web-Apps\adhaar-ocr-app\assets\front.jpg"

# === Preprocess for name/dob/gender ===
def preprocess_image_full(image_stream):
    image = Image.open(image_stream).convert('RGB')
    image_np = np.array(image)
    gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    filtered = cv2.bilateralFilter(gray, 9, 75, 75)
    return filtered

# === Preprocess for Aadhaar number ===
def preprocess_image_for_aadhaar(image_stream):
    image = Image.open(image_stream).convert('RGB')
    image_np = np.array(image)
    gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh

# === OCR functions ===
def extract_text_with_boxes(image):
    raw_text = pytesseract.image_to_string(image, config='--oem 3 --psm 6', lang='eng')
    ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    return raw_text, ocr_data

def extract_raw_text_only(image):
    return pytesseract.image_to_string(image)

# === Aadhaar number extractor ===
def extract_aadhaar_number(text):
    aadhaar_raw_matches = re.findall(r'(\d[\d\s\-]{10,})', text)
    for match in aadhaar_raw_matches:
        digits = re.sub(r'\D', '', match)
        if len(digits) == 12:
            return ' '.join([digits[i:i+4] for i in range(0, 12, 4)])
    return None

# === Extract Name, DOB, Gender ===
def extract_remaining_fields(text, ocr_data):
    data = {}
    clean_text = text.lower()

    # DOB
    dob_match = re.search(r'\d{2}/\d{2}/\d{4}', text)
    if dob_match:
        data['dob'] = dob_match.group()

    # Gender
    if 'female' in clean_text:
        data['gender'] = 'Female'
    elif 'male' in clean_text:
        data['gender'] = 'Male'
    elif 'other' in clean_text:
        data['gender'] = 'Other'

    # Name from OCR boxes (with confidence filtering)
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

# === Main runner ===
def test_full_aadhaar_extraction(image_path):
    try:
        # Step 1: Preprocess for name/dob/gender
        with open(image_path, 'rb') as img_file_1:
            print("🔍 Preprocessing image for name/dob/gender...")
            processed_main = preprocess_image_full(img_file_1)

        print("🧠 Running OCR for fields...")
        raw_text_main, ocr_data_main = extract_text_with_boxes(processed_main)

        # Step 2: Preprocess again for Aadhaar number
        with open(image_path, 'rb') as img_file_2:
            print("🔢 Preprocessing image for Aadhaar number...")
            processed_aadhaar = preprocess_image_for_aadhaar(img_file_2)

        raw_text_aadhaar = extract_raw_text_only(processed_aadhaar)
        aadhaar_number = extract_aadhaar_number(raw_text_aadhaar)

        # Step 3: Extract name, dob, gender
        fields = extract_remaining_fields(raw_text_main, ocr_data_main)
        if aadhaar_number:
            fields['aadhaar_number'] = aadhaar_number

        print("\n===== EXTRACTED FIELDS =====")
        if fields:
            for key, value in fields.items():
                print(f"{key}: {value}")
        else:
            print("❌ No relevant fields found.")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_full_aadhaar_extraction(IMAGE_PATH)
