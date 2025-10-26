"""
OrchestratorAgent.
This is the main coordinator agent that can do following things:
  - Receives customer requests
  - Routes requests to appropriate worker agents
  - Coordinates multi-step workflows
  - Assembles final customer-facing responses
"""

from smolagents import ToolCallingAgent, tool
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from config import model


def create_orchestrator_agent(
    inventory_agent, quoting_agent, ordering_agent, financial_agent
):
    """
    Create the orchestrator agent with access to all worker agents. This creates tools that wrap each worker agent, allowing the orchestrator to delegate tasks to specialized agent.

    Args:
        inventory_agent: The InventoryAgent
        quoting_agent: The QuotingAgent
        ordering_agent: The OrderingAgent
        financial_agent: The FinancialAgent

    Returns:
        ToolCallingAgent: The configured orchestrator agent
    """

    @tool
    def delegate_to_inventory_specialist(task: str) -> str:
        """
        Delegate to the Inventory Specialist for:
          - Checking stock levels for specific items (always include the date!)
          - Searching for items in the inventory catalog
          - Finding items by category or keyword
          - Getting item prices
          - Mapping customer requests to actual inventory item names

        Args:
          task: The task to delegate to the inventory specialist (include dates!)

        Returns:
          str: The specialist's response
        """
        return str(inventory_agent.run(task))

    @tool
    def delegate_to_quoting_specialist(task: str) -> str:
        """
        Delegate to the Quoting Specialist for:
        - Calculating price quotes with bulk discounts
        - Searching historical quotes for similar orders
        - Looking up multiple item prices at once
        - Generating customer-facing price breakdowns

        This agent applies automatic bulk discounts based on total units.

        Args:
            task: The task to delegate to the quoting specialist

        Returns:
            str: The specialist's response with pricing information
        """
        return str(quoting_agent.run(task))

    @tool
    def delegate_to_ordering_specialist(task: str) -> str:
        """
        Delegate to the Ordering Specialist for:
        - Processing customer sales transactions
        - Creating stock reorder transactions
        - Checking supplier delivery timelines
        - Determining if items need restocking
        - Getting item unit prices

        This agent handles all database transactions.

        Args:
            task: The task to delegate to the ordering specialist

        Returns:
            str: The specialist's response with transaction/ordering information
        """
        return str(ordering_agent.run(task))

    @tool
    def delegate_to_financial_specialist(task: str) -> str:
        """
        Delegate to the Financial Specialist for:
        - Checking current cash balance
        - Approving or rejecting purchases based on cash reserves
        - Generating financial reports
        - Assessing company financial health

        This agent ensures the company maintains adequate cash reserves (20% safety margin).

        Args:
            task: The task to delegate to the financial specialist

        Returns:
            str: The specialist's response with financial information
        """
        return str(financial_agent.run(task))

    orchestrator = ToolCallingAgent(
        tools=[
            delegate_to_inventory_specialist,
            delegate_to_quoting_specialist,
            delegate_to_ordering_specialist,
            delegate_to_financial_specialist,
        ],
        model=model,
        max_steps=15,
        name="OrchestratorAgent",
        description="""You are the Orchestrator Agent for paper company. You are the main coordinator that receives customer requests and delegates work to specialized agents.

        YOUR WORKER AGENTS:
        1. **inventory_specialist** - Checks stock, finds items, searches catalog
        2. **quoting_specialist** - Calculates quotes with discounts, searches quote history
        3. **ordering_specialist** - Processes sales/orders, checks delivery times, manages restocking
        4. **financial_specialist** - Checks cash, approves purchases, generates financial reports

        WORKFLOW PATTERNS:

        **For QUOTE REQUESTS (customer wants a price estimate):**
        1. Ask inventory_specialist to find matching items and check stock availability
        2. Ask quoting_specialist to calculate the quote with appropriate discounts
        3. Provide a transparent quote to the customer with:
          - Item breakdown with quantities and prices
          - Subtotal before discount
          - Discount information (if applicable)
          - Final total
          - Delivery timeline estimate
          - Clear explanation of pricing

        **For ORDER REQUESTS (customer wants to purchase):**
        1. FIRST: Ask inventory_specialist to find matching items using find_similar_items or get_available_items
           - Map customer's description to EXACT inventory item names
           - Example: "cardboard" might map to "Cardstock"
        2. Ask inventory_specialist to check if we have enough stock using the EXACT item names
        3. If items not found in inventory, inform customer and STOP
        4. Ask quoting_specialist to calculate the final price (SAVE THE TOTAL PRICE)
        5. Ask financial_specialist to check cash balance (for our records, don't share with customer)
        6. Ask ordering_specialist to process the sales transaction
           CRITICAL: You MUST provide the exact price calculated in step 4 to the ordering_specialist
           Example: "Process sales transaction for [EXACT_ITEM_NAME], [quantity] units, price [TOTAL_PRICE], date [DATE]"
        7. Ask inventory_specialist to check if restocking is needed after the sale
        8. If restocking needed:
          - Ask ordering_specialist to check delivery timeline
          - Ask financial_specialist to approve the restock purchase (provide the restock cost)
          - If approved: Ask ordering_specialist to create stock order transaction WITH THE COST
        9. Provide customer with:
          - Order confirmation with total price
          - Expected delivery date
          - Professional thank you message

        **For INVENTORY INQUIRIES:**
        1. Ask inventory_specialist to find items or check stock
        2. Provide availability information to customer

        **For FINANCIAL INQUIRIES (internal only):**
        1. Ask financial_specialist for reports or balance checks
        2. Provide summary (but never reveal sensitive details to customers)

        IMPORTANT RULES:
        - Always extract the date from customer requests
        - Use exact item names from inventory
        - For ambiguous item names, ask inventory_specialist to find similar items
        - Calculate quotes before processing orders
        - **CRITICAL: When processing orders, you MUST pass the calculated price to the ordering_specialist**
        - When delegating to ordering_specialist for sales, include: item name, quantity, price, and date
        - When delegating to ordering_specialist for stock orders, include: item name, quantity, cost, and date
        - Check stock availability before confirming orders
        - Never share internal financial details (profit margins, exact cash balance) with customers
        - Always provide transparent, customer-friendly responses
        - If an order cannot be fulfilled, explain why clearly and professionally
        - Track restock needs after large sales

        CUSTOMER-FACING COMMUNICATION:
        - Be professional and friendly
        - Provide clear breakdowns of pricing
        - Explain discounts when applied
        - Include delivery estimates when relevant
        - Never use internal jargon or system details
        - Format prices clearly (e.g., $XX.XX)
        - Always thank customers for their business

        Remember: You coordinate the workflow but delegate actual tasks to specialists!
        """,
    )
    return orchestrator


def process_customer_request(orchestrator, request: str, date: str) -> str:
    """
    Process a customer request through the orchestrator agent.

    Args:
      orchestrator: The orchestrator agent instance
      request: The customer's request text
      date: The date of the request (ISO format YYYY-MM-DD)

    Returns:
      str: The customer-facing response
    """
    full_request = f"{request}\n\n(Request date: {date})"

    try:
        response = orchestrator.run(full_request)
        return str(response)
    except Exception as e:
        return f"We apologize, but we encountered an error processing your request: {str(e)}"
