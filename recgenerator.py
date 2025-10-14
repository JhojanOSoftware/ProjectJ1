"""
Virtual Receipt Generator
A comprehensive Python system for generating virtual receipts in multiple formats.
"""

import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from decimal import Decimal, ROUND_HALF_UP


@dataclass
class ReceiptItem:
    """Individual item on a receipt"""
    name: str
    quantity: int
    unit_price: int
    
    @property
    def subtotal(self) -> float:
        return (self.quantity * self.unit_price)
    
  
    
    @property
    def total(self) -> float:
        return (self.subtotal)


@dataclass
class BusinessInfo:
    """Business information for receipt header"""
    name: str
    direccion_ubicacion: str
    city: str
    nombre_ubicacion: str
    phone: Optional[str] = None
    email: Optional[str] = None
    
    website: Optional[str] = None


@dataclass
class CustomerInfo:
    """Customer information"""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    direccion_ubicacion: Optional[str] = None


@dataclass
class Receipt:
    """Main receipt class"""
    business_info: BusinessInfo
    items: List[ReceiptItem]
    customer_info: Optional[CustomerInfo] = None
    receipt_id: str = None
    date: datetime = None
    payment_method: str = "Cash"
    notes: Optional[str] = None
    discount: float = 0.0
    
    def __post_init__(self):
        if self.receipt_id is None:
            self.receipt_id = str(uuid.uuid4())[:8].upper()
        if self.date is None:
            self.date = datetime.now()
    
    @property
    def subtotal(self) -> float:
        return round(sum(item.subtotal for item in self.items), 2)
    
   
    
    @property
    def discount_amount(self) -> float:
        return round(self.subtotal * self.discount, 2)
    
    @property
    def total(self) -> float:
        return round(self.subtotal )


class ReceiptGenerator:
    """Receipt generator with multiple output formats"""
    
    def __init__(self):
        self.receipts_history = []
    
    def create_receipt(self, business_info: BusinessInfo, items: List[ReceiptItem], 
                      customer_info: Optional[CustomerInfo] = None, **kwargs) -> Receipt:
        """Create a new receipt"""
        receipt = Receipt(
            business_info=business_info,
            items=items,
            customer_info=customer_info,
            **kwargs
        )
        self.receipts_history.append(receipt)
        return receipt
    
    def to_text(self, receipt: Receipt) -> str:
        """Generate receipt as formatted text"""
        lines = []
        
        # Header
        lines.append("=" * 50)
        lines.append(f"{receipt.business_info.name}".center(50))
        lines.append(f"{receipt.business_info.direccion_ubicacion}".center(50))
        lines.append(f"{receipt.business_info.city}, {receipt.business_info.nombre_ubicacion}".center(50))
        
        if receipt.business_info.phone:
            lines.append(f"Phone: {receipt.business_info.phone}".center(50))
        if receipt.business_info.email:
            lines.append(f"Email: {receipt.business_info.email}".center(50))
        
        lines.append("=" * 50)
        
        # Receipt info
        lines.append(f"Receipt ID: {receipt.receipt_id}")
        lines.append(f"Date: {receipt.date.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Payment Method: {receipt.payment_method}")
        
        if receipt.customer_info and receipt.customer_info.name:
            lines.append(f"Customer: {receipt.customer_info.name}")
        
        lines.append("-" * 50)
        
        # Items header
        lines.append(f"{'Item':<20} {'Qty':<5} {'Price':<10} {'Total':<10}")
        lines.append("-" * 50)
        
        # Items
        for item in receipt.items:
            lines.append(f"{item.name[:20]:<20} {item.quantity:<5} ${item.unit_price:<9.2f} ${item.total:<9.2f}")
           
        
        lines.append("-" * 50)
        
        # Totals
        lines.append(f"{'Subtotal:':<40} ${receipt.subtotal:>9.2f}")
        
        if receipt.discount > 0:
            lines.append(f"{'Discount (' + str(int(receipt.discount * 100)) + '%):':<40} -${receipt.discount_amount:>8.2f}")
        
        
        
        lines.append(f"{'TOTAL:':<40} ${receipt.total:>9.2f}")
        lines.append("=" * 50)
        
        if receipt.notes:
            lines.append(f"Notes: {receipt.notes}")
            lines.append("=" * 50)
        
        lines.append("=" * 50)
        
        return "\n".join(lines)
    
    def to_html(self, receipt: Receipt) -> str:
        """Generate receipt as HTML"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Receipt #{receipt.receipt_id}</title>
            <style>
                body {{ 
                    font-family: 'Courier New', monospace; 
                    margin: 20px; 
                    background-color: #f5f5f5;
                }}
                .receipt {{ 
                    background: white; 
                    padding: 20px; 
                    max-width: 400px; 
                    margin: 0 auto; 
                    border: 1px solid #ddd;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }}
                .header {{ 
                    text-align: center; 
                    border-bottom: 2px solid #333; 
                    padding-bottom: 10px; 
                    margin-bottom: 15px;
                }}
                .business-name {{ 
                    font-size: 18px; 
                    font-weight: bold; 
                    margin-bottom: 5px;
                }}
                .receipt-info {{ 
                    margin: 15px 0; 
                    border-bottom: 1px dashed #333; 
                    padding-bottom: 10px;
                }}
                .items-table {{ 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin: 15px 0;
                }}
                .items-table th, .items-table td {{ 
                    text-align: left; 
                    padding: 5px 0; 
                    border-bottom: 1px dotted #ccc;
                }}
                .items-table th {{ 
                    font-weight: bold; 
                    border-bottom: 1px solid #333;
                }}
                .totals {{ 
                    margin-top: 15px; 
                    border-top: 1px solid #333; 
                    padding-top: 10px;
                }}
                .total-line {{ 
                    display: flex; 
                    justify-content: space-between; 
                    margin: 5px 0;
                }}
                .final-total {{ 
                    font-weight: bold; 
                    font-size: 16px; 
                    border-top: 1px solid #333; 
                    padding-top: 5px; 
                    margin-top: 10px;
                }}
                .footer {{ 
                    text-align: center; 
                    margin-top: 20px; 
                    border-top: 1px dashed #333; 
                    padding-top: 15px;
                }}
            </style>
        </head>
        <body>
            <div class="receipt">
                <div class="header">
                    <div class="business-name">{receipt.business_info.name}</div>
                    <div>{receipt.business_info.direccion_ubicacion}</div>
                    <div>{receipt.business_info.city}, {receipt.business_info.nombre_ubicacion}</div>"""

        if receipt.business_info.phone:
            html += f"<div>Phone: {receipt.business_info.phone}</div>"
        if receipt.business_info.email:
            html += f"<div>Email: {receipt.business_info.email}</div>"
        
        html += f"""
                </div>
                
                <div class="receipt-info">
                    <div>Receipt ID: {receipt.receipt_id}</div>
                    <div>Date: {receipt.date.strftime('%Y-%m-%d %H:%M:%S')}</div>
                    <div>Payment: {receipt.payment_method}</div>"""
        
        if receipt.customer_info and receipt.customer_info.name:
            html += f"<div>Customer: {receipt.customer_info.name}</div>"
        
        html += """
                </div>
                
                <table class="items-table">
                    <thead>
                        <tr>
                            <th>Item</th>
                            <th>Qty</th>
                            <th>Price</th>
                            <th>Total</th>
                        </tr>
                    </thead>
                    <tbody>"""
        
        for item in receipt.items:
            html += f"""
                        <tr>
                            <td>{item.name}</td>
                            <td>{item.quantity}</td>
                            <td>${item.unit_price:.2f}</td>
                            <td>${item.total:.2f}</td>
                        </tr>"""
            
        html += """
                    </tbody>
                </table>
                
                <div class="totals">
                    <div class="total-line">
                        <span>Subtotal:</span>
                        <span>${:.2f}</span>
                    </div>""".format(receipt.subtotal)
        
        if receipt.discount > 0:
            html += f"""
                    <div class="total-line">
                        <span>Discount ({int(receipt.discount * 100)}%):</span>
                        <span>-${receipt.discount_amount:.2f}</span>
                    </div>"""
        
        
        html += f"""
                    <div class="total-line final-total">
                        <span>TOTAL:</span>
                        <span>${receipt.total:.2f}</span>
                    </div>
                </div>"""
        
        if receipt.notes:
            html += f"""
                <div style="margin-top: 15px; padding: 10px; background-color: #f9f9f9; border-left: 3px solid #007bff;">
                    <strong>Notes:</strong> {receipt.notes}
                </div>"""
        
        html += """
                <div class="footer">
                </div>
            </div>
        </body>
        </html>"""
        
        return html
    
    def to_json(self, receipt: Receipt) -> str:
        """Generate receipt as JSON"""
        receipt_dict = {
            'receipt_id': receipt.receipt_id,
            'date': receipt.date.isoformat(),
            'business_info': asdict(receipt.business_info),
            'customer_info': asdict(receipt.customer_info) if receipt.customer_info else None,
            'items': [asdict(item) for item in receipt.items],
            'payment_method': receipt.payment_method,
            'notes': receipt.notes,
            'discount': receipt.discount,
            'totals': {
                'subtotal': receipt.subtotal,
                'discount_amount': receipt.discount_amount,
                'total': receipt.total
            }
        }
        return json.dumps(receipt_dict, indent=2, ensure_ascii=False)
    
    def save_to_file(self, receipt: Receipt, format_type: str = "text", filename: str = None):
        """Save receipt to file"""
        if filename is None:
            filename = f"receipt_{receipt.receipt_id}.{format_type.lower()}"
        
        if format_type.lower() == "text":
            content = self.to_text(receipt)
        elif format_type.lower() == "html":
            content = self.to_html(receipt)
        elif format_type.lower() == "json":
            content = self.to_json(receipt)
        else:
            raise ValueError("Format must be 'text', 'html', or 'json'")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filename


# Utility functions for quick receipt creation
def create_sample_business(nombre_ubicacion:str, direccion_ubicacion:str) -> BusinessInfo:
    """Testeo Inicial"""
    return BusinessInfo(
        name="Servicios de Arrendamiento" + " " + nombre_ubicacion,
        direccion_ubicacion=direccion_ubicacion,
        city="Bogota",
        nombre_ubicacion=nombre_ubicacion,
        phone="3102145373",
        email="N/A",
        
    )


def create_sample_customer(nombre_arrendatario:str) -> CustomerInfo:
    """Create a sample customer for testing"""
    return CustomerInfo(
        name=nombre_arrendatario,
        email="example@email.com",
        phone="000 000 0000"
    )

