"""
Budget Planner for migration budget management.

Provides budget planning features:
- Budget allocation
- Cost tracking
- Variance analysis
- Budget forecasting
"""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from ..security import SecurityAuditLogger


@dataclass
class BudgetItem:
    """Budget line item."""
    item_id: str
    category: str
    description: str
    estimated_cost: float
    actual_cost: float
    variance: float
    status: str
    created_at: str


@dataclass
class BudgetPlan:
    """Complete budget plan."""
    plan_id: str
    project_name: str
    total_budget: float
    items: List[BudgetItem]
    contingency_reserve: float
    spent_to_date: float
    remaining_budget: float
    created_at: str
    updated_at: str


class BudgetPlanner:
    """
    Migration budget planning and tracking.
    
    Features:
    - Budget allocation
    - Cost tracking
    - Variance analysis
    - Forecasting
    """
    
    def __init__(self, project_path: Path):
        """
        Initialize budget planner.
        
        Args:
            project_path: Path to project directory
        """
        self.project_path = Path(project_path)
        self.budget_plans: Dict[str, BudgetPlan] = {}
        
        log_dir = self.project_path / '.migration-logs'
        self.audit_logger = SecurityAuditLogger(log_dir)
        
        self.budgets_file = self.project_path / '.migration-budgets.json'
        self._load_budget_plans()
    
    def create_budget_plan(
        self,
        project_name: str,
        total_budget: float,
        categories: Optional[List[str]] = None
    ) -> BudgetPlan:
        """
        Create a new budget plan.
        
        Args:
            project_name: Project name
            total_budget: Total budget amount
            categories: Optional list of budget categories
            
        Returns:
            BudgetPlan object
        """
        plan_id = f"budget_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Default categories if not provided
        if categories is None:
            categories = [
                'Development',
                'Testing',
                'Infrastructure',
                'Training',
                'Risk Mitigation',
                'Contingency'
            ]
        
        # Create budget items
        items = []
        category_budget = total_budget * 0.85 / len(categories)  # 85% allocated to categories
        
        for i, category in enumerate(categories):
            item_id = f"{plan_id}_item_{i}"
            item = BudgetItem(
                item_id=item_id,
                category=category,
                description=f"Budget for {category}",
                estimated_cost=category_budget,
                actual_cost=0.0,
                variance=0.0,
                status='PLANNED',
                created_at=datetime.now().isoformat()
            )
            items.append(item)
        
        # Contingency reserve (15%)
        contingency = total_budget * 0.15
        
        plan = BudgetPlan(
            plan_id=plan_id,
            project_name=project_name,
            total_budget=total_budget,
            items=items,
            contingency_reserve=contingency,
            spent_to_date=0.0,
            remaining_budget=total_budget,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        self.budget_plans[plan_id] = plan
        self._save_budget_plans()
        
        self.audit_logger.log_migration_event(
            migration_type='budget',
            project_path=str(self.project_path),
            user='system',
            action='CREATE_BUDGET_PLAN',
            result='SUCCESS',
            details={
                'plan_id': plan_id,
                'project': project_name,
                'total_budget': total_budget
            }
        )
        
        return plan
    
    def record_expense(
        self,
        plan_id: str,
        item_id: str,
        amount: float,
        description: str = ''
    ) -> bool:
        """
        Record an expense against a budget item.
        
        Args:
            plan_id: Budget plan ID
            item_id: Budget item ID
            amount: Expense amount
            description: Expense description
            
        Returns:
            True if recorded successfully
        """
        if plan_id not in self.budget_plans:
            return False
        
        plan = self.budget_plans[plan_id]
        
        # Find budget item
        item = None
        for budget_item in plan.items:
            if budget_item.item_id == item_id:
                item = budget_item
                break
        
        if not item:
            return False
        
        # Update actual cost
        item.actual_cost += amount
        item.variance = item.actual_cost - item.estimated_cost
        
        # Update status based on variance
        if item.variance > item.estimated_cost * 0.2:  # Over budget by 20%
            item.status = 'OVER_BUDGET'
        elif item.variance > 0:
            item.status = 'WARNING'
        else:
            item.status = 'ON_TRACK'
        
        # Update plan totals
        plan.spent_to_date = sum(i.actual_cost for i in plan.items)
        plan.remaining_budget = plan.total_budget - plan.spent_to_date
        plan.updated_at = datetime.now().isoformat()
        
        self._save_budget_plans()
        
        self.audit_logger.log_migration_event(
            migration_type='budget',
            project_path=str(self.project_path),
            user='system',
            action='RECORD_EXPENSE',
            result='SUCCESS',
            details={
                'plan_id': plan_id,
                'item_id': item_id,
                'amount': amount,
                'description': description
            }
        )
        
        return True
    
    def get_budget_summary(self, plan_id: str) -> Optional[Dict]:
        """
        Get budget summary.
        
        Args:
            plan_id: Budget plan ID
            
        Returns:
            Budget summary dict or None
        """
        if plan_id not in self.budget_plans:
            return None
        
        plan = self.budget_plans[plan_id]
        
        # Calculate category breakdown
        category_breakdown = {}
        for item in plan.items:
            category_breakdown[item.category] = {
                'estimated': item.estimated_cost,
                'actual': item.actual_cost,
                'variance': item.variance,
                'status': item.status
            }
        
        # Calculate burn rate
        if plan.spent_to_date > 0:
            days_since_creation = (
                datetime.now() - datetime.fromisoformat(plan.created_at)
            ).days
            daily_burn_rate = plan.spent_to_date / max(days_since_creation, 1)
            projected_days_remaining = plan.remaining_budget / max(daily_burn_rate, 1)
        else:
            daily_burn_rate = 0
            projected_days_remaining = 0
        
        return {
            'plan_id': plan.plan_id,
            'project_name': plan.project_name,
            'total_budget': plan.total_budget,
            'spent_to_date': plan.spent_to_date,
            'remaining_budget': plan.remaining_budget,
            'contingency_reserve': plan.contingency_reserve,
            'budget_utilization': plan.spent_to_date / plan.total_budget if plan.total_budget > 0 else 0,
            'category_breakdown': category_breakdown,
            'daily_burn_rate': daily_burn_rate,
            'projected_days_remaining': projected_days_remaining,
            'status': self._determine_budget_status(plan),
            'last_updated': plan.updated_at
        }
    
    def generate_budget_report(
        self,
        plan_id: str,
        output_format: str = 'text'
    ) -> Optional[str]:
        """
        Generate budget report.
        
        Args:
            plan_id: Budget plan ID
            output_format: Output format (text, json, html)
            
        Returns:
            Budget report or None
        """
        summary = self.get_budget_summary(plan_id)
        if not summary:
            return None
        
        if output_format == 'json':
            return json.dumps(summary, indent=2)
        elif output_format == 'html':
            return self._generate_html_budget_report(summary)
        else:
            return self._generate_text_budget_report(summary)
    
    def forecast_budget(
        self,
        plan_id: str,
        months_ahead: int = 6
    ) -> Optional[Dict]:
        """
        Forecast future budget needs.
        
        Args:
            plan_id: Budget plan ID
            months_ahead: Number of months to forecast
            
        Returns:
            Forecast dict or None
        """
        if plan_id not in self.budget_plans:
            return None
        
        plan = self.budget_plans[plan_id]
        
        # Calculate monthly burn rate
        days_since_start = (
            datetime.now() - datetime.fromisoformat(plan.created_at)
        ).days
        months_elapsed = days_since_start / 30
        
        if months_elapsed > 0:
            monthly_burn_rate = plan.spent_to_date / months_elapsed
        else:
            monthly_burn_rate = plan.total_budget / 6  # Assume 6-month project
        
        # Forecast
        forecasted_spending = []
        cumulative_spend = plan.spent_to_date
        
        for month in range(1, months_ahead + 1):
            cumulative_spend += monthly_burn_rate
            forecasted_spending.append({
                'month': month,
                'projected_spend': monthly_burn_rate,
                'cumulative_spend': cumulative_spend,
                'remaining_budget': max(0, plan.total_budget - cumulative_spend)
            })
        
        # Determine if budget will be exceeded
        budget_exceeded = cumulative_spend > plan.total_budget
        months_until_depletion = (
            plan.remaining_budget / monthly_burn_rate
            if monthly_burn_rate > 0 else float('inf')
        )
        
        return {
            'current_monthly_burn_rate': monthly_burn_rate,
            'months_forecasted': months_ahead,
            'forecasted_spending': forecasted_spending,
            'budget_exceeded': budget_exceeded,
            'projected_budget_depletion_months': months_until_depletion,
            'recommendation': self._generate_forecast_recommendation(
                budget_exceeded, months_until_depletion, plan.remaining_budget
            )
        }
    
    def compare_budgets(self, plan_ids: List[str]) -> Dict:
        """
        Compare multiple budget plans.
        
        Args:
            plan_ids: List of budget plan IDs
            
        Returns:
            Comparison results
        """
        comparisons = []
        
        for plan_id in plan_ids:
            summary = self.get_budget_summary(plan_id)
            if summary:
                comparisons.append({
                    'plan_id': plan_id,
                    'project_name': summary['project_name'],
                    'total_budget': summary['total_budget'],
                    'spent_to_date': summary['spent_to_date'],
                    'remaining_budget': summary['remaining_budget'],
                    'utilization': summary['budget_utilization']
                })
        
        # Sort by utilization
        comparisons.sort(key=lambda x: x['utilization'], reverse=True)
        
        return {
            'comparisons': comparisons,
            'total_combined_budget': sum(c['total_budget'] for c in comparisons),
            'total_combined_spent': sum(c['spent_to_date'] for c in comparisons),
            'average_utilization': sum(c['utilization'] for c in comparisons) / len(comparisons) if comparisons else 0
        }
    
    def _determine_budget_status(self, plan: BudgetPlan) -> str:
        """Determine budget status."""
        utilization = plan.spent_to_date / plan.total_budget if plan.total_budget > 0 else 0
        
        # Check for overspend
        if plan.spent_to_date > plan.total_budget:
            return 'OVER_BUDGET'
        
        # Check individual items
        over_budget_items = sum(1 for item in plan.items if item.status == 'OVER_BUDGET')
        warning_items = sum(1 for item in plan.items if item.status == 'WARNING')
        
        if over_budget_items > 0:
            return 'AT_RISK'
        elif warning_items > 0:
            return 'WARNING'
        elif utilization >= 0.9:
            return 'NEAR_LIMIT'
        elif utilization >= 0.75:
            return 'ON_TRACK'
        else:
            return 'HEALTHY'
    
    def _generate_forecast_recommendation(
        self,
        budget_exceeded: bool,
        months_until_depletion: float,
        remaining_budget: float
    ) -> str:
        """Generate forecast recommendation."""
        if budget_exceeded:
            return "CRITICAL: Budget will be exceeded based on current spending rate. Consider increasing budget or reducing scope."
        elif months_until_depletion < 3:
            return f"WARNING: Budget will be depleted in {months_until_depletion:.1f} months. Monitor spending closely."
        elif months_until_depletion < 6:
            return f"CAUTION: Budget will be depleted in {months_until_depletion:.1f} months. Plan accordingly."
        else:
            return f"Budget appears sufficient for {months_until_depletion:.1f} months at current spending rate."
    
    def _generate_text_budget_report(self, summary: Dict) -> str:
        """Generate text format budget report."""
        report = f"""
BUDGET REPORT: {summary['project_name']}
{'=' * (len(summary['project_name']) + 14)}

OVERALL STATUS: {summary['status']}

Budget Overview:
---------------
Total Budget:          ${summary['total_budget']:,.2f}
Spent to Date:         ${summary['spent_to_date']:,.2f}
Remaining Budget:      ${summary['remaining_budget']:,.2f}
Contingency Reserve:   ${summary['contingency_reserve']:,.2f}

Utilization:           {summary['budget_utilization']:.1%}
Daily Burn Rate:       ${summary['daily_burn_rate']:,.2f}

Category Breakdown:
------------------
"""
        
        for category, data in summary['category_breakdown'].items():
            report += f"{category}:\n"
            report += f"  Estimated: ${data['estimated']:,.2f}\n"
            report += f"  Actual:    ${data['actual']:,.2f}\n"
            report += f"  Variance:  ${data['variance']:,.2f} ({data['status']})\n\n"
        
        report += f"""
Last Updated: {summary['last_updated']}
"""
        
        return report
    
    def _generate_html_budget_report(self, summary: Dict) -> str:
        """Generate HTML format budget report."""
        status_colors = {
            'HEALTHY': '#4CAF50',
            'ON_TRACK': '#8BC34A',
            'WARNING': '#FF9800',
            'AT_RISK': '#F44336',
            'OVER_BUDGET': '#D32F2F',
            'NEAR_LIMIT': '#FFC107'
        }
        
        status_color = status_colors.get(summary['status'], '#9E9E9E')
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Budget Report - {summary['project_name']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background: {status_color}; color: white; padding: 20px; border-radius: 8px; }}
        .metric {{ background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .progress-bar {{ width: 100%; height: 30px; background: #e0e0e0; border-radius: 15px; overflow: hidden; }}
        .progress-fill {{ height: 100%; background: {status_color}; width: {summary['budget_utilization'] * 100}%; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #4CAF50; color: white; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Budget Report: {summary['project_name']}</h1>
        <p>Status: {summary['status']}</p>
    </div>
    
    <div class="metric">
        <h3>Budget Utilization</h3>
        <div class="progress-bar">
            <div class="progress-fill"></div>
        </div>
        <p>{summary['budget_utilization']:.1%} (${summary['spent_to_date']:,.2f} / ${summary['total_budget']:,.2f})</p>
    </div>
    
    <div class="metric">
        <h3>Financial Summary</h3>
        <table>
            <tr>
                <th>Category</th>
                <th>Estimated</th>
                <th>Actual</th>
                <th>Variance</th>
                <th>Status</th>
            </tr>
"""
        
        for category, data in summary['category_breakdown'].items():
            html += f"""
            <tr>
                <td>{category}</td>
                <td>${data['estimated']:,.2f}</td>
                <td>${data['actual']:,.2f}</td>
                <td>${data['variance']:,.2f}</td>
                <td>{data['status']}</td>
            </tr>
"""
        
        html += f"""
        </table>
    </div>
    
    <p style="text-align: center; color: #999; margin-top: 40px;">
        Last Updated: {summary['last_updated']}
    </p>
</body>
</html>
"""
        
        return html
    
    def _load_budget_plans(self) -> None:
        """Load budget plans from file."""
        if self.budgets_file.exists():
            try:
                with open(self.budgets_file, 'r') as f:
                    data = json.load(f)
                    for plan_data in data.get('budget_plans', []):
                        # Reconstruct items
                        items = [
                            BudgetItem(**item_data)
                            for item_data in plan_data.get('items', [])
                        ]
                        
                        plan = BudgetPlan(
                            plan_id=plan_data['plan_id'],
                            project_name=plan_data['project_name'],
                            total_budget=plan_data['total_budget'],
                            items=items,
                            contingency_reserve=plan_data['contingency_reserve'],
                            spent_to_date=plan_data['spent_to_date'],
                            remaining_budget=plan_data['remaining_budget'],
                            created_at=plan_data['created_at'],
                            updated_at=plan_data['updated_at']
                        )
                        
                        self.budget_plans[plan.plan_id] = plan
            except Exception:
                pass
    
    def _save_budget_plans(self) -> None:
        """Save budget plans to file."""
        try:
            data = {
                'budget_plans': [
                    {
                        'plan_id': p.plan_id,
                        'project_name': p.project_name,
                        'total_budget': p.total_budget,
                        'items': [
                            {
                                'item_id': i.item_id,
                                'category': i.category,
                                'description': i.description,
                                'estimated_cost': i.estimated_cost,
                                'actual_cost': i.actual_cost,
                                'variance': i.variance,
                                'status': i.status,
                                'created_at': i.created_at
                            }
                            for i in p.items
                        ],
                        'contingency_reserve': p.contingency_reserve,
                        'spent_to_date': p.spent_to_date,
                        'remaining_budget': p.remaining_budget,
                        'created_at': p.created_at,
                        'updated_at': p.updated_at
                    }
                    for p in self.budget_plans.values()
                ],
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.budgets_file, 'w') as f:
                json.dump(data, f, indent=2)
        
        except Exception:
            pass
