# Multi-Agent System - Agent Classes

This directory contains all agent implementations for the Munder Difflin paper company management system.

## Agent Structure

Each agent is implemented as a class that wraps a `ToolCallingAgent` from smolagents framework.

### Current Agents

#### 1. InventoryAgent (`inventory_agent.py`)
- **Responsibilities:**
  - Check stock levels for items
  - Search inventory by keywords (semantic search with embeddings)
  - Map customer requests to actual inventory items
  - Get item prices and categories

- **Tools:**
  - `check_item_stock(item_name, date)` - Check specific item stock
  - `check_all_inventory(date)` - Get complete inventory snapshot
  - `get_available_items()` - List all catalog items
  - `find_similar_items(search_term, top_k)` - Semantic search with embeddings
  - `get_item_price(item_name)` - Get unit price
  - `find_items_by_category(category)` - Filter by category

### Planned Agents

#### 2. QuotingAgent (TODO)
- Generate price quotes with bulk discounts
- Search historical quotes for similar orders
- Calculate pricing based on event type and order size

#### 3. OrderingAgent (TODO)
- Process confirmed orders
- Manage restocking decisions
- Create sales and stock order transactions

#### 4. FinancialAgent (TODO)
- Monitor cash flow
- Approve/reject purchase requests
- Generate financial reports

#### 5. OrchestratorAgent (TODO)
- Route customer requests to appropriate agents
- Coordinate multi-agent communication
- Assemble final responses

## Usage Example

```python
from agents import InventoryAgent

# Initialize agent
inventory_agent = InventoryAgent(db_engine, model, client)

# Use directly
result = inventory_agent.run("Check stock for Glossy paper on 2025-04-01")

# Agent-to-agent communication
response = inventory_agent.process_request(
    request="Find items similar to 'printer paper'",
    date="2025-04-01"
)
```

## Design Pattern

All agents follow this structure:

```python
class AgentName:
    def __init__(self, db_engine, model, client):
        self.db_engine = db_engine
        self.model = model
        self.client = client
        self.name = "AgentName"

        # Create internal ToolCallingAgent
        self.agent = ToolCallingAgent(
            tools=[self.tool1, self.tool2, ...],
            model=self.model,
            name=self.name,
            description=self._get_description()
        )

    def _get_description(self) -> str:
        """Return agent description/prompt"""
        pass

    @tool
    def tool1(self, ...):
        """Tool implementation"""
        pass

    def run(self, task: str) -> str:
        """Execute task using agent"""
        return self.agent.run(task)

    def process_request(self, request: str, context: dict) -> dict:
        """High-level method for agent-to-agent communication"""
        pass
```

## Benefits

- **Encapsulation**: Each agent's logic is self-contained
- **Reusability**: Agents can be instantiated multiple times
- **Testability**: Easy to mock and test independently
- **Maintainability**: Clean separation of concerns
- **Agent Communication**: Structured inter-agent messaging
