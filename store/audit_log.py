from sqlalchemy import create_engine, Column, String, DateTime, Integer
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime
import os

Base = declarative_base()
engine = create_engine(os.getenv("DATABASE_URL", "sqlite:///audit.db"))
Session = sessionmaker(bind=engine)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    agent = Column(String)
    action = Column(String)
    details = Column(String)

class ItemCache(Base):
    __tablename__ = "item_cache"
    id = Column(String, primary_key=True)
    content_hash = Column(String)
    item_type = Column(String)

Base.metadata.create_all(engine)

def log_action(agent, action, details):
    session = Session()
    log = AuditLog(agent=agent, action=action, details=details)
    session.add(log)
    session.commit()
    session.close()
