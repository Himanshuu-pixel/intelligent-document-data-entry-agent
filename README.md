# Intelligent Document/Data Entry Agent

A beginner-friendly OCR automation project for invoice processing.

### Flow
Upload invoice → OpenCV preprocessing → Tesseract OCR → Regex field extraction → Validation → Human Review → SQLite → CSV

### Run
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Install Tesseract OCR on Windows if needed. The app automatically checks common Tesseract installation paths.

### Demo
Upload `demo_invoice.png`.

Expected:
- Invoice Number: INV-2034
- Invoice Date: 21/02/2026
- Vendor: ABC Technologies
- Customer: XYZ Pvt Ltd
- Subtotal: 525.00
- Tax: 22.31
- Total: 547.31
- Currency: USD

### Interview explanation
"I preprocess the invoice image with OpenCV, run Tesseract OCR, use simple regex rules to convert OCR text into structured fields, validate required fields and amount consistency, send uncertain records to human review, and store the final data in SQLite."

### Project structure
app.py, src/ocr_engine.py, src/extractor.py, src/validator.py, src/database.py, demo_invoice.png


### Data quality
- Monetary fields are normalized to two decimal places (for example, 525.00, 22.31, 547.31).
- Invoice total validation checks subtotal + tax against total with a small rounding tolerance.
