from sqlalchemy import Integer, String, DateTime, func, Column, Float, Text, Date

from db import Base


class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    phone = Column(String, unique=True, nullable=False)
    full_name = Column(String, nullable=False)
    registration_date = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<User(id={self.user_id}, name='{self.full_name}')>"


class Course(Base):
    __tablename__ = 'courses'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Float)
    start_date = Column(Date)

    def __repr__(self):
        return f"<Course(id={self.id}, name='{self.name}')>"


class RequestModel(Base):
    __tablename__ = 'requests'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    department = Column(String)
    request_type = Column(String)
    status = Column(String, default='pending')
    details = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    resolved_at = Column(DateTime)

    def __repr__(self):
        return f"<RequestModel(id={self.id}, department='{self.department}')>"


class Refund(Base):
    __tablename__ = 'refunds'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    name = Column(String)
    surname = Column(String)
    course = Column(String)
    stream = Column(String)
    reason = Column(Text)
    status = Column(String, default='pending')
    admin_notes = Column(Text)

    def __repr__(self):
        return f"<Refund(id={self.id}, course='{self.course}')>"
