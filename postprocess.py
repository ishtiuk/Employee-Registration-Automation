import os
import re
import logging
import textwrap
from utils import read_yaml
from ast import literal_eval
import google.generativeai as genai

logging_str = "[%(asctime)s: %(levelname)s: %(module)s]: %(message)s"
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(filename=os.path.join(log_dir, "extraction_logs.log"), level=logging.INFO, format=logging_str, filemode="a")

config_path = "config.yaml"
config = read_yaml(config_path)
artifacts = config['artifacts']
genai.configure(api_key=artifacts['GOOGLE_API_KEY'])
model = genai.GenerativeModel("gemini-1.5-flash-latest")


def extract_information_regex(text):
    logging.info("Starting information extraction (Regex).")
    
    patterns = {
        "ID": r'(?i)(?:id\s*no|id|roll\s*no)\s*[:\s]*([\d]+)',
        "Full Name": r'(?i)(?:full\s*name|name|employee\s*name)\s*[:\s]*([A-Za-z\s]+)',
        "Job Position": r'(?i)(?:job\s*position|position|designation|role)\s*[:\s]*([A-Za-z\s]+)',
        "Department": r'(?i)(?:department|technology|field|major)\s*[:\s]*([A-Za-z\s]+)',
        "Email": r'(?i)(?:email|e[-\s]*mail|mail)\s*[:\s]*(\S+)',
        "Phone": r'(?i)(?:phone|contact\s*number)\s*[:\s]*([\d\s]+)',
        "Blood Group": r'(?i)(?:blood\s*group|blood\s*type)\s*[:\s]*([A-Z+-]+)',
        "DOB": r'(?i)(?:date\s*of\s*birth|d\.?o\.?b\.?)\s*[:\s]*([\d]{2}[\/\.\-][\d]{2}[\/\.\-][\d]{2,4})'
    }

    extracted_info = {}
    text = re.sub(r'\*{2,}', '*', text)

    try:
        logging.info("Inside Try Except for information extraction (Regex).")
        for key, pattern in patterns.items():
            match = re.search(pattern, text)
            if match:
                extracted_info[key] = match.group(1).strip()
            else:
                extracted_info[key] = None

        if extracted_info["Full Name"] is None:
            extracted_info["Full Name"] = text.split("*")[0]

        if extracted_info["Job Position"] is None:
            extracted_info["Job Position"] = text.split("*")[1]

    except Exception as e:
        logging.error(f"Error during regex extraction: {e}")
        extracted_info["Full Name"] = None
        extracted_info["Job Position"] = None

    if extracted_info["Email"] is not None:
        extracted_info["Email"] = extracted_info["Email"].lower()
    
    extracted_info = {key: (lambda v: v.replace("*", "") if v is not None else v)(value) for key, value in extracted_info.items()}

    logging.info(f"Extracted information (Regex)")
    return extracted_info

def extract_information_genai(text):
    logging.info("Starting information extraction (GenAI).")
    prompt = config['artifacts']['PROMPT']

    try:
        pattern = r'python\s*({[^{}]*})'
        logging.info("Inside Try Except for information extraction (GenAI).")
        extracted_info = re.findall(pattern, model.generate_content(textwrap.dedent(prompt.format(text=text))).text.strip())[0]
        logging.info(f"Extracted information (GenAI)")
        return literal_eval(extracted_info)
    except Exception as e:
        logging.error(f"An error occurred during text extraction (GenAI): {e}")  
        return e

