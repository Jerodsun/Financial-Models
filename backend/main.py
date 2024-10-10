from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import numpy as np
from scipy.stats import norm
from typing import Dict
from database import SessionLocal, engine
from models import Base, AgentCreate, Agent, SimulationResult
from agent_behaviors import run_simulation
import random

app = FastAPI()

Base.metadata.create_all(bind=engine)

class OptionData(BaseModel):
    S: float = Field(..., gt=0, description="Current stock price must be greater than 0")
    K: float = Field(..., gt=0, description="Option strike price must be greater than 0")
    T: float = Field(..., gt=0, description="Time to maturity (in years) must be greater than 0")
    r: float = Field(..., ge=0, description="Risk-free interest rate must be non-negative")
    sigma: float = Field(..., gt=0, le=1, description="Volatility of the underlying stock must be between 0 and 1")

class AgentBehavior(BaseModel):
    name: str
    behavior: str

# In-memory storage for agent behaviors
agent_behaviors: Dict[str, AgentBehavior] = {}

def black_scholes_merton(S, K, T, r, sigma):
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    call_price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    put_price = K * np.exp(-r * T) * norm.cdf(-d2) - S * np.cdf(-d1)
    return call_price, put_price

@app.get("/")
def read_root():
    return {"message": "Welcome to the Option Pricing API"}

@app.post("/calculate")
def calculate_option_price(option_data: OptionData):
    call_price, put_price = black_scholes_merton(
        option_data.S, option_data.K, option_data.T, option_data.r, option_data.sigma
    )
    return {"call_price": call_price, "put_price": put_price}

@app.get("/agent_behaviors")
def get_agent_behaviors():
    return agent_behaviors

@app.post("/agent_behaviors")
def add_agent_behavior(agent_behavior: AgentBehavior):
    if agent_behavior.name in agent_behaviors:
        raise HTTPException(status_code=400, detail="Agent behavior already exists")
    agent_behaviors[agent_behavior.name] = agent_behavior
    return agent_behavior

@app.put("/agent_behaviors/{name}")
def update_agent_behavior(name: str, agent_behavior: AgentBehavior):
    if name not in agent_behaviors:
        raise HTTPException(status_code=404, detail="Agent behavior not found")
    agent_behaviors[name] = agent_behavior
    return agent_behavior

@app.post("/run_simulation")
def run_simulation_endpoint(db: Session = Depends(SessionLocal)):
    results = run_simulation(db)
    return results

@app.post("/add_random_agents")
def add_random_agents(count: int, db: Session = Depends(SessionLocal)):
    agent_types = list(AgentType)
    for _ in range(count):
        agent_type = random.choice(agent_types)
        agent_name = f"Agent_{random.randint(1000, 9999)}"
        agent = Agent(name=agent_name, agent_type=agent_type)
        db.add(agent)
    db.commit()
    return {"message": f"{count} random agents added"}