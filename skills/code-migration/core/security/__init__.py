"""
Security module for Code Migration Assistant.

Provides enterprise-grade security features:
- Input validation and sanitization
- Path traversal prevention
- Secure file operations
- Secrets detection
- Audit logging
- Rate limiting
"""

from .input_validator import SecurityError, CodeValidator
from .path_sanitizer import PathSanitizer
from .code_sandbox import SafeCodeAnalyzer
from .secrets_detector import SecretsDetector
from .crypto_handler import SecureFileHandler
from .audit_logger import SecurityAuditLogger
from .rate_limiter import RateLimiter

__all__ = [
    'SecurityError',
    'CodeValidator', 
    'PathSanitizer',
    'SafeCodeAnalyzer',
    'SecretsDetector',
    'SecureFileHandler',
    'SecurityAuditLogger',
    'RateLimiter'
]
