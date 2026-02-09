"""
Code complexity calculation utilities.

Calculates various complexity metrics:
- Cyclomatic complexity
- Cognitive complexity
- Maintainability index
- Technical debt ratio
"""

import ast
from pathlib import Path
from typing import Dict, List, Tuple

from ..security import SafeCodeAnalyzer


class ComplexityCalculator:
    """
    Calculates various code complexity metrics.
    
    Metrics:
    - Cyclomatic Complexity: Control flow complexity
    - Cognitive Complexity: How hard to understand
    - Maintainability Index: Overall maintainability
    - Technical Debt: Estimated effort to fix issues
    """
    
    def __init__(self, project_path: Path):
        """
        Initialize complexity calculator.
        
        Args:
            project_path: Path to project to analyze
        """
        self.project_path = Path(project_path)
        self.code_analyzer = SafeCodeAnalyzer()
    
    def calculate_project_complexity(self) -> Dict:
        """
        Calculate complexity metrics for entire project.
        
        Returns:
            Dict with complexity metrics
        """
        try:
            analysis = self.code_analyzer.analyze_directory(self.project_path)
            
            # Calculate additional metrics
            total_functions = len(analysis['functions'])
            total_classes = len(analysis['classes'])
            total_complexity = analysis['total_complexity']
            total_lines = analysis['total_lines']
            
            # Calculate averages
            avg_complexity = total_complexity / max(total_functions, 1)
            avg_lines_per_function = total_lines / max(total_functions, 1)
            
            # Calculate maintainability index
            maintainability_index = self._calculate_maintainability_index(
                total_lines, total_complexity, total_functions
            )
            
            # Calculate technical debt
            technical_debt = self._calculate_technical_debt(analysis)
            
            return {
                'total_files': analysis['files_analyzed'],
                'total_lines': total_lines,
                'total_functions': total_functions,
                'total_classes': total_classes,
                'total_complexity': total_complexity,
                'average_complexity': avg_complexity,
                'average_lines_per_function': avg_lines_per_function,
                'maintainability_index': maintainability_index,
                'technical_debt_hours': technical_debt,
                'complexity_distribution': self._get_complexity_distribution(analysis),
                'most_complex_files': self._get_most_complex_files(analysis)
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'total_files': 0,
                'total_lines': 0,
                'total_functions': 0,
                'total_classes': 0,
                'total_complexity': 0,
                'average_complexity': 0,
                'maintainability_index': 0,
                'technical_debt_hours': 0
            }
    
    def calculate_file_complexity(self, file_path: Path) -> Dict:
        """
        Calculate complexity metrics for a single file.
        
        Args:
            file_path: Path to file to analyze
            
        Returns:
            Dict with file complexity metrics
        """
        try:
            analysis = self.code_analyzer.analyze(file_path)
            
            if not analysis.get('parsed'):
                return {
                    'error': analysis.get('error', 'Failed to parse file'),
                    'file_path': str(file_path)
                }
            
            # Calculate metrics
            functions = analysis['functions']
            classes = analysis['classes']
            
            total_complexity = sum(f.get('complexity', 0) for f in functions)
            total_lines = analysis['line_count']
            
            # Cognitive complexity (simplified)
            cognitive_complexity = self._calculate_cognitive_complexity(file_path)
            
            # Maintainability index
            maintainability_index = self._calculate_maintainability_index(
                total_lines, total_complexity, len(functions)
            )
            
            return {
                'file_path': str(file_path),
                'total_lines': total_lines,
                'functions_count': len(functions),
                'classes_count': len(classes),
                'cyclomatic_complexity': total_complexity,
                'cognitive_complexity': cognitive_complexity,
                'maintainability_index': maintainability_index,
                'functions': functions,
                'classes': classes,
                'complexity_level': self._get_complexity_level(total_complexity)
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'file_path': str(file_path)
            }
    
    def _calculate_maintainability_index(
        self, 
        total_lines: int, 
        total_complexity: int, 
        function_count: int
    ) -> float:
        """
        Calculate maintainability index.
        
        Higher is better (0-100 scale).
        """
        if function_count == 0:
            return 100.0
        
        # Simplified maintainability index calculation
        # Based on Microsoft's maintainability index formula
        volume = total_lines * (1.0 if total_lines > 0 else 0.0)
        complexity = total_complexity
        functions = function_count
        
        # Maintainability Index (simplified)
        if volume > 0:
            mi = max(0, 
                171 - 5.2 * (volume ** 0.23) - 0.23 * complexity - 16.2 * (functions ** 0.5)
            )
        else:
            mi = 100
        
        # Scale to 0-100
        return min(100, max(0, mi))
    
    def _calculate_technical_debt(self, analysis: Dict) -> float:
        """
        Calculate technical debt in hours.
        
        Based on complexity and code quality issues.
        """
        total_complexity = analysis['total_complexity']
        total_lines = analysis['total_lines']
        file_count = analysis['files_analyzed']
        
        # Base technical debt (hours)
        debt = 0.0
        
        # Complexity debt
        if total_complexity > 1000:
            debt += (total_complexity - 1000) * 0.1  # 6 minutes per point over 1000
        elif total_complexity > 500:
            debt += (total_complexity - 500) * 0.05  # 3 minutes per point over 500
        
        # Size debt
        if total_lines > 50000:
            debt += (total_lines - 50000) / 1000 * 2  # 2 hours per 1000 lines over 50k
        
        # File count debt
        if file_count > 100:
            debt += (file_count - 100) * 0.5  # 30 minutes per file over 100
        
        return round(debt, 1)
    
    def _calculate_cognitive_complexity(self, file_path: Path) -> int:
        """
        Calculate cognitive complexity.
        
        Measures how hard the code is to understand.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            complexity = 0
            nesting_level = 0
            
            for node in ast.walk(tree):
                # Increment for nesting
                if isinstance(node, (ast.If, ast.While, ast.For, ast.With)):
                    complexity += 1 + nesting_level
                    nesting_level += 1
                elif isinstance(node, ast.BoolOp):
                    complexity += len(node.values) - 1 + nesting_level
                elif isinstance(node, ast.ExceptHandler):
                    complexity += 1 + nesting_level
                elif isinstance(node, ast.ListComp):
                    complexity += 1 + nesting_level
                # Reset nesting level when leaving block
                elif hasattr(node, 'body') and node.body:
                    # This is a bit simplified, but works for basic cases
                    pass
            
            return complexity
            
        except Exception:
            return 0
    
    def _get_complexity_distribution(self, analysis: Dict) -> Dict:
        """Get distribution of function complexities."""
        functions = analysis['functions']
        
        if not functions:
            return {'simple': 0, 'moderate': 0, 'complex': 0, 'very_complex': 0}
        
        distribution = {'simple': 0, 'moderate': 0, 'complex': 0, 'very_complex': 0}
        
        for func in functions:
            complexity = func.get('complexity', 0)
            if complexity <= 5:
                distribution['simple'] += 1
            elif complexity <= 10:
                distribution['moderate'] += 1
            elif complexity <= 20:
                distribution['complex'] += 1
            else:
                distribution['very_complex'] += 1
        
        return distribution
    
    def _get_most_complex_files(self, analysis: Dict, limit: int = 5) -> List[Dict]:
        """Get most complex files."""
        # This is a simplified version - in practice, you'd analyze each file
        # and sort by complexity
        
        # For now, return empty list as this would require additional analysis
        return []
    
    def _get_complexity_level(self, complexity: int) -> str:
        """Get complexity level description."""
        if complexity <= 10:
            return "LOW"
        elif complexity <= 20:
            return "MEDIUM"
        elif complexity <= 50:
            return "HIGH"
        else:
            return "VERY_HIGH"
    
    def generate_complexity_report(self, complexity_data: Dict) -> str:
        """
        Generate formatted complexity report.
        
        Args:
            complexity_data: Complexity analysis results
            
        Returns:
            Formatted report string
        """
        if 'error' in complexity_data:
            return f"❌ Error calculating complexity: {complexity_data['error']}"
        
        report_lines = [
            "📊 CODE COMPLEXITY ANALYSIS",
            "=" * 50,
            "",
            "📈 OVERALL METRICS:",
            f"  Total Files: {complexity_data['total_files']}",
            f"  Total Lines: {complexity_data['total_lines']:,}",
            f"  Total Functions: {complexity_data['total_functions']}",
            f"  Total Classes: {complexity_data['total_classes']}",
            "",
            "🎯 COMPLEXITY SCORES:",
            f"  Cyclomatic Complexity: {complexity_data['total_complexity']}",
            f"  Average Complexity: {complexity_data['average_complexity']:.1f}",
            f"  Maintainability Index: {complexity_data['maintainability_index']:.1f}/100",
            f"  Technical Debt: {complexity_data['technical_debt_hours']:.1f} hours",
            ""
        ]
        
        # Complexity distribution
        if 'complexity_distribution' in complexity_data:
            dist = complexity_data['complexity_distribution']
            report_lines.extend([
                "📊 COMPLEXITY DISTRIBUTION:",
                f"  Simple (≤5): {dist['simple']} functions",
                f"  Moderate (6-10): {dist['moderate']} functions", 
                f"  Complex (11-20): {dist['complex']} functions",
                f"  Very Complex (>20): {dist['very_complex']} functions",
                ""
            ])
        
        # Assessment
        mi = complexity_data['maintainability_index']
        avg_complexity = complexity_data['average_complexity']
        
        report_lines.extend([
            "🔍 ASSESSMENT:",
        ])
        
        if mi >= 85:
            report_lines.append("  ✅ Excellent maintainability")
        elif mi >= 70:
            report_lines.append("  ✅ Good maintainability")
        elif mi >= 50:
            report_lines.append("  ⚠️  Moderate maintainability - consider refactoring")
        else:
            report_lines.append("  ❌ Poor maintainability - refactoring required")
        
        if avg_complexity <= 5:
            report_lines.append("  ✅ Low complexity")
        elif avg_complexity <= 10:
            report_lines.append("  ⚠️  Moderate complexity")
        elif avg_complexity <= 20:
            report_lines.append("  ⚠️  High complexity")
        else:
            report_lines.append("  ❌ Very high complexity")
        
        return "\n".join(report_lines)
