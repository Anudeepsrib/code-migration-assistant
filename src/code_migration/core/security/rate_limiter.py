"""
Rate limiting to prevent abuse and DoS attacks.

Limits:
- Max migrations per hour per user
- Max file operations per minute
- Max API calls (if using external APIs)

Algorithm: Token bucket with sliding window.
"""

import time
from collections import defaultdict
from threading import Lock
from typing import Dict, List


class RateLimiter:
    """
    Prevent abuse and DoS attacks.
    
    Limits:
    - Max migrations per hour per user
    - Max file operations per minute
    - Max API calls (if using external APIs)
    
    Algorithm: Token bucket with sliding window
    """
    
    def __init__(self, max_requests: int, time_window: int):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum allowed requests
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: Dict[str, List[float]] = defaultdict(list)
        self.lock = Lock()
    
    def is_allowed(self, user_id: str) -> bool:
        """
        Check if request is allowed.
        
        Args:
            user_id: Unique identifier for user/client
            
        Returns:
            bool: True if request is allowed
        """
        with self.lock:
            now = time.time()
            
            # Clean old requests outside time window
            self.requests[user_id] = [
                req_time for req_time in self.requests[user_id]
                if now - req_time < self.time_window
            ]
            
            # Check if under limit
            if len(self.requests[user_id]) < self.max_requests:
                self.requests[user_id].append(now)
                return True
            
            return False
    
    def get_retry_after(self, user_id: str) -> int:
        """
        Get seconds until next allowed request.
        
        Args:
            user_id: User identifier
            
        Returns:
            int: Seconds until next request is allowed
        """
        with self.lock:
            if not self.requests[user_id]:
                return 0
            
            oldest_request = min(self.requests[user_id])
            retry_after = int(self.time_window - (time.time() - oldest_request))
            return max(0, retry_after)
    
    def reset_user(self, user_id: str) -> None:
        """
        Reset rate limit for specific user.
        
        Args:
            user_id: User to reset
        """
        with self.lock:
            self.requests[user_id].clear()
    
    def get_stats(self) -> Dict:
        """
        Get rate limiting statistics.
        
        Returns:
            Dict with current statistics
        """
        with self.lock:
            now = time.time()
            active_users = 0
            total_requests = 0
            
            for user_id, requests in self.requests.items():
                # Clean old requests
                requests = [req_time for req_time in requests 
                           if now - req_time < self.time_window]
                self.requests[user_id] = requests
                
                if requests:
                    active_users += 1
                    total_requests += len(requests)
            
            return {
                'active_users': active_users,
                'total_requests': total_requests,
                'max_requests_per_user': self.max_requests,
                'time_window': self.time_window
            }


class MultiRateLimiter:
    """
    Multiple rate limiters for different operation types.
    """
    
    def __init__(self):
        """Initialize multiple rate limiters."""
        self.limiters = {
            'migration': RateLimiter(max_requests=10, time_window=3600),  # 10 per hour
            'file_ops': RateLimiter(max_requests=100, time_window=60),    # 100 per minute
            'api_calls': RateLimiter(max_requests=1000, time_window=3600), # 1000 per hour
            'analysis': RateLimiter(max_requests=50, time_window=3600),   # 50 per hour
        }
    
    def is_allowed(self, operation: str, user_id: str) -> bool:
        """
        Check if operation is allowed.
        
        Args:
            operation: Type of operation
            user_id: User identifier
            
        Returns:
            bool: True if operation is allowed
        """
        if operation not in self.limiters:
            return True  # Unknown operations are not rate limited
        
        return self.limiters[operation].is_allowed(user_id)
    
    def get_retry_after(self, operation: str, user_id: str) -> int:
        """
        Get retry time for operation.
        
        Args:
            operation: Type of operation
            user_id: User identifier
            
        Returns:
            int: Seconds until retry
        """
        if operation not in self.limiters:
            return 0
        
        return self.limiters[operation].get_retry_after(user_id)
    
    def get_all_stats(self) -> Dict:
        """
        Get statistics for all rate limiters.
        
        Returns:
            Dict with all statistics
        """
        return {
            operation: limiter.get_stats()
            for operation, limiter in self.limiters.items()
        }
