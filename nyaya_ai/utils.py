import os
import re
import hashlib
from requests import get as getReq
from logging import getLogger
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
from time import time


logger = getLogger(__name__)

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept": "application/pdf,application/octet-stream;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Pragma": "no-cache",
}


# ------------------------------------------------------------
# HINDI DETECTION
# ------------------------------------------------------------
def is_hindi(text):
    """
    Check if the text contains Hindi/Devanagari characters.
    Unicode range: 0900–097F
    """
    return any("\u0900" <= ch <= "\u097f" for ch in text)


# ------------------------------------------------------------
# HINDI TO ENGLISH TRANSLITERATION
# ------------------------------------------------------------
def convert_to_english(text):
    if is_hindi(text):
        return transliterate(text, sanscript.DEVANAGARI, sanscript.ITRANS)
    return text


# ------------------------------------------------------------
# SAFE + SHORT FILENAME GENERATOR
# ------------------------------------------------------------
def sanitize_and_shorten(name, max_length=120):
    """
    - removes bad characters
    - makes lowercase
    - truncates if too long
    - adds hash to ensure uniqueness
    """

    # clean name: alpha–numeric only
    clean = name.lower()
    clean = re.sub(r"[^a-z0-9]+", "-", clean).strip("-")

    # hash for uniqueness
    hash_suffix = hashlib.md5(clean.encode()).hexdigest()[:8]

    # limit filename length (minus hash + extension)
    cutoff = max_length - len(hash_suffix) - 1

    if len(clean) > cutoff:
        clean = clean[:cutoff]

    return f"{clean}-{hash_suffix}"


def download_pdf(item: dict):
    pdf_url = item.get("pdf_url")
    save_dir = item.get("save_dir")
    filename = item.get("filename")
    formatter = item.get("formatter", "PDF-DOWNLOADER")
    updated_headers = item.get("updated_headers", headers)
    os.makedirs(save_dir, exist_ok=True)

    filename = f"{sanitize_and_shorten(filename)}.pdf"
    save_path = os.path.join(save_dir, filename)

    # # Download file
    response = getReq(pdf_url, stream=True, headers=updated_headers, allow_redirects=True)
    if response.status_code != 200:
        logger.error(
            f"[{formatter}] Failed to download PDF from {pdf_url}, status code: {response.status_code}"
        )
        return None

    content_length = int(response.headers.get("Content-Length", 0))
    if os.path.exists(save_path) and os.path.getsize(save_path) == content_length:
        logger.info(f"[{formatter}] PDF already exists at {save_path}, size: {content_length}")
        return save_path

    logger.info(f"[{formatter}] Downloading PDF from {pdf_url} to {save_path}, size: {content_length}")
    with open(save_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    return save_path


def fetch_time():
    return int(time())
