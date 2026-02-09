"""
ROI Analyzer for return on investment calculations.

Calculates ROI metrics:
- Payback period
- Net present value
- Cost-benefit analysis
- Risk-adjusted returns
"""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from ..security import SecurityAuditLogger


@dataclass
class ROIMetrics:
    """ROI analysis metrics."""
    payback_period_months: float
    net_present_value: float
    roi_percentage: float
    cost_benefit_ratio: float
    break_even_point: float
    total_investment: float
    total_returns: float
    risk_adjusted_roi: float


class ROIAnalyzer:
    """
    ROI analysis for migration projects.
    
    Features:
    - Payback period calculation
    - NPV analysis
    - Cost-benefit analysis
    - Risk-adjusted returns
    """
    
    def __init__(self, project_path: Path, discount_rate: float = 0.1):
        """
        Initialize ROI analyzer.
        
        Args:
            project_path: Path to project directory
            discount_rate: Annual discount rate for NPV
        """
        self.project_path = Path(project_path)
        self.discount_rate = discount_rate
        
        log_dir = self.project_path / '.migration-logs'
        self.audit_logger = SecurityAuditLogger(log_dir)
        
        self.roi_file = self.project_path / '.migration-roi.json'
    
    def calculate_roi(
        self,
        investment_cost: float,
        monthly_savings: float,
        monthly_revenue_increase: float = 0,
        time_period_months: int = 24
    ) -> ROIMetrics:
        """
        Calculate ROI metrics.
        
        Args:
            investment_cost: Total investment cost
            monthly_savings: Monthly operational savings
            monthly_revenue_increase: Monthly revenue increase
            time_period_months: Analysis time period
            
        Returns:
            ROIMetrics object
        """
        # Calculate total returns
        total_monthly_benefit = monthly_savings + monthly_revenue_increase
        total_returns = total_monthly_benefit * time_period_months
        
        # Calculate ROI percentage
        net_profit = total_returns - investment_cost
        roi_percentage = (net_profit / investment_cost) * 100 if investment_cost > 0 else 0
        
        # Calculate payback period
        payback_period_months = investment_cost / total_monthly_benefit if total_monthly_benefit > 0 else float('inf')
        
        # Calculate NPV
        npv = self._calculate_npv(
            initial_investment=investment_cost,
            monthly_cash_flow=total_monthly_benefit,
            time_period_months=time_period_months
        )
        
        # Calculate cost-benefit ratio
        cost_benefit_ratio = total_returns / investment_cost if investment_cost > 0 else 0
        
        # Calculate break-even point
        break_even_months = investment_cost / total_monthly_benefit if total_monthly_benefit > 0 else float('inf')
        
        # Calculate risk-adjusted ROI (conservative estimate)
        risk_adjusted_returns = total_returns * 0.8  # 20% risk discount
        risk_adjusted_roi = ((risk_adjusted_returns - investment_cost) / investment_cost) * 100 if investment_cost > 0 else 0
        
        metrics = ROIMetrics(
            payback_period_months=payback_period_months,
            net_present_value=npv,
            roi_percentage=roi_percentage,
            cost_benefit_ratio=cost_benefit_ratio,
            break_even_point=break_even_months,
            total_investment=investment_cost,
            total_returns=total_returns,
            risk_adjusted_roi=risk_adjusted_roi
        )
        
        # Log calculation
        self.audit_logger.log_migration_event(
            migration_type='roi-analysis',
            project_path=str(self.project_path),
            user='system',
            action='CALCULATE_ROI',
            result='SUCCESS',
            details={
                'investment': investment_cost,
                'roi_percentage': roi_percentage,
                'payback_months': payback_period_months,
                'npv': npv
            }
        )
        
        return metrics
    
    def calculate_scenario_comparison(
        self,
        scenarios: List[Dict],
        time_period_months: int = 24
    ) -> Dict:
        """
        Compare multiple ROI scenarios.
        
        Args:
            scenarios: List of scenario dicts with investment and savings
            time_period_months: Analysis time period
            
        Returns:
            Comparison results
        """
        comparison_results = []
        
        for scenario in scenarios:
            name = scenario.get('name', 'Unnamed Scenario')
            investment = scenario.get('investment', 0)
            monthly_savings = scenario.get('monthly_savings', 0)
            monthly_revenue = scenario.get('monthly_revenue_increase', 0)
            
            metrics = self.calculate_roi(
                investment_cost=investment,
                monthly_savings=monthly_savings,
                monthly_revenue_increase=monthly_revenue,
                time_period_months=time_period_months
            )
            
            comparison_results.append({
                'scenario_name': name,
                'investment': investment,
                'monthly_benefit': monthly_savings + monthly_revenue,
                'roi_percentage': metrics.roi_percentage,
                'payback_months': metrics.payback_period_months,
                'npv': metrics.net_present_value,
                'rank_score': self._calculate_rank_score(metrics)
            })
        
        # Sort by rank score
        comparison_results.sort(key=lambda x: x['rank_score'], reverse=True)
        
        return {
            'scenarios': comparison_results,
            'best_scenario': comparison_results[0] if comparison_results else None,
            'comparison_period_months': time_period_months
        }
    
    def generate_roi_report(
        self,
        metrics: ROIMetrics,
        output_format: str = 'text'
    ) -> str:
        """
        Generate ROI report.
        
        Args:
            metrics: ROIMetrics object
            output_format: Output format (text, json, html)
            
        Returns:
            Formatted ROI report
        """
        if output_format == 'json':
            return self._generate_json_report(metrics)
        elif output_format == 'html':
            return self._generate_html_report(metrics)
        else:
            return self._generate_text_report(metrics)
    
    def _calculate_npv(
        self,
        initial_investment: float,
        monthly_cash_flow: float,
        time_period_months: int
    ) -> float:
        """Calculate Net Present Value."""
        monthly_discount_rate = self.discount_rate / 12
        
        npv = -initial_investment  # Initial investment is negative
        
        for month in range(1, time_period_months + 1):
            # Discount future cash flows
            discounted_cash_flow = monthly_cash_flow / ((1 + monthly_discount_rate) ** month)
            npv += discounted_cash_flow
        
        return npv
    
    def _calculate_rank_score(self, metrics: ROIMetrics) -> float:
        """Calculate ranking score for scenario comparison."""
        # Weight factors
        roi_weight = 0.4
        payback_weight = 0.3
        npv_weight = 0.3
        
        # Normalize metrics for scoring
        # ROI: Higher is better
        roi_score = min(metrics.roi_percentage / 100, 2.0)  # Cap at 200%
        
        # Payback: Lower is better (inverted)
        payback_score = max(0, 1 - (metrics.payback_period_months / 24))  # Normalize to 24 months
        
        # NPV: Higher is better (relative to investment)
        npv_score = max(0, metrics.net_present_value / max(metrics.total_investment, 1))
        
        # Calculate weighted score
        rank_score = (
            roi_score * roi_weight +
            payback_score * payback_weight +
            npv_score * npv_weight
        )
        
        return rank_score
    
    def _generate_text_report(self, metrics: ROIMetrics) -> str:
        """Generate text format ROI report."""
        return f"""
ROI ANALYSIS REPORT
===================

Investment Summary:
-------------------
Total Investment:      ${metrics.total_investment:,.2f}
Total Returns:         ${metrics.total_returns:,.2f}
Net Profit:            ${metrics.total_returns - metrics.total_investment:,.2f}

ROI Metrics:
------------
ROI Percentage:        {metrics.roi_percentage:.1f}%
Risk-Adjusted ROI:     {metrics.risk_adjusted_roi:.1f}%
Cost-Benefit Ratio:    {metrics.cost_benefit_ratio:.2f}:1

Financial Analysis:
-------------------
Payback Period:        {metrics.payback_period_months:.1f} months
Break-Even Point:      {metrics.break_even_point:.1f} months
Net Present Value:     ${metrics.net_present_value:,.2f}
Discount Rate:         {self.discount_rate:.1%}

Interpretation:
--------------
{self._generate_interpretation(metrics)}

Generated: {datetime.now().isoformat()}
"""
    
    def _generate_json_report(self, metrics: ROIMetrics) -> str:
        """Generate JSON format ROI report."""
        data = {
            'metrics': {
                'total_investment': metrics.total_investment,
                'total_returns': metrics.total_returns,
                'net_profit': metrics.total_returns - metrics.total_investment,
                'roi_percentage': metrics.roi_percentage,
                'risk_adjusted_roi': metrics.risk_adjusted_roi,
                'payback_period_months': metrics.payback_period_months,
                'break_even_point': metrics.break_even_point,
                'net_present_value': metrics.net_present_value,
                'cost_benefit_ratio': metrics.cost_benefit_ratio,
                'discount_rate': self.discount_rate
            },
            'interpretation': self._generate_interpretation(metrics),
            'generated_at': datetime.now().isoformat()
        }
        
        return json.dumps(data, indent=2)
    
    def _generate_html_report(self, metrics: ROIMetrics) -> str:
        """Generate HTML format ROI report."""
        interpretation = self._generate_interpretation(metrics)
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>ROI Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #333; }}
        .metric {{ background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }}
        .positive {{ color: #4CAF50; }}
        .negative {{ color: #F44336; }}
        .neutral {{ color: #FF9800; }}
    </style>
</head>
<body>
    <h1>ROI Analysis Report</h1>
    
    <h2>Key Metrics</h2>
    <div class="metric">
        <strong>ROI Percentage:</strong> 
        <span class="{'positive' if metrics.roi_percentage > 0 else 'negative'}">{metrics.roi_percentage:.1f}%</span>
    </div>
    <div class="metric">
        <strong>Payback Period:</strong> {metrics.payback_period_months:.1f} months
    </div>
    <div class="metric">
        <strong>Net Present Value:</strong> ${metrics.net_present_value:,.2f}
    </div>
    <div class="metric">
        <strong>Cost-Benefit Ratio:</strong> {metrics.cost_benefit_ratio:.2f}:1
    </div>
    
    <h2>Investment Summary</h2>
    <div class="metric">
        <strong>Total Investment:</strong> ${metrics.total_investment:,.2f}
    </div>
    <div class="metric">
        <strong>Total Returns:</strong> ${metrics.total_returns:,.2f}
    </div>
    <div class="metric">
        <strong>Net Profit:</strong> 
        <span class="{'positive' if metrics.total_returns > metrics.total_investment else 'negative'}">
            ${metrics.total_returns - metrics.total_investment:,.2f}
        </span>
    </div>
    
    <h2>Interpretation</h2>
    <p>{interpretation}</p>
    
    <p><small>Generated: {datetime.now().isoformat()}</small></p>
</body>
</html>
"""
    
    def _generate_interpretation(self, metrics: ROIMetrics) -> str:
        """Generate interpretation of ROI metrics."""
        interpretations = []
        
        # ROI interpretation
        if metrics.roi_percentage >= 100:
            interpretations.append(f"Excellent ROI of {metrics.roi_percentage:.1f}% - Investment pays for itself and generates significant returns.")
        elif metrics.roi_percentage >= 50:
            interpretations.append(f"Strong ROI of {metrics.roi_percentage:.1f}% - Investment is highly profitable.")
        elif metrics.roi_percentage >= 20:
            interpretations.append(f"Good ROI of {metrics.roi_percentage:.1f}% - Investment is profitable.")
        elif metrics.roi_percentage > 0:
            interpretations.append(f"Modest ROI of {metrics.roi_percentage:.1f}% - Investment is marginally profitable.")
        else:
            interpretations.append(f"Negative ROI of {metrics.roi_percentage:.1f}% - Investment does not generate positive returns.")
        
        # Payback interpretation
        if metrics.payback_period_months <= 6:
            interpretations.append(f"Fast payback period of {metrics.payback_period_months:.1f} months - Investment recovers quickly.")
        elif metrics.payback_period_months <= 12:
            interpretations.append(f"Reasonable payback period of {metrics.payback_period_months:.1f} months - Investment recovers within a year.")
        elif metrics.payback_period_months <= 24:
            interpretations.append(f"Moderate payback period of {metrics.payback_period_months:.1f} months - Investment recovers within two years.")
        else:
            interpretations.append(f"Long payback period of {metrics.payback_period_months:.1f} months - Investment takes significant time to recover.")
        
        # NPV interpretation
        if metrics.net_present_value > 0:
            interpretations.append(f"Positive NPV of ${metrics.net_present_value:,.2f} - Investment creates value.")
        else:
            interpretations.append(f"Negative NPV of ${metrics.net_present_value:,.2f} - Investment destroys value.")
        
        return " ".join(interpretations)
