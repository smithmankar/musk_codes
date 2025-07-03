import pyautogui
import pytesseract
import cv2
import numpy as np
import csv
import time
import os

# ========== CONFIG ==========

# Path to Tesseract executable if needed
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

OUTPUT_CSV = "wati_numbers.csv"

# Region to capture for number OCR (adjust for your screen)
CAPTURE_REGION = (1627, 287, 133, 17)  # left, top, width, height

# Click position for contact
CONTACT_CLICK_POSITION = (73, 406)

# Scroll settings
SCROLL_AMOUNT = -108  # Each contact is spaced 108 pixels vertically

# Delay between steps
DELAY_BETWEEN_CONTACTS = 30

# ========== FUNCTIONS ==========

def extract_number_from_screen(region):
    screenshot = pyautogui.screenshot(region=region)
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    text = pytesseract.image_to_string(img, config='--psm 6')
    text = text.strip().replace(" ", "").replace("\n", "")
    return text

def is_valid_number(text):
    # Adjust validation as per your data
    return text.startswith("+91") and len(text) >= 10

def append_to_csv(number):
    file_exists = os.path.isfile(OUTPUT_CSV)
    with open(OUTPUT_CSV, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Number"])
        writer.writerow([number])

def main():
    print("🚀 Starting WATI OCR to CSV pipeline. Move mouse to (0,0) to stop.")
    seen_numbers = set()

    while True:
        if pyautogui.position() == (0, 0):
            print("🛑 Stopping pipeline.")
            break

        text = extract_number_from_screen(CAPTURE_REGION)
        print(f"OCR Extracted: {text}")

        if is_valid_number(text):
            if text not in seen_numbers:
                seen_numbers.add(text)
                append_to_csv(text)
                print(f"✅ Number saved: {text}")
            else:
                print(f"⚠️ Duplicate, skipped: {text}")
        else:
            print("⚠️ Invalid or no number detected.")

        # Scroll to next contact
        pyautogui.moveTo(CONTACT_CLICK_POSITION)
        pyautogui.scroll(SCROLL_AMOUNT)
        pyautogui.click(CONTACT_CLICK_POSITION)
        print(f"✅ Moved to next contact and clicked at {CONTACT_CLICK_POSITION}")

        time.sleep(DELAY_BETWEEN_CONTACTS)

    print("✅ Pipeline completed. Numbers saved in:", OUTPUT_CSV)

if __name__ == "__main__":
    main()
