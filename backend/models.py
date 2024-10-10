from sqlalchemy import Column, Integer, String, Float, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pydantic import BaseModel
import enum

Base = declarative_base()


class AgentType(enum.Enum):
    INTELLIGENT = "intelligent"
    TECHNICAL = "technical"
    THESIS = "thesis"


class Agent(Base):
    __tablename__ = "agents"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    agent_type = Column(Enum(AgentType))
    balance = Column(Float, default=10000.0)  # Initialize with a default balance
    simulation_results = relationship("SimulationResult", back_populates="agent")


class AgentCreate(BaseModel):
    name: str


class OrderType(enum.Enum):
    BUY = "buy"
    SELL = "sell"


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"))
    order_type = Column(Enum(OrderType))
    price = Column(Float)
    quantity = Column(Integer)
    agent = relationship("Agent")


class OrderBook(Base):
    __tablename__ = "order_books"
    id = Column(Integer, primary_key=True, index=True)
    orders = relationship("Order", back_populates="order_book")


class SimulationResult(Base):
    __tablename__ = "simulation_results"
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"))
    profit_loss = Column(Float)
    agent = relationship("Agent", back_populates="simulation_results")
