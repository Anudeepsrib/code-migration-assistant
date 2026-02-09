"""
Data lineage tracking for compliance.

Tracks data flow through the application:
- Data source identification
- Data transformation tracking
- Data flow mapping
- Compliance validation
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple

from ..security import SecurityAuditLogger, SafeCodeAnalyzer


class DataLineageTracker:
    """
    Track data flow for compliance and audit purposes.
    
    Features:
    - Data source identification
    - Data transformation tracking
    - Data flow mapping
    - PII flow tracking
    - Compliance validation
    """
    
    def __init__(self, project_path: Path):
        """
        Initialize data lineage tracker.
        
        Args:
            project_path: Path to project to analyze
        """
        self.project_path = Path(project_path)
        self.code_analyzer = SafeCodeAnalyzer()
        
        # Initialize audit logger
        log_dir = self.project_path / '.migration-logs'
        self.audit_logger = SecurityAuditLogger(log_dir)
        
        # Data lineage graph
        self.data_flow = {}
        self.data_sources = set()
        self.data_transformations = []
        self pii_flows = []
    
    def analyze_data_lineage(self) -> Dict:
        """
        Analyze data flow through the codebase.
        
        Returns:
            Data lineage analysis results
        """
        self.audit_logger.log_migration_event(
            migration_type='data_lineage',
            project_path=str(self.project_path),
            user='system',
            action='ANALYZE_LINEAGE',
            result='STARTED'
        )
        
        try:
            # Reset tracking
            self.data_flow = {}
            self.data_sources = set()
            self.data_transformations = []
            self.pii_flows = []
            
            # Analyze Python files
            for py_file in self.project_path.rglob('*.py'):
                self._analyze_python_file(py_file)
            
            # Analyze JavaScript/TypeScript files
            for js_file in self.project_path.rglob('*'):
                if js_file.suffix in ['.js', '.jsx', '.ts', '.tsx']:
                    self._analyze_javascript_file(js_file)
            
            # Analyze configuration files
            for config_file in self.project_path.rglob('*'):
                if config_file.suffix in ['.json', '.yaml', '.yml', '.env']:
                    self._analyze_config_file(config_file)
            
            # Generate lineage graph
            lineage_graph = self._build_lineage_graph()
            
            # Identify compliance issues
            compliance_issues = self._identify_compliance_issues()
            
            results = {
                'analysis_timestamp': datetime.now().isoformat(),
                'project_path': str(self.project_path),
                'data_sources': list(self.data_sources),
                'data_transformations': self.data_transformations,
                'pii_flows': self.pii_flows,
                'lineage_graph': lineage_graph,
                'compliance_issues': compliance_issues,
                'summary': self._generate_lineage_summary()
            }
            
            self.audit_logger.log_migration_event(
                migration_type='data_lineage',
                project_path=str(self.project_path),
                user='system',
                action='ANALYZE_LINEAGE',
                result='COMPLETED',
                details={
                    'data_sources': len(self.data_sources),
                    'transformations': len(self.data_transformations),
                    'pii_flows': len(self.pii_flows),
                    'compliance_issues': len(compliance_issues)
                }
            )
            
            return results
            
        except Exception as e:
            self.audit_logger.log_migration_event(
                migration_type='data_lineage',
                project_path=str(self.project_path),
                user='system',
                action='ANALYZE_LINEAGE',
                result='FAILURE',
                details={'error': str(e)}
            )
            raise
    
    def _analyze_python_file(self, file_path: Path) -> None:
        """Analyze Python file for data operations."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            relative_path = str(file_path.relative_to(self.project_path))
            
            # Find database connections
            db_patterns = [
                r'connect\(["\']([^"\']+)["\']',
                r'create_engine\(["\']([^"\']+)["\']',
                r'psycopg2\.connect\(["\']([^"\']+)["\']',
                r'mysql\.connect\(["\']([^"\']+)["\']',
                r'sqlite3\.connect\(["\']([^"\']+)["\']'
            ]
            
            for pattern in db_patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    connection_string = match.group(1)
                    self.data_sources.add({
                        'type': 'database',
                        'connection_string': self._sanitize_connection_string(connection_string),
                        'file': relative_path,
                        'line': content[:match.start()].count('\n') + 1
                    })
            
            # Find data operations
            data_operations = [
                (r'(\w+)\.execute\(', 'sql_execute'),
                (r'(\w+)\.select\(', 'data_select'),
                (r'(\w+)\.insert\(', 'data_insert'),
                (r'(\w+)\.update\(', 'data_update'),
                (r'(\w+)\.delete\(', 'data_delete'),
                (r'requests\.(get|post|put|delete)\(', 'http_request'),
                (r'json\.loads\(', 'json_parse'),
                (r'json\.dumps\(', 'json_serialize')
            ]
            
            for pattern, operation_type in data_operations:
                matches = re.finditer(pattern, content)
                for match in matches:
                    self.data_transformations.append({
                        'type': operation_type,
                        'file': relative_path,
                        'line': content[:match.start()].count('\n') + 1,
                        'context': self._get_line_context(content, match.start())
                    })
            
            # Find PII handling
            pii_patterns = [
                (r'(email|phone|ssn|credit_card|password)', 'pii_field'),
                (r'(user|customer|patient)', 'entity_with_pii'),
                (r'(encrypt|decrypt|hash)', 'crypto_operation'),
                (r'(mask|anonymize|redact)', 'data_protection')
            ]
            
            for pattern, pii_type in pii_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    self.pii_flows.append({
                        'type': pii_type,
                        'file': relative_path,
                        'line': content[:match.start()].count('\n') + 1,
                        'match': match.group(),
                        'context': self._get_line_context(content, match.start())
                    })
        
        except Exception:
            pass
    
    def _analyze_javascript_file(self, file_path: Path) -> None:
        """Analyze JavaScript/TypeScript file for data operations."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            relative_path = str(file_path.relative_to(self.project_path))
            
            # Find API calls
            api_patterns = [
                r'fetch\(["\']([^"\']+)["\']',
                r'axios\.(get|post|put|delete)\(["\']([^"\']+)["\']',
                r'\$\.ajax\(["\']([^"\']+)["\']',
                r'request\(["\']([^"\']+)["\']'
            ]
            
            for pattern in api_patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    endpoint = match.group(2) if len(match.groups()) > 1 else match.group(1)
                    self.data_sources.add({
                        'type': 'api_endpoint',
                        'endpoint': endpoint,
                        'file': relative_path,
                        'line': content[:match.start()].count('\n') + 1
                    })
            
            # Find data operations
            data_operations = [
                (r'\.then\(', 'async_operation'),
                (r'localStorage\.(get|set)Item', 'local_storage'),
                (r'sessionStorage\.(get|set)Item', 'session_storage'),
                (r'JSON\.(parse|stringify)', 'json_operation'),
                (r'\.map\(', 'data_transformation'),
                (r'\.filter\(', 'data_filtering'),
                (r'\.reduce\(', 'data_aggregation')
            ]
            
            for pattern, operation_type in data_operations:
                matches = re.finditer(pattern, content)
                for match in matches:
                    self.data_transformations.append({
                        'type': operation_type,
                        'file': relative_path,
                        'line': content[:match.start()].count('\n') + 1,
                        'context': self._get_line_context(content, match.start())
                    })
        
        except Exception:
            pass
    
    def _analyze_config_file(self, file_path: Path) -> None:
        """Analyze configuration file for data sources."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            relative_path = str(file_path.relative_to(self.project_path))
            
            # Find database configurations
            db_keys = ['DATABASE_URL', 'DB_HOST', 'DB_NAME', 'DB_USER', 'API_KEY', 'SECRET_KEY']
            
            for key in db_keys:
                if key in content:
                    self.data_sources.add({
                        'type': 'config_database',
                        'config_key': key,
                        'file': relative_path,
                        'line': content[:content.find(key)].count('\n') + 1
                    })
        
        except Exception:
            pass
    
    def _build_lineage_graph(self) -> Dict:
        """Build data lineage graph from analysis."""
        graph = {
            'nodes': [],
            'edges': []
        }
        
        # Add data sources as nodes
        for i, source in enumerate(self.data_sources):
            node_id = f"source_{i}"
            graph['nodes'].append({
                'id': node_id,
                'type': 'data_source',
                'label': source.get('type', 'unknown'),
                'details': source
            })
        
        # Add transformations as nodes
        for i, transform in enumerate(self.data_transformations):
            node_id = f"transform_{i}"
            graph['nodes'].append({
                'id': node_id,
                'type': 'transformation',
                'label': transform['type'],
                'details': transform
            })
        
        # Add PII flows as special nodes
        for i, pii_flow in enumerate(self.pii_flows):
            node_id = f"pii_{i}"
            graph['nodes'].append({
                'id': node_id,
                'type': 'pii_flow',
                'label': pii_flow['type'],
                'details': pii_flow
            })
        
        # Add edges (simplified - would need more sophisticated analysis)
        for i in range(len(graph['nodes']) - 1):
            graph['edges'].append({
                'source': graph['nodes'][i]['id'],
                'target': graph['nodes'][i + 1]['id'],
                'type': 'data_flow'
            })
        
        return graph
    
    def _identify_compliance_issues(self) -> List[Dict]:
        """Identify potential compliance issues."""
        issues = []
        
        # Check for unencrypted data storage
        for transform in self.data_transformations:
            if transform['type'] == 'local_storage' and 'pii' in str(transform).lower():
                issues.append({
                    'severity': 'HIGH',
                    'type': 'UNENCRYPTED_PII_STORAGE',
                    'description': 'PII data stored in localStorage without encryption',
                    'file': transform['file'],
                    'line': transform['line'],
                    'recommendation': 'Use encryption for PII data in client-side storage'
                })
        
        # Check for hardcoded database credentials
        for source in self.data_sources:
            if source.get('type') == 'database' and 'password' in str(source).lower():
                issues.append({
                    'severity': 'CRITICAL',
                    'type': 'HARDCODED_CREDENTIALS',
                    'description': 'Database credentials found in source code',
                    'file': source['file'],
                    'line': source['line'],
                    'recommendation': 'Move credentials to environment variables or secure vault'
                })
        
        # Check for PII in API endpoints
        for source in self.data_sources:
            if source.get('type') == 'api_endpoint':
                endpoint = source.get('endpoint', '')
                if any(pii in endpoint.lower() for pii in ['user', 'customer', 'patient']):
                    issues.append({
                        'severity': 'MEDIUM',
                        'type': 'PII_IN_API_ENDPOINT',
                        'description': 'PII-related API endpoint detected',
                        'file': source['file'],
                        'line': source['line'],
                        'recommendation': 'Ensure proper authentication and authorization for PII endpoints'
                    })
        
        return issues
    
    def _generate_lineage_summary(self) -> Dict:
        """Generate summary of data lineage analysis."""
        return {
            'total_data_sources': len(self.data_sources),
            'total_transformations': len(self.data_transformations),
            'total_pii_flows': len(self.pii_flows),
            'data_source_types': list(set(s.get('type', 'unknown') for s in self.data_sources)),
            'transformation_types': list(set(t.get('type', 'unknown') for t in self.data_transformations)),
            'pii_flow_types': list(set(p.get('type', 'unknown') for p in self.pii_flows))
        }
    
    def _sanitize_connection_string(self, connection_string: str) -> str:
        """Sanitize database connection string for logging."""
        # Remove sensitive parts
        sanitized = re.sub(r'password=[^;]+', 'password=***', connection_string, flags=re.IGNORECASE)
        sanitized = re.sub(r'pwd=[^;]+', 'pwd=***', sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r'//[^:]+:[^@]+@', '//***:***@', sanitized)
        return sanitized
    
    def _get_line_context(self, content: str, position: int) -> str:
        """Get context around a position in content."""
        lines = content.split('\n')
        line_num = content[:position].count('\n')
        
        start_line = max(0, line_num - 1)
        end_line = min(len(lines), line_num + 2)
        
        context_lines = lines[start_line:end_line]
        return '\n'.join(context_lines).strip()
    
    def generate_lineage_report(self, lineage_results: Dict) -> str:
        """Generate formatted data lineage report."""
        report_lines = [
            "📊 DATA LINEAGE ANALYSIS REPORT",
            "=" * 50,
            f"📅 Analysis Date: {lineage_results['analysis_timestamp']}",
            f"📁 Project: {lineage_results['project_path']}",
            "",
            "📈 SUMMARY:",
            f"  Data Sources: {lineage_results['summary']['total_data_sources']}",
            f"  Data Transformations: {lineage_results['summary']['total_transformations']}",
            f"  PII Flows: {lineage_results['summary']['total_pii_flows']}",
            ""
        ]
        
        # Data sources
        if lineage_results['data_sources']:
            report_lines.extend([
                "🗄️  DATA SOURCES:",
            ])
            
            for source in lineage_results['data_sources'][:10]:  # Limit to 10
                report_lines.extend([
                    f"  • {source['type']}: {source.get('connection_string', source.get('endpoint', 'N/A'))}",
                    f"    File: {source['file']}:{source['line']}"
                ])
        
        # PII flows
        if lineage_results['pii_flows']:
            report_lines.extend([
                "",
                "🔒 PII DATA FLOWS:",
            ])
            
            for pii_flow in lineage_results['pii_flows'][:10]:  # Limit to 10
                report_lines.extend([
                    f"  • {pii_flow['type']}: {pii_flow['match']}",
                    f"    File: {pii_flow['file']}:{pii_flow['line']}"
                ])
        
        # Compliance issues
        if lineage_results['compliance_issues']:
            report_lines.extend([
                "",
                "⚠️  COMPLIANCE ISSUES:",
            ])
            
            for issue in lineage_results['compliance_issues']:
                severity_emoji = {
                    'CRITICAL': '🔴',
                    'HIGH': '🟠',
                    'MEDIUM': '🟡',
                    'LOW': '🟢'
                }.get(issue['severity'], '⚪')
                
                report_lines.extend([
                    f"  {severity_emoji} {issue['type']} ({issue['severity']})",
                    f"    Description: {issue['description']}",
                    f"    File: {issue['file']}:{issue['line']}",
                    f"    Recommendation: {issue['recommendation']}",
                    ""
                ])
        
        return "\n".join(report_lines)
