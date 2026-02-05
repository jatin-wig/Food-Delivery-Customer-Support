from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import func

engine = create_engine("sqlite:///support.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String)
    issue_type = Column(String)
    conversation = Column(Text)
    status = Column(String, default="OPEN")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String)
    item = Column(String)
    price = Column(Integer)
    status = Column(String)
    eta = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


Base.metadata.create_all(bind=engine)


with engine.connect() as conn:
    cols = [r[1] for r in conn.exec_driver_sql("PRAGMA table_info('orders')").fetchall()]
    if "created_at" not in cols:
        conn.exec_driver_sql("ALTER TABLE orders ADD COLUMN created_at DATETIME DEFAULT (CURRENT_TIMESTAMP);")
    else:
        conn.exec_driver_sql("UPDATE orders SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL;")

    cols = [r[1] for r in conn.exec_driver_sql("PRAGMA table_info('tickets')").fetchall()]
    if "created_at" not in cols:
        conn.exec_driver_sql("ALTER TABLE tickets ADD COLUMN created_at DATETIME DEFAULT (CURRENT_TIMESTAMP);")
    else:
        conn.exec_driver_sql("UPDATE tickets SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL;")