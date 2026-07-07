from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class VendorCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    type: str = Field(..., pattern="^(Food|Beverage|Merchandise)$")
    zone_id: str

class VendorResponse(VendorCreate):
    id: str
    status: str

    class Config:
        from_attributes = True

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    category: str
    price: float = Field(..., ge=0.0)
    cost: float = Field(..., ge=0.0)

class ProductResponse(ProductCreate):
    id: str

    class Config:
        from_attributes = True

class InventoryCreate(BaseModel):
    vendor_id: str
    product_id: str
    current_stock: int = Field(0, ge=0)
    min_threshold: int = Field(10, ge=0)
    max_capacity: int = Field(500, ge=1)

class InventoryUpdate(BaseModel):
    current_stock: int = Field(..., ge=0)

class InventoryResponse(BaseModel):
    id: str
    vendor_id: str
    product_id: str
    current_stock: int
    min_threshold: int
    max_capacity: int

    class Config:
        from_attributes = True

class RestockRequest(BaseModel):
    vendor_id: str
    product_id: str
    quantity: int = Field(..., ge=1)

class RestockOrderResponse(RestockRequest):
    id: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class VendorAnalyticsResponse(BaseModel):
    vendor_id: str
    sales_volume_units: int
    revenue_usd: float
    cost_usd: float
    net_profit_usd: float
    popular_products: List[str]
