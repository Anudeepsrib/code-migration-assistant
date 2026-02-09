"""
Cost Calculator for migration cost estimation.

Calculates migration costs including:
- Developer time costs
- Infrastructure costs
- Testing costs
- Risk mitigation costs
"""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from ..security import SecurityAuditLogger


@dataclass
class CostBreakdown:
    """Detailed cost breakdown."""
    development_hours: float
    development_cost: float
    testing_hours: float
    testing_cost: float
    infrastructure_cost: float
    training_cost: float
    risk_mitigation_cost: float
    contingency_cost: float
    total_cost: float


class CostCalculator:
    """
    Migration cost calculator.
    
    Features:
    - Time-based cost estimation
    - Infrastructure cost calculation
    - Risk-adjusted costs
    - Contingency planning
    """
    
    def __init__(
        self,
        project_path: Path,
        hourly_rate: float = 100.0,
        currency: str = 'USD'
    ):
        """
        Initialize cost calculator.
        
        Args:
            project_path: Path to project directory
            hourly_rate: Developer hourly rate
            currency: Currency code
        """
        self.project_path = Path(project_path)
        self.hourly_rate = hourly_rate
        self.currency = currency
        
        log_dir = self.project_path / '.migration-logs'
        self.audit_logger = SecurityAuditLogger(log_dir)
        
        self.estimates_file = self.project_path / '.migration-costs.json'
    
    def calculate_migration_cost(
        self,
        migration_type: str,
        file_count: int,
        complexity_score: float,
        team_size: int = 1,
        risk_level: str = 'MEDIUM'
    ) -> CostBreakdown:
        """
        Calculate total migration cost.
        
        Args:
            migration_type: Type of migration
            file_count: Number of files to migrate
            complexity_score: Complexity score (0-100)
            team_size: Team size
            risk_level: Risk level (LOW, MEDIUM, HIGH, CRITICAL)
            
        Returns:
            CostBreakdown object
        """
        # Calculate development time
        development_hours = self._calculate_development_time(
            file_count, complexity_score, team_size
        )
        development_cost = development_hours * self.hourly_rate
        
        # Calculate testing time
        testing_hours = development_hours * 0.3  # 30% of development time
        testing_cost = testing_hours * self.hourly_rate
        
        # Calculate infrastructure costs
        infrastructure_cost = self._calculate_infrastructure_cost(
            migration_type, file_count
        )
        
        # Calculate training costs
        training_cost = self._calculate_training_cost(team_size, migration_type)
        
        # Calculate risk mitigation costs
        risk_mitigation_cost = self._calculate_risk_mitigation_cost(
            development_cost, risk_level
        )
        
        # Calculate contingency (10-20% based on risk)
        base_cost = development_cost + testing_cost + infrastructure_cost + training_cost
        contingency_rate = self._get_contingency_rate(risk_level)
        contingency_cost = base_cost * contingency_rate
        
        # Calculate total
        total_cost = base_cost + risk_mitigation_cost + contingency_cost
        
        breakdown = CostBreakdown(
            development_hours=development_hours,
            development_cost=development_cost,
            testing_hours=testing_hours,
            testing_cost=testing_cost,
            infrastructure_cost=infrastructure_cost,
            training_cost=training_cost,
            risk_mitigation_cost=risk_mitigation_cost,
            contingency_cost=contingency_cost,
            total_cost=total_cost
        )
        
        # Log calculation
        self.audit_logger.log_migration_event(
            migration_type=migration_type,
            project_path=str(self.project_path),
            user='system',
            action='CALCULATE_COST',
            result='SUCCESS',
            details={
                'total_cost': total_cost,
                'development_hours': development_hours,
                'hourly_rate': self.hourly_rate,
                'currency': self.currency
            }
        )
        
        return breakdown
    
    def estimate_team_cost(
        self,
        team_roles: Dict[str, Dict],
        duration_weeks: float
    ) -> float:
        """
        Estimate team cost for migration.
        
        Args:
            team_roles: Dict of role -> {count, hourly_rate}
            duration_weeks: Duration in weeks
            
        Returns:
            Total team cost
        """
        total_cost = 0
        
        for role, details in team_roles.items():
            count = details.get('count', 1)
            rate = details.get('hourly_rate', self.hourly_rate)
            hours_per_week = details.get('hours_per_week', 40)
            
            role_cost = count * rate * hours_per_week * duration_weeks
            total_cost += role_cost
        
        return total_cost
    
    def calculate_savings(
        self,
        current_maintenance_hours: float,
        projected_maintenance_hours: float,
        time_period_months: int = 12
    ) -> Dict:
        """
        Calculate projected savings from migration.
        
        Args:
            current_maintenance_hours: Current monthly maintenance hours
            projected_maintenance_hours: Projected monthly maintenance hours
            time_period_months: Time period for calculation
            
        Returns:
            Savings analysis dict
        """
        # Calculate monthly savings
        monthly_savings_hours = current_maintenance_hours - projected_maintenance_hours
        monthly_savings_cost = monthly_savings_hours * self.hourly_rate
        
        # Calculate total savings over period
        total_savings = monthly_savings_cost * time_period_months
        
        # Calculate efficiency gain
        if current_maintenance_hours > 0:
            efficiency_gain = (monthly_savings_hours / current_maintenance_hours) * 100
        else:
            efficiency_gain = 0
        
        return {
            'monthly_savings_hours': monthly_savings_hours,
            'monthly_savings_cost': monthly_savings_cost,
            'total_savings': total_savings,
            'efficiency_gain_percentage': efficiency_gain,
            'time_period_months': time_period_months
        }
    
    def generate_cost_report(
        self,
        cost_breakdown: CostBreakdown,
        output_format: str = 'text'
    ) -> str:
        """
        Generate cost report.
        
        Args:
            cost_breakdown: Cost breakdown object
            output_format: Output format (text, json, html)
            
        Returns:
            Formatted cost report
        """
        if output_format == 'json':
            return self._generate_json_report(cost_breakdown)
        elif output_format == 'html':
            return self._generate_html_report(cost_breakdown)
        else:
            return self._generate_text_report(cost_breakdown)
    
    def _calculate_development_time(
        self,
        file_count: int,
        complexity_score: float,
        team_size: int
    ) -> float:
        """Calculate estimated development hours."""
        # Base time per file (2-4 hours depending on complexity)
        base_time_per_file = 2 + (complexity_score / 100) * 2
        
        # Total development time
        total_hours = file_count * base_time_per_file
        
        # Adjust for team size (coordination overhead)
        if team_size > 1:
            coordination_factor = 1 + (team_size - 1) * 0.1  # 10% per additional team member
            total_hours *= coordination_factor
        
        return total_hours
    
    def _calculate_infrastructure_cost(
        self,
        migration_type: str,
        file_count: int
    ) -> float:
        """Calculate infrastructure costs."""
        # Base infrastructure cost
        base_cost = 500
        
        # Add cost based on file count (CI/CD, testing environments)
        file_based_cost = file_count * 10
        
        # Migration type specific costs
        type_costs = {
            'react-hooks': 300,
            'vue3': 300,
            'python3': 200,
            'typescript': 250
        }
        
        type_cost = type_costs.get(migration_type, 200)
        
        return base_cost + file_based_cost + type_cost
    
    def _calculate_training_cost(
        self,
        team_size: int,
        migration_type: str
    ) -> float:
        """Calculate training costs."""
        # Training hours per team member
        training_hours_per_person = 8
        
        # Training cost
        training_cost = team_size * training_hours_per_person * self.hourly_rate
        
        # Additional materials cost
        materials_cost = team_size * 100
        
        return training_cost + materials_cost
    
    def _calculate_risk_mitigation_cost(
        self,
        base_cost: float,
        risk_level: str
    ) -> float:
        """Calculate risk mitigation costs."""
        # Risk mitigation rates
        risk_rates = {
            'LOW': 0.05,
            'MEDIUM': 0.1,
            'HIGH': 0.2,
            'CRITICAL': 0.3
        }
        
        rate = risk_rates.get(risk_level, 0.1)
        return base_cost * rate
    
    def _get_contingency_rate(self, risk_level: str) -> float:
        """Get contingency rate based on risk level."""
        rates = {
            'LOW': 0.1,
            'MEDIUM': 0.15,
            'HIGH': 0.2,
            'CRITICAL': 0.25
        }
        
        return rates.get(risk_level, 0.15)
    
    def _generate_text_report(self, cost_breakdown: CostBreakdown) -> str:
        """Generate text format cost report."""
        return f"""
MIGRATION COST ESTIMATE
=======================

Cost Breakdown:
---------------
Development ({cost_breakdown.development_hours:.1f} hours):  {self.currency} {cost_breakdown.development_cost:,.2f}
Testing ({cost_breakdown.testing_hours:.1f} hours):        {self.currency} {cost_breakdown.testing_cost:,.2f}
Infrastructure:                                        {self.currency} {cost_breakdown.infrastructure_cost:,.2f}
Training:                                              {self.currency} {cost_breakdown.training_cost:,.2f}
Risk Mitigation:                                       {self.currency} {cost_breakdown.risk_mitigation_cost:,.2f}
Contingency (10-20%):                                  {self.currency} {cost_breakdown.contingency_cost:,.2f}

TOTAL ESTIMATED COST:                                  {self.currency} {cost_breakdown.total_cost:,.2f}

Notes:
- Hourly rate: {self.currency} {self.hourly_rate}
- Costs include development, testing, infrastructure, and training
- Contingency included for unexpected issues
- Generated: {datetime.now().isoformat()}
"""
    
    def _generate_json_report(self, cost_breakdown: CostBreakdown) -> str:
        """Generate JSON format cost report."""
        data = {
            'currency': self.currency,
            'hourly_rate': self.hourly_rate,
            'cost_breakdown': {
                'development_hours': cost_breakdown.development_hours,
                'development_cost': cost_breakdown.development_cost,
                'testing_hours': cost_breakdown.testing_hours,
                'testing_cost': cost_breakdown.testing_cost,
                'infrastructure_cost': cost_breakdown.infrastructure_cost,
                'training_cost': cost_breakdown.training_cost,
                'risk_mitigation_cost': cost_breakdown.risk_mitigation_cost,
                'contingency_cost': cost_breakdown.contingency_cost,
                'total_cost': cost_breakdown.total_cost
            },
            'generated_at': datetime.now().isoformat()
        }
        
        return json.dumps(data, indent=2)
    
    def _generate_html_report(self, cost_breakdown: CostBreakdown) -> str:
        """Generate HTML format cost report."""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Migration Cost Estimate</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #333; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #4CAF50; color: white; }}
        .total {{ font-weight: bold; font-size: 1.2em; background-color: #f5f5f5; }}
    </style>
</head>
<body>
    <h1>Migration Cost Estimate</h1>
    
    <table>
        <tr>
            <th>Category</th>
            <th>Hours</th>
            <th>Cost ({self.currency})</th>
        </tr>
        <tr>
            <td>Development</td>
            <td>{cost_breakdown.development_hours:.1f}</td>
            <td>{cost_breakdown.development_cost:,.2f}</td>
        </tr>
        <tr>
            <td>Testing</td>
            <td>{cost_breakdown.testing_hours:.1f}</td>
            <td>{cost_breakdown.testing_cost:,.2f}</td>
        </tr>
        <tr>
            <td>Infrastructure</td>
            <td>-</td>
            <td>{cost_breakdown.infrastructure_cost:,.2f}</td>
        </tr>
        <tr>
            <td>Training</td>
            <td>-</td>
            <td>{cost_breakdown.training_cost:,.2f}</td>
        </tr>
        <tr>
            <td>Risk Mitigation</td>
            <td>-</td>
            <td>{cost_breakdown.risk_mitigation_cost:,.2f}</td>
        </tr>
        <tr>
            <td>Contingency</td>
            <td>-</td>
            <td>{cost_breakdown.contingency_cost:,.2f}</td>
        </tr>
        <tr class="total">
            <td>TOTAL</td>
            <td>-</td>
            <td>{cost_breakdown.total_cost:,.2f}</td>
        </tr>
    </table>
    
    <p><small>Generated: {datetime.now().isoformat()}</small></p>
</body>
</html>
"""
