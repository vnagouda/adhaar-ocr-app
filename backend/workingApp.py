from flask import Flask, request
import os
import requests
import time
import numpy as np
import cv2
from dotenv import load_dotenv
from PIL import ImageFile
from twilio.rest import Client
from final import extract_front_fields, extract_back_address

# Allow truncated images to be loaded safely
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Load environment variables
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=env_path)

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

app = Flask(__name__)
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    from_number = request.form.get("From", "").split(":")[-1]
    sender_whatsapp = request.form.get("From")
    num_media = int(request.form.get("NumMedia", 0))

    print(f"\n📩 Received message from {from_number} with {num_media} media files.")

    if num_media == 0:
        print("⚠️ No media found in message.")
        return "OK", 200

    user_dir = os.path.join(UPLOAD_DIR, from_number)
    os.makedirs(user_dir, exist_ok=True)

    # Save incoming images
    for i in range(num_media):
        media_url = request.form.get(f"MediaUrl{i}")
        content_type = request.form.get(f"MediaContentType{i}")
        file_ext = content_type.split("/")[-1]
        timestamp = int(time.time() * 1000)
        filename = f"image_{timestamp}.{file_ext}"
        save_path = os.path.join(user_dir, filename)

        try:
            response = requests.get(media_url, auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN), stream=True)
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"✅ Saved {filename} to {save_path}")
        except Exception as e:
            print(f"❌ Failed to save {filename}: {str(e)}")

    # Delay to let second webhook call complete
    time.sleep(1.0)

    # Check if exactly 2 images are present
    image_files = sorted(
        [os.path.join(user_dir, f) for f in os.listdir(user_dir) if f.startswith("image_")],
        key=os.path.getmtime
    )

    if len(image_files) != 2:
        print("⏳ Waiting for 2 images... Found:", len(image_files))
        return "OK", 200

    img1, img2 = image_files

    # Identify front vs back using gender detection
    print("🔍 Determining which image is the front...")
    fields1 = extract_front_fields(img1)
    fields2 = extract_front_fields(img2)

    if 'gender' in fields1:
        front, back = img1, img2
        front_fields = fields1
    elif 'gender' in fields2:
        front, back = img2, img1
        front_fields = fields2
    else:
        print("❌ Could not determine gender in either image.")
        return "OK", 200

    print(f"✅ Identified {os.path.basename(front)} as FRONT")
    print(f"📦 Extracting address from {os.path.basename(back)}")

    try:
        address, pincode = extract_back_address(back)
    except Exception as e:
        print(f"❌ Address extraction error: {e}")
        address, pincode = None, None

    front_fields['address'] = address
    front_fields['pincode'] = pincode

    print("\n======= FINAL EXTRACTED DATA =======")
    for k, v in front_fields.items():
        print(f"{k}: {v}")

    return "OK", 200

if __name__ == "__main__":
    app.run(debug=True)
