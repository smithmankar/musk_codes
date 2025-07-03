import pyautogui
import pytesseract
import gspread
from google.oauth2.service_account import Credentials
import time

# --------------- CONFIG ---------------
# Set your screen resolution region where phone number is visible
REGION = (1627, 287, 133, 17)  # x, y, width, height (adjust to your system)
import pyautogui

# Test capture visually
img = pyautogui.screenshot(region=REGION)
img.save("test_capture.png")

# Google Sheets config
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_FILE = "C:/Users/dhruv/Documents/codes/wati-tl-tag-5c57ac4e111b.json"
SPREADSHEET_ID = "1yQLUUkvTTrRN3DcoO6YQqBmTd0JAdq5eWXavbzL_ImI"
SHEET_NAME = "Sheet1"

# Tesseract config (if custom path, set below)
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# --------------- SETUP GOOGLE SHEETS ---------------
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

# --------------- EXTRACTION LOOP ---------------
def extract_number_and_upload():
    img = pyautogui.screenshot(region=REGION)
    text = pytesseract.image_to_string(img, config='--psm 6')
    print(f"OCR Extracted: {text.strip()}")
    
    # Basic cleaning: extract last 10 digits
    import re
    numbers = re.findall(r'\d{10}', text)
    if not numbers:
        print("⚠️ No valid number detected.")
        return

    number = numbers[0]
    print(f"✅ Extracted Number: {number}")

    # Check for duplicates
    existing_numbers = set(sum(sheet.get_all_values(), []))
    if number in existing_numbers:
        print(f"⚠️ Number {number} already in sheet. Skipping.")
        return

    # Append to sheet
    sheet.append_row([number], value_input_option="USER_ENTERED")
    print(f"✅ Appended {number} to Google Sheet.")

# --------------- AUTO LOOP ---------------
if __name__ == "__main__":
    print("🚀 Starting WATI OCR extraction pipeline. Move mouse to top-left corner to stop.")

    try:
        while True:
            extract_number_and_upload()
            time.sleep(1)  # wait before scroll
            pyautogui.scroll(-300)  # scroll down
            time.sleep(2)  # wait for UI to update

            # Stop if mouse moved to top-left (emergency exit)
            if pyautogui.position() == (0, 0):
                print("🛑 Stopping due to mouse at (0,0).")
                break

    except KeyboardInterrupt:
        print("🛑 Stopped manually with KeyboardInterrupt.")
    print("✅ Extraction pipeline complete.")
