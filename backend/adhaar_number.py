import pytesseract
import cv2
import re
from PIL import Image
import numpy as np

# Path to Aadhaar image
IMAGE_PATH = r"C:\Viresh\Projects\Web-Apps\adhaar-ocr-app\assets\front.jpg"

def preprocess_image(image_stream):
    """
    Convert image to grayscale and apply Otsu thresholding.
    """
    image = Image.open(image_stream).convert('RGB')
    image_np = np.array(image)
    gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh

def extract_text_from_image(processed_image):
    """
    Run OCR to get raw text from the image using legacy engine.
    """
    return pytesseract.image_to_string(
        processed_image
    )

def extract_aadhaar_number(text):
    """
    Use flexible regex to extract Aadhaar number from OCR text.
    """
    aadhaar_raw_matches = re.findall(r'(\d[\d\s\-]{10,})', text)
    for match in aadhaar_raw_matches:
        digits = re.sub(r'\D', '', match)
        if len(digits) == 12:
            formatted = ' '.join([digits[i:i+4] for i in range(0, 12, 4)])
            return formatted
    return None

def run_aadhaar_number_extraction(image_path):
    try:
        with open(image_path, 'rb') as img_file:
            print("🔍 Preprocessing image...")
            processed_image = preprocess_image(img_file)

            print("🧠 Running OCR...")
            raw_text = extract_text_from_image(processed_image)

            print("\n===== RAW OCR TEXT =====")
            print(raw_text)

            print("\n🔢 Extracting Aadhaar Number...")
            aadhaar_number = extract_aadhaar_number(raw_text)
            if aadhaar_number:
                print(f"✅ Aadhaar Number: {aadhaar_number}")
            else:
                print("❌ Aadhaar number not found.")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    run_aadhaar_number_extraction(IMAGE_PATH)
