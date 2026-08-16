import sqlite3
from pathlib import Path
import pandas as pd

def conn(db):
    Path(db).parent.mkdir(parents=True,exist_ok=True)
    return sqlite3.connect(db)

def init_db(db):
    with conn(db) as c:
        c.execute("""CREATE TABLE IF NOT EXISTS documents(
        id INTEGER PRIMARY KEY AUTOINCREMENT,file_name TEXT,document_type TEXT,
        ocr_confidence REAL,status TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        invoice_number TEXT,invoice_date TEXT,vendor_name TEXT,customer_name TEXT,
        subtotal REAL,total_amount REAL,tax_amount REAL,currency TEXT)""")

def num(v):
    try:return float(str(v).replace(",","").strip())
    except:return None

def save_document(db,file_name,doc_type,confidence,status,f):
    with conn(db) as c:
        cur=c.execute("""INSERT INTO documents
        (file_name,document_type,ocr_confidence,status,invoice_number,invoice_date,
        vendor_name,customer_name,subtotal,total_amount,tax_amount,currency)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
        (file_name,doc_type,confidence,status,f.get("invoice_number"),f.get("invoice_date"),
         f.get("vendor_name"),f.get("customer_name"),num(f.get("subtotal")),
         num(f.get("total_amount")),num(f.get("tax_amount")),f.get("currency")))
        return cur.lastrowid

def get_documents(db):
    with conn(db) as c:
        return pd.read_sql_query("SELECT * FROM documents ORDER BY id DESC",c)
