'''
Loads raw text out of PDF/Excel files so it can be chunked and embedded.
'''

from pathlib import Path
from pypdf import PdfReader
import pandas as pd

from app.utils.logger import get_logger

logger = get_logger(__name__)


def load_pdf(path:str) -> str:
    """Extracts all text from a PDF file, page by page."""
    reader = PdfReader(path)
    text = '\n'.join(page.extract_text() or '' for page in reader.pages)
    logger.info(f'Loaded PDF: {path} ({len(reader.pages)} pages, {len(text)} chars)')
    return text

def load_excel(path: str) -> str:
    """Extracts all sheets from an Excel file as text (each row as a line)."""
    sheets = pd.read_excel(path, sheet_name=None) # dict of {sheet_name:df}
    parts=[]
    for sheet_name, df in sheets.items():
        parts.append(f"--- Sheet: {sheet_name} ---")
        parts.append(df.to_string(index=False))
    text = "\n".join(parts)
    logger.info(f"Loaded Excel: {path} ({len(sheets)} sheets, {len(text)} chars)")
    return text

def load_document(path: str) -> str:
    """Dispatches to the right loader based on file extension."""
    ext = Path(path).suffix.lower()
    if ext == ".pdf":
        return load_pdf(path)
    elif ext in (".xlsx", ".xls"):
        return load_excel(path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")