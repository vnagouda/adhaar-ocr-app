import cv2
import pytesseract
from PIL import Image
import re
import numpy as np

IMAGE_PATH = r"C:\Viresh\Projects\Web-Apps\adhaar-ocr-app\assets\front.jpg"

def preprocess_image(image_stream):
    image = Image.open(image_stream).convert('RGB')
    image_np = np.array(image)
    gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    filtered = cv2.bilateralFilter(gray, 9, 75, 75)
    return filtered

def extract_text_from_image(processed_image):
    raw_text = pytesseract.image_to_string(
        processed_image, config='--oem 3 --psm 6', lang='eng'
    )
    ocr_data = pytesseract.image_to_data(
        processed_image, output_type=pytesseract.Output.DICT
    )
    return raw_text, ocr_data

def extract_fields(text, ocr_data):
    data = {}
    clean_text = text.lower()

    # === Aadhaar number from OCR boxes ===
    digit_words = []
    for word in ocr_data['text']:
        word = word.strip()
        if word and word.replace(' ', '').isdigit() and 3 <= len(word.replace(' ', '')) <= 5:
            digit_words.append(word.replace(' ', ''))

    possible_number = ''.join(digit_words)
    if len(possible_number) >= 12:
        for i in range(0, len(possible_number) - 11):
            segment = possible_number[i:i+12]
            if segment.isdigit():
                data['aadhaar_number'] = ' '.join([segment[j:j+4] for j in range(0, 12, 4)])
                break

    # === Date of Birth ===
    dob_match = re.search(r'\d{2}/\d{2}/\d{4}', text)
    if dob_match:
        data['dob'] = dob_match.group()

    # === Gender ===
    if 'female' in clean_text:
        data['gender'] = 'Female'
    elif 'male' in clean_text:
        data['gender'] = 'Male'
    elif 'other' in clean_text:
        data['gender'] = 'Other'

    # === Name from adjacent high-confidence OCR boxes ===
    for i in range(len(ocr_data['text']) - 1):
        w1 = ocr_data['text'][i].strip()
        w2 = ocr_data['text'][i + 1].strip()
        if all(word.isalpha() for word in [w1, w2]) and w1 and w2:
            full_name = f"{w1} {w2}"
            if 2 <= len(full_name.split()) <= 5 and not any(kw in full_name.lower() for kw in ['dob', 'india', 'government', 'female', 'male', 'aadhaar']):
                data['name'] = full_name
                break

    return data

def test_aadhaar_ocr(image_path):
    try:
        with open(image_path, 'rb') as img_file:
            print("🔍 Preprocessing image...")
            processed_image = preprocess_image(img_file)

            print("🧠 Running OCR...")
            raw_text, ocr_data = extract_text_from_image(processed_image)

            print("\n===== RAW OCR TEXT =====")
            print(raw_text)

            print("\n📦 Extracting structured Aadhaar fields...")
            extracted_data = extract_fields(raw_text, ocr_data)

            print("\n===== EXTRACTED FIELDS =====")
            if extracted_data:
                for key, value in extracted_data.items():
                    print(f"{key}: {value}")
            else:
                print("No relevant fields found.")

    except FileNotFoundError:
        print(f"❌ Image file not found: {image_path}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_aadhaar_ocr(IMAGE_PATH)
