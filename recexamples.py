"""
Receipt Generator Usage Examples
Demonstrates how to use the virtual receipt generator with various scenarios.
"""
from datetime import datetime
import os


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

def example_basic_receipt():
    """Example 1: Basic cash receipt"""
    print("=== EXAMPLE 1: Basic Cash Receipt ===")
    
    # Create generator
    generator = ReceiptGenerator()
    
    # Create business info
    business = BusinessInfo(
        name="Jhojan's Coffee Shop",
        direccion_ubicacion="123 Main Street",
        city="Springfield",
        nombre_ubicacion="IL",
        phone="(217) 555-0123",
        email="info@joescoffee.com"
    )
    
    # Create items
    items = [
        ReceiptItem("Large Coffee", 2, 3.50),
        ReceiptItem("Blueberry Muffin", 1, 2.25),
        ReceiptItem("Croissant", 1, 1.75)
    ]
    
    # Create receipt
    receipt = generator.create_receipt(
        business_info=business,
        items=items,
        payment_method="Cash"
    )
    
    # Display text version
    print(generator.to_text(receipt))
    
    # Save to files
    generator.save_to_file(receipt, "text", "basic_receipt.txt")
    generator.save_to_file(receipt, "html", "basic_receipt.html")
    generator.save_to_file(receipt, "json", "basic_receipt.json")
    
    print(f"Receipt saved as: basic_receipt.txt, basic_receipt.html, basic_receipt.json")
    return receipt

def example_restaurant_receipt():
    """Example 2: Restaurant receipt with taxes and customer info"""
    print("\n=== EXAMPLE 2: Restaurant Receipt with Tax ===")
    
    generator = ReceiptGenerator()
    
    business = BusinessInfo(
        name="Bella Vista Restaurant",
        direccion_ubicacion="456 Oak Avenue",
        city="Chicago",
        nombre_ubicacion="IL",
        phone="(312) 555-0456",
        email="orders@bellavista.com",
        tax_id="36-1234567"
    )
    
    customer = CustomerInfo(
        name="Alice Johnson",
        phone="(555) 123-4567"
    )
    
    # Items with tax
    items = [
        ReceiptItem("Caesar Salad", 1, 12.95, tax_rate=0.08),
        ReceiptItem("Grilled Salmon", 2, 24.95, tax_rate=0.08),
        ReceiptItem("Red Wine Glass", 2, 8.50, tax_rate=0.08),
        ReceiptItem("Tiramisu", 1, 6.95, tax_rate=0.08)
    ]
    
    receipt = generator.create_receipt(
        business_info=business,
        items=items,
        customer_info=customer,
        payment_method="Credit Card",
        notes="Table 12 - "
    )
    
    print(generator.to_text(receipt))
    
    # Save files
    generator.save_to_file(receipt, "html", "restaurant_receipt.html")
    return receipt

def example_retail_receipt():
    """Example 3: Retail receipt with discounts"""
    print("\n=== EXAMPLE 3: Retail Receipt with Discount ===")
    
    generator = ReceiptGenerator()
    
    business = BusinessInfo(
        name="TechGear Electronics",
        direccion_ubicacion="789 Technology Blvd",
        city="San Francisco",
        nombre_ubicacion="CA",
        phone="(415) 555-0789",
        email="sales@techgear.com",
        website="www.techgear.com"
    )
    
    customer = CustomerInfo(
        name="Bob Smith",
        email="bob.smith@email.com",
        phone="(555) 987-6543"
    )
    
    items = [
        ReceiptItem("Wireless Bluetooth Headphones", 1, 129.99, tax_rate=0.0875),
        ReceiptItem("USB-C Cable (3ft)", 2, 19.99, tax_rate=0.0875),
        ReceiptItem("Phone Case", 1, 24.99, tax_rate=0.0875),
        ReceiptItem("Screen Protector", 1, 12.99, tax_rate=0.0875)
    ]
    
    receipt = generator.create_receipt(
        business_info=business,
        items=items,
        customer_info=customer,
        payment_method="Debit Card",
        discount=0.10,  # 10% discount
        notes="Member discount applied. Warranty valid for 1 year."
    )
    receipt2 = generator.create_receipt(
        business_info=business,
        items=items,
        customer_info=customer,
        payment_method="Debit Card",
        discount=0.10,  # 10% discount
        notes="Member discount applied. Warranty valid for 1 year."
    )
    
    print(generator.to_text(receipt))
    print(generator.to_text(receipt2))
    # Save files
    generator.save_to_file(receipt, "json", "retail_receipt.json")
    
    return receipt

def example_service_receipt():
    """Example 4: Service-based receipt"""
    print("\n=== EXAMPLE 4: Service Receipt ===")
    
    generator = ReceiptGenerator()
    
    business = BusinessInfo(
        name="QuickFix Auto Repair",
        direccion_ubicacion="321 Garage Lane",
        city="Austin",
        nombre_ubicacion="TX",
        phone="(512) 555-0321",
        email="service@quickfix.com"
    )
    
    customer = CustomerInfo(
        name="Maria Garcia",
        phone="(555) 456-7890",
        direccion_ubicacion="123 Residential St, Austin, TX"
    )
    
    items = [
        ReceiptItem("Oil Change Service", 1, 45.00, tax_rate=0.0625),
        ReceiptItem("Air Filter Replacement", 1, 25.00, tax_rate=0.0625),
        ReceiptItem("Brake Inspection", 1, 30.00, tax_rate=0.0625),
        ReceiptItem("Labor (2 hours)", 2, 85.00, tax_rate=0.0625)
    ]
    
    receipt = generator.create_receipt(
        business_info=business,
        items=items,
        customer_info=customer,
        payment_method="Cash",
        notes="Vehicle: 2018 Honda Civic, License: ABC-1234. Next service recommended in 6 months."
    )
    receipt2 = generator.create_receipt(
        business_info=business,
        items=items,
        customer_info=customer,
        payment_method="Cash",
        notes="Vehicle: 2018 Honda Civic, License: ABC-1234. Next service recommended in 6 months."
    )

    print(generator.to_text(receipt, receipt2))
    return receipt, receipt2



def GenerarComprobantes(WaterValue:int, LuzValue: int, AseoValue:int, GasValue:int, nombre_arrendatario: str, nombre_ubicacion:str, direccion_ubicacion:str, personas_por_arrendatario:int, Arrendatarios=int,output_path=None):

    
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
        #simple_pdf = pdf_generator.to_pdf_simple(receipt, "sample_receipt_simple.pdf")
        #print(f"Simple PDF generated: {simple_pdf}")
        
        # crear nombre de archivo y si se pasa output_path usarlo
        safe_name = nombre_arrendatario.replace(" ", "_")
        filename = f"{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        if output_path:
            filepath = os.path.join(output_path, filename)
        else:
            filepath = filename

        # to_pdf_advanced debe escribir el PDF en la ruta completa que le pasemos
        pdf_generator.to_pdf_advanced(receipt, filepath)
        return filepath

    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None
    
    



def main():
    """Run all examples"""
    print("🧾 Virtual Receipt Generator Examples")
    print("=" * 50)
    
    
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
