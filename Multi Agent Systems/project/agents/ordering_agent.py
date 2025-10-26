"""
OrderingAgent for Munder Difflin Paper Company.

This agent is responsible for:
- Processing customer sales orders
- Creating stock reorder transactions
- Checking supplier delivery dates
- Determining when inventory needs restocking
"""

import pandas as pd
from smolagents import ToolCallingAgent, tool
from typing import Dict
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from config import model
from helpers import (
    create_transaction,
    get_supplier_delivery_date,
    get_stock_level,
    db_engine,
)


@tool
def process_sales_transaction(
    item_name: str, quantity: int, price: float, date: str
) -> Dict:
    """
    Create a sales transaction in the database.
    This records a customer purchase and reduces inventory.

    Args:
        item_name: The exact name of the item being sold
        quantity: Number of units sold
        price: Total price of the sale
        date: Date of sale in ISO format (YYYY-MM-DD)

    Returns:
        Dict with transaction_id and confirmation details
    """
    try:
        transaction_id = create_transaction(
            item_name=item_name,
            transaction_type="sales",
            quantity=quantity,
            price=price,
            date=date,
        )

        return {
            "success": True,
            "transaction_id": transaction_id,
            "transaction_type": "sales",
            "item_name": item_name,
            "quantity": quantity,
            "price": price,
            "date": date,
            "message": f"Sales transaction created successfully for {quantity} units of {item_name}",
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to create sales transaction: {str(e)}",
        }


@tool
def process_stock_order_transaction(
    item_name: str, quantity: int, price: float, date: str
) -> Dict:
    """
    Create a stock order transaction in the database.
    This records a purchase from supplier and increases inventory.

    Args:
        item_name: The exact name of the item being ordered from supplier
        quantity: Number of units to order
        price: Total cost of the stock order
        date: Date of order in ISO format (YYYY-MM-DD)

    Returns:
        Dict with transaction_id and confirmation details
    """
    try:
        transaction_id = create_transaction(
            item_name=item_name,
            transaction_type="stock_orders",
            quantity=quantity,
            price=price,
            date=date,
        )

        return {
            "success": True,
            "transaction_id": transaction_id,
            "transaction_type": "stock_orders",
            "item_name": item_name,
            "quantity": quantity,
            "price": price,
            "date": date,
            "message": f"Stock order created successfully for {quantity} units of {item_name}",
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to create stock order: {str(e)}",
        }


@tool
def check_delivery_timeline(date: str, quantity: int) -> Dict:
    """
    Get estimated supplier delivery date based on order quantity.

    Delivery lead times:
    - 0-10 units: Same day
    - 11-100 units: 1 day
    - 101-1000 units: 4 days
    - 1001+ units: 7 days

    Args:
        date: Order date in ISO format (YYYY-MM-DD)
        quantity: Number of units being ordered

    Returns:
        Dict with delivery_date and lead_time details
    """
    try:
        delivery_date = get_supplier_delivery_date(date, quantity)

        # Calculate lead time in days
        if quantity <= 10:
            lead_time_days = 0
        elif quantity <= 100:
            lead_time_days = 1
        elif quantity <= 1000:
            lead_time_days = 4
        else:
            lead_time_days = 7

        return {
            "order_date": date,
            "delivery_date": delivery_date,
            "lead_time_days": lead_time_days,
            "quantity": quantity,
            "message": f"Estimated delivery by {delivery_date} ({lead_time_days} days lead time)",
        }
    except Exception as e:
        return {
            "error": str(e),
            "message": f"Failed to calculate delivery timeline: {str(e)}",
        }


@tool
def check_restock_needed(item_name: str, date: str) -> Dict:
    """
    Check if an item needs restocking by comparing current stock to minimum levels.

    Args:
        item_name: The exact name of the item to check
        date: Date to check stock levels (ISO format YYYY-MM-DD)

    Returns:
        Dict with restock recommendation and stock level details
    """
    try:
        # Get current stock level
        stock_info = get_stock_level(item_name, date)
        current_stock = int(stock_info["current_stock"].iloc[0])

        # Get minimum stock level from inventory table
        inventory_df = pd.read_sql(
            "SELECT min_stock_level, unit_price FROM inventory WHERE item_name = :item_name",
            db_engine,
            params={"item_name": item_name},
        )

        if inventory_df.empty:
            return {
                "item_name": item_name,
                "current_stock": current_stock,
                "needs_restock": False,
                "error": "Item not found in inventory catalog",
                "message": f"Item '{item_name}' not found in inventory catalog",
            }

        min_stock = int(inventory_df["min_stock_level"].iloc[0])
        unit_price = float(inventory_df["unit_price"].iloc[0])

        needs_restock = current_stock < min_stock

        # Calculate recommended reorder quantity (restore to 2x minimum)
        if needs_restock:
            reorder_qty = (min_stock * 2) - current_stock
            reorder_cost = reorder_qty * unit_price
        else:
            reorder_qty = 0
            reorder_cost = 0.0

        return {
            "item_name": item_name,
            "current_stock": current_stock,
            "min_stock_level": min_stock,
            "needs_restock": needs_restock,
            "recommended_reorder_qty": reorder_qty,
            "estimated_reorder_cost": round(reorder_cost, 2),
            "unit_price": unit_price,
            "message": (
                f"Item needs restocking! Current: {current_stock}, Minimum: {min_stock}. "
                f"Recommend ordering {reorder_qty} units (${reorder_cost:.2f})"
                if needs_restock
                else f"Stock level OK. Current: {current_stock}, Minimum: {min_stock}"
            ),
        }
    except Exception as e:
        return {"error": str(e), "message": f"Failed to check restock status: {str(e)}"}


@tool
def get_item_unit_price(item_name: str) -> Dict:
    """
    Get the unit price for a specific item from inventory.

    Args:
        item_name: The exact name of the item

    Returns:
        Dict with unit_price and item details
    """
    try:
        inventory_df = pd.read_sql(
            "SELECT item_name, unit_price, category FROM inventory WHERE item_name = :item_name",
            db_engine,
            params={"item_name": item_name},
        )

        if inventory_df.empty:
            return {
                "item_name": item_name,
                "found": False,
                "error": "Item not found",
                "message": f"Item '{item_name}' not found in inventory",
            }

        return {
            "item_name": item_name,
            "unit_price": float(inventory_df["unit_price"].iloc[0]),
            "category": inventory_df["category"].iloc[0],
            "found": True,
            "message": f"Unit price for '{item_name}': ${inventory_df['unit_price'].iloc[0]}",
        }
    except Exception as e:
        return {"error": str(e), "message": f"Failed to get item price: {str(e)}"}


# Create the OrderingAgent
ordering_agent = ToolCallingAgent(
    tools=[
        process_sales_transaction,
        process_stock_order_transaction,
        check_delivery_timeline,
        check_restock_needed,
        get_item_unit_price,
    ],
    model=model,
    max_steps=8,
    name="OrderingAgent",
    description="""You are the Ordering Agent for Munder Difflin paper company.

Your responsibilities:
1. Process customer sales orders by creating sales transactions
2. Create stock reorder transactions when inventory is low
3. Check supplier delivery timelines for stock orders
4. Monitor inventory levels and recommend restocking
5. Calculate costs for stock orders

IMPORTANT RULES:
- **CRITICAL**: Only process transactions for items that exist in the inventory catalog
- If get_item_unit_price returns "found": False, IMMEDIATELY return an error - DO NOT create transactions
- Always use exact item names from the inventory
- For sales transactions: Use transaction_type="sales" and record the selling price
- For stock orders: Use transaction_type="stock_orders" and record the cost
- Check current stock levels before processing large orders
- Recommend restocking when current stock falls below minimum levels
- Calculate delivery timelines based on order quantity
- Always include dates in ISO format (YYYY-MM-DD)
- Verify item prices from inventory before creating transactions
- If an item is not found, explain to the orchestrator that the item doesn't exist in inventory

Workflow for processing a customer order:
1. Check current stock levels for requested items
2. Verify if we have enough inventory to fulfill the order
3. If stock is sufficient: Create sales transaction
4. If stock is low after sale: Recommend restocking
5. If restocking needed: Calculate delivery timeline

Workflow for restocking:
1. Check if item needs restocking (current < minimum)
2. Calculate recommended reorder quantity (restore to 2x minimum)
3. Get unit price and calculate total cost
4. Create stock order transaction
5. Calculate delivery timeline

Always provide clear status messages about transaction success or failure.
""",
)
