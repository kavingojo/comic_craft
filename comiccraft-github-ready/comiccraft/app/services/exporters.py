"""PDF export with FPDF2 (one comic panel per page)."""
import textwrap
import unicodedata
from datetime import datetime
from typing import Dict, List

from fpdf import FPDF
from PIL import Image

from app.config import get_settings
from app.services.media import local_path_from_url

_REPLACEMENTS = {
    "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
    "\u2013": "-", "\u2014": "-", "\u2026": "...", "\u00a0": " ",
}


def _pdf_text(value, width: int = 90) -> str:
    """Make text safe for FPDF core fonts (Latin-1/ASCII) and wrap it so long words never crash."""
    value = str(value or "")
    for old, new in _REPLACEMENTS.items():
        value = value.replace(old, new)
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    lines: List[str] = []
    for paragraph in value.splitlines() or [""]:
        lines.extend(textwrap.wrap(paragraph, width=width, break_long_words=True, break_on_hyphens=True) or [""])
    return "\n".join(lines).strip() or " "


def _write_block(pdf: FPDF, label: str, text: str, style: str = "") -> None:
    if not str(text or "").strip():
        return
    pdf.set_font("Helvetica", "B", 11)
    pdf.multi_cell(0, 6, _pdf_text(label, 90), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", style, 11)
    pdf.multi_cell(0, 6, _pdf_text(text), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)


def save_pdf(layout: List[Dict]) -> str:
    """Build the PDF and return its '/static/exports/<file>.pdf' URL path."""
    settings = get_settings()
    settings.exports_dir.mkdir(parents=True, exist_ok=True)
    filename = f"comiccraft_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    output = settings.exports_dir / filename

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_title("ComicCraft comic")

    for panel in layout:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 18)
        pdf.multi_cell(0, 9, _pdf_text(f"Panel {panel['panel_number']}: {panel['title']}", 50), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

        image_file = local_path_from_url(panel.get("image_path", ""))
        top = pdf.get_y()
        image_height = 20.0
        if image_file and image_file.is_file():
            try:
                with Image.open(image_file) as img:
                    ratio = img.height / img.width
                width_mm = 120.0
                image_height = width_mm * ratio
                pdf.image(str(image_file), x=(210 - width_mm) / 2, y=top, w=width_mm, h=image_height)
            except Exception:  # noqa: BLE001 - never let one bad image break the export
                pdf.set_font("Helvetica", "I", 11)
                pdf.cell(0, 8, "(image could not be embedded)", new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.set_font("Helvetica", "I", 11)
            pdf.cell(0, 8, "(image missing)", new_x="LMARGIN", new_y="NEXT")

        pdf.set_y(top + image_height + 6)
        _write_block(pdf, "Scene", panel.get("scene_description", ""), "I")
        _write_block(pdf, "Caption", panel.get("caption", ""))
        _write_block(pdf, "Narration", panel.get("narration", ""))
        _write_block(pdf, "Dialogue", panel.get("dialogue", ""))

    pdf.output(str(output))
    return f"/static/exports/{filename}"
