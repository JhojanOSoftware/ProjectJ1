"""
Receipt Generator Usage Examples
Demonstrates how to use the virtual receipt generator with various scenarios.
"""

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
        zip_code="62701",
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
        zip_code="60601",
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
        notes="Table 12 - Thank you for dining with us!"
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
        zip_code="94105",
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
        zip_code="73301",
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


def GenerarComprobantes(WaterValue:int, LuzValue: int, AseoValue:int, GasValue:int, nombre_arrendatario: str, nombre_ubicacion:str, direccion_ubicacion:str, Arrendatarios=int):
    """Example 5: PDF Generation"""
    if not PDF_AVAILABLE:
        print("\n=== EXAMPLE 5: PDF Generation (UNAVAILABLE) ===")
        print("Install reportlab to enable PDF generation: pip install reportlab")
        return
    
    print("\n=== EXAMPLE 5: PDF Generation ===")
    
    # Use PDF-enabled generator
    pdf_generator = PDFReceiptGenerator()
    
    business = create_sample_business(nombre_ubicacion, direccion_ubicacion)
    customer = create_sample_customer(nombre_arrendatario)


  
    WaterValue = WaterValue/Arrendatarios
    LuzValue = LuzValue/Arrendatarios
    AseoValue = AseoValue/Arrendatarios
    GasValue = GasValue/Arrendatarios

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
        advanced_pdf = pdf_generator.to_pdf_advanced(receipt, "sample_receipt_advanced.pdf")
        print(f"Advanced PDF generated: {advanced_pdf}")
        
    except Exception as e:
        print(f"Error generating PDF: {e}")
    
    return receipt

def example_bulk_receipts():
    """Example 6: Bulk receipt generation"""
    print("\n=== EXAMPLE 6: Bulk Receipt Generation ===")
    
    generator = ReceiptGenerator()
    business = create_sample_business()
    
    # Generate multiple receipts
    receipt_data = [
        {
            "customer": "John Doe",
            "items": [ReceiptItem("Product A", 2, 15.99), ReceiptItem("Product B", 1, 25.00)],
            "payment": "Credit Card"
        },
        {
            "customer": "Jane Smith", 
            "items": [ReceiptItem("Service X", 1, 100.00, tax_rate=0.08)],
            "payment": "Cash"
        },
        {
            "customer": "Bob Johnson",
            "items": [ReceiptItem("Item 1", 3, 12.50), ReceiptItem("Item 2", 1, 8.75)],
            "payment": "Debit Card"
        }
    ]
    
    receipts = []
    for i, data in enumerate(receipt_data, 1):
        customer = CustomerInfo(name=data["customer"])
        
        receipt = generator.create_receipt(
            business_info=business,
            items=data["items"],
            customer_info=customer,
            payment_method=data["payment"]
        )
        
        # Save each receipt
        filename = f"bulk_receipt_{i:03d}.txt"
        generator.save_to_file(receipt, "text", filename)
        receipts.append(receipt)
        
        print(f"Generated receipt {i}: {receipt.receipt_id} for {data['customer']}")
    
    return receipts

def example_integration_with_fastapi():
    """Example 7: Integration example for FastAPI"""
    print("\n=== EXAMPLE 7: FastAPI Integration Template ===")
    
    integration_code = '''
# Add this to your existing FastAPI app (example.py)

from receipt_generator import ReceiptGenerator, ReceiptItem, BusinessInfo, CustomerInfo
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

# Pydantic models for API
class ReceiptItemModel(BaseModel):
    name: str
    quantity: int
    unit_price: float
    tax_rate: float = 0.0

class BusinessInfoModel(BaseModel):
    name: str
    direccion_ubicacion: str
    city: str
    nombre_ubicacion: str
    zip_code: str
    phone: Optional[str] = None
    email: Optional[str] = None

class CustomerInfoModel(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

class ReceiptCreateModel(BaseModel):
    business_info: BusinessInfoModel
    items: List[ReceiptItemModel]
    customer_info: Optional[CustomerInfoModel] = None
    payment_method: str = "Cash"
    discount: float = 0.0
    format_type: str = "text"  # text, html, json

# Initialize receipt generator
receipt_generator = ReceiptGenerator()

@app.post("/create_receipt")
async def create_virtual_receipt(receipt_data: ReceiptCreateModel):
    try:
        # Convert Pydantic models to dataclasses
        business = BusinessInfo(**receipt_data.business_info.dict())
        
        items = [ReceiptItem(**item.dict()) for item in receipt_data.items]
        
        customer = None
        if receipt_data.customer_info:
            customer = CustomerInfo(**receipt_data.customer_info.dict())
        
        # Create receipt
        receipt = receipt_generator.create_receipt(
            business_info=business,
            items=items,
            customer_info=customer,
            payment_method=receipt_data.payment_method,
            discount=receipt_data.discount
        )
        
        # Generate output based on format
        if receipt_data.format_type.lower() == "html":
            content = receipt_generator.to_html(receipt)
            media_type = "text/html"
        elif receipt_data.format_type.lower() == "json":
            content = receipt_generator.to_json(receipt)
            media_type = "application/json"
        else:  # default to text
            content = receipt_generator.to_text(receipt)
            media_type = "text/plain"
        
        return {
            "receipt_id": receipt.receipt_id,
            "format": receipt_data.format_type,
            "content": content,
            "total": receipt.total
        }
        
    except Exception as e:
        return JSONResponse(
            content={"error": f"Failed to create receipt: {str(e)}"}, 
            status_code=400
        )

# Example usage with curl:
# curl -X POST "http://localhost:8000/create_receipt" -H "Content-Type: application/json" -d '{
#   "business_info": {
#     "name": "Test Store",
#     "direccion_ubicacion": "123 Main St",
#     "city": "Anytown", 
#     "nombre_ubicacion": "CA",
#     "zip_code": "12345"
#   },
#   "items": [
#     {"name": "Item 1", "quantity": 2, "unit_price": 10.50},
#     {"name": "Item 2", "quantity": 1, "unit_price": 25.00}
#   ],
#   "format_type": "html"
# }'
'''
    
    print(integration_code)

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
