"""
Health checking system for deployment monitoring.

Performs health checks on deployments:
- HTTP endpoint monitoring
- Response time tracking
- Error rate monitoring
- Custom health check functions
- Alerting on failures
"""

import json
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional

import requests

from ..security import SecurityAuditLogger


@dataclass
class HealthCheck:
    """Health check configuration."""
    check_id: str
    deployment_id: str
    check_type: str
    target_url: Optional[str]
    check_function: Optional[str]
    interval: int
    timeout: int
    healthy_threshold: int
    unhealthy_threshold: int
    status: str
    consecutive_failures: int
    consecutive_successes: int
    last_check: Optional[str]
    created_at: str


class HealthChecker:
    """
    Health checking system for deployment monitoring.
    
    Features:
    - HTTP endpoint monitoring
    - Response time tracking
    - Custom health check functions
    - Alerting on status changes
    - Health score calculation
    """
    
    def __init__(self, project_path: Path):
        """
        Initialize health checker.
        
        Args:
            project_path: Path to project directory
        """
        self.project_path = Path(project_path)
        self.health_checks: Dict[str, HealthCheck] = {}
        self.monitoring_threads: Dict[str, threading.Thread] = {}
        self.stop_monitoring: Dict[str, bool] = {}
        self.status_callbacks: List[Callable] = []
        self.check_results: Dict[str, List[Dict]] = {}
        
        log_dir = self.project_path / '.migration-logs'
        self.audit_logger = SecurityAuditLogger(log_dir)
        
        self.checks_file = self.project_path / '.migration-health-checks.json'
        self._load_health_checks()
    
    def add_http_health_check(
        self,
        deployment_id: str,
        url: str,
        method: str = 'GET',
        expected_status: int = 200,
        interval: int = 30,
        timeout: int = 10,
        healthy_threshold: int = 2,
        unhealthy_threshold: int = 3,
        headers: Optional[Dict] = None
    ) -> str:
        """
        Add HTTP health check.
        
        Args:
            deployment_id: Deployment ID
            url: URL to check
            method: HTTP method
            expected_status: Expected HTTP status code
            interval: Check interval in seconds
            timeout: Request timeout in seconds
            healthy_threshold: Consecutive successes to mark healthy
            unhealthy_threshold: Consecutive failures to mark unhealthy
            headers: Optional request headers
            
        Returns:
            Health check ID
        """
        check_id = f"health_{deployment_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        check = HealthCheck(
            check_id=check_id,
            deployment_id=deployment_id,
            check_type='http',
            target_url=url,
            check_function=json.dumps({
                'method': method,
                'expected_status': expected_status,
                'headers': headers or {}
            }),
            interval=interval,
            timeout=timeout,
            healthy_threshold=healthy_threshold,
            unhealthy_threshold=unhealthy_threshold,
            status='UNKNOWN',
            consecutive_failures=0,
            consecutive_successes=0,
            last_check=None,
            created_at=datetime.now().isoformat()
        )
        
        self.health_checks[check_id] = check
        
        # Start monitoring
        self.stop_monitoring[check_id] = False
        monitoring_thread = threading.Thread(
            target=self._run_health_check,
            args=(check_id,),
            daemon=True
        )
        monitoring_thread.start()
        self.monitoring_threads[check_id] = monitoring_thread
        
        self.audit_logger.log_migration_event(
            migration_type='health-check',
            project_path=str(self.project_path),
            user='system',
            action='ADD_HEALTH_CHECK',
            result='SUCCESS',
            details={
                'check_id': check_id,
                'deployment_id': deployment_id,
                'url': url,
                'interval': interval
            }
        )
        
        self._save_health_checks()
        return check_id
    
    def add_custom_health_check(
        self,
        deployment_id: str,
        check_function: Callable[[], bool],
        check_name: str,
        interval: int = 60,
        healthy_threshold: int = 2,
        unhealthy_threshold: int = 3
    ) -> str:
        """
        Add custom health check function.
        
        Args:
            deployment_id: Deployment ID
            check_function: Function that returns True if healthy
            check_name: Name of the check
            interval: Check interval in seconds
            healthy_threshold: Consecutive successes to mark healthy
            unhealthy_threshold: Consecutive failures to mark unhealthy
            
        Returns:
            Health check ID
        """
        check_id = f"health_custom_{deployment_id}_{check_name}"
        
        check = HealthCheck(
            check_id=check_id,
            deployment_id=deployment_id,
            check_type='custom',
            target_url=None,
            check_function=check_name,
            interval=interval,
            timeout=30,
            healthy_threshold=healthy_threshold,
            unhealthy_threshold=unhealthy_threshold,
            status='UNKNOWN',
            consecutive_failures=0,
            consecutive_successes=0,
            last_check=None,
            created_at=datetime.now().isoformat()
        )
        
        self.health_checks[check_id] = check
        
        # Store custom function
        self._custom_functions[check_id] = check_function
        
        # Start monitoring
        self.stop_monitoring[check_id] = False
        monitoring_thread = threading.Thread(
            target=self._run_custom_health_check,
            args=(check_id, check_function),
            daemon=True
        )
        monitoring_thread.start()
        self.monitoring_threads[check_id] = monitoring_thread
        
        self._save_health_checks()
        return check_id
    
    def remove_health_check(self, check_id: str) -> bool:
        """
        Remove a health check.
        
        Args:
            check_id: Health check ID
            
        Returns:
            True if removed successfully
        """
        if check_id not in self.health_checks:
            return False
        
        # Stop monitoring
        if check_id in self.monitoring_threads:
            self.stop_monitoring[check_id] = True
            self.monitoring_threads[check_id].join(timeout=5)
            del self.monitoring_threads[check_id]
            del self.stop_monitoring[check_id]
        
        # Remove from storage
        del self.health_checks[check_id]
        if check_id in self.check_results:
            del self.check_results[check_id]
        if check_id in self._custom_functions:
            del self._custom_functions[check_id]
        
        self._save_health_checks()
        return True
    
    def get_health_status(self, deployment_id: str) -> Dict:
        """
        Get health status for a deployment.
        
        Args:
            deployment_id: Deployment ID
            
        Returns:
            Dict with health status
        """
        deployment_checks = [
            check for check in self.health_checks.values()
            if check.deployment_id == deployment_id
        ]
        
        if not deployment_checks:
            return {
                'deployment_id': deployment_id,
                'overall_status': 'UNKNOWN',
                'health_score': 0.0,
                'checks': []
            }
        
        # Calculate overall health
        healthy_count = sum(1 for c in deployment_checks if c.status == 'HEALTHY')
        total_count = len(deployment_checks)
        health_score = healthy_count / total_count if total_count > 0 else 0.0
        
        # Determine overall status
        if all(c.status == 'HEALTHY' for c in deployment_checks):
            overall_status = 'HEALTHY'
        elif any(c.status == 'UNHEALTHY' for c in deployment_checks):
            overall_status = 'UNHEALTHY'
        elif any(c.status == 'DEGRADED' for c in deployment_checks):
            overall_status = 'DEGRADED'
        else:
            overall_status = 'UNKNOWN'
        
        return {
            'deployment_id': deployment_id,
            'overall_status': overall_status,
            'health_score': health_score,
            'total_checks': total_count,
            'healthy_checks': healthy_count,
            'unhealthy_checks': sum(1 for c in deployment_checks if c.status == 'UNHEALTHY'),
            'checks': [
                {
                    'check_id': c.check_id,
                    'check_type': c.check_type,
                    'status': c.status,
                    'target_url': c.target_url,
                    'last_check': c.last_check,
                    'consecutive_failures': c.consecutive_failures,
                    'consecutive_successes': c.consecutive_successes
                }
                for c in deployment_checks
            ]
        }
    
    def register_status_callback(self, callback: Callable) -> None:
        """
        Register callback for status changes.
        
        Args:
            callback: Function to call on status change
        """
        self.status_callbacks.append(callback)
    
    def _run_health_check(self, check_id: str) -> None:
        """Run HTTP health check in background."""
        check = self.health_checks[check_id]
        
        while not self.stop_monitoring.get(check_id, False):
            try:
                # Parse check function config
                config = json.loads(check.check_function) if check.check_function else {}
                method = config.get('method', 'GET')
                expected_status = config.get('expected_status', 200)
                headers = config.get('headers', {})
                
                # Make HTTP request
                start_time = time.time()
                
                if method == 'GET':
                    response = requests.get(
                        check.target_url,
                        headers=headers,
                        timeout=check.timeout
                    )
                elif method == 'POST':
                    response = requests.post(
                        check.target_url,
                        headers=headers,
                        timeout=check.timeout
                    )
                else:
                    response = requests.request(
                        method,
                        check.target_url,
                        headers=headers,
                        timeout=check.timeout
                    )
                
                response_time = (time.time() - start_time) * 1000  # ms
                
                # Check if successful
                success = response.status_code == expected_status
                
                # Record result
                self._record_check_result(check_id, success, response_time, response.status_code)
                
            except requests.RequestException:
                self._record_check_result(check_id, False, None, None)
            except Exception:
                self._record_check_result(check_id, False, None, None)
            
            # Sleep before next check
            time.sleep(check.interval)
    
    def _run_custom_health_check(self, check_id: str, check_function: Callable) -> None:
        """Run custom health check in background."""
        while not self.stop_monitoring.get(check_id, False):
            try:
                start_time = time.time()
                success = check_function()
                response_time = (time.time() - start_time) * 1000  # ms
                
                self._record_check_result(check_id, success, response_time, None)
                
            except Exception:
                self._record_check_result(check_id, False, None, None)
            
            # Sleep before next check
            check = self.health_checks[check_id]
            time.sleep(check.interval)
    
    def _record_check_result(
        self,
        check_id: str,
        success: bool,
        response_time: Optional[float],
        status_code: Optional[int]
    ) -> None:
        """Record health check result."""
        if check_id not in self.health_checks:
            return
        
        check = self.health_checks[check_id]
        check.last_check = datetime.now().isoformat()
        
        # Store result
        if check_id not in self.check_results:
            self.check_results[check_id] = []
        
        self.check_results[check_id].append({
            'timestamp': check.last_check,
            'success': success,
            'response_time': response_time,
            'status_code': status_code
        })
        
        # Keep only last 100 results
        self.check_results[check_id] = self.check_results[check_id][-100:]
        
        # Update consecutive counters
        if success:
            check.consecutive_successes += 1
            check.consecutive_failures = 0
        else:
            check.consecutive_failures += 1
            check.consecutive_successes = 0
        
        # Update status
        old_status = check.status
        
        if check.consecutive_successes >= check.healthy_threshold:
            check.status = 'HEALTHY'
        elif check.consecutive_failures >= check.unhealthy_threshold:
            check.status = 'UNHEALTHY'
        elif check.consecutive_successes > 0 or check.consecutive_failures > 0:
            check.status = 'DEGRADED'
        
        # Notify on status change
        if old_status != check.status:
            self._notify_status_change(check_id, old_status, check.status)
        
        self._save_health_checks()
    
    def _notify_status_change(self, check_id: str, old_status: str, new_status: str) -> None:
        """Notify callbacks of status change."""
        check = self.health_checks[check_id]
        
        for callback in self.status_callbacks:
            try:
                callback(check_id, check.deployment_id, old_status, new_status)
            except Exception:
                pass
    
    def _load_health_checks(self) -> None:
        """Load health checks from file."""
        self._custom_functions: Dict[str, Callable] = {}
        
        if self.checks_file.exists():
            try:
                with open(self.checks_file, 'r') as f:
                    data = json.load(f)
                    for check_data in data.get('health_checks', []):
                        check = HealthCheck(**check_data)
                        self.health_checks[check.check_id] = check
            except Exception:
                pass
    
    def _save_health_checks(self) -> None:
        """Save health checks to file."""
        try:
            data = {
                'health_checks': [
                    {
                        'check_id': c.check_id,
                        'deployment_id': c.deployment_id,
                        'check_type': c.check_type,
                        'target_url': c.target_url,
                        'check_function': c.check_function,
                        'interval': c.interval,
                        'timeout': c.timeout,
                        'healthy_threshold': c.healthy_threshold,
                        'unhealthy_threshold': c.unhealthy_threshold,
                        'status': c.status,
                        'consecutive_failures': c.consecutive_failures,
                        'consecutive_successes': c.consecutive_successes,
                        'last_check': c.last_check,
                        'created_at': c.created_at
                    }
                    for c in self.health_checks.values()
                ]
            }
            
            with open(self.checks_file, 'w') as f:
                json.dump(data, f, indent=2)
        
        except Exception:
            pass
