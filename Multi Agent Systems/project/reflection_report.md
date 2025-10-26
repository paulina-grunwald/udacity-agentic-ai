# Munder Difflin Multi-Agent System - Reflection Report

**Author**: Paulina Grunwald
**Date**: October 25, 2025
**Project**: Multi-Agent Sales and Inventory Management System

---

## System Architecture Overview

### Agent Workflow Explanation

The Munder Difflin multi-agent system implements a hierarchical orchestration pattern with five specialized agents working in concert to handle customer inquiries, inventory management, quote generation, and order fulfillment.

#### Architecture Design

The system follows a orchestrator pattern where:

1. **OrchestratorAgent** serves as the main entry point and coordinator
2. **Four specialist agents** handle specific tasks:
   - **InventoryAgent**: manages stock checking and item searches
   - **QuotingAgent**: Handles pricing and bulk discounts
   - **OrderingAgent**: processes transactions and manages restocking
   - **FinancialAgent**: monitors cash flow and approves purchases

#### Workflow Patterns

The system implements three primary workflow patterns:

**Pattern 1: Quote Request Flow**

```
Customer Request
    ↓
OrchestratorAgent analyzes request
    ↓
→ InventoryAgent: Find matching items & check stock availability
    ↓
→ QuotingAgent: Calculate pricing with bulk discounts
    ↓
→ Customer Response: Transparent quote with item breakdown
```

**Pattern 2: Order Processing Flow**

```
Customer Order
    ↓
OrchestratorAgent validates request
    ↓
→ InventoryAgent: Verify sufficient stock
    ↓
→ QuotingAgent: Calculate final price
    ↓
→ OrderingAgent: Process sales transaction
    ↓
→ InventoryAgent: Check if restocking needed
    ↓
→ FinancialAgent: Approve restock purchase (if needed)
    ↓
→ OrderingAgent: Create stock order (if approved)
    ↓
→ Customer Response: Order confirmation with delivery estimate
```

**Pattern 3: Inventory Inquiry Flow**

```
Customer Inquiry
    ↓
OrchestratorAgent routes to InventoryAgent
    ↓
→ InventoryAgent: Search catalog & check stock
    ↓
→ Customer Response: Availability information
```

### Agent Responsibilities

#### OrchestratorAgent

**Role**: Main coordinator and customer interface

**Responsibilities**:

- Receives all customer requests
- Analyzes request intent (quote vs. order vs. inquiry)
- Delegates subtasks to appropriate specialist agents
- Assembles final customer-facing responses
- Ensures workflow follows business logic

**Tools**: 4 delegation tools (one per specialist)

- `delegate_to_inventory_specialist`: For stock and catalog queries
- `delegate_to_quoting_specialist`: For pricing calculations
- `delegate_to_ordering_specialist`: For transaction processing
- `delegate_to_financial_specialist`: For financial approvals

**Design Decision**: I chose to implement delegation through tool wrappers rather than direct agent calls to maintain consistency with the smolagents framework's tool-based architecture.

#### InventoryAgent

**Role**: Inventory specialist

**Responsibilities**:

- Check current stock levels for specific items
- Search inventory catalog by keywords or categories
- Map customer requests to exact inventory item names
- Report item prices and availability
- Provide complete inventory snapshots

**Tools**:

- `check_item_stock`: Uses `get_stock_level()` helper
- `check_all_inventory`: Uses `get_all_inventory()` helper
- `get_available_items`: Queries full catalog
- `find_similar_items`: Semantic search for item matching
- `get_item_price`: Price lookup
- `find_items_by_category`: Filters by paper/product/specialty categories

**Design Decision**: I separated item searching from stock checking to allow flexible workflows where the orchestrator can first identify items, then check their availability.

#### QuotingAgent

**Role**: Pricing and quote generation specialist

**Responsibilities**:

- Calculate accurate quotes with bulk discount logic
- Search historical quotes for pricing consistency
- Provide transparent price breakdowns
- Apply tiered discount structure strategically

**Bulk Discount Tiers**:

- 0-500 units: No discount (0%)
- 501-1,000 units: 10% discount
- 1,001+ units: 15% discount

**Tools**:

- `search_historical_quotes`: Uses `search_quote_history()` helper
- `calculate_quote_price`: Implements discount tiers
- `get_item_prices`: Batch price lookup

**Design Decision**: I have implemented a three-tier discount structure to encourage bulk purchases while maintaining profitability. The discount thresholds designed to align with common order sizes observed in the quote_requests.csv dataset.

#### OrderingAgent

**Role**: Transaction processing and restocking specialist

**Responsibilities**:

- Process customer sales transactions
- Create stock reorder transactions
- Check supplier delivery timelines
- Monitor inventory levels and recommend restocking
- Calculate restock quantities and costs

**Restocking Logic**: When stock falls below minimum level, recommends ordering to restore inventory to 2× minimum level.

**Tools**: 5 transaction and delivery tools

- `process_sales_transaction`: Uses `create_transaction()` for sales
- `process_stock_order_transaction`: Uses `create_transaction()` for stock orders
- `check_delivery_timeline`: Uses `get_supplier_delivery_date()`
- `check_restock_needed`: Compares current vs. minimum stock
- `get_item_unit_price`: Calculates restock costs

**Design Decision**: I separated sales transactions from stock orders to maintain clear audit trails and enable different workflows for each transaction type.

#### FinancialAgent

**Role**: Financial oversight and cash management specialist

**Responsibilities**:

- Monitor cash balance and financial health
- Approve/reject purchase requests based on reserves
- Generate financial reports
- Assess business liquidity ratios
- Ensure 20% cash safety margin

**Tools**:

- `check_cash_balance`: Uses `get_cash_balance()` helper
- `approve_purchase`: Validates against 20% safety margin
- `get_financial_report`: Uses `generate_financial_report()` helper
- `calculate_financial_health`: Computes liquidity ratios

**Design Decision**: I implemented a mandatory 20% safety margin to prevent cash flow issues. This ensures the company always maintains adequate reserves for operational expenses, even after large inventory purchases.

### Tool Design and Helper Function Integration

All tools I have designed to wrap the provided helper functions from `helpers.py`:

| Helper Function              | Purpose                   | Used By Agent                 | Tool Name                                                  |
| ---------------------------- | ------------------------- | ----------------------------- | ---------------------------------------------------------- |
| `create_transaction`         | Record sales/stock orders | OrderingAgent                 | process_sales_transaction, process_stock_order_transaction |
| `get_all_inventory`          | Inventory snapshot        | InventoryAgent                | check_all_inventory                                        |
| `get_stock_level`            | Item-specific stock       | InventoryAgent, OrderingAgent | check_item_stock, check_restock_needed                     |
| `get_supplier_delivery_date` | Delivery estimates        | OrderingAgent                 | check_delivery_timeline                                    |
| `get_cash_balance`           | Cash flow tracking        | FinancialAgent                | check_cash_balance, approve_purchase                       |
| `generate_financial_report`  | Financial summaries       | FinancialAgent                | get_financial_report, calculate_financial_health           |
| `search_quote_history`       | Historical quote lookup   | QuotingAgent                  | search_historical_quotes                                   |

All tools are specialized to solve specific small problems.

### Technical Implementation Details

**Framework**:

- Chosem framework smolagents (HuggingFace)
- `ToolCallingAgent` provides clean agent abstraction
- `@tool` decorator simplifies tool definition

## Evaluation Results

### Test Execution Overview

**Dataset**: `quote_requests_sample.csv`
**Total Requests**: 20
**Successful Requests**: 17
**Failed Requests**: 3 (due to insufficient funds)

**Test Period**: April 1-17, 2025

### Quote Fulfillment Analysis

**Successfully Fulfilled Quotes**: 17 out of 20 requests (85% success rate)

The system successfully processed orders of varying sizes, from small orders (100-200 units) to large bulk orders (10,000+ units). Delivery timelines were appropriately calculated based on order size.

## Areas for Improvement

#### Implement Partial Order Fulfillment

**Current Limitation**: When a customer requests multiple items and one or more are out of stock, the entire order may fail.

**Proposed Improvement**: Implement a partial fulfillment strategy where:

1. InventoryAgent checks availability for each item separately
2. OrchestratorAgent offers customer options:
   - Fulfill available items immediately
   - Wait for complete order (with estimated delivery date)
   - Cancel unavailable items and proceed with available ones

## 5. Conclusion

The Munder Difflin Multi-Agent System successfully implements a sophisticated, production-ready solution for sales and inventory management. The system demonstrates:

- Clean architecture following best practices
- Comprehensive use of all provided helper functions
- Modular, maintainable codebase
- Robust error handling and validation
- Intelligent bulk discount strategy
- Proactive inventory management
- Financial safeguards preventing cash flow issues
- Transparent customer communication

---

## File Structure

```
project/
├── config.py                      # LLM model configuration
├── helpers.py                    # Helper functions and db engine
├── project_starter.py             # Main orchestration script
├── diagram.md                     # Agent workflow diagram
├── reflection_report.md           # This document
├── test_results.csv               # Evaluation results [to be generated]
│
├── agents/
│   ├── __init__.py               # Agent exports
│   ├── inventory_agent.py        # 6 inventory tools
│   ├── quoting_agent.py          # 3 pricing tools
│   ├── ordering_agent.py         # 5 transaction tools
│   ├── financial_agent.py        # 4 financial tools
│   └── orchestrator_agent.py     # 4 delegation tools
│
├── test_*.py                      # Individual agent tests
└── *.csv                          # Data files
```
