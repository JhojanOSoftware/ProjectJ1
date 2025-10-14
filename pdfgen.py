"""
PDF Receipt Generator Extension
Extends the basic receipt generator with PDF output capability.
"""

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
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
        """Generate advanced PDF using reportlab platypus"""
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab is required for PDF generation. Install with: pip install reportlab")
        
        if filename is None:
            filename = f"receipt_{receipt.receipt_id}_advanced.pdf"
        
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title = Paragraph(f"<para align=center><b>{receipt.business_info.name}</b></para>", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Business info
        business_info = f"""
        <para align=center>
        {receipt.business_info.direccion_ubicacion}<br/>
        {receipt.business_info.city}, {receipt.business_info.nombre_ubicacion} <br/>
        """
        
        if receipt.business_info.phone:
            business_info += f"Numero: {receipt.business_info.phone}<br/>"
        if receipt.business_info.email:
            business_info += f"Email: {receipt.business_info.email}<br/>"
        
        business_info += "</para>"
        
        business_para = Paragraph(business_info, styles['Normal'])
        story.append(business_para)
        story.append(Spacer(1, 20))
        
        # Receipt info
        receipt_info_data = [
            ['Receipt ID:', receipt.receipt_id, 'Fecha:', receipt.date.strftime('%Y-%m-%d %H:%M:%S')],
            ['Metodo de pago:', receipt.payment_method, 'Cliente:', 
             receipt.customer_info.name if receipt.customer_info and receipt.customer_info.name else 'N/A']
        ]
        
        receipt_info_table = Table(receipt_info_data)
        receipt_info_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        
        story.append(receipt_info_table)
        story.append(Spacer(1, 20))
        
        # Items table
        items_data = [['Servicio', 'Precio Unit.', 'Total']]
        
        for item in receipt.items:
            items_data.append([
                item.name,
                f"{item.quantity}",
                f"${item.total:.1f}"
            ])
            
            
        
        items_table = Table(items_data)
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Item names left-aligned
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),  # Prices right-aligned
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(items_table)
        story.append(Spacer(1, 20))
        
        # Totals table
        totals_data = [['Subtotal:', f"${receipt.subtotal:.2f}"]]
        
  
        
        totals_data.append(['TOTAL:', f"${receipt.total:.2f}"])
        
        totals_table = Table(totals_data, colWidths=[3*inch, 1*inch])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
        ]))
        
        story.append(totals_table)
        
        # Notes
        if receipt.notes:
            story.append(Spacer(1, 20))
            notes_para = Paragraph(f"<b>Notes:</b> {receipt.notes}", styles['Normal'])
            story.append(notes_para)
        
        # Footer
        story.append(Spacer(1, 30))
        
        doc.build(story)
 
