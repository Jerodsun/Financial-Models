from sqlalchemy.orm import Session
from models import Agent, SimulationResult, Order, OrderType
import random


def run_simulation(db: Session):
    agents = db.query(Agent).all()
    order_book = []

    for agent in agents:
        # Create orders for each agent
        order = create_order(agent)
        order_book.append(order)

    # Match orders and calculate P&L
    matched_orders = match_orders(order_book)
    agent_profit_loss = calculate_profit_loss(matched_orders)

    # Store simulation results and update agent balances
    results = []
    for agent in agents:
        profit_loss = agent_profit_loss.get(agent.id, 0)
        agent.balance += profit_loss  # Update agent balance
        result = SimulationResult(agent_id=agent.id, profit_loss=profit_loss)
        results.append(result)
        db.add(result)

    db.commit()
    return results


def create_order(agent: Agent):
    order_type = random.choice([OrderType.BUY, OrderType.SELL])
    price = random.uniform(1, 100)
    quantity = random.randint(1, 10)
    return Order(
        agent_id=agent.id, order_type=order_type, price=price, quantity=quantity
    )


def match_orders(order_book):
    buy_orders = [order for order in order_book if order.order_type == OrderType.BUY]
    sell_orders = [order for order in order_book if order.order_type == OrderType.SELL]

    # Sort buy orders by price descending and sell orders by price ascending
    buy_orders.sort(key=lambda x: x.price, reverse=True)
    sell_orders.sort(key=lambda x: x.price)

    matched_orders = []

    while buy_orders and sell_orders:
        buy_order = buy_orders[0]
        sell_order = sell_orders[0]

        if buy_order.price >= sell_order.price:
            matched_quantity = min(buy_order.quantity, sell_order.quantity)
            matched_orders.append((buy_order, sell_order, matched_quantity))

            buy_order.quantity -= matched_quantity
            sell_order.quantity -= matched_quantity

            if buy_order.quantity == 0:
                buy_orders.pop(0)
            if sell_order.quantity == 0:
                sell_orders.pop(0)
        else:
            break

    return matched_orders


def calculate_profit_loss(matched_orders):
    agent_profit_loss = {}

    for buy_order, sell_order, quantity in matched_orders:
        profit_loss_buy = (sell_order.price - buy_order.price) * quantity
        profit_loss_sell = (buy_order.price - sell_order.price) * quantity

        if buy_order.agent_id not in agent_profit_loss:
            agent_profit_loss[buy_order.agent_id] = 0
        if sell_order.agent_id not in agent_profit_loss:
            agent_profit_loss[sell_order.agent_id] = 0

        agent_profit_loss[buy_order.agent_id] += profit_loss_buy
        agent_profit_loss[sell_order.agent_id] += profit_loss_sell

    return agent_profit_loss
