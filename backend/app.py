from datetime import datetime
from flask import Flask, request
import os
import requests
import time
from dotenv import load_dotenv
from PIL import ImageFile
import pandas as pd
from final import extract_front_fields, extract_back_address

# Load .env variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# Setup
ImageFile.LOAD_TRUNCATED_IMAGES = True
app = Flask(__name__)
UPLOAD_DIR = "uploads"
CSV_FILE = "aadhaar_data.csv"
os.makedirs(UPLOAD_DIR, exist_ok=True)

recent_trigger = {}  # phone_number: timestamp

@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    from_number = request.form.get("From", "").split(":")[-1]
    num_media = int(request.form.get("NumMedia", 0))

    print(f"\n📩 Received message from {from_number} with {num_media} media files.")

    if num_media == 0:
        print("⚠️ No media found.")
        return "OK", 200

    user_dir = os.path.join(UPLOAD_DIR, from_number)
    os.makedirs(user_dir, exist_ok=True)

    for i in range(num_media):
        media_url = request.form.get(f"MediaUrl{i}")
        content_type = request.form.get(f"MediaContentType{i}")
        ext = content_type.split("/")[-1]
        ts = int(time.time() * 1000)
        file_path = os.path.join(user_dir, f"image_{ts}.{ext}")

        response = requests.get(media_url, auth=(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN")))
        with open(file_path, "wb") as f:
            f.write(response.content)
        print(f"✅ Saved {file_path}")

    # Wait for disk I/O flush
    time.sleep(1.5)

    image_paths = sorted(
        [os.path.join(user_dir, f) for f in os.listdir(user_dir) if f.startswith("image_")],
        key=os.path.getmtime,
        reverse=True
    )

    if len(image_paths) < 2:
        print(f"⏳ Waiting for 2 images... Found: {len(image_paths)}")
        return "OK", 200

    # Prevent duplicate OCR triggers
    now = time.time()
    if from_number in recent_trigger and now - recent_trigger[from_number] < 20:
        print("⏱ OCR already triggered recently. Skipping duplicate.")
        return "OK", 200
    recent_trigger[from_number] = now

    img1, img2 = image_paths[:2]

    print("🔍 Detecting which image is FRONT using gender detection...")
    fields1 = extract_front_fields(img1)
    fields2 = extract_front_fields(img2)

    if 'gender' in fields1:
        front_img, back_img, front_fields = img1, img2, fields1
    elif 'gender' in fields2:
        front_img, back_img, front_fields = img2, img1, fields2
    else:
        print("❌ Could not identify front image.")
        return "OK", 200

    print(f"✅ Identified {os.path.basename(front_img)} as FRONT")
    print(f"📦 Processing address from {os.path.basename(back_img)}")

    try:
        address, pincode = extract_back_address(back_img)
    except Exception as e:
        print(f"❌ Address extraction error: {e}")
        address, pincode = None, None

    result = front_fields
    result['address'] = address
    result['pincode'] = pincode
    result['timestamp'] = datetime.now().isoformat()
    result['phone_number'] = from_number

    print("\n======= FINAL EXTRACTED DATA =======")
    for k, v in result.items():
        print(f"{k}: {v}")
 # Save to CSV
    try:
        if not os.path.exists(CSV_FILE):
            pd.DataFrame(columns=[
                "timestamp", "phone_number", "name", "dob", "gender",
                "aadhaar_number", "address", "pincode"
            ]).to_csv(CSV_FILE, index=False)

        df = pd.read_csv(CSV_FILE)
        df = pd.concat([df, pd.DataFrame([result])], ignore_index=True)
        df.to_csv(CSV_FILE, index=False)
        print(f"📁 Data saved to {CSV_FILE}")
    except Exception as e:
        print(f"❌ Failed to save to CSV: {e}")

    return "OK", 200

if __name__ == "__main__":
    app.run(debug=True)
