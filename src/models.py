import os
import logging
from decimal import Decimal
from datetime import datetime
from contextlib import contextmanager
from collections import OrderedDict

from sqlalchemy import create_engine, UniqueConstraint, func
from sqlalchemy import or_, and_
from sqlalchemy import MetaData, Column, Table, ForeignKey, TypeDecorator
from sqlalchemy import BigInteger, Integer, String, DateTime, Enum, Boolean, Date, Numeric, Text, Unicode, UnicodeText
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, scoped_session, sessionmaker
from sqlalchemy.sql import select
from sqlalchemy.pool import NullPool

from utils import *
from config import *

class CoerceToInt(TypeDecorator):
  impl = Integer
  def process_result_value(self, value, dialect):
    
    if value is not None:
      value = int(value)
    else:
      value = 0

    return value

naming_convention = {
  "ix": 'ix_%(column_0_label)s',
  "uq": "uq_%(table_name)s_%(column_0_name)s",
  "ck": "ck_%(table_name)s_%(constraint_name)s",
  "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
  "pk": "pk_%(table_name)s"
}

def get_engine():
  strconn = DB_URL
  return create_engine(strconn, echo=False, poolclass=NullPool)

def get_metadata():
  return MetaData(bind=get_engine(), naming_convention=naming_convention)

def get_session():
  return scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=get_engine()))

@contextmanager
def session_scope():
  """Provide a transactional scope around a series of operations."""
  session = get_session()
  try:
      yield session
      session.commit()
  except:
      session.rollback()
      raise
  finally:
      session.close()

Base = declarative_base(metadata=get_metadata())

def get_or_create(session, model, **kwargs):
  instance = session.query(model).filter_by(**kwargs).first()
  if instance:
    return instance, False
  else:
    instance = model(**kwargs)
    session.add(instance)
    return instance, True

class TimestampMixin(object):
  created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
  updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, index=True)

  def older_than(self, delta):
    return datetime.utcnow() - self.created_at > delta

class PushInfo(Base, TimestampMixin):
  __tablename__ = 'push_info'
  
  id      = Column(Integer, primary_key=True)
  name    = Column(String(128), unique=True)
  push_id = Column(String(256))

class Block(Base, TimestampMixin):
  __tablename__ = 'block'
  
  id         = Column(Integer, primary_key=True)
  block_id   = Column(String(256), unique=True)
  block_num  = Column(Integer, unique=True)

class AccountBalance(Base, TimestampMixin):
  __tablename__ = 'account_balance'
  
  id            = Column(Integer, primary_key=True)
  account_id    = Column(String(32))
  account_name  = Column(String(63))
  asset_id      = Column(String(32))
  amount        = Column(BigInteger, default=0)

  def to_dict(self):
    return {
      'id'     : self.account_id,
      'name'   : real_name(self.account_name),
      'amount' : amount_value(self.amount,{'precision':4})
    }

class UserData(Base, TimestampMixin):
  __tablename__ = 'user_data'
  
  id             = Column(Integer, primary_key=True)
  wallet_name    = Column(String(64))

  name           = Column(String(64))
  category       = Column(String(64))
  address        = Column(String(64))
  lat            = Column(String(64))
  lon            = Column(String(64))
  emp_web        = Column(String(64))
  contacto_email = Column(String(64))
  contacto_tel   = Column(String(64))


class Transfer(Base, TimestampMixin):
  __tablename__ = 'transfer'
  
  block_id     = Column(Integer, ForeignKey("block.id", ondelete="CASCADE"), nullable=False) 
  
  id           = Column(Integer, primary_key=True)
  
  from_id      = Column(String(32))
  from_name    = Column(String(63))
  
  to_id        = Column(String(32))
  to_name      = Column(String(63))

  amount       = Column(BigInteger)
  amount_asset = Column(String(32))
 
  fee          = Column(Integer)
  fee_asset    = Column(String(32))

  timestamp    = Column(DateTime)
  
  block_num    = Column(Integer)
  trx_in_block = Column(Integer)
  op_in_trx    = Column(Integer)
  
  memo         = Column(String(256))

  processed    = Column(Integer, default=0, index=True)

class LastError(Base, TimestampMixin):
  __tablename__ = 'last_error'

  id           = Column(Integer, primary_key=True)
  transfer_id  = Column(Integer, ForeignKey("transfer.id", ondelete="CASCADE"), nullable=False, unique=True) 
  description  = Column(Text)
  
  txid         = Column(String(64), index=True)
  
  block_num    = Column(Integer)
  trx_in_block = Column(Integer)

