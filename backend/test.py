import cv2
import pytesseract
import matplotlib.pyplot as plt
from ocr_utils import preprocess_image, extract_fields

# OPTIONAL: Uncomment this line if pytesseract can’t find Tesseract on your machine
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ✅ Aadhaar front image path
IMAGE_PATH = r"C:\Viresh\Projects\Web-Apps\adhaar-ocr-app\assets\front.jpg"

# === OCR + Visualization Functions ===

def extract_text_from_image(image):
    """Run OCR and return raw text and full OCR data"""
    raw_text = pytesseract.image_to_string(image)
    ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    return raw_text, ocr_data

def visualize_ocr_boxes(image, ocr_data):
    """Show image with OCR bounding boxes and words"""
    img = image.copy()
    for i in range(len(ocr_data['text'])):
        if int(ocr_data['conf'][i]) > 60:
            x, y, w, h = ocr_data['left'][i], ocr_data['top'][i], ocr_data['width'][i], ocr_data['height'][i]
            text = ocr_data['text'][i]
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(img, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1, cv2.LINE_AA)

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    plt.figure(figsize=(12, 12))
    plt.imshow(img_rgb)
    plt.title("🔍 OCR Debug Visualization")
    plt.axis('off')
    plt.show()

# === Main Aadhaar OCR Test ===

def test_aadhaar_ocr(image_path):
    try:
        with open(image_path, 'rb') as img_file:
            print("🔍 Preprocessing image...")
            processed_image = preprocess_image(img_file)

            print("🧠 Running OCR...")
            raw_text, ocr_data = extract_text_from_image(processed_image)

            print("\n===== RAW OCR TEXT =====")
            print(raw_text)

            print("\n🖼️ Showing OCR debug image...")
            visualize_ocr_boxes(processed_image, ocr_data)

            print("\n📦 Extracting structured Aadhaar fields...")
            extracted_data = extract_fields(raw_text)

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
