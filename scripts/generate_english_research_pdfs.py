from __future__ import annotations

import html
import re
import unicodedata
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "outputs" / "pdf"

PDF_SPECS = [
    ("docs/architecture/motomap_rapor.md", "motomap_rapor_en.pdf"),
    ("docs/issue_4/motomap_yokus_ve_viraj_Algoritmasi.md", "motomap_yokus_ve_viraj_Algoritmasi_issue4_en.pdf"),
    ("docs/issue_4/issue4.md", "issue4_index_en.pdf"),
    ("docs/research_suggestion/Ali_Ozuysal_Projesi.md", "Ali_Ozuysal_Projesi_en.pdf"),
    ("docs/research_suggestion/MOTOMAP_YOKUS.md", "MOTOMAP_YOKUS_en.pdf"),
    ("docs/research_suggestion/motomap_yokus_ve_viraj_Algoritmasi.md", "motomap_yokus_ve_viraj_Algoritmasi_research_en.pdf"),
]


def _repair_text(text: str) -> str:
    if any(marker in text for marker in ("Ã", "Å", "Â")):
        try:
            text = text.encode("latin1").decode("utf-8")
        except UnicodeEncodeError:
            pass
        except UnicodeDecodeError:
            pass

    replacements = {
        "°": " deg",
        "º": " deg",
        "–": "-",
        "—": "-",
        "−": "-",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")


def _clean_inline_markdown(text: str) -> str:
    text = _repair_text(text).strip()
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`([^`]+)`", r'<font name="Courier">\1</font>', text)
    return text


def _build_styles():
    sample = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle(
            "MotoTitle",
            parent=sample["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            spaceAfter=14,
            textColor=colors.HexColor("#143d59"),
        ),
        "h2": ParagraphStyle(
            "MotoHeading2",
            parent=sample["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=19,
            spaceBefore=8,
            spaceAfter=8,
            textColor=colors.HexColor("#0f5c78"),
        ),
        "h3": ParagraphStyle(
            "MotoHeading3",
            parent=sample["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            spaceBefore=6,
            spaceAfter=5,
            textColor=colors.HexColor("#0f5c78"),
        ),
        "body": ParagraphStyle(
            "MotoBody",
            parent=sample["BodyText"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            spaceAfter=7,
        ),
        "bullet": ParagraphStyle(
            "MotoBullet",
            parent=sample["BodyText"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            leftIndent=14,
            firstLineIndent=0,
            spaceAfter=4,
        ),
        "mono": ParagraphStyle(
            "MotoMono",
            parent=sample["Code"],
            fontName="Courier",
            fontSize=9,
            leading=12,
            leftIndent=10,
            spaceAfter=8,
        ),
        "meta": ParagraphStyle(
            "MotoMeta",
            parent=sample["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#4d4d4d"),
        ),
    }
    return styles


def _table_from_lines(lines: list[str], styles) -> Table:
    rows = []
    for line in lines:
        stripped = _repair_text(line).strip()
        if not stripped:
            continue
        if re.fullmatch(r"\|?[\-\:\s|]+\|?", stripped):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        rows.append([Paragraph(_clean_inline_markdown(cell), styles["body"]) for cell in cells])

    if not rows:
        rows = [[Paragraph("", styles["body"])]]

    table = Table(rows, repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dceef5")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#143d59")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#9bbbc8")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def _add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#5f6b73"))
    canvas.drawString(doc.leftMargin, 18, _repair_text(doc.title))
    canvas.drawRightString(A4[0] - doc.rightMargin, 18, f"Page {canvas.getPageNumber()}")
    canvas.restoreState()


def _render_markdown(source_path: Path, output_path: Path) -> None:
    styles = _build_styles()
    lines = source_path.read_text(encoding="utf-8").splitlines()
    story = []
    title = source_path.stem.replace("_", " ")

    paragraph_lines: list[str] = []
    table_lines: list[str] = []
    block_lines: list[str] = []
    in_code_block = False
    in_math_block = False

    def flush_paragraph() -> None:
        if not paragraph_lines:
            return
        text = " ".join(part.strip() for part in paragraph_lines if part.strip())
        story.append(Paragraph(_clean_inline_markdown(text), styles["body"]))
        paragraph_lines.clear()

    def flush_table() -> None:
        if not table_lines:
            return
        story.append(_table_from_lines(table_lines, styles))
        story.append(Spacer(1, 8))
        table_lines.clear()

    def flush_block() -> None:
        if not block_lines:
            return
        text = "\n".join(_repair_text(line) for line in block_lines)
        story.append(Preformatted(text, styles["mono"]))
        block_lines.clear()

    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()

        if stripped.startswith("[!["):
            continue

        if stripped == "```":
            flush_paragraph()
            flush_table()
            if in_code_block:
                flush_block()
            in_code_block = not in_code_block
            continue

        if stripped == "$$":
            flush_paragraph()
            flush_table()
            if in_math_block:
                flush_block()
            in_math_block = not in_math_block
            continue

        if in_code_block or in_math_block:
            block_lines.append(line)
            continue

        if stripped.startswith("|"):
            flush_paragraph()
            table_lines.append(line)
            continue

        flush_table()

        if not stripped:
            flush_paragraph()
            story.append(Spacer(1, 4))
            continue

        if stripped in {"---", "***"}:
            flush_paragraph()
            story.append(Spacer(1, 8))
            continue

        if stripped.startswith("# "):
            flush_paragraph()
            title = _repair_text(stripped[2:].strip())
            story.append(Paragraph(_clean_inline_markdown(stripped[2:]), styles["title"]))
            continue

        if stripped.startswith("## "):
            flush_paragraph()
            story.append(Paragraph(_clean_inline_markdown(stripped[3:]), styles["h2"]))
            continue

        if stripped.startswith("### "):
            flush_paragraph()
            story.append(Paragraph(_clean_inline_markdown(stripped[4:]), styles["h3"]))
            continue

        if re.match(r"^[-*] ", stripped):
            flush_paragraph()
            bullet_text = _clean_inline_markdown(stripped[2:].strip())
            story.append(Paragraph(bullet_text, styles["bullet"], bulletText="-"))
            continue

        if re.match(r"^\d+\. ", stripped):
            flush_paragraph()
            story.append(Paragraph(_clean_inline_markdown(stripped), styles["bullet"]))
            continue

        paragraph_lines.append(line)

    flush_paragraph()
    flush_table()
    flush_block()

    if not story:
        story.append(Paragraph(_clean_inline_markdown(source_path.name), styles["title"]))

    meta = Paragraph(
        _clean_inline_markdown(f"English PDF generated from {source_path.relative_to(ROOT)}"),
        styles["meta"],
    )
    story.insert(1, meta)
    story.insert(2, Spacer(1, 10))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=46,
        rightMargin=46,
        topMargin=54,
        bottomMargin=34,
        title=title,
        author="OpenAI Codex",
    )
    doc.build(story, onFirstPage=_add_page_number, onLaterPages=_add_page_number)


def main() -> None:
    for source_rel, output_name in PDF_SPECS:
        source_path = ROOT / source_rel
        output_path = OUTPUT_DIR / output_name
        _render_markdown(source_path, output_path)
        print(f"Generated {output_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
