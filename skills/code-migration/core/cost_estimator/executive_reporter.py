"""
Executive Reporter for high-level migration reports.

Generates executive-friendly reports:
- Executive summaries
- Key metrics dashboards
- Risk assessments
- Recommendation reports
"""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from ..security import SecurityAuditLogger


@dataclass
class ExecutiveSummary:
    """Executive summary data structure."""
    project_name: str
    migration_type: str
    overall_status: str
    total_files: int
    completed_files: int
    progress_percentage: float
    total_cost: float
    expected_roi: float
    risk_level: str
    key_recommendations: List[str]
    milestones_achieved: List[str]
    next_steps: List[str]


class ExecutiveReporter:
    """
    Executive reporting for migration projects.
    
    Features:
    - Executive summaries
    - Dashboard reports
    - Risk assessments
    - Recommendation reports
    """
    
    def __init__(self, project_path: Path):
        """
        Initialize executive reporter.
        
        Args:
            project_path: Path to project directory
        """
        self.project_path = Path(project_path)
        
        log_dir = self.project_path / '.migration-logs'
        self.audit_logger = SecurityAuditLogger(log_dir)
        
        self.reports_file = self.project_path / '.migration-executive-reports.json'
    
    def generate_executive_summary(
        self,
        project_name: str,
        migration_type: str,
        progress_data: Dict,
        cost_data: Dict,
        risk_data: Dict
    ) -> ExecutiveSummary:
        """
        Generate executive summary.
        
        Args:
            project_name: Project name
            migration_type: Type of migration
            progress_data: Progress metrics
            cost_data: Cost information
            risk_data: Risk assessment data
            
        Returns:
            ExecutiveSummary object
        """
        total_files = progress_data.get('total_files', 0)
        completed_files = progress_data.get('completed_files', 0)
        progress_percentage = (completed_files / max(total_files, 1)) * 100
        
        total_cost = cost_data.get('total_cost', 0)
        expected_roi = cost_data.get('expected_roi_percentage', 0)
        
        risk_level = risk_data.get('overall_risk', 'MEDIUM')
        
        # Generate recommendations
        key_recommendations = self._generate_recommendations(
            progress_percentage, risk_level, cost_data
        )
        
        # Determine status
        overall_status = self._determine_status(progress_percentage, risk_level)
        
        # Generate milestones
        milestones_achieved = self._identify_milestones(progress_data)
        
        # Generate next steps
        next_steps = self._generate_next_steps(progress_percentage, risk_level)
        
        summary = ExecutiveSummary(
            project_name=project_name,
            migration_type=migration_type,
            overall_status=overall_status,
            total_files=total_files,
            completed_files=completed_files,
            progress_percentage=progress_percentage,
            total_cost=total_cost,
            expected_roi=expected_roi,
            risk_level=risk_level,
            key_recommendations=key_recommendations,
            milestones_achieved=milestones_achieved,
            next_steps=next_steps
        )
        
        # Log generation
        self.audit_logger.log_migration_event(
            migration_type=migration_type,
            project_path=str(self.project_path),
            user='system',
            action='GENERATE_EXECUTIVE_SUMMARY',
            result='SUCCESS',
            details={
                'project': project_name,
                'progress': progress_percentage,
                'risk_level': risk_level
            }
        )
        
        return summary
    
    def generate_dashboard_report(
        self,
        summary: ExecutiveSummary,
        output_format: str = 'html'
    ) -> str:
        """
        Generate dashboard-style report.
        
        Args:
            summary: ExecutiveSummary object
            output_format: Output format (html, pdf, json)
            
        Returns:
            Report content
        """
        if output_format == 'json':
            return self._generate_json_dashboard(summary)
        elif output_format == 'html':
            return self._generate_html_dashboard(summary)
        else:
            return self._generate_text_dashboard(summary)
    
    def generate_risk_assessment_report(
        self,
        risk_data: Dict,
        mitigation_strategies: List[str]
    ) -> str:
        """
        Generate risk assessment report.
        
        Args:
            risk_data: Risk assessment data
            mitigation_strategies: List of mitigation strategies
            
        Returns:
            Risk report content
        """
        report = f"""
RISK ASSESSMENT REPORT
=====================

Executive Summary:
------------------
Overall Risk Level: {risk_data.get('overall_risk', 'UNKNOWN')}
Risk Score: {risk_data.get('risk_score', 0):.1f}/100

Risk Categories:
----------------
"""
        
        # Add risk categories
        for category, details in risk_data.get('categories', {}).items():
            level = details.get('level', 'UNKNOWN')
            score = details.get('score', 0)
            report += f"• {category}: {level} (Score: {score:.1f})\n"
        
        report += f"""

Key Risks Identified:
---------------------
"""
        
        # Add specific risks
        for risk in risk_data.get('key_risks', []):
            report += f"• {risk.get('description', 'Unknown risk')}\n"
            report += f"  Impact: {risk.get('impact', 'Unknown')}, Probability: {risk.get('probability', 'Unknown')}\n\n"
        
        report += f"""

Mitigation Strategies:
----------------------
"""
        
        for i, strategy in enumerate(mitigation_strategies, 1):
            report += f"{i}. {strategy}\n"
        
        report += f"""

Recommendations:
---------------
{self._generate_risk_recommendations(risk_data)}

Report Generated: {datetime.now().isoformat()}
"""
        
        return report
    
    def generate_recommendation_report(
        self,
        recommendations: List[Dict],
        priority: str = 'all'
    ) -> str:
        """
        Generate recommendation report.
        
        Args:
            recommendations: List of recommendation dictionaries
            priority: Priority filter (high, medium, low, all)
            
        Returns:
            Recommendation report
        """
        # Filter by priority
        if priority != 'all':
            recommendations = [
                r for r in recommendations
                if r.get('priority', '').lower() == priority
            ]
        
        # Sort by priority
        priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        recommendations.sort(
            key=lambda r: priority_order.get(r.get('priority', 'LOW'), 4)
        )
        
        report = f"""
RECOMMENDATION REPORT
=====================

Total Recommendations: {len(recommendations)}
Filtered by Priority: {priority.upper()}

"""
        
        # Group by priority
        by_priority: Dict[str, List[Dict]] = {}
        for rec in recommendations:
            p = rec.get('priority', 'UNKNOWN')
            if p not in by_priority:
                by_priority[p] = []
            by_priority[p].append(rec)
        
        # Add recommendations by priority
        for priority_level in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            if priority_level in by_priority:
                report += f"\n{priority_level} PRIORITY:\n"
                report += "-" * (len(priority_level) + 10) + "\n\n"
                
                for i, rec in enumerate(by_priority[priority_level], 1):
                    report += f"{i}. {rec.get('title', 'Untitled')}\n"
                    report += f"   {rec.get('description', 'No description')}\n\n"
        
        report += f"\nReport Generated: {datetime.now().isoformat()}\n"
        
        return report
    
    def export_to_pdf(self, report_content: str, output_path: Path) -> bool:
        """
        Export report to PDF format.
        
        Args:
            report_content: Report content
            output_path: Output PDF path
            
        Returns:
            True if successful
        """
        # Placeholder for PDF export
        # In real implementation, would use library like reportlab or weasyprint
        try:
            # For now, save as HTML with PDF extension indicator
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Executive Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        pre {{ white-space: pre-wrap; font-family: monospace; }}
    </style>
</head>
<body>
    <pre>{report_content}</pre>
</body>
</html>
"""
            
            output_path.write_text(html_content, encoding='utf-8')
            return True
        except Exception:
            return False
    
    def _generate_recommendations(
        self,
        progress_percentage: float,
        risk_level: str,
        cost_data: Dict
    ) -> List[str]:
        """Generate key recommendations."""
        recommendations = []
        
        # Progress-based recommendations
        if progress_percentage < 25:
            recommendations.append("Continue with pilot migration to validate approach")
            recommendations.append("Set up comprehensive monitoring before scaling")
        elif progress_percentage < 50:
            recommendations.append("Review progress and adjust timeline if needed")
            recommendations.append("Ensure rollback capabilities are tested")
        elif progress_percentage < 75:
            recommendations.append("Focus on completing core functionality migration")
            recommendations.append("Begin planning for production deployment")
        else:
            recommendations.append("Prepare for production deployment")
            recommendations.append("Conduct final testing and validation")
        
        # Risk-based recommendations
        if risk_level == 'HIGH' or risk_level == 'CRITICAL':
            recommendations.append("Implement additional risk mitigation strategies")
            recommendations.append("Consider phased rollout approach")
        
        # Cost-based recommendations
        if cost_data.get('over_budget', False):
            recommendations.append("Review budget and identify cost optimization opportunities")
        
        return recommendations
    
    def _determine_status(self, progress_percentage: float, risk_level: str) -> str:
        """Determine overall project status."""
        if risk_level == 'CRITICAL':
            return 'AT_RISK'
        elif progress_percentage >= 100:
            return 'COMPLETED'
        elif progress_percentage >= 75:
            return 'NEAR_COMPLETION'
        elif progress_percentage >= 50:
            return 'IN_PROGRESS'
        elif progress_percentage >= 25:
            return 'UNDERWAY'
        else:
            return 'STARTED'
    
    def _identify_milestones(self, progress_data: Dict) -> List[str]:
        """Identify achieved milestones."""
        milestones = []
        
        progress_percentage = progress_data.get('progress_percentage', 0)
        
        if progress_percentage >= 10:
            milestones.append("Project kickoff completed")
        if progress_percentage >= 25:
            milestones.append("First migration wave completed")
        if progress_percentage >= 50:
            milestones.append("Halfway point reached")
        if progress_percentage >= 75:
            milestones.append("Three-quarters completion")
        if progress_percentage >= 100:
            milestones.append("Migration completed")
        
        return milestones
    
    def _generate_next_steps(self, progress_percentage: float, risk_level: str) -> List[str]:
        """Generate next steps."""
        steps = []
        
        if progress_percentage < 100:
            steps.append(f"Continue migration (currently at {progress_percentage:.1f}%)")
        
        if risk_level in ['HIGH', 'CRITICAL']:
            steps.append("Address high-priority risks")
        
        if progress_percentage >= 75:
            steps.append("Prepare production deployment plan")
        
        return steps
    
    def _generate_risk_recommendations(self, risk_data: Dict) -> str:
        """Generate risk-specific recommendations."""
        recommendations = []
        
        overall_risk = risk_data.get('overall_risk', 'MEDIUM')
        
        if overall_risk == 'CRITICAL':
            recommendations.append("Immediate executive attention required")
            recommendations.append("Consider project pause until risks are mitigated")
        elif overall_risk == 'HIGH':
            recommendations.append("Increase risk monitoring frequency")
            recommendations.append("Develop detailed contingency plans")
        elif overall_risk == 'MEDIUM':
            recommendations.append("Continue with planned risk mitigation")
        else:
            recommendations.append("Maintain current risk management approach")
        
        return "\n".join(f"• {rec}" for rec in recommendations)
    
    def _generate_json_dashboard(self, summary: ExecutiveSummary) -> str:
        """Generate JSON format dashboard."""
        data = {
            'executive_summary': {
                'project_name': summary.project_name,
                'migration_type': summary.migration_type,
                'overall_status': summary.overall_status,
                'progress': {
                    'total_files': summary.total_files,
                    'completed_files': summary.completed_files,
                    'percentage': summary.progress_percentage
                },
                'financials': {
                    'total_cost': summary.total_cost,
                    'expected_roi': summary.expected_roi
                },
                'risk': {
                    'level': summary.risk_level
                },
                'recommendations': summary.key_recommendations,
                'milestones': summary.milestones_achieved,
                'next_steps': summary.next_steps
            },
            'generated_at': datetime.now().isoformat()
        }
        
        return json.dumps(data, indent=2)
    
    def _generate_html_dashboard(self, summary: ExecutiveSummary) -> str:
        """Generate HTML format dashboard."""
        status_colors = {
            'COMPLETED': '#4CAF50',
            'NEAR_COMPLETION': '#8BC34A',
            'IN_PROGRESS': '#FFC107',
            'UNDERWAY': '#FF9800',
            'STARTED': '#03A9F4',
            'AT_RISK': '#F44336'
        }
        
        status_color = status_colors.get(summary.overall_status, '#9E9E9E')
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Executive Dashboard - {summary.project_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .header {{ background: {status_color}; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .card {{ background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .metric {{ font-size: 24px; font-weight: bold; color: #333; }}
        .label {{ color: #666; font-size: 14px; }}
        .progress-bar {{ width: 100%; height: 20px; background: #e0e0e0; border-radius: 10px; overflow: hidden; }}
        .progress-fill {{ height: 100%; background: {status_color}; width: {summary.progress_percentage}%; }}
        .recommendation {{ background: #e3f2fd; padding: 10px; margin: 5px 0; border-left: 4px solid #2196f3; }}
        .milestone {{ background: #e8f5e9; padding: 10px; margin: 5px 0; border-left: 4px solid #4caf50; }}
        .next-step {{ background: #fff3e0; padding: 10px; margin: 5px 0; border-left: 4px solid #ff9800; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{summary.project_name}</h1>
        <p>Migration Type: {summary.migration_type} | Status: {summary.overall_status}</p>
    </div>
    
    <div class="card">
        <h2>Progress Overview</h2>
        <div class="progress-bar">
            <div class="progress-fill"></div>
        </div>
        <p>{summary.progress_percentage:.1f}% Complete ({summary.completed_files}/{summary.total_files} files)</p>
    </div>
    
    <div class="card">
        <h2>Financial Summary</h2>
        <div style="display: flex; gap: 40px;">
            <div>
                <div class="metric">${summary.total_cost:,.0f}</div>
                <div class="label">Total Investment</div>
            </div>
            <div>
                <div class="metric">{summary.expected_roi:.1f}%</div>
                <div class="label">Expected ROI</div>
            </div>
            <div>
                <div class="metric">{summary.risk_level}</div>
                <div class="label">Risk Level</div>
            </div>
        </div>
    </div>
    
    <div class="card">
        <h2>Key Recommendations</h2>
        {''.join(f'<div class="recommendation">{rec}</div>' for rec in summary.key_recommendations)}
    </div>
    
    <div class="card">
        <h2>Milestones Achieved</h2>
        {''.join(f'<div class="milestone">{milestone}</div>' for milestone in summary.milestones_achieved)}
    </div>
    
    <div class="card">
        <h2>Next Steps</h2>
        {''.join(f'<div class="next-step">{step}</div>' for step in summary.next_steps)}
    </div>
    
    <p style="text-align: center; color: #999; margin-top: 40px;">
        Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </p>
</body>
</html>
"""
    
    def _generate_text_dashboard(self, summary: ExecutiveSummary) -> str:
        """Generate text format dashboard."""
        return f"""
EXECUTIVE DASHBOARD: {summary.project_name}
{'=' * (len(summary.project_name) + 22)}

PROJECT STATUS: {summary.overall_status}
MIGRATION TYPE: {summary.migration_type}
RISK LEVEL: {summary.risk_level}

PROGRESS:
---------
Files: {summary.completed_files}/{summary.total_files} ({summary.progress_percentage:.1f}%)

FINANCIALS:
-----------
Total Investment: ${summary.total_cost:,.2f}
Expected ROI: {summary.expected_roi:.1f}%

KEY RECOMMENDATIONS:
--------------------
{chr(10).join(f"• {rec}" for rec in summary.key_recommendations)}

MILESTONES ACHIEVED:
--------------------
{chr(10).join(f"✓ {milestone}" for milestone in summary.milestones_achieved)}

NEXT STEPS:
-----------
{chr(10).join(f"→ {step}" for step in summary.next_steps)}

Generated: {datetime.now().isoformat()}
"""
