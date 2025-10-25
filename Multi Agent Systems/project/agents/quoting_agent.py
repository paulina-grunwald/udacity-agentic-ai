"""
QuotingAgent

This agent is responsible for:
- Searching historical quote data for similar requests
- Calculating pricing for customer orders with bulk discounts
- Generating transparent, customer-facing quotes with explanations
"""

import pandas as pd
from smolagents import ToolCallingAgent, tool
from typing import List, Dict
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from project_starter import (
    search_quote_history,
    db_engine,
    model,
)


@tool
def search_historical_quotes(search_terms: List[str], limit: int = 5) -> List[Dict]:
    """
    Search historical quotes for similar past requests.
    Useful for understanding pricing patterns and quote explanations for similar orders.

    Args:
        search_terms: List of keywords to search for (e.g., ["glossy", "ceremony"])
        limit: Maximum number of results to return (default: 5)

    Returns:
        List of matching historical quotes with details including:
        - original_request
        - total_amount
        - quote_explanation
        - job_type
        - order_size
        - event_type
        - order_date
    """
    return search_quote_history(search_terms, limit)


@tool
def calculate_quote_price(items_with_quantities: List[Dict]) -> Dict:
    """
    Calculate the total price for a quote with bulk discount pricing.

    Discount tiers:
    - 0-500 total units: No discount (0%)
    - 501-1000 total units: 10% discount
    - 1001+ total units: 15% discount

    Args:
        items_with_quantities: List of dicts with 'item_name', 'quantity', and 'unit_price'
                              Example: [{"item_name": "A4 paper", "quantity": 100, "unit_price": 0.05}]

    Returns:
        Dictionary containing:
        - subtotal: Price before discount
        - discount_percent: Discount percentage applied
        - discount_amount: Dollar amount of discount
        - total: Final price after discount
        - total_units: Total number of units across all items
        - breakdown: List of items with individual calculations
    """
    if not items_with_quantities:
        return {
            "subtotal": 0.0,
            "discount_percent": 0.0,
            "discount_amount": 0.0,
            "total": 0.0,
            "total_units": 0,
            "breakdown": []
        }

    subtotal = 0.0
    total_units = 0
    breakdown = []

    for item in items_with_quantities:
        item_name = item.get("item_name", "Unknown")
        quantity = item.get("quantity", 0)
        unit_price = item.get("unit_price", 0.0)

        item_total = quantity * unit_price
        subtotal += item_total
        total_units += quantity

        breakdown.append({
            "item_name": item_name,
            "quantity": quantity,
            "unit_price": unit_price,
            "item_total": round(item_total, 2)
        })

    if total_units <= 500:
        discount_percent = 0.0
    elif total_units <= 1000:
        discount_percent = 10.0
    else:
        discount_percent = 15.0

    discount_amount = subtotal * (discount_percent / 100)
    total = subtotal - discount_amount

    return {
        "subtotal": round(subtotal, 2),
        "discount_percent": discount_percent,
        "discount_amount": round(discount_amount, 2),
        "total": round(total, 2),
        "total_units": total_units,
        "breakdown": breakdown
    }


@tool
def get_item_prices(item_names: List[str]) -> List[Dict]:
    """
    Look up unit prices for multiple items from the inventory.

    Args:
        item_names: List of exact item names to look up

    Returns:
        List of dicts with 'item_name', 'unit_price', and 'found' status
        Example: [{"item_name": "A4 paper", "unit_price": 0.05, "found": True}]
    """
    results = []

    for item_name in item_names:
        # Query database for the item
        inventory_df = pd.read_sql(
            "SELECT item_name, unit_price FROM inventory WHERE item_name = :item_name",
            db_engine,
            params={"item_name": item_name}
        )

        if not inventory_df.empty:
            results.append({
                "item_name": item_name,
                "unit_price": float(inventory_df["unit_price"].iloc[0]),
                "found": True
            })
        else:
            results.append({
                "item_name": item_name,
                "unit_price": 0.0,
                "found": False
            })

    return results


quoting_agent = ToolCallingAgent(
    tools=[
        search_historical_quotes,
        calculate_quote_price,
        get_item_prices,
    ],
    model=model,
    max_steps=5,
    name="QuotingAgent",
    description="""You are the Quoting Agent for Munder Difflin paper company.

Your responsibilities:
1. Search historical quotes to understand pricing patterns for similar orders
2. Calculate accurate quotes with appropriate bulk discounts
3. Provide transparent, customer-facing price breakdowns
4. Explain pricing rationale including any discounts applied

IMPORTANT RULES:
- Always use exact item names from the inventory
- Apply bulk discounts based on total units:
  * 0-500 units: No discount
  * 501-1000 units: 10% discount
  * 1001+ units: 15% discount
- Provide clear breakdowns showing:
  * Individual item costs
  * Subtotal before discount
  * Discount amount and percentage (if applicable)
  * Final total
- Explain why discounts were or weren't applied
- Search historical quotes for similar requests to maintain pricing consistency
- NEVER reveal internal profit margins or cost structures
- Format prices as currency with 2 decimal places

Example quote response format:
"Based on your request for [items], here is your quote:

Item Breakdown:
- [Item 1]: [qty] units × $[price] = $[total]
- [Item 2]: [qty] units × $[price] = $[total]

Subtotal: $[amount]
Bulk Discount ([X]% for [Y] total units): -$[discount]
Total: $[final]

[Explanation of why this pricing applies, any discounts, and delivery considerations]"
"""
)
