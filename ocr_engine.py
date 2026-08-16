import io, os, shutil
from pathlib import Path
import cv2, numpy as np, pytesseract
from PIL import Image

def configure_tesseract():
    if shutil.which("tesseract"):
        return
    for p in [r"C:\Program Files\Tesseract-OCR\tesseract.exe",
              r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"]:
        if Path(p).exists():
            pytesseract.pytesseract.tesseract_cmd = p
            return
    env = os.getenv("TESSERACT_CMD")
    if env and Path(env).exists():
        pytesseract.pytesseract.tesseract_cmd = env

def run_ocr(image_bytes):
    configure_tesseract()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    gray = cv2.resize(gray, None, fx=1.7, fy=1.7, interpolation=cv2.INTER_CUBIC)
    gray = cv2.GaussianBlur(gray, (3,3), 0)
    processed = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    text = pytesseract.image_to_string(processed, config="--oem 3 --psm 6")
    data = pytesseract.image_to_data(processed, config="--oem 3 --psm 6",
                                     output_type=pytesseract.Output.DICT)
    vals = []
    for x in data.get("conf", []):
        try:
            if float(x) >= 0: vals.append(float(x))
        except: pass
    confidence = sum(vals)/len(vals) if vals else 0
    return " ".join(text.split()), confidence
