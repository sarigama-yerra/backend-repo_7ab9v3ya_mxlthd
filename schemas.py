"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
Each Pydantic model name maps to a lowercase collection name.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class RafaelSession(BaseModel):
    """
    Clinical session logs
    Collection name: "rafaelsession"
    """
    role: str = Field(..., description="Clinician or Patient")
    simple_view: bool = Field(False, description="Simple vs Clinical view")
    symptoms: Optional[str] = Field(None)
    vitals: Optional[str] = Field(None)
    history: Optional[str] = Field(None)
    image_filename: Optional[str] = None
    video_filename: Optional[str] = None
    output: Dict[str, Any] = Field(default_factory=dict, description="Final fused JSON output")
    confidence: Optional[float] = Field(None, ge=0, le=1)

# Example schemas kept for reference
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = None
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
