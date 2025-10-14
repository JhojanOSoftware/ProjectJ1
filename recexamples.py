"""
Receipt Generator Usage Examples
Demonstrates how to use the virtual receipt generator with various scenarios.
"""
from datetime import datetime


from recgenerator import (
    ReceiptGenerator, ReceiptItem, BusinessInfo, CustomerInfo,
    create_sample_business, create_sample_customer
)

# Try to import PDF generator (optional)
try:
    from pdfgen import PDFReceiptGenerator
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("PDF generation not available. Install reportlab for PDF support.")



def GenerarComprobantes(WaterValue:int, LuzValue: int, AseoValue:int, GasValue:int, nombre_arrendatario: str, nombre_ubicacion:str, direccion_ubicacion:str, personas_por_arrendatario:int, Arrendatarios=int):

    
    # Use PDF-enabled generator
    pdf_generator = PDFReceiptGenerator()
    
    business = create_sample_business(nombre_ubicacion, direccion_ubicacion)
    customer = create_sample_customer(nombre_arrendatario)
    


    

    items = [
        ReceiptItem("Agua", 1, WaterValue),
        ReceiptItem("Luz", 1, LuzValue),
        ReceiptItem("Aseo", 1, AseoValue),
        ReceiptItem("Gas", 1, GasValue)
    ]
    
    receipt = pdf_generator.create_receipt(
        business_info=business,
        items=items,
        customer_info=customer,
        payment_method="Efectivo",
    )
    

    
    
    try:
        # Generate simple PDF
        simple_pdf = pdf_generator.to_pdf_simple(receipt, "sample_receipt_simple.pdf")
        print(f"Simple PDF generated: {simple_pdf}")
        
        # Generate advanced PDF
        archivopdf = f"{nombre_arrendatario}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        advanced_pdf = pdf_generator.to_pdf_advanced(receipt, archivopdf)
        print(f"Advanced PDF generated: {advanced_pdf}")
        
    except Exception as e:
        print(f"Error generating PDF: {e}")
    



def main():
    """Run all examples"""
    print("🧾 Virtual Receipt Generator Examples")
    print("=" * 50)
    
    # Run all examples
    examples = [
        #example_basic_receipt,
        #example_restaurant_receipt,
        #example_retail_receipt,
        #example_service_receipt,
        GenerarComprobantes,
        #example_bulk_receipts,
        #example_integration_with_fastapi
    ]
    
    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"Error in {example_func.__name__}: {e}")
        print("\n" + "-" * 50)
    
    print("\n✅ All examples completed!")
    print("Check the generated files in the current directory.")

if __name__ == "__main__":
    main()
