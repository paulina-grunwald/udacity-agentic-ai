"""
Multi-Agent System for Munder Difflin Paper Company.

This package contains all agents for the system:
- InventoryAgent: Handles stock checking and item searching
- QuotingAgent: Generates price quotes
- OrderingAgent: Processes orders and manages restocking
- FinancialAgent: Monitors cash flow and approves purchases
- OrchestratorAgent: Routes requests and coordinates agents
"""

from .inventory_agent import inventory_agent
from .quoting_agent import quoting_agent
from .ordering_agent import ordering_agent
from .financial_agent import financial_agent
from .orchestrator_agent import create_orchestrator_agent, process_customer_request

__all__ = [
    "inventory_agent",
    "quoting_agent",
    "ordering_agent",
    "financial_agent",
    "create_orchestrator_agent",
    "process_customer_request",
]
