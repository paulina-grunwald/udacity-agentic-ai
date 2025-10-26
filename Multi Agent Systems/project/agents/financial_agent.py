"""
FinancialAgent

This agent is responsible for:
  - Checking cash balance and financial health
  - Approving or rejecting purchases based on available funds
  - Generating financial reports
  - Monitoring company assets and cash flow
"""

from smolagents import ToolCallingAgent, tool
from typing import Dict
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from config import model
from helpers import get_cash_balance, generate_financial_report


@tool
def check_cash_balance(date: str) -> Dict:
    """
    Check the current cash balance as of a specific date.
    The balance represents total revenue from sales minus total costs from stock purchases.

    Args:
      date: Date to check balance (ISO format YYYY-MM-DD)

    Returns:
      Dict with cash_balance and date
    """
    try:
        balance = get_cash_balance(date)

        return {
            "date": date,
            "cash_balance": round(balance, 2),
            "message": f"Cash balance as of {date}: ${balance:,.2f}",
        }
    except Exception as e:
        return {"error": str(e), "message": f"Failed to check cash balance: {str(e)}"}


@tool
def approve_purchase(
    purchase_amount: float, date: str, safety_margin: float = 0.2
) -> Dict:
    """
    Approve or reject a purchase based on available cash balance.
    Approval logic:
      - Ensures company maintains a safety margin (default 20%) of cash reserves
      - Rejects purchases that would reduce cash below the safety threshold

    Args:
      purchase_amount: The total cost of the purchase to approve
      date: Date of the proposed purchase (ISO format YYYY-MM-DD)
      safety_margin: Percentage of current cash to keep as reserve (default 0.2 = 20%)

    Returns:
      Dict with approval decision and financial details
    """
    try:
        current_balance = get_cash_balance(date)
        minimum_balance = current_balance * safety_margin
        available_for_purchase = current_balance - minimum_balance
        balance_after_purchase = current_balance - purchase_amount

        approved = purchase_amount <= available_for_purchase

        return {
            "approved": approved,
            "purchase_amount": round(purchase_amount, 2),
            "current_balance": round(current_balance, 2),
            "balance_after_purchase": round(balance_after_purchase, 2),
            "available_for_purchase": round(available_for_purchase, 2),
            "minimum_balance": round(minimum_balance, 2),
            "safety_margin_percent": safety_margin * 100,
            "message": (
                f"APPROVED: Purchase of ${purchase_amount:,.2f} approved. "
                f"Balance will be ${balance_after_purchase:,.2f} (above minimum ${minimum_balance:,.2f})"
                if approved
                else f"REJECTED: Purchase of ${purchase_amount:,.2f} would bring balance to "
                f"${balance_after_purchase:,.2f}, below safety margin of ${minimum_balance:,.2f}. "
                f"Maximum approved amount: ${available_for_purchase:,.2f}"
            ),
        }
    except Exception as e:
        return {
            "approved": False,
            "error": str(e),
            "message": f"Failed to approve purchase: {str(e)}",
        }


@tool
def get_financial_report(date: str) -> Dict:
    """
    Generate a comprehensive financial report including:
      - Cash balance
      - Inventory valuation
      - Total assets
      - Inventory breakdown by item
      - Top 5 best-selling products

    Args:
      date: Date for the report (ISO format YYYY-MM-DD)

    Returns:
      Dict with complete financial report
    """
    try:
        report = generate_financial_report(date)
        return {
            "as_of_date": report["as_of_date"],
            "cash_balance": round(report["cash_balance"], 2),
            "inventory_value": round(report["inventory_value"], 2),
            "total_assets": round(report["total_assets"], 2),
            "inventory_count": len(report["inventory_summary"]),
            "top_selling_products": report["top_selling_products"],
            "inventory_summary": report["inventory_summary"],
            "message": (
                f"Financial Report as of {date}:\n"
                f"  Cash: ${report['cash_balance']:,.2f}\n"
                f"  Inventory: ${report['inventory_value']:,.2f}\n"
                f"  Total Assets: ${report['total_assets']:,.2f}\n"
                f"  Items in Stock: {len(report['inventory_summary'])}"
            ),
        }
    except Exception as e:
        return {
            "error": str(e),
            "message": f"Failed to generate financial report: {str(e)}",
        }


@tool
def calculate_financial_health(date: str) -> Dict:
    """
    Calculate financial health metrics for the business.

    Metrics include:
    - Cash to assets ratio (liquidity)
    - Inventory to assets ratio
    - Overall financial health assessment

    Args:
        date: Date for the analysis (ISO format YYYY-MM-DD)

    Returns:
        Dict with financial health metrics and assessment
    """
    try:
        report = generate_financial_report(date)

        cash = report["cash_balance"]
        inventory_value = report["inventory_value"]
        total_assets = report["total_assets"]

        if total_assets > 0:
            cash_ratio = cash / total_assets
            inventory_ratio = inventory_value / total_assets
        else:
            cash_ratio = 0.0
            inventory_ratio = 0.0

        # Assess financial health
        if cash_ratio >= 0.3:
            health_status = "EXCELLENT"
            health_message = "Strong cash position with good liquidity"
        elif cash_ratio >= 0.2:
            health_status = "GOOD"
            health_message = "Healthy cash reserves, moderate liquidity"
        elif cash_ratio >= 0.1:
            health_status = "FAIR"
            health_message = "Cash reserves are adequate but could be improved"
        else:
            health_status = "POOR"
            health_message = "Low cash reserves, limited purchasing power"

        return {
            "date": date,
            "health_status": health_status,
            "cash_balance": round(cash, 2),
            "inventory_value": round(inventory_value, 2),
            "total_assets": round(total_assets, 2),
            "cash_to_assets_ratio": round(cash_ratio, 3),
            "inventory_to_assets_ratio": round(inventory_ratio, 3),
            "message": (
                f"Financial Health: {health_status}\n"
                f"{health_message}\n"
                f"Cash Ratio: {cash_ratio:.1%} | Inventory Ratio: {inventory_ratio:.1%}"
            ),
        }
    except Exception as e:
        return {
            "error": str(e),
            "message": f"Failed to calculate financial health: {str(e)}",
        }


financial_agent = ToolCallingAgent(
    tools=[
        check_cash_balance,
        approve_purchase,
        get_financial_report,
        calculate_financial_health,
    ],
    model=model,
    max_steps=5,
    name="FinancialAgent",
    description="""You are the Financial Agent for Munder Difflin paper company.

Your responsibilities:
1. Monitor cash balance and company financial health
2. Approve or reject purchase requests based on available funds
3. Generate comprehensive financial reports
4. Assess business liquidity and financial ratios
5. Ensure the company maintains adequate cash reserves

IMPORTANT RULES:
- Always check current cash balance before approving purchases
- Maintain a safety margin (default 20%) of cash reserves
- Never approve purchases that would bring cash below the safety threshold
- Provide clear explanations for approval or rejection decisions
- Include specific dollar amounts in all financial decisions
- Use ISO date format (YYYY-MM-DD) for all dates
- Monitor financial health regularly to prevent cash flow issues

Approval Process:
1. Check current cash balance as of the purchase date
2. Calculate minimum balance (20% safety margin)
3. Determine available funds for purchase
4. Approve if purchase amount ≤ available funds
5. Reject if purchase would bring balance below safety margin
6. Provide detailed reasoning for the decision

Financial Health Assessment:
- EXCELLENT: Cash ratio ≥ 30% of total assets
- GOOD: Cash ratio 20-30% of total assets
- FAIR: Cash ratio 10-20% of total assets
- POOR: Cash ratio < 10% of total assets

Always provide transparent, detailed financial information to support business decisions.
DO NOT reveal sensitive profit margins or internal cost structures to external parties.
""",
)
