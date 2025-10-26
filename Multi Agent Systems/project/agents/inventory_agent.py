"""
InventoryAgent

This agent is responsible for:
  - Checking stock levels for specific items
  - Searching for items in the inventory catalog
  - Finding items by category or keyword
  - Getting item prices
  - Mapping customer requests to actual inventory item names
"""

import pandas as pd
from smolagents import ToolCallingAgent, tool
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from config import model
from helpers import (get_stock_level, get_all_inventory, db_engine)


@tool
def check_item_stock(item_name: str, date: str) -> dict:
    """
    Check the current stock level for a specific item as of a given date.

    Args:
        item_name: The exact name of the item to check
        date: Date in ISO format (YYYY-MM-DD)

    Returns:
        dict: Contains item_name and current_stock level
    """
    result = get_stock_level(item_name, date)
    if result.empty:
        return {"item_name": item_name, "current_stock": 0}
    return {
        "item_name": result["item_name"].iloc[0],
        "current_stock": int(result["current_stock"].iloc[0]),
    }


@tool
def check_all_inventory(date: str) -> dict:
    """
    Get a complete snapshot of all inventory items and their stock levels as of a given date.

    Args:
        date: Date in ISO format (YYYY-MM-DD)

    Returns:
        dict: Mapping of item names to their current stock levels
    """
    return get_all_inventory(date)


@tool
def get_available_items() -> list:
    """
    Get a list of all items available in the inventory catalog with their prices and categories.

    Returns:
      list: List of dicts containing item_name, category, and unit_price
    """
    inventory_df = pd.read_sql(
        "SELECT item_name, category, unit_price FROM inventory", db_engine
    )
    return inventory_df.to_dict(orient="records")


@tool
def find_similar_items(search_term: str) -> list:
    """
    Find items in inventory that match or are similar to a search term.
    Useful for mapping customer requests to actual inventory items.

    Args:
        search_term: The term to search for (e.g., "glossy", "A4", "cardstock")

    Returns:
        list: List of matching items with their details
    """
    inventory_df = pd.read_sql("SELECT * FROM inventory", db_engine)
    matches = inventory_df[
        inventory_df["item_name"]
        .str.lower()
        .str.contains(search_term.lower(), na=False)
    ]
    return matches.to_dict(orient="records")


@tool
def get_item_price(item_name: str) -> float:
    """
    Retrieve the unit price of a specific item from the inventory.

    Args:
        item_name: The exact name of the item to look up

    Returns:
        float: The unit price of the item, or -1.0 if not found
    """
    inventory_df = pd.read_sql(
        "SELECT item_name, unit_price FROM inventory WHERE item_name = :item_name",
        db_engine,
        params={"item_name": item_name},
    )
    if inventory_df.empty:
        return -1.0
    return float(inventory_df["unit_price"].iloc[0])


@tool
def find_items_by_category(category: str) -> list:
    """
    Find all items in inventory that belong to a specific category.

    Args:
        category: Category to filter by. Options: 'paper', 'product', 'large_format', 'specialty'

    Returns:
        list: List of items in that category with their details
    """
    inventory_df = pd.read_sql(
        "SELECT * FROM inventory WHERE category = :category",
        db_engine,
        params={"category": category},
    )
    return inventory_df.to_dict(orient="records")


inventory_agent = ToolCallingAgent(
    tools=[
        check_item_stock,
        check_all_inventory,
        get_available_items,
        find_similar_items,
        get_item_price,
        find_items_by_category,
    ],
    model=model,
    max_steps=5,
    name="InventoryAgent",
    description="""You are the Inventory Agent for Munder Difflin paper company.
    Your responsibilities:
      1. Check stock levels for specific items on specific dates
      2. Search for items in inventory catalog by keywords or category
      3. Map customer requests to actual inventory item names
      4. Report current inventory status and prices
      5. Identify if items are in stock or out of stock

    IMPORTANT RULES:
      - Always include the DATE in your stock checks
      - Use exact item names from the inventory when reporting
      - When customer requests don't match exact item names, use find_similar_items to search
      - Use find_items_by_category when asked about categories: 'paper', 'product', 'large_format', 'specialty'
      - Report stock levels as integers
      - If an item is not in the catalog, clearly state that

    Example interactions:
      - "Check if we have Glossy paper in stock on 2025-04-01" -> Use check_item_stock
      - "What items do we have related to 'cardstock'?" -> Use find_similar_items
      - "Show me all inventory on 2025-04-01" -> Use check_all_inventory
      - "What paper items do we have?" -> Use find_items_by_category with category='paper'
      - "What's the price of A4 paper?" -> Use get_item_price
""",
)
