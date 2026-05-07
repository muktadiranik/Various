from sqlalchemy import Column, Integer, DateTime, func
from typing import Optional


class AuditMixin(object):
    __abstract__ = True
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, nullable=True)  # user_id
