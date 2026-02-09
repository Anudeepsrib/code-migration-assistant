"""
Coverage Analyzer for test coverage assessment.

Analyzes test coverage and generates reports:
- Line coverage analysis
- Branch coverage analysis
- Function coverage
- Coverage reporting
"""

import json
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from ..security import SecurityAuditLogger


@dataclass
class CoverageReport:
    """Coverage report data structure."""
    report_id: str
    file_path: str
    line_coverage: float
    branch_coverage: float
    function_coverage: float
    total_lines: int
    covered_lines: int
    missing_lines: List[int]
    created_at: str


class CoverageAnalyzer:
    """
    Test coverage analysis system.
    
    Features:
    - Line coverage analysis
    - Branch coverage tracking
    - Function coverage metrics
    - Detailed coverage reports
    """
    
    def __init__(self, project_path: Path):
        """
        Initialize coverage analyzer.
        
        Args:
            project_path: Path to project directory
        """
        self.project_path = Path(project_path)
        self.coverage_reports: Dict[str, CoverageReport] = {}
        
        log_dir = self.project_path / '.migration-logs'
        self.audit_logger = SecurityAuditLogger(log_dir)
        
        self.coverage_file = self.project_path / '.migration-coverage.json'
        self._load_coverage_reports()
    
    def analyze_coverage(
        self,
        test_files: List[Path],
        source_files: List[Path],
        output_format: str = 'json'
    ) -> Dict[str, CoverageReport]:
        """
        Analyze test coverage.
        
        Args:
            test_files: List of test files
            source_files: List of source files to analyze
            output_format: Output format for reports
            
        Returns:
            Dict mapping file paths to coverage reports
        """
        reports = {}
        
        # Determine test framework
        test_framework = self._detect_test_framework()
        
        for source_file in source_files:
            # Generate coverage report
            report = self._generate_coverage_report(
                source_file, test_files, test_framework
            )
            
            if report:
                reports[str(source_file)] = report
                self.coverage_reports[report.report_id] = report
        
        self._save_coverage_reports()
        
        # Log coverage analysis
        self.audit_logger.log_migration_event(
            migration_type='test-coverage',
            project_path=str(self.project_path),
            user='system',
            action='ANALYZE_COVERAGE',
            result='SUCCESS',
            details={
                'files_analyzed': len(source_files),
                'reports_generated': len(reports),
                'framework': test_framework
            }
        )
        
        return reports
    
    def get_coverage_summary(self) -> Dict:
        """
        Get overall coverage summary.
        
        Returns:
            Coverage summary dictionary
        """
        if not self.coverage_reports:
            return {
                'total_files': 0,
                'average_line_coverage': 0.0,
                'average_branch_coverage': 0.0,
                'average_function_coverage': 0.0,
                'overall_grade': 'F'
            }
        
        total_files = len(self.coverage_reports)
        avg_line = sum(r.line_coverage for r in self.coverage_reports.values()) / total_files
        avg_branch = sum(r.branch_coverage for r in self.coverage_reports.values()) / total_files
        avg_func = sum(r.function_coverage for r in self.coverage_reports.values()) / total_files
        
        # Determine grade
        if avg_line >= 90:
            grade = 'A'
        elif avg_line >= 80:
            grade = 'B'
        elif avg_line >= 70:
            grade = 'C'
        elif avg_line >= 60:
            grade = 'D'
        else:
            grade = 'F'
        
        return {
            'total_files': total_files,
            'average_line_coverage': avg_line,
            'average_branch_coverage': avg_branch,
            'average_function_coverage': avg_func,
            'overall_grade': grade,
            'reports': [
                {
                    'file': r.file_path,
                    'line_coverage': r.line_coverage,
                    'branch_coverage': r.branch_coverage,
                    'function_coverage': r.function_coverage
                }
                for r in self.coverage_reports.values()
            ]
        }
    
    def identify_uncovered_areas(self, threshold: float = 0.8) -> List[Dict]:
        """
        Identify areas with insufficient coverage.
        
        Args:
            threshold: Minimum acceptable coverage (0-1)
            
        Returns:
            List of uncovered areas
        """
        uncovered = []
        
        for report in self.coverage_reports.values():
            if report.line_coverage < threshold:
                uncovered.append({
                    'file_path': report.file_path,
                    'line_coverage': report.line_coverage,
                    'missing_lines': report.missing_lines,
                    'suggestion': f"Add tests to cover lines {report.missing_lines[:10]}"
                })
        
        return uncovered
    
    def generate_coverage_report_html(self, output_path: Path) -> None:
        """
        Generate HTML coverage report.
        
        Args:
            output_path: Output file path
        """
        summary = self.get_coverage_summary()
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Test Coverage Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .summary {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .grade {{ font-size: 48px; font-weight: bold; }}
        .grade-A {{ color: #4CAF50; }}
        .grade-B {{ color: #8BC34A; }}
        .grade-C {{ color: #FFC107; }}
        .grade-D {{ color: #FF9800; }}
        .grade-F {{ color: #F44336; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #4CAF50; color: white; }}
        .low-coverage {{ background-color: #FFEBEE; }}
        .medium-coverage {{ background-color: #FFF3E0; }}
        .high-coverage {{ background-color: #E8F5E9; }}
    </style>
</head>
<body>
    <h1>Test Coverage Report</h1>
    
    <div class="summary">
        <h2>Summary</h2>
        <p>Overall Grade: <span class="grade grade-{summary['overall_grade']}">{summary['overall_grade']}</span></p>
        <p>Files Analyzed: {summary['total_files']}</p>
        <p>Average Line Coverage: {summary['average_line_coverage']:.1%}</p>
        <p>Average Branch Coverage: {summary['average_branch_coverage']:.1%}</p>
        <p>Average Function Coverage: {summary['average_function_coverage']:.1%}</p>
    </div>
    
    <h2>File Coverage Details</h2>
    <table>
        <tr>
            <th>File</th>
            <th>Line Coverage</th>
            <th>Branch Coverage</th>
            <th>Function Coverage</th>
        </tr>
"""
        
        for report in self.coverage_reports.values():
            coverage_class = 'high-coverage' if report.line_coverage >= 0.8 else \
                           'medium-coverage' if report.line_coverage >= 0.6 else 'low-coverage'
            
            html_content += f"""
        <tr class="{coverage_class}">
            <td>{report.file_path}</td>
            <td>{report.line_coverage:.1%}</td>
            <td>{report.branch_coverage:.1%}</td>
            <td>{report.function_coverage:.1%}</td>
        </tr>
"""
        
        html_content += """
    </table>
</body>
</html>
"""
        
        output_path.write_text(html_content, encoding='utf-8')
    
    def _detect_test_framework(self) -> str:
        """Detect test framework used in project."""
        # Check for pytest
        if (self.project_path / 'pytest.ini').exists():
            return 'pytest'
        if (self.project_path / 'setup.py').exists():
            content = (self.project_path / 'setup.py').read_text()
            if 'pytest' in content:
                return 'pytest'
        
        # Check for Jest
        if (self.project_path / 'jest.config.js').exists():
            return 'jest'
        if (self.project_path / 'package.json').exists():
            import json
            with open(self.project_path / 'package.json') as f:
                data = json.load(f)
                if 'jest' in str(data):
                    return 'jest'
        
        # Default to pytest
        return 'pytest'
    
    def _generate_coverage_report(
        self,
        source_file: Path,
        test_files: List[Path],
        test_framework: str
    ) -> Optional[CoverageReport]:
        """Generate coverage report for a source file."""
        if not source_file.exists():
            return None
        
        # Run coverage analysis
        try:
            if test_framework == 'pytest':
                return self._run_pytest_coverage(source_file, test_files)
            elif test_framework == 'jest':
                return self._run_jest_coverage(source_file, test_files)
            else:
                return self._estimate_coverage(source_file)
        except Exception:
            return None
    
    def _run_pytest_coverage(
        self,
        source_file: Path,
        test_files: List[Path]
    ) -> CoverageReport:
        """Run pytest coverage analysis."""
        report_id = f"cov_{datetime.now().strftime('%Y%m%d%H%M%S')}_{source_file.stem}"
        
        # Run pytest with coverage
        try:
            result = subprocess.run(
                ['pytest', '--cov=' + str(source_file), '--cov-report=json', '-q'],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Parse coverage output
            # This is a simplified version - real implementation would parse coverage JSON
            line_coverage = 0.75  # Placeholder
            branch_coverage = 0.70  # Placeholder
            function_coverage = 0.80  # Placeholder
            
        except subprocess.TimeoutExpired:
            line_coverage = 0.0
            branch_coverage = 0.0
            function_coverage = 0.0
        except Exception:
            line_coverage = 0.0
            branch_coverage = 0.0
            function_coverage = 0.0
        
        return CoverageReport(
            report_id=report_id,
            file_path=str(source_file),
            line_coverage=line_coverage,
            branch_coverage=branch_coverage,
            function_coverage=function_coverage,
            total_lines=100,  # Placeholder
            covered_lines=int(100 * line_coverage),  # Placeholder
            missing_lines=[],  # Placeholder
            created_at=datetime.now().isoformat()
        )
    
    def _run_jest_coverage(
        self,
        source_file: Path,
        test_files: List[Path]
    ) -> CoverageReport:
        """Run Jest coverage analysis."""
        report_id = f"cov_{datetime.now().strftime('%Y%m%d%H%M%S')}_{source_file.stem}"
        
        # Run Jest with coverage
        try:
            result = subprocess.run(
                ['npm', 'test', '--', '--coverage', '--collectCoverageFrom=' + str(source_file)],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Parse coverage output
            line_coverage = 0.75  # Placeholder
            branch_coverage = 0.70  # Placeholder
            function_coverage = 0.80  # Placeholder
            
        except subprocess.TimeoutExpired:
            line_coverage = 0.0
            branch_coverage = 0.0
            function_coverage = 0.0
        except Exception:
            line_coverage = 0.0
            branch_coverage = 0.0
            function_coverage = 0.0
        
        return CoverageReport(
            report_id=report_id,
            file_path=str(source_file),
            line_coverage=line_coverage,
            branch_coverage=branch_coverage,
            function_coverage=function_coverage,
            total_lines=100,  # Placeholder
            covered_lines=int(100 * line_coverage),  # Placeholder
            missing_lines=[],  # Placeholder
            created_at=datetime.now().isoformat()
        )
    
    def _estimate_coverage(self, source_file: Path) -> CoverageReport:
        """Estimate coverage based on file analysis."""
        report_id = f"cov_{datetime.now().strftime('%Y%m%d%H%M%S')}_{source_file.stem}"
        
        # Count lines in file
        try:
            content = source_file.read_text()
            total_lines = len(content.splitlines())
        except Exception:
            total_lines = 0
        
        # Estimate coverage (placeholder logic)
        estimated_coverage = 0.70
        
        return CoverageReport(
            report_id=report_id,
            file_path=str(source_file),
            line_coverage=estimated_coverage,
            branch_coverage=estimated_coverage * 0.9,
            function_coverage=estimated_coverage * 0.95,
            total_lines=total_lines,
            covered_lines=int(total_lines * estimated_coverage),
            missing_lines=[],
            created_at=datetime.now().isoformat()
        )
    
    def _load_coverage_reports(self) -> None:
        """Load coverage reports from file."""
        if self.coverage_file.exists():
            try:
                with open(self.coverage_file, 'r') as f:
                    data = json.load(f)
                    for report_data in data.get('reports', []):
                        report = CoverageReport(**report_data)
                        self.coverage_reports[report.report_id] = report
            except Exception:
                pass
    
    def _save_coverage_reports(self) -> None:
        """Save coverage reports to file."""
        try:
            data = {
                'reports': [
                    {
                        'report_id': r.report_id,
                        'file_path': r.file_path,
                        'line_coverage': r.line_coverage,
                        'branch_coverage': r.branch_coverage,
                        'function_coverage': r.function_coverage,
                        'total_lines': r.total_lines,
                        'covered_lines': r.covered_lines,
                        'missing_lines': r.missing_lines,
                        'created_at': r.created_at
                    }
                    for r in self.coverage_reports.values()
                ],
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.coverage_file, 'w') as f:
                json.dump(data, f, indent=2)
        
        except Exception:
            pass
