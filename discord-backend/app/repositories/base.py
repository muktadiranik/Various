# app/repositories/base.py
from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.sql import Select
from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session
    
    async def create(self, **kwargs) -> ModelType:
        """Create a new record"""
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance
    
    async def get(self, id: int) -> Optional[ModelType]:
        """Get record by ID"""
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_multi(
        self, 
        skip: int = 0, 
        limit: int = 100,
        order_by: Optional[str] = None,
        desc: bool = False,
        **filters
    ) -> List[ModelType]:
        """Get multiple records with filters and pagination"""
        query = select(self.model)
        
        for key, value in filters.items():
            if hasattr(self.model, key) and value is not None:
                query = query.where(getattr(self.model, key) == value)
        
        if order_by and hasattr(self.model, order_by):
            order_col = getattr(self.model, order_by)
            if desc:
                query = query.order_by(order_col.desc())
            else:
                query = query.order_by(order_col)
        
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def update(self, id: int, **kwargs) -> Optional[ModelType]:
        """Update a record"""
        await self.session.execute(
            update(self.model)
            .where(self.model.id == id)
            .values(**kwargs)
        )
        await self.session.flush()
        return await self.get(id)
    
    async def delete(self, id: int) -> bool:
        """Delete a record"""
        result = await self.session.execute(
            delete(self.model).where(self.model.id == id)
        )
        await self.session.flush()
        return result.rowcount > 0
    
    async def exists(self, **filters) -> bool:
        """Check if a record exists"""
        query = select(func.count()).select_from(self.model)
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
        result = await self.session.execute(query)
        return result.scalar() > 0
    
    async def count(self, **filters) -> int:
        """Count records with filters"""
        query = select(func.count()).select_from(self.model)
        for key, value in filters.items():
            if hasattr(self.model, key) and value is not None:
                query = query.where(getattr(self.model, key) == value)
        result = await self.session.execute(query)
        return result.scalar()
    
    async def bulk_create(self, items: List[Dict[str, Any]]) -> List[ModelType]:
        """Bulk create records"""
        instances = [self.model(**item) for item in items]
        self.session.add_all(instances)
        await self.session.flush()
        for instance in instances:
            await self.session.refresh(instance)
        return instances
    
    async def bulk_update(self, updates: List[Dict[str, Any]]) -> int:
        """Bulk update records"""
        updated_count = 0
        for update_data in updates:
            id = update_data.pop("id")
            result = await self.session.execute(
                update(self.model)
                .where(self.model.id == id)
                .values(**update_data)
            )
            updated_count += result.rowcount
        await self.session.flush()
        return updated_count