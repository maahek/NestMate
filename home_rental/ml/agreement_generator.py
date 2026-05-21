"""
NestMate — Rental Agreement PDF Generator
Feature 9: Instant Rental Agreement Generation using ReportLab

Generates a fully formatted A4 PDF rental agreement including:
  - Party details (tenant + owner)
  - Property address
  - Financial terms (rent, deposit, maintenance)
  - Tenancy period
  - 8 standard legal clauses
  - Custom clauses (from form input)
  - Signature blocks
  - NestMate branding header

Usage:
  from ml.agreement_generator import generate_agreement_pdf

  generate_agreement_pdf(agreement_data, '/path/to/output.pdf')
"""

import os
from datetime import datetime
from typing import List

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether,
)
from reportlab.platypus.flowables import HRFlowable


# ══════════════════════════════════════════════════════════════════════════════
# COLOUR PALETTE
# ══════════════════════════════════════════════════════════════════════════════

NAVY      = colors.HexColor('#0f172a')
NAVY_MID  = colors.HexColor('#1e293b')
OCHRE     = colors.HexColor('#d97706')
OCHRE_LT  = colors.HexColor('#fef3c7')
GREEN     = colors.HexColor('#16a34a')
GREEN_LT  = colors.HexColor('#dcfce7')
CREAM     = colors.HexColor('#fffbf5')
LIGHT_GRAY= colors.HexColor('#f8fafc')
BORDER    = colors.HexColor('#e2e8f0')
TEXT_GRAY = colors.HexColor('#64748b')
RED_LIGHT = colors.HexColor('#fee2e2')


# ══════════════════════════════════════════════════════════════════════════════
# STANDARD LEGAL CLAUSES
# Included in every agreement automatically
# ══════════════════════════════════════════════════════════════════════════════

STANDARD_CLAUSES = [
    (
        'Rent Payment',
        'The Tenant shall pay the monthly rent by the 5th day of each calendar '
        'month. Payments shall be made via bank transfer, UPI, or cheque. '
        'Late payments shall attract a penalty of ₹100 per day after the '
        'due date, unless otherwise agreed in writing.'
    ),
    (
        'Security Deposit',
        'The security deposit shall be refunded by the Owner to the Tenant '
        'within 30 days of vacating the premises, after deducting any dues '
        'for unpaid rent, utility bills, or damages beyond normal wear and tear. '
        'No interest shall be payable on the security deposit.'
    ),
    (
        'Subletting Prohibited',
        'The Tenant shall not sublet, assign, or part with possession of the '
        'premises or any part thereof without the prior written consent of '
        'the Owner. Any such act without consent shall be grounds for immediate '
        'termination of this agreement.'
    ),
    (
        'Maintenance and Care',
        'The Tenant shall maintain the property in good and clean condition '
        'and shall not cause any wilful damage. Minor day-to-day repairs (up to '
        '₹500 per incident) shall be borne by the Tenant. Major structural '
        'repairs and maintenance of built-in fixtures shall be the '
        'responsibility of the Owner.'
    ),
    (
        'Structural Alterations',
        'The Tenant shall not make any structural alterations, additions, '
        'or improvements to the premises without the prior written consent '
        'of the Owner. Any permitted modifications shall become the property '
        'of the Owner upon vacation, unless otherwise agreed.'
    ),
    (
        'Inspection Rights',
        'The Owner or their authorised representative shall have the right '
        'to inspect the premises at any reasonable time, with a minimum of '
        '24 hours prior notice to the Tenant, except in cases of emergency '
        'where immediate access may be required.'
    ),
    (
        'Termination Notice',
        'Either party may terminate this agreement after the lock-in period '
        'by providing 30 days written notice to the other party. During the '
        'notice period, the Tenant shall continue to pay rent and maintain '
        'the premises. Vacation must be complete by the end of the notice period.'
    ),
    (
        'Dispute Resolution',
        'Any disputes arising out of or in connection with this agreement '
        'shall first be resolved through mutual discussion and mediation. '
        'If unresolved within 30 days, either party may approach the '
        'appropriate court of law having jurisdiction over the property location.'
    ),
]


# ══════════════════════════════════════════════════════════════════════════════
# STYLE BUILDER
# ══════════════════════════════════════════════════════════════════════════════

def _build_styles() -> dict:
    """Build and return all custom paragraph styles."""
    base = getSampleStyleSheet()

    return {
        'doc_title': ParagraphStyle(
            'DocTitle',
            parent     = base['Normal'],
            fontName   = 'Helvetica-Bold',
            fontSize   = 22,
            textColor  = NAVY,
            alignment  = TA_CENTER,
            spaceAfter = 4,
        ),
        'doc_subtitle': ParagraphStyle(
            'DocSubtitle',
            parent     = base['Normal'],
            fontName   = 'Helvetica',
            fontSize   = 10,
            textColor  = TEXT_GRAY,
            alignment  = TA_CENTER,
            spaceAfter = 6,
        ),
        'brand': ParagraphStyle(
            'Brand',
            parent     = base['Normal'],
            fontName   = 'Helvetica-Bold',
            fontSize   = 14,
            textColor  = OCHRE,
            alignment  = TA_CENTER,
            spaceAfter = 2,
        ),
        'section_heading': ParagraphStyle(
            'SectionHeading',
            parent      = base['Normal'],
            fontName    = 'Helvetica-Bold',
            fontSize    = 11,
            textColor   = NAVY,
            spaceBefore = 14,
            spaceAfter  = 8,
        ),
        'clause_title': ParagraphStyle(
            'ClauseTitle',
            parent     = base['Normal'],
            fontName   = 'Helvetica-Bold',
            fontSize   = 9,
            textColor  = NAVY,
            spaceAfter = 3,
        ),
        'body': ParagraphStyle(
            'Body',
            parent     = base['Normal'],
            fontName   = 'Helvetica',
            fontSize   = 9,
            textColor  = colors.HexColor('#1e293b'),
            leading    = 15,
            alignment  = TA_JUSTIFY,
            spaceAfter = 6,
        ),
        'body_center': ParagraphStyle(
            'BodyCenter',
            parent     = base['Normal'],
            fontName   = 'Helvetica',
            fontSize   = 9,
            textColor  = colors.HexColor('#1e293b'),
            alignment  = TA_CENTER,
        ),
        'small_gray': ParagraphStyle(
            'SmallGray',
            parent     = base['Normal'],
            fontName   = 'Helvetica',
            fontSize   = 8,
            textColor  = TEXT_GRAY,
            alignment  = TA_CENTER,
            spaceAfter = 4,
        ),
        'footer': ParagraphStyle(
            'Footer',
            parent     = base['Normal'],
            fontName   = 'Helvetica-Oblique',
            fontSize   = 7.5,
            textColor  = TEXT_GRAY,
            alignment  = TA_CENTER,
        ),
        'label': ParagraphStyle(
            'Label',
            parent   = base['Normal'],
            fontName = 'Helvetica-Bold',
            fontSize = 8,
            textColor= TEXT_GRAY,
        ),
        'value': ParagraphStyle(
            'Value',
            parent   = base['Normal'],
            fontName = 'Helvetica',
            fontSize = 9,
            textColor= NAVY,
        ),
        'amount': ParagraphStyle(
            'Amount',
            parent   = base['Normal'],
            fontName = 'Helvetica-Bold',
            fontSize = 13,
            textColor= NAVY,
        ),
    }


# ══════════════════════════════════════════════════════════════════════════════
# SECTION BUILDERS
# Each function returns a list of ReportLab flowables
# ══════════════════════════════════════════════════════════════════════════════

def _build_header(data: dict, styles: dict) -> list:
    """Build the document header with branding and title."""
    elements = []

    # Brand name
    elements.append(Paragraph('🏠 NestMate', styles['brand']))
    elements.append(Paragraph(
        'RESIDENTIAL RENTAL AGREEMENT',
        styles['doc_title'],
    ))
    elements.append(Paragraph(
        f"Generated on {datetime.now().strftime('%d %B %Y at %I:%M %p')}  "
        f"| Ref: NM-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        styles['doc_subtitle'],
    ))

    elements.append(Spacer(1, 0.3 * cm))
    elements.append(HRFlowable(
        width='100%', thickness=2,
        color=OCHRE, spaceAfter=12,
    ))

    return elements


def _build_parties_section(data: dict, styles: dict) -> list:
    """Build the parties (tenant + owner) section."""
    elements = []

    elements.append(Paragraph('1. PARTIES TO THE AGREEMENT', styles['section_heading']))

    # Two-column party table
    party_table_data = [
        [
            Paragraph('TENANT (Lessee)', ParagraphStyle(
                'PH', fontName='Helvetica-Bold', fontSize=9,
                textColor=colors.white, alignment=TA_CENTER,
            )),
            Paragraph('OWNER (Lessor)', ParagraphStyle(
                'PH2', fontName='Helvetica-Bold', fontSize=9,
                textColor=colors.white, alignment=TA_CENTER,
            )),
        ],
        [
            _party_cell(
                name    = data.get('tenant_name',    'N/A'),
                phone   = data.get('tenant_phone',   ''),
                address = data.get('tenant_address', ''),
                styles  = styles,
            ),
            _party_cell(
                name    = data.get('owner_name',    'N/A'),
                phone   = data.get('owner_phone',   ''),
                address = data.get('owner_address', ''),
                styles  = styles,
            ),
        ],
    ]

    party_table = Table(party_table_data, colWidths=[9 * cm, 9 * cm])
    party_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND',   (0, 0), (0, 0), GREEN),
        ('BACKGROUND',   (1, 0), (1, 0), NAVY),
        ('TEXTCOLOR',    (0, 0), (-1, 0), colors.white),
        ('TOPPADDING',   (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING',(0, 0), (-1, 0), 8),
        # Data rows
        ('BACKGROUND',   (0, 1), (0, 1), GREEN_LT),
        ('BACKGROUND',   (1, 1), (1, 1), colors.HexColor('#eff6ff')),
        ('VALIGN',       (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING',   (0, 1), (-1, 1), 10),
        ('BOTTOMPADDING',(0, 1), (-1, 1), 10),
        ('LEFTPADDING',  (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('GRID',         (0, 0), (-1, -1), 0.5, BORDER),
        ('ROUNDEDCORNERS', [6]),
    ]))
    elements.append(party_table)
    elements.append(Spacer(1, 0.4 * cm))

    return elements


def _party_cell(name: str, phone: str, address: str, styles: dict) -> list:
    """Build the content for one party cell."""
    cell = []
    cell.append(Paragraph(f'<b>{name}</b>', styles['value']))
    if phone:
        cell.append(Paragraph(f'📱 {phone}', styles['body']))
    if address:
        cell.append(Paragraph(f'📍 {address}', styles['body']))
    return cell


def _build_property_section(data: dict, styles: dict) -> list:
    """Build the property details section."""
    elements = []

    elements.append(Paragraph('2. PROPERTY DETAILS', styles['section_heading']))
    elements.append(Paragraph(
        f"<b>Property Address:</b> "
        f"{data.get('property_address', 'As described in listing')}",
        styles['body'],
    ))

    return elements


def _build_financial_section(data: dict, styles: dict) -> list:
    """Build the financial terms section with a styled table."""
    elements = []

    elements.append(Paragraph('3. FINANCIAL TERMS', styles['section_heading']))

    rent        = int(data.get('rent',            0))
    deposit     = int(data.get('deposit',         0))
    maintenance = int(data.get('maintenance',     0))
    duration    = int(data.get('duration_months', 1))
    late_fee    = max(100, rent // 100)

    fin_data = [
        ['Term', 'Amount', 'Notes'],
        ['Monthly Rent',
         f'₹{rent:,}',
         'Payable by 5th of each month'],
        ['Security Deposit',
         f'₹{deposit:,}',
         'Refundable within 30 days of vacating'],
        ['Monthly Maintenance',
         f'₹{maintenance:,}' if maintenance else 'Included',
         'Society / maintenance charges'],
        ['Late Payment Penalty',
         f'₹{late_fee:,}/day',
         'After 5th of month'],
        ['Total Rent (Full Term)',
         f'₹{rent * duration:,}',
         f'Over {duration} months'],
        ['Total Upfront Payment',
         f'₹{rent + deposit:,}',
         '1st month + security deposit'],
    ]

    fin_table = Table(fin_data, colWidths=[5.5 * cm, 4 * cm, 8.5 * cm])
    fin_table.setStyle(TableStyle([
        # Header
        ('BACKGROUND',   (0, 0), (-1, 0), NAVY),
        ('TEXTCOLOR',    (0, 0), (-1, 0), colors.white),
        ('FONTNAME',     (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',     (0, 0), (-1, 0), 9),
        ('TOPPADDING',   (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING',(0, 0), (-1, 0), 8),
        # Data rows
        ('FONTNAME',     (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE',     (0, 1), (-1, -1), 9),
        ('FONTNAME',     (1, 1), (-1, -1), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [LIGHT_GRAY, colors.white]),
        ('GRID',         (0, 0), (-1, -1), 0.5, BORDER),
        ('ALIGN',        (1, 0), (1, -1), 'RIGHT'),
        ('TOPPADDING',   (0, 1), (-1, -1), 7),
        ('BOTTOMPADDING',(0, 1), (-1, -1), 7),
        ('LEFTPADDING',  (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        # Highlight total row
        ('BACKGROUND',   (0, -1), (-1, -1), OCHRE_LT),
        ('FONTNAME',     (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))

    elements.append(fin_table)
    elements.append(Spacer(1, 0.4 * cm))

    return elements


def _build_tenancy_section(data: dict, styles: dict) -> list:
    """Build the tenancy period section."""
    elements = []

    elements.append(Paragraph('4. TENANCY PERIOD', styles['section_heading']))

    start    = data.get('start_date', 'N/A')
    end      = data.get('end_date',   'N/A')
    duration = data.get('duration_months', 'N/A')

    period_data = [
        ['Start Date', 'End Date', 'Duration', 'Lock-in Period'],
        [start, end, f'{duration} months', f'{min(6, int(duration or 6))} months'],
    ]

    period_table = Table(period_data, colWidths=[4.5 * cm, 4.5 * cm, 4.5 * cm, 4.5 * cm])
    period_table.setStyle(TableStyle([
        ('BACKGROUND',   (0, 0), (-1, 0), NAVY_MID),
        ('TEXTCOLOR',    (0, 0), (-1, 0), colors.white),
        ('FONTNAME',     (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',     (0, 0), (-1, -1), 9),
        ('FONTNAME',     (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('BACKGROUND',   (0, 1), (-1, 1), OCHRE_LT),
        ('ALIGN',        (0, 0), (-1, -1), 'CENTER'),
        ('GRID',         (0, 0), (-1, -1), 0.5, BORDER),
        ('TOPPADDING',   (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 8),
    ]))

    elements.append(period_table)
    elements.append(Spacer(1, 0.4 * cm))

    return elements


def _build_standard_clauses(styles: dict) -> list:
    """Build the standard legal clauses section."""
    elements = []

    elements.append(Paragraph('5. STANDARD TERMS & CONDITIONS', styles['section_heading']))
    elements.append(Paragraph(
        'The following terms and conditions form an integral part of this '
        'agreement and are binding on both parties:',
        styles['body'],
    ))
    elements.append(Spacer(1, 0.2 * cm))

    for i, (title, text) in enumerate(STANDARD_CLAUSES, 1):
        clause_block = [
            Paragraph(f'5.{i}  {title.upper()}', styles['clause_title']),
            Paragraph(text, styles['body']),
            Spacer(1, 0.15 * cm),
        ]
        elements.append(KeepTogether(clause_block))

    return elements


def _build_custom_clauses(custom_terms: List[str], styles: dict) -> list:
    """Build the custom / special conditions section."""
    if not custom_terms:
        return []

    elements = []
    elements.append(Paragraph('6. SPECIAL CONDITIONS', styles['section_heading']))
    elements.append(Paragraph(
        'The following special conditions have been mutually agreed upon '
        'by both parties and form part of this agreement:',
        styles['body'],
    ))
    elements.append(Spacer(1, 0.2 * cm))

    for i, term in enumerate(custom_terms, 1):
        elements.append(Paragraph(
            f'6.{i}  {term}',
            styles['body'],
        ))

    elements.append(Spacer(1, 0.3 * cm))
    return elements


def _build_signatures_section(data: dict, styles: dict) -> list:
    """Build the signature blocks section."""
    elements = []

    elements.append(HRFlowable(
        width='100%', thickness=1,
        color=BORDER, spaceBefore=10, spaceAfter=10,
    ))
    elements.append(Paragraph('SIGNATURES', styles['section_heading']))
    elements.append(Paragraph(
        'By signing below, both parties confirm that they have read, '
        'understood, and agreed to all terms of this agreement.',
        styles['body'],
    ))
    elements.append(Spacer(1, 0.5 * cm))

    tenant_signed_at = data.get('tenant_signed_at', '')
    owner_signed_at  = data.get('owner_signed_at',  '')

    sig_data = [
        [
            Paragraph('TENANT SIGNATURE', ParagraphStyle(
                'SH', fontName='Helvetica-Bold', fontSize=8,
                textColor=TEXT_GRAY, alignment=TA_CENTER,
            )),
            Paragraph('', styles['body']),
            Paragraph('OWNER SIGNATURE', ParagraphStyle(
                'SH2', fontName='Helvetica-Bold', fontSize=8,
                textColor=TEXT_GRAY, alignment=TA_CENTER,
            )),
        ],
        [
            Paragraph(
                (f'<b>Digitally Signed: ✅</b><br/>'
                 f'{data.get("tenant_name", "")}<br/>'
                 f'Date: {tenant_signed_at}')
                if tenant_signed_at
                else '<br/><br/>________________________<br/>Signature',
                ParagraphStyle(
                    'SB', fontName='Helvetica', fontSize=9,
                    alignment=TA_CENTER, leading=16,
                )
            ),
            Paragraph('', styles['body']),
            Paragraph(
                (f'<b>Digitally Signed: ✅</b><br/>'
                 f'{data.get("owner_name", "")}<br/>'
                 f'Date: {owner_signed_at}')
                if owner_signed_at
                else '<br/><br/>________________________<br/>Signature',
                ParagraphStyle(
                    'SB2', fontName='Helvetica', fontSize=9,
                    alignment=TA_CENTER, leading=16,
                )
            ),
        ],
        [
            Paragraph(
                f'<b>{data.get("tenant_name", "Tenant Name")}</b><br/>'
                f'Date: {"_____________" if not tenant_signed_at else tenant_signed_at}',
                ParagraphStyle(
                    'SN', fontName='Helvetica', fontSize=8,
                    alignment=TA_CENTER, textColor=TEXT_GRAY,
                )
            ),
            Paragraph('', styles['body']),
            Paragraph(
                f'<b>{data.get("owner_name", "Owner Name")}</b><br/>'
                f'Date: {"_____________" if not owner_signed_at else owner_signed_at}',
                ParagraphStyle(
                    'SN2', fontName='Helvetica', fontSize=8,
                    alignment=TA_CENTER, textColor=TEXT_GRAY,
                )
            ),
        ],
    ]

    sig_table = Table(sig_data, colWidths=[8.5 * cm, 1 * cm, 8.5 * cm])
    sig_table.setStyle(TableStyle([
        ('BACKGROUND',   (0, 1), (0, 1), GREEN_LT),
        ('BACKGROUND',   (2, 1), (2, 1), colors.HexColor('#eff6ff')),
        ('ALIGN',        (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN',       (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID',         (0, 0), (0, -1), 0.5, BORDER),
        ('GRID',         (2, 0), (2, -1), 0.5, BORDER),
        ('TOPPADDING',   (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 10),
        ('LEFTPADDING',  (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))

    elements.append(sig_table)
    return elements


def _build_footer(styles: dict) -> list:
    """Build the document footer."""
    elements = []
    elements.append(Spacer(1, 1 * cm))
    elements.append(HRFlowable(
        width='100%', thickness=0.5,
        color=BORDER, spaceAfter=8,
    ))
    elements.append(Paragraph(
        'This document was generated by NestMate (www.nestmate.in). '
        'Both parties should retain a signed copy of this agreement. '
        'This agreement is subject to the laws of India.',
        styles['footer'],
    ))
    elements.append(Paragraph(
        f'Generated: {datetime.now().strftime("%d %B %Y, %I:%M %p")}  '
        f'| NestMate Platform  |  Confidential Document',
        styles['footer'],
    ))
    return elements


# ══════════════════════════════════════════════════════════════════════════════
# MAIN PDF GENERATOR
# ══════════════════════════════════════════════════════════════════════════════

def generate_agreement_pdf(
    agreement_data: dict,
    output_path:    str,
) -> str:
    """
    Generate a professional rental agreement PDF.

    Args:
        agreement_data: dict containing:
            tenant_name       (str)  Tenant's full name
            tenant_phone      (str)  Tenant's phone number
            tenant_address    (str)  Tenant's address
            owner_name        (str)  Owner's full name
            owner_phone       (str)  Owner's phone number
            owner_address     (str)  Owner's address
            property_address  (str)  Full property address
            rent              (int)  Monthly rent in ₹
            deposit           (int)  Security deposit in ₹
            maintenance       (int)  Monthly maintenance in ₹ (0 if none)
            duration_months   (int)  Agreement duration in months
            start_date        (str)  Start date formatted string
            end_date          (str)  End date formatted string
            custom_terms      (list) List of custom clause strings
            tenant_signed_at  (str)  Optional: date tenant signed
            owner_signed_at   (str)  Optional: date owner signed

        output_path: Absolute path where PDF should be saved.

    Returns:
        output_path on success.

    Raises:
        Exception on PDF generation failure.
    """

    # ── Ensure output directory exists ────────────────────────────────────────
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # ── Configure document ─────────────────────────────────────────────────────
    doc = SimpleDocTemplate(
        output_path,
        pagesize     = A4,
        rightMargin  = 2.0 * cm,
        leftMargin   = 2.0 * cm,
        topMargin    = 2.0 * cm,
        bottomMargin = 2.0 * cm,
        title        = 'NestMate Rental Agreement',
        author       = 'NestMate Platform',
        subject      = f'Rental Agreement — {agreement_data.get("property_address", "")}',
    )

    # ── Build styles ───────────────────────────────────────────────────────────
    styles = _build_styles()

    # ── Assemble all flowable sections ─────────────────────────────────────────
    story = []

    story += _build_header(agreement_data, styles)
    story += _build_parties_section(agreement_data, styles)
    story += _build_property_section(agreement_data, styles)
    story += _build_financial_section(agreement_data, styles)
    story += _build_tenancy_section(agreement_data, styles)
    story += _build_standard_clauses(styles)

    # Custom terms (only if provided)
    custom_terms = agreement_data.get('custom_terms', [])
    if isinstance(custom_terms, (list, tuple)) and custom_terms:
        story += _build_custom_clauses(list(custom_terms), styles)

    story += _build_signatures_section(agreement_data, styles)
    story += _build_footer(styles)

    # ── Build PDF ──────────────────────────────────────────────────────────────
    doc.build(story)

    return output_path


# ══════════════════════════════════════════════════════════════════════════════
# QUICK TEST (run this file directly to test generation)
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    sample_data = {
        'tenant_name':      'Rahul Sharma',
        'tenant_phone':     '+91 98765 43210',
        'tenant_address':   '45, Sector 12, Navi Mumbai, Maharashtra 400703',
        'owner_name':       'Priya Mehta',
        'owner_phone':      '+91 91234 56789',
        'owner_address':    '12, Bandra West, Mumbai, Maharashtra 400050',
        'property_address': 'Flat 3B, Sunrise Apartments, Andheri West, Mumbai 400058',
        'rent':             22000,
        'deposit':          44000,
        'maintenance':      1500,
        'duration_months':  11,
        'start_date':       '01 January 2025',
        'end_date':         '30 November 2025',
        'custom_terms': [
            'Parking space No. B-12 is included in the rent.',
            'Tenant may keep one small pet (under 10 kg) with prior approval.',
            'Power backup for 4 hours is provided by the society.',
        ],
        'tenant_signed_at': '15 December 2024',
        'owner_signed_at':  '15 December 2024',
    }

    out = generate_agreement_pdf(sample_data, '/tmp/test_agreement.pdf')
    print(f'✅ Agreement PDF generated: {out}')