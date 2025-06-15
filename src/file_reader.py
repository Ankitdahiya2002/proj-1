import pandas as pd
import fitz  # PyMuPDF

def extract_pdf(uploaded_pdf):
    doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_txt(uploaded_txt):
    return uploaded_txt.read().decode("utf-8")

def extract_excel(uploaded_xlsx):
    df = pd.read_excel(uploaded_xlsx)
    return df.to_string(index=False)

        
def extract_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_pdf(uploaded_file)
    elif uploaded_file.type == "text/plain":
        return extract_txt(uploaded_file)
    elif uploaded_file.type in ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/vnd.ms-excel"]:
        return extract_excel(uploaded_file)
    else:
        raise ValueError("Unsupported file type")
