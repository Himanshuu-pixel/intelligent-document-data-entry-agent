def num(v):
    try: return float(str(v).replace(",","").replace("$","").replace("₹","").strip())
    except: return None

def validate_invoice(fields, confidence, threshold):
    required=["invoice_number","invoice_date","vendor_name","customer_name","subtotal","total_amount","tax_amount","currency"]
    issues=[f"Missing required field: {x}" for x in required if not str(fields.get(x) or "").strip()]
    if confidence < threshold:
        issues.append(f"OCR confidence {confidence:.2f}% is below threshold {threshold}%.")
    s,t,tot=num(fields.get("subtotal")),num(fields.get("tax_amount")),num(fields.get("total_amount"))
    if s is not None and t is not None and tot is not None and abs(s+t-tot)>0.02:
        issues.append("Amount check failed: subtotal + tax does not match total.")
    return {"status":"PASS" if not issues else "REVIEW","issues":issues}
