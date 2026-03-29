from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import io

# --- Clean Color Palette (white background) ---
BLUE = colors.HexColor("#4F6EF7")
DARK = colors.HexColor("#1a1d2e")
RED = colors.HexColor("#e05c5c")
ORANGE = colors.HexColor("#f0a500")
GREEN = colors.HexColor("#4caf80")
GREY = colors.HexColor("#888888")
LIGHT_GREY = colors.HexColor("#f5f5f5")
MID_GREY = colors.HexColor("#dddddd")
BLACK = colors.HexColor("#222222")
WHITE = colors.white

def clean(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    text = text.replace("\u2026", "...").replace("\u00a0", " ")
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return text.strip()

def severity_color(score):
    if score >= 7: return RED
    elif score >= 4: return ORANGE
    return GREEN

def manipulation_color(score):
    if score >= 7: return RED
    elif score >= 4: return ORANGE
    return GREEN

def make_styles():
    return {
        "title": ParagraphStyle("title",
            fontSize=28, textColor=BLUE, fontName="Helvetica-Bold",
            alignment=TA_CENTER, spaceAfter=4),
        "subtitle": ParagraphStyle("subtitle",
            fontSize=11, textColor=GREY, fontName="Helvetica",
            alignment=TA_CENTER, spaceAfter=4),
        "report_name": ParagraphStyle("report_name",
            fontSize=10, textColor=GREY, fontName="Helvetica-Oblique",
            alignment=TA_CENTER, spaceAfter=20),
        "section": ParagraphStyle("section",
            fontSize=13, textColor=BLUE, fontName="Helvetica-Bold",
            spaceBefore=20, spaceAfter=8),
        "body": ParagraphStyle("body",
            fontSize=10, textColor=BLACK, fontName="Helvetica",
            leading=16, spaceAfter=6),
        "bold": ParagraphStyle("bold",
            fontSize=10, textColor=BLACK, fontName="Helvetica-Bold",
            spaceAfter=4),
        "quote": ParagraphStyle("quote",
            fontSize=9, textColor=GREY, fontName="Helvetica-Oblique",
            leftIndent=12, spaceAfter=4),
        "small": ParagraphStyle("small",
            fontSize=9, textColor=GREY, fontName="Helvetica",
            spaceAfter=4),
        "footer": ParagraphStyle("footer",
            fontSize=8, textColor=GREY, fontName="Helvetica",
            alignment=TA_CENTER, spaceBefore=8),
        "score_num": ParagraphStyle("score_num",
            fontSize=22, fontName="Helvetica-Bold",
            alignment=TA_CENTER),
        "center": ParagraphStyle("center",
            fontSize=10, textColor=BLACK, fontName="Helvetica",
            alignment=TA_CENTER),
        "center_bold": ParagraphStyle("center_bold",
            fontSize=10, textColor=BLACK, fontName="Helvetica-Bold",
            alignment=TA_CENTER),
    }

def generate_report(analysis: dict, article_title: str = "Analyzed Article", report_name: str = "VeritasAI Report") -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=20*mm, bottomMargin=20*mm
    )

    s = make_styles()
    story = []

    # --- Header ---
    story.append(Paragraph("VeritasAI", s["title"]))
    story.append(Paragraph("Media Bias &amp; Manipulation Analysis Report", s["subtitle"]))
    story.append(Paragraph(clean(report_name), s["report_name"]))
    story.append(HRFlowable(width="100%", thickness=2, color=BLUE, spaceAfter=16))
    story.append(Paragraph(clean(article_title), s["bold"]))
    story.append(Spacer(1, 8))

    # --- Manipulation Score ---
    score = analysis.get("overall_manipulation_score", 0)
    score_color = manipulation_color(score)
    score_label = (
        "Low Manipulation - Mostly clean writing."
        if score <= 3 else
        "Moderate Manipulation - Read critically."
        if score <= 6 else
        "High Manipulation - Be very skeptical."
    )

    story.append(Paragraph("Manipulation Score", s["section"]))

    score_table = Table(
        [[
            Paragraph(f"{score:.1f}/10", ParagraphStyle("sn",
                fontSize=22, textColor=score_color,
                fontName="Helvetica-Bold", alignment=TA_CENTER)),
            Paragraph(score_label, ParagraphStyle("sl",
                fontSize=10, textColor=BLACK,
                fontName="Helvetica", leading=14))
        ]],
        colWidths=[35*mm, 125*mm]
    )
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), LIGHT_GREY),
        ("BACKGROUND", (1, 0), (1, 0), WHITE),
        ("BOX", (0, 0), (-1, -1), 1, MID_GREY),
        ("LINEAFTER", (0, 0), (0, 0), 1, MID_GREY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("PADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 8))

    # --- Political Leaning ---
    leaning = analysis.get("political_leaning", {})
    if leaning:
        story.append(Paragraph("Political Leaning", s["section"]))
        signals = ", ".join([clean(sig) for sig in leaning.get("key_signals", [])])
        leaning_table = Table(
            [[
                Paragraph(clean(leaning.get("label", "Unknown")), ParagraphStyle("ll",
                    fontSize=14, textColor=BLUE,
                    fontName="Helvetica-Bold", alignment=TA_CENTER)),
                Paragraph(
                    f"Confidence: {leaning.get('confidence', 0)}%<br/>Key signals: {clean(signals)}",
                    ParagraphStyle("ld", fontSize=9, textColor=BLACK,
                        fontName="Helvetica", leading=14))
            ]],
            colWidths=[35*mm, 125*mm]
        )
        leaning_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), LIGHT_GREY),
            ("BACKGROUND", (1, 0), (1, 0), WHITE),
            ("BOX", (0, 0), (-1, -1), 1, MID_GREY),
            ("LINEAFTER", (0, 0), (0, 0), 1, MID_GREY),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("PADDING", (0, 0), (-1, -1), 10),
        ]))
        story.append(leaning_table)
        story.append(Spacer(1, 8))

    # --- Rhetorical Summary ---
    story.append(Paragraph("What This Article Is Doing", s["section"]))
    story.append(Paragraph(clean(analysis.get("rhetorical_summary", "N/A")), s["body"]))

    # --- Detected Patterns ---
    patterns = analysis.get("detected_patterns", [])
    story.append(Paragraph(f"Detected Manipulation Patterns ({len(patterns)} found)", s["section"]))

    for p in patterns:
        sev = p.get("severity", 0)
        sev_color = severity_color(sev)

        pattern_table = Table(
            [
                [
                    Paragraph(clean(f"{p.get('category')} - {p.get('subcategory')}"),
                        ParagraphStyle("ph", fontSize=10, textColor=BLACK,
                            fontName="Helvetica-Bold")),
                    Paragraph(f"Severity: {sev}/10",
                        ParagraphStyle("ps", fontSize=10, textColor=sev_color,
                            fontName="Helvetica-Bold", alignment=TA_RIGHT))
                ],
                [Paragraph(clean(f'"{p.get("quote", "")}"'), s["quote"]), ""],
                [Paragraph(f'What this is: {clean(p.get("what_this_means", ""))}', s["body"]), ""],
                [Paragraph(f'Why it\'s a problem: {clean(p.get("why_its_problematic", ""))}', s["body"]), ""],
            ],
            colWidths=[120*mm, 40*mm]
        )
        pattern_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GREY),
            ("BOX", (0, 0), (-1, -1), 1, MID_GREY),
            ("LINEBEFORE", (0, 0), (0, -1), 3, sev_color),
            ("SPAN", (0, 1), (1, 1)),
            ("SPAN", (0, 2), (1, 2)),
            ("SPAN", (0, 3), (1, 3)),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("PADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(pattern_table)
        story.append(Spacer(1, 6))

    # --- Factual Claims ---
    claims = analysis.get("factual_claims", [])
    if claims:
        story.append(Paragraph(f"Factual Claims ({len(claims)} extracted)", s["section"]))
        for c in claims:
            verdict = c.get("verdict", "Unverifiable")
            if "True" in verdict: v_color = GREEN
            elif "False" in verdict: v_color = RED
            else: v_color = GREY

            claim_table = Table(
                [[
                    Paragraph(clean(c.get("claim", "")), s["body"]),
                    Paragraph(clean(verdict), ParagraphStyle("cv",
                        fontSize=9, textColor=v_color,
                        fontName="Helvetica-Bold", alignment=TA_RIGHT))
                ]],
                colWidths=[120*mm, 40*mm]
            )
            claim_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), WHITE),
                ("BOX", (0, 0), (-1, -1), 1, MID_GREY),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("PADDING", (0, 0), (-1, -1), 8),
            ]))
            story.append(claim_table)
            story.append(Spacer(1, 4))

    # --- Clean Rewrite ---
    story.append(Paragraph("Clean Rewrite", s["section"]))
    rewrite_table = Table(
        [[Paragraph(clean(analysis.get("clean_rewrite", "N/A")), s["body"])]],
        colWidths=[160*mm]
    )
    rewrite_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GREY),
        ("BOX", (0, 0), (-1, -1), 1, MID_GREY),
        ("PADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(rewrite_table)

    # --- Footer ---
    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", thickness=1, color=MID_GREY))
    story.append(Paragraph(
        "Generated by VeritasAI - AI-powered Media Bias and Manipulation Detector",
        s["footer"]
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()