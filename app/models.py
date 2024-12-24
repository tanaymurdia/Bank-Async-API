from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship, selectinload
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

class Base(DeclarativeBase, AsyncAttrs):
    pass

class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    accounts = relationship("BankAccount", back_populates="customer", lazy="selectin")

class BankAccount(Base):
    __tablename__ = 'bank_accounts'
    id = Column(Integer, primary_key=True, index=True)
    balance = Column(Float, default=0)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    customer = relationship("Customer", back_populates="accounts", lazy="selectin")

class TransferHistory(Base):
    __tablename__ = 'transfer_history'
    id = Column(Integer, primary_key=True, index=True)
    from_account_id = Column(Integer, ForeignKey('bank_accounts.id'))
    to_account_id = Column(Integer, ForeignKey('bank_accounts.id'))
    amount = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)