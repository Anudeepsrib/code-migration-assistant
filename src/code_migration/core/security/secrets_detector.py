"""
Secrets detection to prevent credential leaks.

Detects exposed credentials before migration.
Supports multiple cloud providers and common secret patterns.
"""

import hashlib
import re
from typing import List, Dict, Tuple


class SecretsDetector:
    """
    Detect exposed credentials before migration.
    
    Security Use Cases:
    - Prevent API keys in migrated code
    - Find hardcoded passwords
    - Detect private keys
    - Identify tokens
    """
    
    # Regex patterns for various secret types
    PATTERNS = {
        # AWS
        'aws_access_key': r'AKIA[0-9A-Z]{16}',
        'aws_secret': r'(?i)aws(.{0,20})?[\'\"][0-9a-zA-Z\/+]{40}[\'\"]',
        
        # GitHub
        'github_token': r'ghp_[0-9a-zA-Z]{36}',
        'github_oauth': r'gho_[0-9a-zA-Z]{36}',
        'github_app': r'ghu_[0-9a-zA-Z]{36}',
        'github_refresh': r'ghr_[0-9a-zA-Z]{36}',
        
        # Slack
        'slack_token': r'xox[baprs]-[0-9a-zA-Z\-]{10,48}',
        'slack_webhook': r'https://hooks\.slack\.com/services/[A-Z0-9]{9}/[A-Z0-9]{9}/[A-Z0-9]{24}',
        
        # Google Cloud
        'gcp_service_account': r'"type": "service_account"',
        'gcp_private_key': r'-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----',
        
        # Azure
        'azure_client_secret': r'[\'\"][a-zA-Z0-9~!@#$%^&*()_+`\-={}|\[\]:;\'<>?,./]{32,}[\'\"]',
        
        # Database
        'database_url': r'(?i)(mysql|postgresql|mongodb|redis)://[^\s\'"]+',
        'connection_string': r'(?i)server=.*;database=.*;user id=.*;password=.*',
        
        # JWT Tokens
        'jwt_token': r'eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*',
        
        # SSH Keys
        'ssh_private_key': r'-----BEGIN (RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----',
        'ssh_public_key': r'ssh-(rsa|dsa|ecdsa|ed25519) [A-Z0-9]+',
        
        # Generic patterns
        'generic_api_key': r'(?i)(api|key|token|secret|password|pwd|pass)\s*[:=]\s*[\'\"][a-zA-Z0-9\-_]{20,}[\'\"]',
        'private_key_header': r'-----BEGIN [A-Z ]+KEY-----',
        
        # Common passwords (weak detection)
        'weak_password': r'(?i)(password|pwd|pass)\s*[:=]\s*[\'\"](123456|password|admin|root|test|guest)[\'\"]',
        
        # Email addresses (PII)
        'email_address': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        
        # Credit cards (PCI-DSS)
        'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
        
        # Social Security Numbers (PII)
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        
        # IP addresses
        'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
    }
    
    # Severity levels
    SEVERITY_LEVELS = {
        'CRITICAL': [
            'aws_access_key', 'aws_secret', 'github_token', 'slack_token',
            'gcp_private_key', 'ssh_private_key', 'database_url'
        ],
        'HIGH': [
            'azure_client_secret', 'jwt_token', 'connection_string',
            'generic_api_key', 'private_key_header'
        ],
        'MEDIUM': [
            'github_oauth', 'github_app', 'github_refresh', 'ssh_public_key',
            'slack_webhook', 'gcp_service_account'
        ],
        'LOW': [
            'email_address', 'ip_address', 'weak_password'
        ],
        'INFO': [
            'credit_card', 'ssn'  # Often false positives
        ]
    }
    
    @staticmethod
    def scan_file(content: str, file_path: str = "") -> List[Dict]:
        """
        Scan file content for secrets.
        
        Args:
            content: File content to scan
            file_path: Optional file path for context
            
        Returns:
            List of findings with metadata
        """
        findings = []
        lines = content.split('\n')
        
        for secret_type, pattern in SecretsDetector.PATTERNS.items():
            try:
                matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
                
                for match in matches:
                    # Calculate line number
                    line_num = content[:match.start()].count('\n') + 1
                    line_content = lines[line_num - 1] if line_num <= len(lines) else ""
                    
                    # Hash the secret (never log plaintext)
                    secret_value = match.group().strip()
                    secret_hash = hashlib.sha256(
                        secret_value.encode()
                    ).hexdigest()[:16]
                    
                    # Determine severity
                    severity = SecretsDetector._get_severity(secret_type)
                    
                    # Create finding
                    finding = {
                        'type': secret_type,
                        'severity': severity,
                        'line': line_num,
                        'column': match.start() - content.rfind('\n', 0, match.start()),
                        'hash': secret_hash,
                        'file': file_path,
                        'context': SecretsDetector._get_context(line_content, secret_value),
                        'recommendation': SecretsDetector._get_recommendation(secret_type)
                    }
                    
                    findings.append(finding)
                    
            except re.error:
                # Skip invalid regex patterns
                continue
        
        return findings
    
    @staticmethod
    def scan_directory(file_paths: List[Tuple[str, str]]) -> Dict:
        """
        Scan multiple files for secrets.
        
        Args:
            file_paths: List of (file_path, content) tuples
            
        Returns:
            Dict with aggregated findings
        """
        all_findings = []
        summary = {
            'total_files': len(file_paths),
            'files_with_secrets': 0,
            'total_findings': 0,
            'by_severity': {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'INFO': 0},
            'by_type': {}
        }
        
        for file_path, content in file_paths:
            try:
                findings = SecretsDetector.scan_file(content, file_path)
                
                if findings:
                    summary['files_with_secrets'] += 1
                    all_findings.extend(findings)
                    
                    # Update summary
                    for finding in findings:
                        summary['total_findings'] += 1
                        summary['by_severity'][finding['severity']] += 1
                        
                        secret_type = finding['type']
                        if secret_type not in summary['by_type']:
                            summary['by_type'][secret_type] = 0
                        summary['by_type'][secret_type] += 1
                        
            except Exception:
                # Skip files that can't be processed
                continue
        
        return {
            'summary': summary,
            'findings': all_findings
        }
    
    @staticmethod
    def _get_severity(secret_type: str) -> str:
        """Get severity level for secret type."""
        for severity, types in SecretsDetector.SEVERITY_LEVELS.items():
            if secret_type in types:
                return severity
        return 'MEDIUM'
    
    @staticmethod
    def _get_context(line_content: str, secret_value: str) -> str:
        """
        Get context around the secret, redacting the actual secret.
        """
        # Replace secret with placeholder
        context = line_content.replace(secret_value, '[REDACTED]')
        
        # Limit context length
        if len(context) > 200:
            context = context[:200] + "..."
        
        return context.strip()
    
    @staticmethod
    def _get_recommendation(secret_type: str) -> str:
        """Get security recommendation for secret type."""
        recommendations = {
            'aws_access_key': 'Remove AWS access key. Use IAM roles instead.',
            'aws_secret': 'Remove AWS secret key. Rotate immediately if exposed.',
            'github_token': 'Remove GitHub token. Use environment variables.',
            'slack_token': 'Remove Slack token. Use app credentials.',
            'gcp_private_key': 'Remove GCP private key. Use service account keys.',
            'database_url': 'Move database URL to environment variables.',
            'jwt_token': 'Remove JWT token. Use proper authentication flow.',
            'ssh_private_key': 'Remove SSH private key. Use SSH agent.',
            'generic_api_key': 'Remove API key. Use secure credential management.',
            'email_address': 'Consider if email address is necessary in code.',
            'credit_card': 'Remove credit card data immediately. PCI-DSS violation.',
            'ssn': 'Remove SSN immediately. HIPAA/GDPR violation.'
        }
        
        return recommendations.get(secret_type, 'Remove sensitive data from code.')
    
    @staticmethod
    def generate_report(findings: List[Dict]) -> str:
        """
        Generate security report from findings.
        
        Args:
            findings: List of secret findings
            
        Returns:
            Formatted report string
        """
        if not findings:
            return "✅ No secrets detected in scanned files."
        
        # Group by severity
        by_severity = {'CRITICAL': [], 'HIGH': [], 'MEDIUM': [], 'LOW': [], 'INFO': []}
        for finding in findings:
            by_severity[finding['severity']].append(finding)
        
        report_lines = [
            "🚨 SECRETS DETECTION REPORT",
            "=" * 50,
            "",
            f"Total Findings: {len(findings)}",
            ""
        ]
        
        # Summary by severity
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']:
            count = len(by_severity[severity])
            if count > 0:
                emoji = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'LOW': '🟢', 'INFO': '🔵'}[severity]
                report_lines.append(f"{emoji} {severity}: {count} findings")
        
        report_lines.extend(["", "DETAILED FINDINGS:", "-" * 30])
        
        # Detailed findings
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']:
            if by_severity[severity]:
                report_lines.append(f"\n{severity}:")
                for finding in by_severity[severity]:
                    report_lines.extend([
                        f"  • {finding['type']} (Line {finding['line']})",
                        f"    File: {finding['file']}",
                        f"    Context: {finding['context']}",
                        f"    Recommendation: {finding['recommendation']}",
                        ""
                    ])
        
        return "\n".join(report_lines)
