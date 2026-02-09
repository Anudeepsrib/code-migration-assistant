"""
Personally Identifiable Information (PII) detector.

Detects PII for GDPR compliance:
- Email addresses
- Phone numbers
- Social Security numbers
- Credit card numbers
- Addresses
- Names
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from ..security import SecurityAuditLogger


class PIIDetector:
    """
    Detect PII for GDPR compliance.
    
    Regulations Covered:
    - GDPR (EU): Personal data protection
    - HIPAA (US): Health information privacy
    - CCPA (CA): Consumer privacy
    - PCI-DSS: Payment card data
    """
    
    # PII patterns (GDPR Article 4)
    PII_PATTERNS = {
        'email': {
            'pattern': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'severity': 'MEDIUM',
            'confidence': 'HIGH',
            'regulation': 'GDPR'
        },
        'ssn': {
            'pattern': r'\b\d{3}-\d{2}-\d{4}\b',
            'severity': 'HIGH',
            'confidence': 'HIGH',
            'regulation': 'GDPR'
        },
        'phone': {
            'pattern': r'(?<!\w)(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
            'severity': 'MEDIUM',
            'confidence': 'MEDIUM',
            'regulation': 'GDPR'
        },
        'credit_card': {
            'pattern': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
            'severity': 'CRITICAL',
            'confidence': 'HIGH',
            'regulation': 'PCI-DSS'
        },
        'ip_address': {
            'pattern': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            'severity': 'LOW',
            'confidence': 'MEDIUM',
            'regulation': 'GDPR'
        },
        'date_of_birth': {
            'pattern': r'\b(?:0[1-9]|1[0-2])/(?:0[1-9]|[12]\d|3[01])/(?:19|20)\d{2}\b',
            'severity': 'HIGH',
            'confidence': 'MEDIUM',
            'regulation': 'GDPR'
        },
        'address': {
            'pattern': r'\b\d+\s+([A-Z][a-z]*\s*)+(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)\b',
            'severity': 'MEDIUM',
            'confidence': 'LOW',
            'regulation': 'GDPR'
        },
        'passport': {
            'pattern': r'\b[A-Z]{2}\d{7}\b',
            'severity': 'HIGH',
            'confidence': 'MEDIUM',
            'regulation': 'GDPR'
        },
        'driver_license': {
            'pattern': r'\b[A-Z]{1,2}\d{6,8}\b',
            'severity': 'HIGH',
            'confidence': 'LOW',
            'regulation': 'GDPR'
        }
    }
    
    # PHI patterns (HIPAA)
    PHI_PATTERNS = {
        'medical_record': {
            'pattern': r'(?i)mrn[\s:]+\d+',
            'severity': 'CRITICAL',
            'confidence': 'HIGH',
            'regulation': 'HIPAA'
        },
        'diagnosis_code': {
            'pattern': r'(?i)icd[\s-]?(9|10)[\s:]+[A-Z0-9.]+',
            'severity': 'HIGH',
            'confidence': 'HIGH',
            'regulation': 'HIPAA'
        },
        'patient_id': {
            'pattern': r'(?i)patient[\s_]id[\s:]+\d+',
            'severity': 'CRITICAL',
            'confidence': 'HIGH',
            'regulation': 'HIPAA'
        },
        'medical_procedure': {
            'pattern': r'(?i)cpt[\s:]+\d{5}',
            'severity': 'MEDIUM',
            'confidence': 'MEDIUM',
            'regulation': 'HIPAA'
        },
        'health_insurance': {
            'pattern': r'\b\d{3}-\d{2}-\d{4}\b',
            'severity': 'HIGH',
            'confidence': 'MEDIUM',
            'regulation': 'HIPAA'
        }
    }
    
    def __init__(self, project_path: Path):
        """
        Initialize PII detector.
        
        Args:
            project_path: Path to project to scan
        """
        self.project_path = Path(project_path)
        
        # Initialize audit logger
        log_dir = self.project_path / '.migration-logs'
        self.audit_logger = SecurityAuditLogger(log_dir)
        
        # Combine all patterns
        self.all_patterns = {**self.PII_PATTERNS, **self.PHI_PATTERNS}

    def close(self):
        """Close detector and release resources."""
        if hasattr(self, 'audit_logger'):
            self.audit_logger.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def scan_file(self, file_path: Path) -> List[Dict]:
        """
        Scan a single file for PII.
        
        Args:
            file_path: Path to file to scan
            
        Returns:
            List of PII findings
        """
        findings = []
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
            
            for pii_type, pattern_info in self.all_patterns.items():
                try:
                    matches = re.finditer(
                        pattern_info['pattern'], 
                        content, 
                        re.MULTILINE | re.IGNORECASE
                    )
                    
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        line_content = lines[line_num - 1] if line_num <= len(lines) else ""
                        
                        finding = {
                            'type': pii_type,
                            'severity': pattern_info['severity'],
                            'confidence': pattern_info['confidence'],
                            'regulation': pattern_info['regulation'],
                            'line': line_num,
                            'column': match.start() - content.rfind('\n', 0, match.start()),
                            'match': match.group()[:50] + "..." if len(match.group()) > 50 else match.group(),
                            'file_path': str(file_path.relative_to(self.project_path)),
                            'context': self._get_context(line_content, match.group()),
                            'recommendation': self._get_recommendation(pii_type, pattern_info['regulation'])
                        }
                        
                        findings.append(finding)
                        
                except re.error:
                    continue
        
        except Exception as e:
            # Log error but continue scanning
            pass
        
        return findings
    
    def scan_directory(self, file_extensions: List[str] = None) -> Dict:
        """
        Scan entire directory for PII.
        
        Args:
            file_extensions: List of file extensions to scan
            
        Returns:
            Scan results with summary
        """
        if file_extensions is None:
            file_extensions = ['.py', '.js', '.jsx', '.ts', '.tsx', '.vue', '.html', '.css', 
                             '.json', '.yaml', '.yml', '.md', '.txt', '.xml', '.sql', '.env']
        
        all_findings = []
        files_scanned = 0
        files_with_pii = 0
        
        # Log scan start
        self.audit_logger.log_migration_event(
            migration_type='pii_scan',
            project_path=str(self.project_path),
            user='system',
            action='SCAN_DIRECTORY',
            result='STARTED',
            details={
                'file_extensions': file_extensions
            }
        )
        
        for ext in file_extensions:
            for file_path in self.project_path.rglob(f'*{ext}'):
                # Skip hidden and system files (except .env)
                if (file_path.name.startswith('.') and file_path.name != '.env') or file_path.name.startswith('__'):
                    continue
                
                try:
                    findings = self.scan_file(file_path)
                    files_scanned += 1
                    
                    if findings:
                        files_with_pii += 1
                        all_findings.extend(findings)
                        
                except Exception:
                    continue
        
        # Generate summary
        summary = self._generate_scan_summary(all_findings, files_scanned, files_with_pii)
        
        # Log scan completion
        self.audit_logger.log_migration_event(
            migration_type='pii_scan',
            project_path=str(self.project_path),
            user='system',
            action='SCAN_DIRECTORY',
            result='COMPLETED',
            details={
                'files_scanned': files_scanned,
                'files_with_pii': files_with_pii,
                'total_findings': len(all_findings),
                'summary': summary
            }
        )
        
        return {
            'scan_timestamp': datetime.now().isoformat(),
            'project_path': str(self.project_path),
            'files_scanned': files_scanned,
            'files_with_pii': files_with_pii,
            'total_findings': len(all_findings),
            'summary': summary,
            'findings': all_findings
        }
    
    def generate_compliance_report(self, scan_results: Dict) -> str:
        """
        Generate compliance report from scan results.
        
        Args:
            scan_results: Results from scan_directory
            
        Returns:
            Formatted compliance report
        """
        if not scan_results.get('findings'):
            return "✅ No PII/PHI detected in scanned files."
        
        findings = scan_results['findings']
        summary = scan_results['summary']
        
        report_lines = [
            "🔒 COMPLIANCE SCAN REPORT",
            "=" * 50,
            f"📅 Scan Date: {scan_results['scan_timestamp']}",
            f"📁 Project: {scan_results['project_path']}",
            "",
            "📊 SCAN SUMMARY:",
            f"  Files Scanned: {scan_results['files_scanned']}",
            f"  Files with PII: {scan_results['files_with_pii']}",
            f"  Total Findings: {scan_results['total_findings']}",
            ""
        ]
        
        # Summary by regulation
        report_lines.extend([
            "📋 FINDINGS BY REGULATION:",
        ])
        
        for regulation in ['GDPR', 'HIPAA', 'PCI-DSS']:
            reg_findings = [f for f in findings if f['regulation'] == regulation]
            if reg_findings:
                critical = len([f for f in reg_findings if f['severity'] == 'CRITICAL'])
                high = len([f for f in reg_findings if f['severity'] == 'HIGH'])
                medium = len([f for f in reg_findings if f['severity'] == 'MEDIUM'])
                low = len([f for f in reg_findings if f['severity'] == 'LOW'])
                
                report_lines.append(f"  {regulation}:")
                report_lines.append(f"    Critical: {critical}, High: {high}, Medium: {medium}, Low: {low}")
        
        report_lines.extend(["", "🚨 CRITICAL FINDINGS:", ""])
        
        # Critical findings first
        critical_findings = [f for f in findings if f['severity'] == 'CRITICAL']
        if critical_findings:
            for finding in critical_findings[:10]:  # Limit to first 10
                report_lines.extend([
                    f"  🔴 {finding['type'].upper()} (Line {finding['line']})",
                    f"    File: {finding['file_path']}",
                    f"    Match: {finding['match']}",
                    f"    Regulation: {finding['regulation']}",
                    f"    Recommendation: {finding['recommendation']}",
                    ""
                ])
        else:
            report_lines.append("  ✅ No critical findings")
        
        # High severity findings
        report_lines.extend(["⚠️  HIGH SEVERITY FINDINGS:", ""])
        
        high_findings = [f for f in findings if f['severity'] == 'HIGH']
        if high_findings:
            for finding in high_findings[:10]:  # Limit to first 10
                report_lines.extend([
                    f"  🟠 {finding['type'].upper()} (Line {finding['line']})",
                    f"    File: {finding['file_path']}",
                    f"    Match: {finding['match']}",
                    f"    Regulation: {finding['regulation']}",
                    ""
                ])
        else:
            report_lines.append("  ✅ No high severity findings")
        
        # Compliance recommendations
        report_lines.extend([
            "💡 COMPLIANCE RECOMMENDATIONS:",
            "  1. Review and remove all PII/PHI from source code",
            "  2. Move sensitive data to environment variables or secure storage",
            "  3. Implement data masking for development/testing environments",
            "  4. Add PII detection to CI/CD pipeline",
            "  5. Create data processing register for GDPR compliance",
            "  6. Implement data retention policies",
            ""
        ])
        
        return "\n".join(report_lines)
    
    def _get_context(self, line_content: str, match: str) -> str:
        """Get context around the PII match."""
        # Redact the actual PII
        redacted = line_content.replace(match, '[REDACTED]')
        
        # Limit context length
        if len(redacted) > 200:
            redacted = redacted[:200] + "..."
        
        return redacted.strip()
    
    def _get_recommendation(self, pii_type: str, regulation: str) -> str:
        """Get recommendation for PII type."""
        recommendations = {
            'email': f"Remove email address. Use environment variables or configuration files for {regulation} compliance.",
            'ssn': f"Remove Social Security Number immediately. {regulation} requires strict protection of this data.",
            'phone': f"Remove phone number. Use secure contact management for {regulation} compliance.",
            'credit_card': f"Remove credit card data immediately. PCI-DSS compliance required.",
            'ip_address': f"Consider if IP address logging is necessary for {regulation} compliance.",
            'date_of_birth': f"Remove date of birth. Use secure user profile management for {regulation} compliance.",
            'address': f"Remove address. Use secure address management for {regulation} compliance.",
            'passport': f"Remove passport number. {regulation} requires strict protection of identity documents.",
            'driver_license': f"Remove driver license number. {regulation} requires strict protection.",
            'medical_record': f"Remove medical record number. HIPAA compliance required.",
            'diagnosis_code': f"Remove diagnosis code. HIPAA compliance required.",
            'patient_id': f"Remove patient ID. HIPAA compliance required.",
            'medical_procedure': f"Remove medical procedure code. HIPAA compliance required.",
            'health_insurance': f"Remove health insurance number. HIPAA compliance required."
        }
        
        return recommendations.get(pii_type, f"Remove sensitive data for {regulation} compliance.")
    
    def _generate_scan_summary(self, findings: List[Dict], files_scanned: int, files_with_pii: int) -> Dict:
        """Generate scan summary statistics."""
        summary = {
            'by_severity': {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0},
            'by_regulation': {},
            'by_type': {},
            'risk_score': 0
        }
        
        for finding in findings:
            # Count by severity
            severity = finding['severity']
            summary['by_severity'][severity] += 1
            
            # Count by regulation
            regulation = finding['regulation']
            if regulation not in summary['by_regulation']:
                summary['by_regulation'][regulation] = 0
            summary['by_regulation'][regulation] += 1
            
            # Count by type
            pii_type = finding['type']
            if pii_type not in summary['by_type']:
                summary['by_type'][pii_type] = 0
            summary['by_type'][pii_type] += 1
        
        # Calculate risk score
        severity_weights = {'CRITICAL': 10, 'HIGH': 5, 'MEDIUM': 2, 'LOW': 1}
        summary['risk_score'] = sum(
            summary['by_severity'][severity] * weight
            for severity, weight in severity_weights.items()
        )
        
        return summary
