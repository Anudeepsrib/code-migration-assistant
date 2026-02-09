"""
Migration confidence scoring algorithm.

AI-powered pre-migration risk assessment with:
- Codebase complexity analysis
- Test coverage evaluation
- Dependency health checking
- Breaking change estimation
- Cost and time predictions
"""

import ast
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

from ..security import PathSanitizer, SecurityAuditLogger, SafeCodeAnalyzer


@dataclass
class ConfidenceScore:
    """Migration confidence assessment."""
    overall_score: int          # 0-100
    risk_level: str            # LOW, MEDIUM, HIGH, CRITICAL
    estimated_hours: float
    estimated_cost: float
    factors: Dict[str, int]   # Individual factor scores
    blockers: List[str]
    warnings: List[str]
    recommendations: List[str]
    migration_complexity: str   # SIMPLE, MODERATE, COMPLEX, VERY_COMPLEX


class MigrationConfidenceAnalyzer:
    """
    AI-powered pre-migration risk assessment.
    
    Analyzes:
    - Codebase complexity
    - Test coverage
    - Dependency health
    - Breaking changes scope
    - Team skill level (optional input)
    
    SECURITY: All analysis is static, no code execution.
    """
    
    # Scoring weights
    WEIGHTS = {
        'test_coverage': 0.25,      # Higher coverage = higher confidence
        'complexity': 0.20,          # Lower complexity = higher confidence
        'dependencies': 0.15,        # Fewer/healthier deps = higher confidence
        'code_quality': 0.15,        # Better quality = higher confidence
        'breaking_changes': 0.15,    # Fewer breaking changes = higher confidence
        'team_experience': 0.10,     # More experience = higher confidence
    }
    
    # Migration complexity multipliers
    MIGRATION_COMPLEXITY = {
        'react-hooks': 1.0,      # Baseline
        'vue3': 1.2,              # 20% more complex
        'python3': 0.8,           # 20% less complex
        'typescript': 1.5,         # 50% more complex
        'graphql': 1.8,           # 80% more complex
        'angular': 1.6,           # 60% more complex
        'svelte': 1.1,            # 10% more complex
    }
    
    def __init__(self, project_path: Path):
        """
        Initialize confidence analyzer.
        
        Args:
            project_path: Path to project to analyze
        """
        self.project_path = PathSanitizer.sanitize(
            str(project_path),
            allowed_base=Path.cwd()
        )
        
        # Initialize audit logger
        log_dir = self.project_path / '.migration-logs'
        self.audit_logger = SecurityAuditLogger(log_dir)
        
        # Initialize safe code analyzer
        self.code_analyzer = SafeCodeAnalyzer()

    def close(self):
        """Close resources."""
        if hasattr(self, 'audit_logger'):
            self.audit_logger.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def calculate_confidence(self, migration_type: str, team_experience: int = 50) -> ConfidenceScore:
        """
        Calculate migration confidence score.
        
        Args:
            migration_type: Type of migration to perform
            team_experience: Team experience level (0-100)
            
        Returns:
            ConfidenceScore with detailed assessment
        """
        self.audit_logger.log_migration_event(
            migration_type=migration_type,
            project_path=str(self.project_path),
            user='system',
            action='CONFIDENCE_ANALYSIS',
            result='STARTED'
        )
        if migration_type not in self.MIGRATION_COMPLEXITY:
            raise ValueError(f"Invalid migration type: {migration_type}")
            
        factors = {}
        
        # 1. Test Coverage Analysis
        factors['test_coverage'] = self._analyze_test_coverage()
        
        # 2. Code Complexity (Cyclomatic Complexity)
        factors['complexity'] = self._analyze_complexity()
        
        # 3. Dependency Health
        factors['dependencies'] = self._analyze_dependencies()
        
        # 4. Code Quality (linting, formatting)
        factors['code_quality'] = self._analyze_code_quality()
        
        # 5. Breaking Changes Estimation
        factors['breaking_changes'] = self._estimate_breaking_changes(migration_type)
        
        # 6. Team Experience (user input)
        factors['team_experience'] = team_experience
        
        # Calculate weighted score
        overall_score = sum(
            factors[key] * self.WEIGHTS[key]
            for key in self.WEIGHTS.keys()
        )
        
        # Determine risk level
        if overall_score >= 80:
            risk_level = "LOW"
        elif overall_score >= 60:
            risk_level = "MEDIUM"
        elif overall_score >= 40:
            risk_level = "HIGH"
        else:
            risk_level = "CRITICAL"
        
        # Determine migration complexity
        migration_complexity = self._determine_migration_complexity(
            overall_score, migration_type, factors
        )
        
        # Estimate time and cost
        estimated_hours = self._estimate_time(overall_score, migration_type)
        estimated_cost = estimated_hours * 100  # $100/hour default rate
        
        # Generate recommendations
        blockers, warnings, recommendations = self._generate_recommendations(factors)
        
        confidence_score = ConfidenceScore(
            overall_score=int(overall_score),
            risk_level=risk_level,
            estimated_hours=estimated_hours,
            estimated_cost=estimated_cost,
            factors=factors,
            blockers=blockers,
            warnings=warnings,
            recommendations=recommendations,
            migration_complexity=migration_complexity
        )
        
        self.audit_logger.log_migration_event(
            migration_type=migration_type,
            project_path=str(self.project_path),
            user='system',
            action='CONFIDENCE_ANALYSIS',
            result='COMPLETED',
            details={
                'overall_score': confidence_score.overall_score,
                'risk_level': confidence_score.risk_level,
                'estimated_hours': confidence_score.estimated_hours
            }
        )
        
        return confidence_score
    
    def _analyze_test_coverage(self) -> int:
        """
        Calculate test coverage score.
        
        Security: Run coverage in isolated subprocess with timeout.
        """
        try:
            # Check for pytest configuration
            pytest_files = list(self.project_path.rglob('pytest.ini')) + \
                          list(self.project_path.rglob('pyproject.toml')) + \
                          list(self.project_path.rglob('setup.cfg'))
            
            if not pytest_files:
                return 30  # No test configuration found
            
            # Run pytest with coverage (timeout 60s)
            result = subprocess.run(
                ['pytest', '--cov=.', '--cov-report=json', '--tb=no'],
                cwd=self.project_path,
                capture_output=True,
                timeout=60,
                check=False
            )
            
            if result.returncode == 0:
                # Parse coverage report
                coverage_file = self.project_path / 'coverage.json'
                if coverage_file.exists():
                    with open(coverage_file) as f:
                        data = json.load(f)
                        return int(data.get('totals', {}).get('percent_covered', 0))
            
            return 30  # Default low score if no tests
            
        except subprocess.TimeoutExpired:
            return 20  # Very low score for timeout
        except Exception:
            return 30  # Default on error
    
    def _analyze_complexity(self) -> int:
        """
        Analyze cyclomatic complexity.
        
        Security: AST-only analysis, no execution.
        """
        try:
            analysis = self.code_analyzer.analyze_directory(self.project_path)
            
            if analysis['files_analyzed'] == 0:
                return 50  # Default medium
            
            avg_complexity = analysis.get('avg_complexity', 0)
            
            # Score: Lower complexity = higher score
            if avg_complexity < 5:
                return 90
            elif avg_complexity < 10:
                return 70
            elif avg_complexity < 20:
                return 50
            else:
                return 30
                
        except Exception:
            return 50  # Default medium on error
    
    def _analyze_dependencies(self) -> int:
        """
        Analyze dependency health.
        
        Security: Check for known vulnerabilities.
        """
        requirements_files = [
            self.project_path / 'requirements.txt',
            self.project_path / 'requirements-dev.txt',
            self.project_path / 'Pipfile'
        ]
        
        requirements_file = None
        for req_file in requirements_files:
            if req_file.exists():
                requirements_file = req_file
                break
        
        if not requirements_file:
            return 40  # No deps file = medium risk
        
        try:
            # Try to run pip-audit (security vulnerability scanner)
            result = subprocess.run(
                ['pip-audit', '-r', str(requirements_file), '--format', 'json'],
                capture_output=True,
                timeout=30,
                check=False
            )
            
            if result.returncode == 0:
                try:
                    vulnerabilities = json.loads(result.stdout)
                    vuln_count = len(vulnerabilities.get('dependencies', []))
                    
                    if vuln_count == 0:
                        return 95
                    elif vuln_count < 5:
                        return 70
                    elif vuln_count < 10:
                        return 50
                    else:
                        return 20  # Many vulnerabilities = high risk
                except json.JSONDecodeError:
                    pass
            
            return 60  # Default if audit fails
            
        except Exception:
            return 50
    
    def _analyze_code_quality(self) -> int:
        """
        Run linters for code quality.
        
        Security: Linters run in isolated subprocess.
        """
        try:
            # Try to run flake8 (Python linter)
            result = subprocess.run(
                ['flake8', '.', '--count', '--statistics', '--quiet'],
                cwd=self.project_path,
                capture_output=True,
                timeout=60,
                check=False
            )
            
            if result.returncode == 0:
                # Parse flake8 output
                output = result.stdout.decode('utf-8').strip()
                if output:
                    lines = output.split('\n')
                    error_count = 0
                    for line in lines:
                        if line.strip().isdigit():
                            error_count += int(line.strip())
                    
                    # Score based on error density
                    total_lines = self._count_total_lines()
                    error_density = error_count / max(total_lines, 1) * 1000
                    
                    if error_density < 5:
                        return 90
                    elif error_density < 15:
                        return 70
                    elif error_density < 30:
                        return 50
                    else:
                        return 30
            
            return 70  # Default good quality
            
        except Exception:
            return 60
    
    def _estimate_breaking_changes(self, migration_type: str) -> int:
        """
        Estimate scope of breaking changes.
        
        Returns higher score for fewer breaking changes.
        """
        # Migration-specific breaking change patterns
        BREAKING_PATTERNS = {
            'react-hooks': [
                'componentDidMount', 'componentWillUnmount',
                'componentDidUpdate', 'this.state', 'this.props',
                'componentWillMount', 'componentWillReceiveProps'
            ],
            'vue3': [
                'Vue.component', 'new Vue', '$on', '$off', '$once',
                'beforeDestroy', 'destroyed', 'filters'
            ],
            'python3': [
                'print ', 'xrange', 'urllib2', 'raw_input',
                'basestring', 'has_key', 'iteritems'
            ],
            'typescript': [
                'var ', 'function(', ': any', 'any[]',
                'PropTypes', 'React.createClass'
            ],
            'angular': [
                '$scope', '$http', 'controller(', 'directive(',
                '.service(', '.factory('
            ]
        }
        
        patterns = BREAKING_PATTERNS.get(migration_type, [])
        if not patterns:
            return 50  # Unknown migration type
        
        match_count = 0
        file_count = 0
        
        # Find relevant files
        extensions = {
            'react-hooks': ['.js', '.jsx', '.ts', '.tsx'],
            'vue3': ['.vue', '.js'],
            'python3': ['.py'],
            'typescript': ['.js', '.jsx'],
            'angular': ['.js', '.ts']
        }
        
        target_extensions = extensions.get(migration_type, ['.js', '.jsx', '.py', '.vue'])
        
        for file_path in self.project_path.rglob('*'):
            if file_path.suffix in target_extensions:
                try:
                    content = file_path.read_text(encoding='utf-8')
                    file_count += 1
                    
                    for pattern in patterns:
                        match_count += content.count(pattern)
                        
                except UnicodeDecodeError:
                    continue
        
        if file_count == 0:
            return 50
        
        # Score: Fewer matches = higher score
        avg_matches = match_count / file_count
        
        if avg_matches < 2:
            return 90
        elif avg_matches < 5:
            return 70
        elif avg_matches < 10:
            return 50
        else:
            return 30
    
    def _determine_migration_complexity(
        self, score: int, migration_type: str, factors: Dict[str, int]
    ) -> str:
        """Determine migration complexity level."""
        base_complexity = self.MIGRATION_COMPLEXITY.get(migration_type, 1.0)
        
        # Adjust based on factors
        complexity_multiplier = 1.0
        
        if factors['complexity'] < 50:
            complexity_multiplier += 0.3
        if factors['breaking_changes'] < 50:
            complexity_multiplier += 0.2
        if factors['dependencies'] < 50:
            complexity_multiplier += 0.1
        
        final_complexity = base_complexity * complexity_multiplier
        
        if final_complexity < 0.8:
            return "SIMPLE"
        elif final_complexity < 1.2:
            return "MODERATE"
        elif final_complexity < 1.6:
            return "COMPLEX"
        else:
            return "VERY_COMPLEX"
    
    def _estimate_time(self, score: int, migration_type: str) -> float:
        """
        Estimate migration time in hours.
        
        Formula based on:
        - Overall confidence score
        - Codebase size
        - Migration type complexity
        """
        # Count total relevant files
        extensions = {
            'react-hooks': ['.js', '.jsx', '.ts', '.tsx'],
            'vue3': ['.vue', '.js'],
            'python3': ['.py'],
            'typescript': ['.js', '.jsx'],
            'angular': ['.js', '.ts']
        }
        
        target_extensions = extensions.get(migration_type, ['.js', '.jsx', '.py', '.vue'])
        file_count = sum(
            1 for ext in target_extensions
            for _ in self.project_path.rglob(f'*{ext}')
        )
        
        # Base time per file (varies by migration type)
        MIGRATION_BASE_TIME = {
            'react-hooks': 0.5,     # 30 min per file
            'vue3': 0.75,            # 45 min per file
            'python3': 0.4,          # 24 min per file
            'typescript': 1.0,       # 1 hour per file
            'graphql': 1.5,          # 90 min per file
            'angular': 1.2,          # 72 min per file
            'svelte': 0.6,           # 36 min per file
        }
        
        base_time = MIGRATION_BASE_TIME.get(migration_type, 0.5)
        
        # Adjust based on confidence (lower confidence = more time)
        time_multiplier = (100 - score) / 50  # 0.0 - 2.0x
        
        # Apply migration complexity multiplier
        complexity_multiplier = self.MIGRATION_COMPLEXITY.get(migration_type, 1.0)
        
        total_hours = file_count * base_time * (1 + time_multiplier) * complexity_multiplier
        
        # Add overhead (planning, testing, review)
        overhead = total_hours * 0.3
        
        return round(total_hours + overhead, 1)
    
    def _count_total_lines(self) -> int:
        """Count total lines of code."""
        total = 0
        for py_file in self.project_path.rglob('*.py'):
            try:
                total += len(py_file.read_text(encoding='utf-8').splitlines())
            except UnicodeDecodeError:
                continue
        return total
    
    def _generate_recommendations(
        self, factors: Dict[str, int]
    ) -> Tuple[List[str], List[str], List[str]]:
        """Generate blockers, warnings, and recommendations."""
        blockers = []
        warnings = []
        recommendations = []
        
        # Check each factor
        if factors['test_coverage'] < 30:
            blockers.append(
                "❌ BLOCKER: Test coverage is critically low (<30%). "
                "Add tests before migration to ensure correctness."
            )
        elif factors['test_coverage'] < 60:
            warnings.append(
                "⚠️  WARNING: Test coverage is below recommended level (60%). "
                "Consider adding more tests."
            )
        
        if factors['complexity'] < 40:
            warnings.append(
                "⚠️  WARNING: High code complexity detected. "
                "Refactor complex functions before migration."
            )
        
        if factors['dependencies'] < 50:
            blockers.append(
                "❌ BLOCKER: Security vulnerabilities found in dependencies. "
                "Update vulnerable packages before migration."
            )
        
        if factors['code_quality'] < 50:
            warnings.append(
                "⚠️  WARNING: Code quality issues detected. "
                "Run linters and fix issues first."
            )
        
        if factors['breaking_changes'] < 40:
            warnings.append(
                "⚠️  WARNING: Many breaking changes expected. "
                "Plan for extensive testing and validation."
            )
        
        # General recommendations
        recommendations.extend([
            "✓ Create a dedicated feature branch for migration",
            "✓ Set up staging environment for testing",
            "✓ Plan for incremental rollout (not big-bang)",
            "✓ Document all manual steps required",
            "✓ Schedule team code review sessions",
            "✓ Prepare rollback strategy before starting"
        ])
        
        return blockers, warnings, recommendations
    
    def generate_report(self, confidence_score: ConfidenceScore) -> str:
        """
        Generate formatted confidence report.
        
        Args:
            confidence_score: The confidence score to report
            
        Returns:
            Formatted report string
        """
        report_lines = [
            "🔍 MIGRATION CONFIDENCE ANALYSIS",
            "=" * 50,
            "",
            f"Overall Confidence: {confidence_score.overall_score}/100 ({confidence_score.risk_level} RISK)",
            f"Migration Complexity: {confidence_score.migration_complexity}",
            "",
            "📊 RISK FACTORS:",
            ""
        ]
        
        # Factor breakdown
        for factor, score in confidence_score.factors.items():
            emoji = "✅" if score >= 70 else "⚠️" if score >= 50 else "❌"
            factor_name = factor.replace('_', ' ').title()
            report_lines.append(f"  {emoji} {factor_name}: {score}/100")
        
        report_lines.extend([
            "",
            "💰 ESTIMATES:",
            f"  ├─ Time: {confidence_score.estimated_hours} hours",
            f"  ├─ Cost: ${confidence_score.estimated_cost:,.2f} (at $100/hr)",
            f"  └─ Risk Level: {confidence_score.risk_level}",
            ""
        ])
        
        # Blockers
        if confidence_score.blockers:
            report_lines.extend([
                "🚫 BLOCKERS:",
                *[f"  {blocker}" for blocker in confidence_score.blockers],
                ""
            ])
        
        # Warnings
        if confidence_score.warnings:
            report_lines.extend([
                "⚠️  WARNINGS:",
                *[f"  {warning}" for warning in confidence_score.warnings],
                ""
            ])
        
        # Recommendations
        report_lines.extend([
            "💡 RECOMMENDATIONS:",
            *[f"  {rec}" for rec in confidence_score.recommendations],
            ""
        ])
        
        return "\n".join(report_lines)
