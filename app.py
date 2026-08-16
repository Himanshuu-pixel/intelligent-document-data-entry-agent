import streamlit as st
from pathlib import Path
from src.ocr_engine import run_ocr
from src.extractor import extract_invoice_fields
from src.validator import validate_invoice
from src.database import init_db, save_document, get_documents

st.set_page_config(page_title="Intelligent Document/Data Entry Agent", page_icon="📄", layout="wide")
BASE = Path(__file__).resolve().parent
DB = BASE / "data" / "documents.db"
init_db(DB)

st.title("📄 Intelligent Document/Data Entry Agent")
st.caption("OCR → Extraction → Validation → Human Review → SQLite")

with st.sidebar:
    st.header("Settings")
    doc_type = st.selectbox("Document type", ["Invoice"])
    threshold = st.slider("OCR confidence threshold", 40, 95, 60)
    st.info("Use a clear, straight JPG/PNG invoice.")

uploaded = st.file_uploader("Upload invoice image", type=["png","jpg","jpeg"])

if uploaded and st.button("🚀 Process Document", type="primary"):
    with st.spinner("Processing..."):
        text, confidence = run_ocr(uploaded.getvalue())
        fields = extract_invoice_fields(text)
        st.session_state.result = {
            "file": uploaded.name, "text": text, "confidence": confidence,
            "fields": fields, "validation": validate_invoice(fields, confidence, threshold)
        }

if "result" in st.session_state:
    r = st.session_state.result
    f = r["fields"]
    st.subheader("1. OCR Output")
    st.text_area("Recognized text", r["text"], height=170)

    a,b,c = st.columns(3)
    a.metric("OCR confidence", f"{r['confidence']:.2f}%")
    b.metric("Fields extracted", sum(bool(v) for v in f.values()))
    c.metric("Validation", r["validation"]["status"])

    st.subheader("2. Extracted Data")
    st.caption("Correct any field before saving.")
    labels = {
        "invoice_number":"Invoice Number","invoice_date":"Invoice Date",
        "vendor_name":"Vendor Name","customer_name":"Customer Name",
        "subtotal":"Subtotal","total_amount":"Total Amount",
        "tax_amount":"Tax Amount","currency":"Currency"
    }
    edited = {}

    # Keep money values consistent for review and export.
    money_fields = {"subtotal", "total_amount", "tax_amount"}

    def display_value(key, value):
        if key in money_fields and value not in (None, ""):
            try:
                return f"{float(str(value).replace(',', '')):.2f}"
            except ValueError:
                pass
        return str(value or "")

    cols = st.columns(2)
    for i,(key,label) in enumerate(labels.items()):
        with cols[i % 2]:
            edited[key] = st.text_input(label, display_value(key, f.get(key)))

    checked = validate_invoice(edited, r["confidence"], threshold)
    st.subheader("3. Validation / Human Review")
    if checked["status"] == "PASS":
        st.success("Document passed validation and is ready for submission.")
    else:
        st.warning("Document needs review before final submission.")
        for issue in checked["issues"]:
            st.error(issue)

    if st.button("💾 Save Reviewed Data"):
        doc_id = save_document(DB, r["file"], doc_type, r["confidence"], checked["status"], edited)
        st.success(f"Saved successfully. Record ID: {doc_id}")
        st.rerun()

st.divider()
st.subheader("📊 Processed Documents")
df = get_documents(DB)
if not df.empty:
    st.dataframe(df, use_container_width=True)
    st.download_button("⬇️ Download CSV", df.to_csv(index=False).encode(), "processed_documents.csv", "text/csv")
else:
    st.info("No processed documents yet.")
