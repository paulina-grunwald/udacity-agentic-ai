"""
Multi-Agent System for Munder Difflin Paper Company.

This package contains all agents for the system:
- InventoryAgent: Handles stock checking and item searching
- QuotingAgent: Generates price quotes
- OrderingAgent: Processes orders and manages restocking
- FinancialAgent: Monitors cash flow and approves purchases
- OrchestratorAgent: Routes requests and coordinates agents
"""

from .inventory_agent import InventoryAgent

__all__ = [
    "InventoryAgent",
]
