from sqlalchemy import Column,Integer,String,DateTime,func,ForeignKey
from .database import Base
from datetime import datetime
from sqlalchemy.orm import relationship




class User(Base):
    __tablename__="users"

    id = Column(Integer, primary_key=True,index=True)
    name=Column(String,index=True)
    mail=Column(String,index=True,unique=True,nullable=False)
    password=Column(String,nullable=False)
    created_date=Column(DateTime,default=func.now())
    updated_date=Column(DateTime,default=func.now(),onupdate=func.now())
    is_active=Column(Integer,default=1)
    files = relationship('UploadedFile', back_populates='user')



class UploadedFile(Base):
    __tablename__ = 'uploaded_files'
    
    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    user = relationship('User', back_populates='files')