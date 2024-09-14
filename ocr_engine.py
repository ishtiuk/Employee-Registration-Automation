import os
import logging
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"D:\Py_Tesseract\tesseract.exe"

log_dir = "logs"
logging_str = "[%(asctime)s: %(levelname)s: %(module)s]: %(message)s"
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(filename=os.path.join(log_dir, "employee_registration_logs.log"), level=logging.INFO, format=logging_str, filemode="a")

def extract_text(image_path, languages='eng'):
    logging.info("Text Extraction Started...")
    
    try:
        logging.info("Inside Try-Catch...")
        img = Image.open(image_path)

        # Use pytesseract to extract text
        # custom_config = custom_config = r'--oem 3 --psm 3 -l eng -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 '

        result = pytesseract.image_to_string(img, lang=languages)

        # Replace newlines with '*' to maintain a similar format to the original function
        filtered_text = "*".join(result.splitlines()) + "*"
        filtered_text = ''.join([char if char in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789:-/*@. " else '' for char in filtered_text])
        print(filtered_text)

        return filtered_text
    except Exception as e:
        print("An error occurred during text extraction:", e)
        logging.info(f"An error occurred during text extraction: {e}")
        return ""
    
