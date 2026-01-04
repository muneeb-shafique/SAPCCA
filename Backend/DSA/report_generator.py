from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import io
import datetime

# Brand Colors
PRIMARY_BLUE = colors.HexColor("#3b82f6")
DARK_BG = colors.HexColor("#0f172a")     
LIGHT_TEXT = colors.HexColor("#f1f5f9")  
ACCENT_CYAN = colors.HexColor("#06b6d4")
GRAY_TEXT = colors.HexColor("#64748b")   

def generate_class_report(class_obj, members, assignments, performance_data):
    """
    Generates a premium, modern PDF report for a specific class using Platypus for advanced layout.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0, bottomMargin=0, leftMargin=0, rightMargin=0)
    elements = []
    
    styles = getSampleStyleSheet()
    
    # Custom Styles
    style_title = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.white,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold',
        spaceAfter=10
    )
    style_subtitle = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor("#94a3b8"),
        alignment=TA_LEFT,
        fontName='Helvetica'
    )
    style_section_header = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=PRIMARY_BLUE,
        spaceBefore=20,
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )
    style_text = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.black,
        spaceAfter=5
    )

    # --- 1. Header Section (Drawing directly on canvas via flowable or background) ---
    # We can use a spacer and then a drawing, but easier to use a Table for layout or just a custom Flowable.
    # For simplicity in Platypus, we'll draw the header background in 'onFirstPage'.

    def draw_header(canvas, doc):
        canvas.saveState()
        # Blue Header Background
        canvas.setFillColor(DARK_BG)
        canvas.rect(0, letter[1] - 1.5*inch, letter[0], 1.5*inch, fill=1, stroke=0)
        
        # Accent Line
        canvas.setFillColor(PRIMARY_BLUE)
        canvas.rect(0, letter[1] - 1.55*inch, letter[0], 0.05*inch, fill=1, stroke=0)
        
        # Logo/Icon placeholder (Circle)
        canvas.setFillColor(ACCENT_CYAN)
        canvas.circle(1*inch, letter[1] - 0.75*inch, 20, fill=1, stroke=0)
        
        # Title Text
        canvas.setFont('Helvetica-Bold', 22)
        canvas.setFillColor(colors.white)
        canvas.drawString(1.5*inch, letter[1] - 0.7*inch, f"{class_obj.name}")
        
        # Subtitle
        canvas.setFont('Helvetica', 10)
        canvas.setFillColor(colors.HexColor("#94a3b8"))
        canvas.drawString(1.5*inch, letter[1] - 0.95*inch, f"REPORT GENERATED: {datetime.datetime.now().strftime('%B %d, %Y')}")
        
        # Footer
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(GRAY_TEXT)
        canvas.drawString(0.5*inch, 0.5*inch, "Confidential Class Report  |  SAPCCA System Generated")
        canvas.drawRightString(letter[0] - 0.5*inch, 0.5*inch, f"Page {doc.page}")
        
        canvas.restoreState()

    # Add content to flowables
    # Padding for header
    elements.append(Spacer(1, 1.8*inch))
    
    # --- Class Stats Grid ---
    elements.append(Paragraph("Performance Overview", style_section_header))
    
    # Data for Stats Table
    stats_data = [
        ['Total Students', 'Assignments', 'Avg Grade', 'Status'],
        [str(len(members)), str(len(assignments)), f"{performance_data.get('average_grade', 'N/A')}", "ACTIVE"]
    ]
    
    t_stats = Table(stats_data, colWidths=[2*inch, 2*inch, 2*inch, 1.5*inch])
    t_stats.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor("#f8fafc")),
        ('TEXTCOLOR', (0, 1), (-1, 1), DARK_BG),
        ('FONTSIZE', (0, 1), (-1, 1), 12),
        ('TOPPADDING', (0, 1), (-1, 1), 12),
        ('BOTTOMPADDING', (0, 1), (-1, 1), 12),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
    ]))
    elements.append(t_stats)
    elements.append(Spacer(1, 0.3*inch))
    
    # --- Student Roster ---
    elements.append(Paragraph("Student Roster", style_section_header))
    
    roster_data = [['Student Name', 'Email Address', 'Role', 'Status']]
    for member in members:
        roster_data.append([
            member.display_name or "Unknown",
            member.email,
            member.role.capitalize(),
            "Enrolled"
        ])
        
    t_roster = Table(roster_data, colWidths=[2.5*inch, 3*inch, 1*inch, 1*inch])
    t_roster.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), DARK_BG),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        # Row Striping
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f5f9")]),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor("#334155")),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    elements.append(t_roster)
    elements.append(Spacer(1, 0.5*inch))
    
    # --- Footer/Disclaimer Note ---
    elements.append(Paragraph("Note: This document contains sensitive academic performance data. Please handle with care.", style_text))

    # Build PDF
    doc.build(elements, onFirstPage=draw_header, onLaterPages=draw_header)
    
    buffer.seek(0)
    return buffer

