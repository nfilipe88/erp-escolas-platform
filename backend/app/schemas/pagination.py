# backend/app/schemas/pagination.py - NOVO ARQUIVO
from pydantic import BaseModel
from typing import Generic, TypeVar, List
from math import ceil

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    """Resposta paginada genérica"""
    items: List[T]
    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_prev: bool
    
    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int,
        per_page: int
    ):
        total_pages = ceil(total / per_page) if per_page > 0 else 0
        
        return cls(
            items=items,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )