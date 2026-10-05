import io
import csv
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def generate_pdf_skill_gap_report(analysis_data: dict) -> bytes:
    """
    Generate downloadable PDF Skill Gap Report using ReportLab.
    Matches exact visual identity palette: Deep Teal (#0f3838), Gold Accent (#d99b00), Mint (#eef7f5).
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        textColor=colors.HexColor('#0f3838'),
        alignment=TA_LEFT,
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        textColor=colors.HexColor('#4a6865'),
        spaceAfter=15
    )
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=colors.HexColor('#0f3838'),
        spaceBefore=12,
        spaceAfter=8
    )
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#112a2a'),
        leading=14
    )

    # Header
    story.append(Paragraph("SkillSphere AI - Personalized Skill Gap Report", title_style))
    story.append(Paragraph(f"Target Role: <b>{analysis_data.get('target_role', 'Data Scientist')}</b> | Date: {datetime.now().strftime('%Y-%m-%d')} | Analytics Version: 1.0", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#d99b00'), spaceAfter=15))

    # Executive Summary Card
    cov_pct = analysis_data.get('coverage_percentage', 0.0)
    summary_text = f"""
    <b>Executive Skill Coverage Score: {cov_pct}%</b><br/>
    Candidate possesses <b>{len(analysis_data.get('matched_skills', []))}</b> matched skills out of 
    <b>{analysis_data.get('total_target_skills_analyzed', 0)}</b> total role requirements analyzed.<br/>
    High Priority Missing Skills: <b>{len(analysis_data.get('missing_high_priority', []))}</b> | Secondary Missing Skills: <b>{len(analysis_data.get('missing_secondary', []))}</b>
    """
    summary_table = Table([[Paragraph(summary_text, body_style)]], colWidths=[540])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#eef7f5')),
        ('BORDER', (0,0), (-1,-1), 1, colors.HexColor('#cce5e0')),
        ('PADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 15))

    # Matched Skills Section
    story.append(Paragraph("Matched Skills (Already Acquired)", section_heading))
    matched = [s.get('skill_name') for s in analysis_data.get('matched_skills', [])]
    matched_str = ", ".join(matched) if matched else "None identified yet."
    story.append(Paragraph(f"<b>Verified Competencies:</b> {matched_str}", body_style))
    story.append(Spacer(1, 15))

    # High Priority Skill Gaps Table
    story.append(Paragraph("High-Priority Skill Gaps & Market Demand Evidence", section_heading))
    gap_data = [["Skill Name", "Category", "Posting Demand %", "Required/Preferred", "Priority Score"]]
    
    for s in analysis_data.get('missing_high_priority', [])[:10]:
        gap_data.append([
            s.get('skill_name', ''),
            s.get('category', ''),
            f"{s.get('demand_percentage', 0)}%",
            "Required" if s.get('is_required') else "Preferred",
            str(s.get('priority_score', 0))
        ])

    if len(gap_data) > 1:
        t_gaps = Table(gap_data, colWidths=[130, 140, 100, 90, 80])
        t_gaps.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f3838')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#ffffff')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cce5e0')),
            ('FONTSIZE', (0,1), (-1,-1), 9),
        ]))
        story.append(t_gaps)
    else:
        story.append(Paragraph("No high-priority missing skills detected!", body_style))

    story.append(Spacer(1, 15))

    # Learning Roadmap Table
    story.append(Paragraph("Recommended Learning Sequence", section_heading))
    road_data = [["Step", "Skill Name", "Priority Level", "Evidence & Rationalization"]]
    
    for r in analysis_data.get('roadmap', [])[:8]:
        road_data.append([
            str(r.get('step', '')),
            r.get('skill_name', ''),
            r.get('priority_level', ''),
            r.get('evidence', '')
        ])

    if len(road_data) > 1:
        t_road = Table(road_data, colWidths=[40, 120, 100, 280])
        t_road.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f3838')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cce5e0')),
            ('FONTSIZE', (0,1), (-1,-1), 8.5),
        ]))
        story.append(t_road)

    story.append(Spacer(1, 15))
    story.append(Paragraph("<b>Methodology & Disclaimers:</b> SkillSphere AI calculates skill coverage based on weighted job postings from its analytical star schema warehouse. High demand skills carry weights of 2.0 (Required) and 1.0 (Preferred). Priority scores combine posting frequency, category relevance, and association rule mining.", ParagraphStyle('FooterNote', parent=styles['Italic'], fontSize=8, textColor=colors.HexColor('#4a6865'))))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def generate_csv_export(records: list, headers: list) -> str:
    """Generate clean CSV string from dictionary list."""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    for row in records:
        writer.writerow({h: row.get(h, '') for h in headers})
    return output.getvalue()
