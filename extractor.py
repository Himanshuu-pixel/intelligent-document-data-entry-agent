import re

def clean(text):
    return re.sub(r"\s+", " ", text.replace("|"," ")).strip()

def date(text):
    for p in [
        r"(?:invoice\s*date|date)\s*[:#-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
        r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b"]:
        m=re.search(p,text,re.I)
        if m: return m.group(1)
    return None

def invoice_no(text):
    for p in [
        r"(?:invoice\s*(?:number|no|#))\s*[:#-]?\s*([A-Z0-9][A-Z0-9._/-]{2,})",
        r"\b(INV[-_/]?[A-Z0-9-]{2,})\b"]:
        m=re.search(p,text,re.I)
        if m: return m.group(1).upper()
    return None

def label_value(text, labels):
    lp="|".join(re.escape(x) for x in labels)
    stop=r"(?=\s+(?:Invoice|Date|Vendor|Customer|Description|Subtotal|Tax|Total|Currency|Amount)\b|$)"
    m=re.search(rf"(?:{lp})\s*[:#-]?\s*([A-Za-z][A-Za-z0-9&.,'() -]{{2,80}}?){stop}",text,re.I)
    return m.group(1).strip(" .:-") if m else None

def amount(text, labels):
    # Check longer labels first, and use word boundaries so
    # "Total" cannot accidentally match inside "Subtotal".
    labels = sorted(labels, key=len, reverse=True)
    for label in labels:
        pattern = rf"\b{re.escape(label)}\b\s*[:#-]?\s*(?:[$€£₹]\s*)?([0-9][0-9,]*(?:\.[0-9]{{1,2}})?)"
        m = re.search(pattern, text, re.I)
        if m:
            raw = m.group(1).replace(",", "")
            return raw
    return None

def currency(text):
    for c in ["USD","INR","EUR","GBP"]:
        if re.search(rf"\b{c}\b",text,re.I): return c
    return {"$":"USD","₹":"INR","€":"EUR","£":"GBP"}.get(next((s for s in "$₹€£" if s in text),""),None)

def extract_invoice_fields(raw):
    text=clean(raw)
    vendor=label_value(text,["Vendor","Supplier","From"])
    customer=label_value(text,["Customer","Bill To","Billed To","Client"])
    if not vendor:
        m=re.search(r"\b([A-Z][A-Za-z& ]+(?:Technologies|Technology|Solutions|Ltd|Limited|Pvt|Inc|Corp))\b",text)
        vendor=m.group(1).strip() if m else None
    if not customer:
        m=re.search(r"\b([A-Z][A-Za-z& ]+(?:Pvt|Ltd|Limited|Inc|Corp))\b",text)
        candidate=m.group(1).strip() if m else None
        customer=candidate if candidate and candidate != vendor else None
    return {
        "invoice_number":invoice_no(text),
        "invoice_date":date(text),
        "vendor_name":vendor,
        "customer_name":customer,
        "subtotal":amount(text,["Subtotal","Sub Total"]),
        "total_amount":amount(text,["Total Amount","Grand Total","Amount Due","Total"]),
        "tax_amount":amount(text,["Tax Amount","Tax","VAT","GST"]),
        "currency":currency(text)
    }
