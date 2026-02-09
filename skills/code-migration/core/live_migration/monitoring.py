"""
Live migration monitoring and alerting system.

Real-time monitoring of live migrations with:
- Performance metrics collection
- Alert generation
- Dashboard data provision
- Historical analysis
"""

import json
import statistics
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from ..security import SecurityAuditLogger


@dataclass
class MetricPoint:
    """Single metric data point."""
    timestamp: str
    metric_name: str
    value: float
    deployment_id: str
    tags: Dict


class LiveMigrationMonitor:
    """
    Real-time monitoring system for live migrations.
    
    Features:
    - Real-time metrics collection
    - Performance trend analysis
    - Alert generation
    - Historical data storage
    - Dashboard data provision
    """
    
    def __init__(self, project_path: Path):
        """
        Initialize live migration monitor.
        
        Args:
            project_path: Path to project directory
        """
        self.project_path = Path(project_path)
        self.metrics: List[MetricPoint] = []
        self.alerts: List[Dict] = []
        self.deployment_metrics: Dict[str, List[MetricPoint]] = {}
        
        log_dir = self.project_path / '.migration-logs'
        self.audit_logger = SecurityAuditLogger(log_dir)
        
        self.metrics_file = self.project_path / '.migration-metrics.json'
        self.alerts_file = self.project_path / '.migration-alerts.json'
        self._load_data()
    
    def record_metric(
        self,
        deployment_id: str,
        metric_name: str,
        value: float,
        tags: Optional[Dict] = None
    ) -> None:
        """
        Record a metric for a deployment.
        
        Args:
            deployment_id: Deployment ID
            metric_name: Name of the metric
            value: Metric value
            tags: Optional tags for categorization
        """
        metric = MetricPoint(
            timestamp=datetime.now().isoformat(),
            metric_name=metric_name,
            value=value,
            deployment_id=deployment_id,
            tags=tags or {}
        )
        
        self.metrics.append(metric)
        
        # Organize by deployment
        if deployment_id not in self.deployment_metrics:
            self.deployment_metrics[deployment_id] = []
        
        self.deployment_metrics[deployment_id].append(metric)
        
        # Keep only last 1000 metrics per deployment
        if len(self.deployment_metrics[deployment_id]) > 1000:
            self.deployment_metrics[deployment_id] = self.deployment_metrics[deployment_id][-1000:]
        
        # Check for alert conditions
        self._check_alert_conditions(deployment_id, metric_name, value, tags)
        
        self._save_data()
    
    def get_deployment_metrics(
        self,
        deployment_id: str,
        metric_name: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get metrics for a deployment.
        
        Args:
            deployment_id: Deployment ID
            metric_name: Optional metric name filter
            start_time: Optional start time filter
            end_time: Optional end time filter
            limit: Maximum number of metrics to return
            
        Returns:
            List of metric dictionaries
        """
        if deployment_id not in self.deployment_metrics:
            return []
        
        metrics = self.deployment_metrics[deployment_id]
        
        # Filter by metric name
        if metric_name:
            metrics = [m for m in metrics if m.metric_name == metric_name]
        
        # Filter by time range
        if start_time:
            metrics = [
                m for m in metrics
                if datetime.fromisoformat(m.timestamp) >= start_time
            ]
        
        if end_time:
            metrics = [
                m for m in metrics
                if datetime.fromisoformat(m.timestamp) <= end_time
            ]
        
        # Sort by timestamp (newest first) and limit
        metrics = sorted(
            metrics,
            key=lambda m: m.timestamp,
            reverse=True
        )[:limit]
        
        return [
            {
                'timestamp': m.timestamp,
                'metric_name': m.metric_name,
                'value': m.value,
                'tags': m.tags
            }
            for m in metrics
        ]
    
    def get_metric_statistics(
        self,
        deployment_id: str,
        metric_name: str,
        time_window_minutes: int = 60
    ) -> Dict:
        """
        Get statistics for a metric over a time window.
        
        Args:
            deployment_id: Deployment ID
            metric_name: Metric name
            time_window_minutes: Time window in minutes
            
        Returns:
            Dict with statistics
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=time_window_minutes)
        
        metrics = self.get_deployment_metrics(
            deployment_id=deployment_id,
            metric_name=metric_name,
            start_time=start_time,
            end_time=end_time
        )
        
        if not metrics:
            return {
                'metric_name': metric_name,
                'count': 0,
                'avg': 0,
                'min': 0,
                'max': 0,
                'median': 0,
                'std_dev': 0
            }
        
        values = [m['value'] for m in metrics]
        
        return {
            'metric_name': metric_name,
            'count': len(values),
            'avg': statistics.mean(values),
            'min': min(values),
            'max': max(values),
            'median': statistics.median(values),
            'std_dev': statistics.stdev(values) if len(values) > 1 else 0
        }
    
    def get_deployment_dashboard_data(self, deployment_id: str) -> Dict:
        """
        Get comprehensive dashboard data for a deployment.
        
        Args:
            deployment_id: Deployment ID
            
        Returns:
            Dict with dashboard data
        """
        # Get all metrics for deployment
        all_metrics = self.get_deployment_metrics(deployment_id, limit=1000)
        
        if not all_metrics:
            return {
                'deployment_id': deployment_id,
                'status': 'NO_DATA',
                'metrics': {},
                'alerts': [],
                'recommendations': []
            }
        
        # Get unique metric names
        metric_names = set(m['metric_name'] for m in all_metrics)
        
        # Calculate statistics for each metric
        metrics_stats = {}
        for metric_name in metric_names:
            metrics_stats[metric_name] = self.get_metric_statistics(
                deployment_id, metric_name, time_window_minutes=60
            )
        
        # Get recent alerts
        recent_alerts = [
            alert for alert in self.alerts
            if alert['deployment_id'] == deployment_id
        ][-10:]  # Last 10 alerts
        
        # Generate recommendations
        recommendations = self._generate_recommendations(deployment_id, metrics_stats)
        
        # Determine overall status
        status = self._determine_deployment_status(deployment_id, metrics_stats)
        
        return {
            'deployment_id': deployment_id,
            'status': status,
            'metrics': metrics_stats,
            'recent_alerts': recent_alerts,
            'recommendations': recommendations,
            'last_updated': datetime.now().isoformat()
        }
    
    def create_alert(
        self,
        deployment_id: str,
        alert_type: str,
        severity: str,
        message: str,
        metric_value: Optional[float] = None,
        threshold: Optional[float] = None
    ) -> str:
        """
        Create an alert for a deployment.
        
        Args:
            deployment_id: Deployment ID
            alert_type: Type of alert
            severity: Severity level (CRITICAL, HIGH, MEDIUM, LOW)
            message: Alert message
            metric_value: Optional metric value that triggered alert
            threshold: Optional threshold that was exceeded
            
        Returns:
            Alert ID
        """
        alert_id = f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        alert = {
            'alert_id': alert_id,
            'deployment_id': deployment_id,
            'alert_type': alert_type,
            'severity': severity,
            'message': message,
            'metric_value': metric_value,
            'threshold': threshold,
            'created_at': datetime.now().isoformat(),
            'acknowledged': False,
            'resolved': False
        }
        
        self.alerts.append(alert)
        
        # Log the alert
        self.audit_logger.log_migration_event(
            migration_type='live-migration',
            project_path=str(self.project_path),
            user='system',
            action='ALERT_CREATED',
            result='SUCCESS',
            details={
                'alert_id': alert_id,
                'deployment_id': deployment_id,
                'alert_type': alert_type,
                'severity': severity,
                'message': message
            }
        )
        
        self._save_data()
        return alert_id
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """
        Acknowledge an alert.
        
        Args:
            alert_id: Alert ID
            
        Returns:
            True if acknowledged successfully
        """
        for alert in self.alerts:
            if alert['alert_id'] == alert_id:
                alert['acknowledged'] = True
                alert['acknowledged_at'] = datetime.now().isoformat()
                self._save_data()
                return True
        
        return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """
        Resolve an alert.
        
        Args:
            alert_id: Alert ID
            
        Returns:
            True if resolved successfully
        """
        for alert in self.alerts:
            if alert['alert_id'] == alert_id:
                alert['resolved'] = True
                alert['resolved_at'] = datetime.now().isoformat()
                self._save_data()
                return True
        
        return False
    
    def get_alerts(
        self,
        deployment_id: Optional[str] = None,
        severity: Optional[str] = None,
        acknowledged: Optional[bool] = None,
        resolved: Optional[bool] = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        Get alerts with optional filters.
        
        Args:
            deployment_id: Optional deployment ID filter
            severity: Optional severity filter
            acknowledged: Optional acknowledged filter
            resolved: Optional resolved filter
            limit: Maximum number of alerts to return
            
        Returns:
            List of alert dictionaries
        """
        alerts = self.alerts
        
        # Apply filters
        if deployment_id:
            alerts = [a for a in alerts if a['deployment_id'] == deployment_id]
        
        if severity:
            alerts = [a for a in alerts if a['severity'] == severity]
        
        if acknowledged is not None:
            alerts = [a for a in alerts if a['acknowledged'] == acknowledged]
        
        if resolved is not None:
            alerts = [a for a in alerts if a['resolved'] == resolved]
        
        # Sort by created_at (newest first) and limit
        alerts = sorted(
            alerts,
            key=lambda a: a['created_at'],
            reverse=True
        )[:limit]
        
        return alerts
    
    def _check_alert_conditions(
        self,
        deployment_id: str,
        metric_name: str,
        value: float,
        tags: Optional[Dict]
    ) -> None:
        """Check if alert conditions are met."""
        # Check for high error rate
        if metric_name == 'error_rate' and value > 0.05:  # 5% error rate
            self.create_alert(
                deployment_id=deployment_id,
                alert_type='high_error_rate',
                severity='HIGH' if value > 0.1 else 'MEDIUM',
                message=f'Error rate is {value:.2%}, exceeding threshold of 5%',
                metric_value=value,
                threshold=0.05
            )
        
        # Check for high response time
        if metric_name == 'response_time' and value > 2000:  # 2 seconds
            self.create_alert(
                deployment_id=deployment_id,
                alert_type='high_response_time',
                severity='HIGH' if value > 5000 else 'MEDIUM',
                message=f'Response time is {value:.0f}ms, exceeding threshold of 2000ms',
                metric_value=value,
                threshold=2000
            )
        
        # Check for low health score
        if metric_name == 'health_score' and value < 0.95:  # 95% health
            self.create_alert(
                deployment_id=deployment_id,
                alert_type='low_health_score',
                severity='HIGH' if value < 0.8 else 'MEDIUM',
                message=f'Health score is {value:.2%}, below threshold of 95%',
                metric_value=value,
                threshold=0.95
            )
    
    def _generate_recommendations(
        self,
        deployment_id: str,
        metrics_stats: Dict
    ) -> List[str]:
        """Generate recommendations based on metrics."""
        recommendations = []
        
        # Check error rate
        if 'error_rate' in metrics_stats:
            error_stats = metrics_stats['error_rate']
            if error_stats['avg'] > 0.05:
                recommendations.append(
                    f"High error rate detected ({error_stats['avg']:.2%}). "
                    "Consider investigating and rolling back if necessary."
                )
        
        # Check response time
        if 'response_time' in metrics_stats:
            response_stats = metrics_stats['response_time']
            if response_stats['avg'] > 1000:
                recommendations.append(
                    f"Response time is elevated ({response_stats['avg']:.0f}ms). "
                    "Consider performance optimization."
                )
        
        # Check health score
        if 'health_score' in metrics_stats:
            health_stats = metrics_stats['health_score']
            if health_stats['avg'] < 0.95:
                recommendations.append(
                    f"Health score is below optimal ({health_stats['avg']:.2%}). "
                    "Investigate health checks and service stability."
                )
        
        return recommendations
    
    def _determine_deployment_status(
        self,
        deployment_id: str,
        metrics_stats: Dict
    ) -> str:
        """Determine overall deployment status."""
        # Check for critical conditions
        if 'error_rate' in metrics_stats:
            if metrics_stats['error_rate']['avg'] > 0.1:  # 10% error rate
                return 'CRITICAL'
        
        if 'health_score' in metrics_stats:
            if metrics_stats['health_score']['avg'] < 0.8:  # 80% health
                return 'CRITICAL'
        
        # Check for warning conditions
        if 'error_rate' in metrics_stats:
            if metrics_stats['error_rate']['avg'] > 0.05:  # 5% error rate
                return 'WARNING'
        
        if 'response_time' in metrics_stats:
            if metrics_stats['response_time']['avg'] > 2000:  # 2 seconds
                return 'WARNING'
        
        # Check for degraded conditions
        if 'health_score' in metrics_stats:
            if metrics_stats['health_score']['avg'] < 0.95:  # 95% health
                return 'DEGRADED'
        
        return 'HEALTHY'
    
    def _load_data(self) -> None:
        """Load metrics and alerts from files."""
        # Load metrics
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r') as f:
                    data = json.load(f)
                    for metric_data in data.get('metrics', []):
                        metric = MetricPoint(**metric_data)
                        self.metrics.append(metric)
                        
                        # Organize by deployment
                        if metric.deployment_id not in self.deployment_metrics:
                            self.deployment_metrics[metric.deployment_id] = []
                        
                        self.deployment_metrics[metric.deployment_id].append(metric)
            except Exception:
                pass
        
        # Load alerts
        if self.alerts_file.exists():
            try:
                with open(self.alerts_file, 'r') as f:
                    data = json.load(f)
                    self.alerts = data.get('alerts', [])
            except Exception:
                pass
    
    def _save_data(self) -> None:
        """Save metrics and alerts to files."""
        try:
            # Save metrics (keep only last 5000)
            recent_metrics = self.metrics[-5000:] if len(self.metrics) > 5000 else self.metrics
            
            metrics_data = {
                'metrics': [
                    {
                        'timestamp': m.timestamp,
                        'metric_name': m.metric_name,
                        'value': m.value,
                        'deployment_id': m.deployment_id,
                        'tags': m.tags
                    }
                    for m in recent_metrics
                ]
            }
            
            with open(self.metrics_file, 'w') as f:
                json.dump(metrics_data, f, indent=2)
            
            # Save alerts (keep only last 1000)
            recent_alerts = self.alerts[-1000:] if len(self.alerts) > 1000 else self.alerts
            
            alerts_data = {'alerts': recent_alerts}
            
            with open(self.alerts_file, 'w') as f:
                json.dump(alerts_data, f, indent=2)
        
        except Exception:
            pass
