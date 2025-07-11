import pytesseract
import cv2
import re
from PIL import Image
import numpy as np

def preprocess_image(image_stream):
    """
    Convert input image to grayscale and apply thresholding to improve OCR.
    """
    image = Image.open(image_stream).convert('RGB')
    image_np = np.array(image)
    gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh

def extract_text_from_image(processed_image):
    """
    Run Tesseract OCR on the processed image.
    """
    return pytesseract.image_to_string(processed_image)

def extract_fields(text):
    """
    Use regex to extract Aadhaar-related fields from OCR text.
    """
    data = {}

    # Normalize the text
    clean_text = text.lower()

    # Aadhaar number (format: XXXX XXXX XXXX)
    aadhaar_match = re.search(r'\b\d{4}\s\d{4}\s\d{4}\b', text)
    if aadhaar_match:
        data['aadhaar_number'] = aadhaar_match.group()

    # Date of Birth (format: dd/mm/yyyy or yyyy)
    dob_match = re.search(r'(\d{2}/\d{2}/\d{4})|(\d{4})', text)
    if dob_match:
        data['dob'] = dob_match.group()

    # Gender detection (more robust)
    if re.search(r'\bfemale\b', clean_text):
        data['gender'] = 'Female'
    elif re.search(r'\bmale\b', clean_text):
        data['gender'] = 'Male'
    elif re.search(r'\bother\b', clean_text):
        data['gender'] = 'Other'

    # Name detection – first all-uppercase line that’s not a known keyword
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if line.isupper() and not any(keyword in line for keyword in ['GOVERNMENT', 'INDIA', 'UNION', 'AADHAAR', 'DOB', 'YEAR', 'MALE', 'FEMALE']):
            data['name'] = line.title()
            break

    return data