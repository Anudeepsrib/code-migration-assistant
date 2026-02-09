"""
Auto-rollback system for automatic failure recovery.

Monitors deployments and automatically rolls back when:
- Health checks fail
- Error rates exceed thresholds
- Performance degrades
- Manual triggers
"""

import json
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional

from ..security import SecurityAuditLogger


@dataclass
class RollbackTrigger:
    """Rollback trigger configuration."""
    trigger_id: str
    deployment_id: str
    trigger_type: str
    threshold: float
    current_value: float
    triggered: bool
    created_at: str
    triggered_at: Optional[str] = None


class AutoRollbackManager:
    """
    Automatic rollback system for deployment failures.
    
    Features:
    - Health-based auto-rollback
    - Error rate monitoring
    - Performance degradation detection
    - Configurable thresholds
    - Graceful degradation
    """
    
    def __init__(self, project_path: Path, live_migration_manager=None):
        """
        Initialize auto-rollback manager.
        
        Args:
            project_path: Path to project directory
            live_migration_manager: LiveMigrationManager instance
        """
        self.project_path = Path(project_path)
        self.live_migration = live_migration_manager
        self.triggers: Dict[str, RollbackTrigger] = {}
        self.monitoring_threads: Dict[str, threading.Thread] = {}
        self.stop_monitoring: Dict[str, bool] = {}
        self.rollback_callbacks: List[Callable] = []
        
        log_dir = self.project_path / '.migration-logs'
        self.audit_logger = SecurityAuditLogger(log_dir)
        
        self.triggers_file = self.project_path / '.migration-triggers.json'
        self._load_triggers()
    
    def setup_auto_rollback(
        self,
        deployment_id: str,
        health_threshold: float = 0.95,
        error_threshold: float = 0.05,
        response_time_threshold: float = 2000.0,
        check_interval: int = 30
    ) -> bool:
        """
        Setup automatic rollback for a deployment.
        
        Args:
            deployment_id: Deployment ID to monitor
            health_threshold: Minimum health score (0-1)
            error_threshold: Maximum error rate (0-1)
            response_time_threshold: Maximum response time in ms
            check_interval: Health check interval in seconds
            
        Returns:
            True if setup successful
        """
        # Create triggers
        triggers = [
            RollbackTrigger(
                trigger_id=f"{deployment_id}_health",
                deployment_id=deployment_id,
                trigger_type='health',
                threshold=health_threshold,
                current_value=1.0,
                triggered=False,
                created_at=datetime.now().isoformat()
            ),
            RollbackTrigger(
                trigger_id=f"{deployment_id}_error",
                deployment_id=deployment_id,
                trigger_type='error_rate',
                threshold=error_threshold,
                current_value=0.0,
                triggered=False,
                created_at=datetime.now().isoformat()
            ),
            RollbackTrigger(
                trigger_id=f"{deployment_id}_response_time",
                deployment_id=deployment_id,
                trigger_type='response_time',
                threshold=response_time_threshold,
                current_value=0.0,
                triggered=False,
                created_at=datetime.now().isoformat()
            )
        ]
        
        # Store triggers
        for trigger in triggers:
            self.triggers[trigger.trigger_id] = trigger
        
        # Start monitoring thread
        self.stop_monitoring[deployment_id] = False
        monitoring_thread = threading.Thread(
            target=self._monitor_deployment,
            args=(deployment_id, check_interval),
            daemon=True
        )
        monitoring_thread.start()
        self.monitoring_threads[deployment_id] = monitoring_thread
        
        self.audit_logger.log_migration_event(
            migration_type='auto-rollback',
            project_path=str(self.project_path),
            user='system',
            action='SETUP_AUTO_ROLLBACK',
            result='SUCCESS',
            details={
                'deployment_id': deployment_id,
                'health_threshold': health_threshold,
                'error_threshold': error_threshold,
                'response_time_threshold': response_time_threshold,
                'check_interval': check_interval
            }
        )
        
        self._save_triggers()
        return True
    
    def update_metric(self, deployment_id: str, metric_type: str, value: float) -> None:
        """
        Update a metric for monitoring.
        
        Args:
            deployment_id: Deployment ID
            metric_type: Type of metric (health, error_rate, response_time)
            value: Metric value
        """
        trigger_id = f"{deployment_id}_{metric_type}"
        
        if trigger_id in self.triggers:
            trigger = self.triggers[trigger_id]
            trigger.current_value = value
            
            # Check if threshold exceeded
            if metric_type == 'health':
                # Health: value should be >= threshold
                if value < trigger.threshold and not trigger.triggered:
                    self._trigger_rollback(trigger_id, f"Health dropped to {value}")
            elif metric_type == 'error_rate':
                # Error rate: value should be <= threshold
                if value > trigger.threshold and not trigger.triggered:
                    self._trigger_rollback(trigger_id, f"Error rate increased to {value}")
            elif metric_type == 'response_time':
                # Response time: value should be <= threshold
                if value > trigger.threshold and not trigger.triggered:
                    self._trigger_rollback(trigger_id, f"Response time increased to {value}ms")
            
            self._save_triggers()
    
    def manual_trigger_rollback(self, deployment_id: str, reason: str = '') -> bool:
        """
        Manually trigger rollback for a deployment.
        
        Args:
            deployment_id: Deployment ID
            reason: Reason for manual rollback
            
        Returns:
            True if rollback triggered successfully
        """
        trigger_id = f"{deployment_id}_manual"
        
        # Create manual trigger
        trigger = RollbackTrigger(
            trigger_id=trigger_id,
            deployment_id=deployment_id,
            trigger_type='manual',
            threshold=1.0,
            current_value=1.0,
            triggered=True,
            created_at=datetime.now().isoformat(),
            triggered_at=datetime.now().isoformat()
        )
        
        self.triggers[trigger_id] = trigger
        
        return self._execute_rollback(trigger_id, reason)
    
    def stop_monitoring_deployment(self, deployment_id: str) -> bool:
        """
        Stop monitoring a deployment.
        
        Args:
            deployment_id: Deployment ID
            
        Returns:
            True if stopped successfully
        """
        if deployment_id in self.monitoring_threads:
            self.stop_monitoring[deployment_id] = True
            
            # Wait for thread to stop
            self.monitoring_threads[deployment_id].join(timeout=5)
            
            del self.monitoring_threads[deployment_id]
            del self.stop_monitoring[deployment_id]
            
            # Remove triggers
            triggers_to_remove = [
                tid for tid in self.triggers.keys()
                if tid.startswith(f"{deployment_id}_")
            ]
            
            for tid in triggers_to_remove:
                del self.triggers[tid]
            
            self._save_triggers()
            return True
        
        return False
    
    def get_trigger_status(self, deployment_id: str) -> List[Dict]:
        """
        Get status of all triggers for a deployment.
        
        Args:
            deployment_id: Deployment ID
            
        Returns:
            List of trigger status dicts
        """
        triggers = [
            trigger for trigger in self.triggers.values()
            if trigger.deployment_id == deployment_id
        ]
        
        return [
            {
                'trigger_id': t.trigger_id,
                'trigger_type': t.trigger_type,
                'threshold': t.threshold,
                'current_value': t.current_value,
                'triggered': t.triggered,
                'created_at': t.created_at,
                'triggered_at': t.triggered_at
            }
            for t in triggers
        ]
    
    def register_rollback_callback(self, callback: Callable) -> None:
        """
        Register a callback to be called when rollback occurs.
        
        Args:
            callback: Function to call on rollback
        """
        self.rollback_callbacks.append(callback)
    
    def _monitor_deployment(self, deployment_id: str, check_interval: int) -> None:
        """Monitor deployment health in background thread."""
        while not self.stop_monitoring.get(deployment_id, False):
            # Check if any triggers are exceeded
            triggers = [
                t for t in self.triggers.values()
                if t.deployment_id == deployment_id and not t.triggered
            ]
            
            for trigger in triggers:
                if self._check_trigger_exceeded(trigger):
                    self._trigger_rollback(
                        trigger.trigger_id,
                        f"Threshold exceeded: {trigger.trigger_type}"
                    )
            
            # Sleep before next check
            time.sleep(check_interval)
    
    def _check_trigger_exceeded(self, trigger: RollbackTrigger) -> bool:
        """Check if trigger threshold is exceeded."""
        if trigger.trigger_type == 'health':
            return trigger.current_value < trigger.threshold
        elif trigger.trigger_type in ['error_rate', 'response_time']:
            return trigger.current_value > trigger.threshold
        return False
    
    def _trigger_rollback(self, trigger_id: str, reason: str) -> bool:
        """Trigger rollback for a specific trigger."""
        if trigger_id not in self.triggers:
            return False
        
        trigger = self.triggers[trigger_id]
        
        if trigger.triggered:
            return False
        
        trigger.triggered = True
        trigger.triggered_at = datetime.now().isoformat()
        
        return self._execute_rollback(trigger_id, reason)
    
    def _execute_rollback(self, trigger_id: str, reason: str) -> bool:
        """Execute rollback for a trigger."""
        trigger = self.triggers[trigger_id]
        deployment_id = trigger.deployment_id
        
        self.audit_logger.log_migration_event(
            migration_type='auto-rollback',
            project_path=str(self.project_path),
            user='system',
            action='AUTO_ROLLBACK_TRIGGERED',
            result='STARTED',
            details={
                'deployment_id': deployment_id,
                'trigger_id': trigger_id,
                'trigger_type': trigger.trigger_type,
                'reason': reason,
                'threshold': trigger.threshold,
                'current_value': trigger.current_value
            }
        )
        
        # Execute rollback through live migration manager
        if self.live_migration:
            success = self.live_migration.rollback_deployment(deployment_id, reason)
        else:
            # Fallback: just log the rollback
            success = True
        
        # Stop monitoring
        self.stop_monitoring_deployment(deployment_id)
        
        # Call registered callbacks
        for callback in self.rollback_callbacks:
            try:
                callback(deployment_id, trigger_id, reason, success)
            except Exception:
                pass
        
        self.audit_logger.log_migration_event(
            migration_type='auto-rollback',
            project_path=str(self.project_path),
            user='system',
            action='AUTO_ROLLBACK_EXECUTED',
            result='SUCCESS' if success else 'FAILURE',
            details={
                'deployment_id': deployment_id,
                'trigger_id': trigger_id,
                'success': success
            }
        )
        
        self._save_triggers()
        return success
    
    def _load_triggers(self) -> None:
        """Load triggers from file."""
        if self.triggers_file.exists():
            try:
                with open(self.triggers_file, 'r') as f:
                    data = json.load(f)
                    for trigger_data in data.get('triggers', []):
                        trigger = RollbackTrigger(**trigger_data)
                        self.triggers[trigger.trigger_id] = trigger
            except Exception:
                pass
    
    def _save_triggers(self) -> None:
        """Save triggers to file."""
        try:
            data = {
                'triggers': [
                    {
                        'trigger_id': t.trigger_id,
                        'deployment_id': t.deployment_id,
                        'trigger_type': t.trigger_type,
                        'threshold': t.threshold,
                        'current_value': t.current_value,
                        'triggered': t.triggered,
                        'created_at': t.created_at,
                        'triggered_at': t.triggered_at
                    }
                    for t in self.triggers.values()
                ]
            }
            
            with open(self.triggers_file, 'w') as f:
                json.dump(data, f, indent=2)
        
        except Exception:
            pass
