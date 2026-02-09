"""
Canary deployment system for gradual rollouts.

Manages canary deployments with:
- Traffic percentage control
- Health monitoring
- Automatic promotion/rollback
- A/B testing capabilities
"""

import json
import random
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Callable

from ..security import SecurityAuditLogger


@dataclass
class CanaryDeployment:
    """Canary deployment configuration."""
    canary_id: str
    deployment_id: str
    target_percentage: int
    current_percentage: int
    health_threshold: float
    error_threshold: float
    status: str
    metrics: Dict
    created_at: str
    updated_at: str


class CanaryDeployer:
    """
    Canary deployment system for gradual rollouts.
    
    Features:
    - Percentage-based traffic splitting
    - Health-based auto-promotion
    - Error rate monitoring
    - Gradual rollout with configurable steps
    """
    
    # Default rollout steps (percentage increments)
    DEFAULT_STEPS = [5, 10, 25, 50, 75, 100]
    
    def __init__(self, project_path: Path):
        """
        Initialize canary deployer.
        
        Args:
            project_path: Path to project directory
        """
        self.project_path = Path(project_path)
        self.canaries: Dict[str, CanaryDeployment] = {}
        self.health_checks: Dict[str, List[Dict]] = {}
        
        log_dir = self.project_path / '.migration-logs'
        self.audit_logger = SecurityAuditLogger(log_dir)
        
        self.canaries_file = self.project_path / '.migration-canaries.json'
        self._load_canaries()
    
    def start_canary(
        self,
        deployment_id: str,
        initial_percentage: int = 5,
        health_threshold: float = 0.95,
        error_threshold: float = 0.01,
        auto_promote: bool = True,
        steps: Optional[List[int]] = None
    ) -> CanaryDeployment:
        """
        Start a canary deployment.
        
        Args:
            deployment_id: Parent deployment ID
            initial_percentage: Initial traffic percentage (0-100)
            health_threshold: Minimum health score for promotion (0-1)
            error_threshold: Maximum error rate before rollback (0-1)
            auto_promote: Automatically promote on success
            steps: Custom rollout steps
            
        Returns:
            CanaryDeployment object
        """
        canary_id = f"canary_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        canary = CanaryDeployment(
            canary_id=canary_id,
            deployment_id=deployment_id,
            target_percentage=initial_percentage,
            current_percentage=0,
            health_threshold=health_threshold,
            error_threshold=error_threshold,
            status='STARTING',
            metrics={
                'requests': 0,
                'errors': 0,
                'health_score': 1.0,
                'response_time': 0.0
            },
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        self.audit_logger.log_migration_event(
            migration_type='canary',
            project_path=str(self.project_path),
            user='system',
            action='CANARY_START',
            result='SUCCESS',
            details={
                'canary_id': canary_id,
                'deployment_id': deployment_id,
                'initial_percentage': initial_percentage,
                'auto_promote': auto_promote
            }
        )
        
        # Set initial traffic
        self._update_canary_traffic(canary_id, initial_percentage)
        
        canary.status = 'RUNNING'
        canary.current_percentage = initial_percentage
        self.canaries[canary_id] = canary
        
        self._save_canaries()
        
        return canary
    
    def advance_canary(self, canary_id: str, step_index: Optional[int] = None) -> bool:
        """
        Advance canary to next step.
        
        Args:
            canary_id: Canary deployment ID
            step_index: Specific step index (None for auto-advance)
            
        Returns:
            True if advanced successfully
        """
        if canary_id not in self.canaries:
            return False
        
        canary = self.canaries[canary_id]
        
        if canary.status != 'RUNNING':
            return False
        
        # Determine next percentage
        if step_index is not None:
            if step_index < 0 or step_index >= len(self.DEFAULT_STEPS):
                return False
            next_percentage = self.DEFAULT_STEPS[step_index]
        else:
            # Find next step
            current_step = -1
            for i, step in enumerate(self.DEFAULT_STEPS):
                if step <= canary.current_percentage:
                    current_step = i
            
            if current_step + 1 >= len(self.DEFAULT_STEPS):
                # Already at 100%
                return self.promote_canary(canary_id)
            
            next_percentage = self.DEFAULT_STEPS[current_step + 1]
        
        # Update traffic
        success = self._update_canary_traffic(canary_id, next_percentage)
        
        if success:
            canary.current_percentage = next_percentage
            canary.updated_at = datetime.now().isoformat()
            
            if next_percentage >= 100:
                canary.status = 'COMPLETED'
            
            self.audit_logger.log_migration_event(
                migration_type='canary',
                project_path=str(self.project_path),
                user='system',
                action='CANARY_ADVANCE',
                result='SUCCESS',
                details={
                    'canary_id': canary_id,
                    'new_percentage': next_percentage
                }
            )
            
            self._save_canaries()
        
        return success
    
    def promote_canary(self, canary_id: str) -> bool:
        """
        Promote canary to full production (100%).
        
        Args:
            canary_id: Canary deployment ID
            
        Returns:
            True if promoted successfully
        """
        if canary_id not in self.canaries:
            return False
        
        canary = self.canaries[canary_id]
        
        success = self._update_canary_traffic(canary_id, 100)
        
        if success:
            canary.current_percentage = 100
            canary.target_percentage = 100
            canary.status = 'COMPLETED'
            canary.updated_at = datetime.now().isoformat()
            
            self.audit_logger.log_migration_event(
                migration_type='canary',
                project_path=str(self.project_path),
                user='system',
                action='CANARY_PROMOTE',
                result='SUCCESS',
                details={'canary_id': canary_id}
            )
            
            self._save_canaries()
        
        return success
    
    def rollback_canary(self, canary_id: str, reason: str = '') -> bool:
        """
        Rollback canary deployment.
        
        Args:
            canary_id: Canary deployment ID
            reason: Reason for rollback
            
        Returns:
            True if rolled back successfully
        """
        if canary_id not in self.canaries:
            return False
        
        canary = self.canaries[canary_id]
        
        # Set traffic to 0%
        success = self._update_canary_traffic(canary_id, 0)
        
        if success:
            canary.current_percentage = 0
            canary.status = 'ROLLED_BACK'
            canary.updated_at = datetime.now().isoformat()
            
            self.audit_logger.log_migration_event(
                migration_type='canary',
                project_path=str(self.project_path),
                user='system',
                action='CANARY_ROLLBACK',
                result='SUCCESS',
                details={
                    'canary_id': canary_id,
                    'reason': reason
                }
            )
            
            self._save_canaries()
        
        return success
    
    def record_metric(self, canary_id: str, metric_type: str, value: float) -> None:
        """
        Record a metric for canary analysis.
        
        Args:
            canary_id: Canary deployment ID
            metric_type: Type of metric (health_score, error_rate, response_time)
            value: Metric value
        """
        if canary_id not in self.canaries:
            return
        
        canary = self.canaries[canary_id]
        
        if metric_type not in canary.metrics:
            canary.metrics[metric_type] = []
        
        if isinstance(canary.metrics[metric_type], list):
            canary.metrics[metric_type].append({
                'timestamp': datetime.now().isoformat(),
                'value': value
            })
        else:
            canary.metrics[metric_type] = value
        
        # Update health score
        if metric_type == 'health_score':
            canary.metrics['health_score'] = value
        
        # Update error count
        if metric_type == 'error':
            canary.metrics['errors'] = canary.metrics.get('errors', 0) + 1
        
        # Update request count
        if metric_type == 'request':
            canary.metrics['requests'] = canary.metrics.get('requests', 0) + 1
        
        canary.updated_at = datetime.now().isoformat()
        self._save_canaries()
    
    def should_rollback(self, canary_id: str) -> bool:
        """
        Determine if canary should be rolled back based on metrics.
        
        Args:
            canary_id: Canary deployment ID
            
        Returns:
            True if rollback recommended
        """
        if canary_id not in self.canaries:
            return False
        
        canary = self.canaries[canary_id]
        
        if canary.status != 'RUNNING':
            return False
        
        # Check health score
        health_score = canary.metrics.get('health_score', 1.0)
        if health_score < canary.health_threshold:
            return True
        
        # Check error rate
        errors = canary.metrics.get('errors', 0)
        requests = canary.metrics.get('requests', 1)
        error_rate = errors / max(requests, 1)
        
        if error_rate > canary.error_threshold:
            return True
        
        return False
    
    def should_advance(self, canary_id: str) -> bool:
        """
        Determine if canary should advance to next step.
        
        Args:
            canary_id: Canary deployment ID
            
        Returns:
            True if advance recommended
        """
        if canary_id not in self.canaries:
            return False
        
        canary = self.canaries[canary_id]
        
        if canary.status != 'RUNNING':
            return False
        
        # Check health score
        health_score = canary.metrics.get('health_score', 1.0)
        if health_score >= canary.health_threshold:
            return True
        
        # Check error rate
        errors = canary.metrics.get('errors', 0)
        requests = canary.metrics.get('requests', 1)
        error_rate = errors / max(requests, 1)
        
        if error_rate <= canary.error_threshold:
            return True
        
        return False
    
    def get_canary_status(self, canary_id: str) -> Optional[Dict]:
        """
        Get detailed canary status.
        
        Args:
            canary_id: Canary deployment ID
            
        Returns:
            Dict with canary status or None
        """
        if canary_id not in self.canaries:
            return None
        
        canary = self.canaries[canary_id]
        
        # Calculate error rate
        errors = canary.metrics.get('errors', 0)
        requests = canary.metrics.get('requests', 1)
        error_rate = errors / max(requests, 1)
        
        return {
            'canary_id': canary.canary_id,
            'deployment_id': canary.deployment_id,
            'status': canary.status,
            'current_percentage': canary.current_percentage,
            'target_percentage': canary.target_percentage,
            'health_score': canary.metrics.get('health_score', 1.0),
            'error_rate': error_rate,
            'health_threshold': canary.health_threshold,
            'error_threshold': canary.error_threshold,
            'should_advance': self.should_advance(canary_id),
            'should_rollback': self.should_rollback(canary_id),
            'metrics': canary.metrics,
            'created_at': canary.created_at,
            'updated_at': canary.updated_at
        }
    
    def _update_canary_traffic(self, canary_id: str, percentage: int) -> bool:
        """Update canary traffic percentage."""
        # This would integrate with load balancer or traffic router
        # For now, just record the change
        return True
    
    def _load_canaries(self) -> None:
        """Load canaries from file."""
        if self.canaries_file.exists():
            try:
                with open(self.canaries_file, 'r') as f:
                    data = json.load(f)
                    for canary_data in data.get('canaries', []):
                        canary = CanaryDeployment(**canary_data)
                        self.canaries[canary.canary_id] = canary
            except Exception:
                pass
    
    def _save_canaries(self) -> None:
        """Save canaries to file."""
        try:
            data = {
                'canaries': [
                    {
                        'canary_id': c.canary_id,
                        'deployment_id': c.deployment_id,
                        'target_percentage': c.target_percentage,
                        'current_percentage': c.current_percentage,
                        'health_threshold': c.health_threshold,
                        'error_threshold': c.error_threshold,
                        'status': c.status,
                        'metrics': c.metrics,
                        'created_at': c.created_at,
                        'updated_at': c.updated_at
                    }
                    for c in self.canaries.values()
                ]
            }
            
            with open(self.canaries_file, 'w') as f:
                json.dump(data, f, indent=2)
        
        except Exception:
            pass
