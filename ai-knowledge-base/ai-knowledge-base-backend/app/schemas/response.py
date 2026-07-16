"""Common response model for API"""

from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel):
    """Standard API response wrapper"""

    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Standard error response"""

    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[dict] = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper"""

    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
