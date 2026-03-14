from __future__ import annotations

import base64
import logging
from io import BytesIO
from typing import Optional

from .config import settings

logger = logging.getLogger(__name__)

try:
    from xhtml2pdf import pisa

    _XHTML2PDF_AVAILABLE = True
    _import_error = ""
except ImportError as e:
    _XHTML2PDF_AVAILABLE = False
    _import_error = str(e)


def html_to_pdf_bytes(html: str) -> Optional[bytes]:
    """
    Convert HTML to PDF using xhtml2pdf (pure Python, no external binaries).

    Returns None if PDF export is disabled or if conversion fails.
    """
    if not settings.enable_pdf_export:
        return None
    if not _XHTML2PDF_AVAILABLE:
        logger.warning("xhtml2pdf not available: %s", _import_error)
        return None

    dest = BytesIO()
    if not html.strip().lower().startswith("<!doctype") and not html.strip().lower().startswith("<html"):
        html = f"<!DOCTYPE html><html><head><meta charset='utf-8'/></head><body>{html}</body></html>"

    try:
        status = pisa.CreatePDF(html, dest=dest, encoding="utf-8")
        if status.err:
            logger.warning("xhtml2pdf conversion failed (err=%s)", status.err)
            return None
        return dest.getvalue()
    except Exception as e:
        logger.warning("xhtml2pdf exception: %s", e)
        return None


def html_to_pdf_b64(html: str) -> Optional[str]:
    """Convert HTML to PDF and return base64-encoded bytes."""
    pdf_bytes = html_to_pdf_bytes(html)
    if pdf_bytes is None:
        return None
    return base64.b64encode(pdf_bytes).decode("ascii")
