import os
import re
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

# Set Tesseract path for macOS Homebrew
pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"

# Folder where payslips are stored
PDF_FOLDER = "payslips"

# Regex pattern to match "Net Amount" line with ₹ amounts like 2,53,170.00 or 253170.00
NET_AMOUNT_REGEX = re.compile(r'net amount\s*[:\-]?\s*([\d,]+\.\d{2})', re.IGNORECASE)

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        images = convert_from_path(pdf_path)
        for image in images:
            gray = image.convert("L")  # Grayscale
            text += pytesseract.image_to_string(gray)
    except Exception as e:
        print(f"❌ Failed to read {pdf_path}: {e}")
    return text

def extract_net_amount(text):
    # Collapse into one line for better matching
    text_normalized = text.lower().replace('\n', ' ')
    match = NET_AMOUNT_REGEX.search(text_normalized)
    if match:
        try:
            return float(match.group(1).replace(',', ''))
        except ValueError:
            pass
    return None

def main():
    highest_salary = 0
    highest_file = None

    for file in os.listdir(PDF_FOLDER):
        if file.lower().endswith(".pdf"):
            file_path = os.path.join(PDF_FOLDER, file)
            print(f"🔍 Processing: {file}")
            text = extract_text_from_pdf(file_path)
            net_salary = extract_net_amount(text)

            if net_salary is not None:
                print(f"💰 Net Salary Found: ₹{net_salary:,.2f}")
                if net_salary > highest_salary:
                    highest_salary = net_salary
                    highest_file = file
            else:
                print("⚠️ Could not extract Net Amount.")

    print("\n🏁 Scan complete.")
    if highest_file:
        print(f"🏆 Highest Net Salary: ₹{highest_salary:,.2f} in file: {highest_file}")
    else:
        print("❌ No Net Salary found in any payslip.")

if __name__ == "__main__":
    main()
