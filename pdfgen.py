"""
PDF Receipt Generator Extension
Extends the basic receipt generator with PDF output capability.
"""

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch, cm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_RIGHT
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.colors import HexColor
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("Warning: reportlab not installed. PDF generation unavailable.")
    print("Install with: pip install reportlab")

from recgenerator import Receipt, ReceiptGenerator


class PDFReceiptGenerator(ReceiptGenerator):
    """Extended receipt generator with PDF support"""
    
    def to_pdf_simple(self, receipt: Receipt, filename: str = None) -> str:
        """Generate simple PDF using reportlab canvas"""
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab is required for PDF generation. Install with: pip install reportlab")
        
        if filename is None:
            filename = f"receipt_{receipt.receipt_id}.pdf"
        
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter
        
        # Starting y position
        y = height - 50
        
        # Title
        c.setFont("Helvetica-Bold", 18)
        y -= 25
        
        # Business info
        c.setFont("Helvetica", 12)
        y -= 15
        y -= 15
        
        if receipt.business_info.phone:
            y -= 15
        
        if receipt.business_info.email:
            y -= 15
        
        # Line separator
        y -= 20
        c.line(50, y, width-50, y)
        y -= 30
        
        # Receipt info
        c.setFont("Helvetica", 10)
        c.drawString(50, y, f"Receipt ID: {receipt.receipt_id}")
        c.drawRightString(width-50, y, f"Fecha: {receipt.date.strftime('%Y-%m-%d %H:%M:%S')}")
        y -= 15
        c.drawString(50, y, f"Metodo de Pago: {receipt.payment_method}")
        
        if receipt.customer_info and receipt.customer_info.name:
            c.drawRightString(width-50, y, f"Cliente: {receipt.customer_info.name}")
        y -= 30
        
        # Items header
        c.line(50, y, width-50, y)
        y -= 10
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, "Servicio")
        c.drawString(250, y, "Cantidad")
        c.drawRightString(width-50, y, "Total")
        y -= 5
        c.line(50, y, width-50, y)
        y -= 15
        
        # Items
        c.setFont("Helvetica", 10)
        for item in receipt.items:
            if y < 100:  # Start new page if needed
                c.showPage()
                y = height - 50
            
            c.drawString(50, y, item.name[:25])
            c.drawRightString(width-50, y, f"${item.total:.2f}")
            y -= 15
            

        # Totals
        y -= 10
        c.line(50, y, width-50, y)
        y -= 20
        
        c.drawString(300, y, "Subtotal:")
        c.drawRightString(width-50, y, f"${receipt.subtotal:.2f}")
        y -= 15
        

        
  
        
        # Final total
        c.line(300, y, width-50, y)
        y -= 15
        c.setFont("Helvetica-Bold", 12)
        c.drawString(300, y, "TOTAL:")
        c.drawRightString(width-50, y, f"${receipt.total:.2f}")
        
        # Notes
        if receipt.notes:
            y -= 30
            c.setFont("Helvetica", 10)
            c.drawString(50, y, f"Notes: {receipt.notes}")
        
        # Footer
        y -= 40
        c.line(50, y, width-50, y)
        y -= 20
        c.setFont("Helvetica-Oblique", 12)
        
        c.save()
        return filename
    
    def to_pdf_advanced(self, receipt: Receipt, filename: str = None) -> str:
        """Generate professional PDF receipt with modern two-column layout."""
        if not REPORTLAB_AVAILABLE:
            raise ImportError(
                "reportlab is required for PDF generation. "
                "Install with: pip install reportlab"
            )

        if filename is None:
            filename = f"receipt_{receipt.receipt_id}_advanced.pdf"

        # ── Color palette ──
        C_PRIMARY   = HexColor("#1a1a2e")
        C_ACCENT    = HexColor("#16213e")
        C_TEXT      = HexColor("#2d2d2d")
        C_MUTED     = HexColor("#6b7280")
        C_TBL_HDR   = HexColor("#374151")
        C_LINE      = HexColor("#d1d5db")
        C_ROW_ALT   = HexColor("#f9fafb")
        C_TOTAL_BG  = HexColor("#f3f4f6")
        C_WHITE     = HexColor("#ffffff")

        # ── Helpers ──
        def fmt_cop(value):
            """Format a number as Colombian pesos ($xx.xxx)."""
            rounded = int(round(float(value)))
            formatted = f"{rounded:,}".replace(",", ".")
            return f"${formatted}"

        def _divider(width):
            """Return a thin horizontal-line flowable."""
            t = Table([[""]], colWidths=[width])
            t.setStyle(TableStyle([
                ('LINEBELOW', (0, 0), (-1, -1), 0.5, C_LINE),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
            return t

        # ── Document setup (A4, comfortable margins) ──
        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            topMargin=1.5 * cm,
            bottomMargin=1.5 * cm,
        )
        W = doc.width          # usable width between margins
        story = []

        # ── Base paragraph styles ──
        s_left = ParagraphStyle(
            'LeftBase', fontName='Helvetica',
            fontSize=10, textColor=C_TEXT, leading=13,
        )
        s_right = ParagraphStyle(
            'RightBase', fontName='Helvetica',
            fontSize=10, textColor=C_TEXT, leading=13,
            alignment=TA_RIGHT,
        )

        # ================================================================
        # 1. HEADER – two-column layout
        # ================================================================
        phone_line = (
            f'<br/><font size="9" color="#6b7280">Teléfono:</font>'
            f'<br/>{receipt.business_info.phone}'
            if receipt.business_info.phone else ''
        )
        email_line = (
            f'<br/><font size="9" color="#6b7280">Email:</font>'
            f'<br/>{receipt.business_info.email}'
            if receipt.business_info.email else ''
        )

        left_html = (
            f'<font size="14"><b>SERVICIOS DE ARRENDAMIENTO</b></font><br/>'
            f'<font size="12" color="#16213e"><b>'
            f'{receipt.business_info.nombre_ubicacion}</b></font>'
            f'<br/><br/>'
            f'<font size="9" color="#6b7280">Dirección:</font><br/>'
            f'{receipt.business_info.direccion_ubicacion}'
            f'{phone_line}{email_line}'
        )
        right_html = (
            f'<font size="12"><b>RECIBO DE PAGO</b></font><br/><br/>'
            f'<font size="9" color="#6b7280">Número:</font><br/>'
            f'{receipt.receipt_id}<br/>'
            f'<br/><font size="9" color="#6b7280">Fecha:</font><br/>'
            f'{receipt.date.strftime("%d/%m/%Y %H:%M")}<br/>'
            f'<br/><font size="9" color="#6b7280">Método de pago:</font><br/>'
            f'{receipt.payment_method}'
        )

        header_table = Table(
            [[Paragraph(left_html, s_left),
              Paragraph(right_html, s_right)]],
            colWidths=[W * 0.55, W * 0.45],
        )
        header_table.setStyle(TableStyle([
            ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING',   (0, 0), (0, 0), 0),
            ('RIGHTPADDING',  (-1, -1), (-1, -1), 0),
            ('TOPPADDING',    (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))

        story.append(header_table)
        story.append(Spacer(1, 14))
        story.append(_divider(W))
        story.append(Spacer(1, 14))

        # ================================================================
        # 2. DATOS DEL ARRENDATARIO
        # ================================================================
        tenant_name = (
            receipt.customer_info.name
            if receipt.customer_info and receipt.customer_info.name
            else 'N/A'
        )
        tenant_html = (
            f'<font size="10" color="#1a1a2e"><b>'
            f'DATOS DEL ARRENDATARIO</b></font><br/><br/>'
            f'<font size="9" color="#6b7280">Nombre:</font><br/>'
            f'<font size="11"><b>{tenant_name}</b></font>'
        )
        story.append(Paragraph(tenant_html, s_left))
        story.append(Spacer(1, 14))
        story.append(_divider(W))
        story.append(Spacer(1, 18))

        # ================================================================
        # 3. SERVICES TABLE – only Concepto | Valor
        # ================================================================
        hdr_l = ParagraphStyle(
            'TblHdrL', fontName='Helvetica-Bold',
            fontSize=10, textColor=C_WHITE, leading=13,
        )
        hdr_r = ParagraphStyle(
            'TblHdrR', fontName='Helvetica-Bold',
            fontSize=10, textColor=C_WHITE, leading=13,
            alignment=TA_RIGHT,
        )
        cel_l = ParagraphStyle(
            'CelL', fontName='Helvetica',
            fontSize=10, textColor=C_TEXT, leading=13,
        )
        cel_r = ParagraphStyle(
            'CelR', fontName='Helvetica',
            fontSize=10, textColor=C_TEXT, leading=13,
            alignment=TA_RIGHT,
        )

        tbl_data = [
            [Paragraph("Concepto", hdr_l),
             Paragraph("Valor", hdr_r)],
        ]
        for item in receipt.items:
            tbl_data.append([
                Paragraph(item.name, cel_l),
                Paragraph(fmt_cop(item.total), cel_r),
            ])

        svc_table = Table(tbl_data, colWidths=[W * 0.65, W * 0.35])

        svc_cmds = [
            ('BACKGROUND',    (0, 0), (-1, 0), C_TBL_HDR),
            ('TOPPADDING',    (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING',   (0, 0), (-1, -1), 12),
            ('RIGHTPADDING',  (0, 0), (-1, -1), 12),
            ('LINEBELOW',     (0, 0), (-1, -1), 0.5, C_LINE),
            ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ]
        # Alternate-row shading
        for i in range(1, len(tbl_data)):
            if i % 2 == 0:
                svc_cmds.append(
                    ('BACKGROUND', (0, i), (-1, i), C_ROW_ALT)
                )

        svc_table.setStyle(TableStyle(svc_cmds))
        story.append(svc_table)
        story.append(Spacer(1, 16))

        # ================================================================
        # 4. TOTALS
        # ================================================================
        lbl_n = ParagraphStyle(
            'TotLbl', fontName='Helvetica',
            fontSize=10, textColor=C_TEXT, leading=13,
            alignment=TA_RIGHT,
        )
        val_n = ParagraphStyle(
            'TotVal', fontName='Helvetica',
            fontSize=10, textColor=C_TEXT, leading=13,
            alignment=TA_RIGHT,
        )
        lbl_b = ParagraphStyle(
            'TotLblB', fontName='Helvetica-Bold',
            fontSize=13, textColor=C_PRIMARY, leading=17,
            alignment=TA_RIGHT,
        )
        val_b = ParagraphStyle(
            'TotValB', fontName='Helvetica-Bold',
            fontSize=13, textColor=C_PRIMARY, leading=17,
            alignment=TA_RIGHT,
        )

        totals_data = [
            [Paragraph("Subtotal", lbl_n),
             Paragraph(fmt_cop(receipt.subtotal), val_n)],
            [Paragraph("TOTAL", lbl_b),
             Paragraph(fmt_cop(receipt.total), val_b)],
        ]

        totals_table = Table(
            totals_data, colWidths=[W * 0.65, W * 0.35],
        )
        totals_table.setStyle(TableStyle([
            ('ALIGN',         (0, 0), (-1, -1), 'RIGHT'),
            ('TOPPADDING',    (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING',   (0, 0), (-1, -1), 12),
            ('RIGHTPADDING',  (0, 0), (-1, -1), 12),
            ('LINEABOVE',     (0, -1), (-1, -1), 1.5, C_PRIMARY),
            ('BACKGROUND',    (0, -1), (-1, -1), C_TOTAL_BG),
        ]))

        story.append(totals_table)

        # ── Notes ──
        if receipt.notes:
            story.append(Spacer(1, 20))
            ns = ParagraphStyle(
                'Notes', fontName='Helvetica',
                fontSize=9, textColor=C_MUTED, leading=12,
            )
            story.append(Paragraph(
                f"<b>Notas:</b> {receipt.notes}", ns,
            ))

        doc.build(story)
        return filename
