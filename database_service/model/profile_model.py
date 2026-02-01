from sqlalchemy import Column, DateTime, String

from model.base import Base


class ProfileModel(Base):
    __tablename__ = "profiles"

    id = Column(String, primary_key=True)    
    created_at = Column(
        DateTime,        
        nullable=False,
    )
