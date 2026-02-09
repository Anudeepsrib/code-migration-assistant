"""
Migration confidence assessment module.

Provides AI-powered pre-migration risk assessment:
- Codebase complexity analysis
- Test coverage evaluation
- Dependency health checking
- Breaking change estimation
- Cost and time predictions
"""

from .scorer import ConfidenceScore, MigrationConfidenceAnalyzer
from .risk_analyzer import RiskAnalyzer
from .complexity_calculator import ComplexityCalculator

__all__ = [
    'ConfidenceScore',
    'MigrationConfidenceAnalyzer',
    'RiskAnalyzer',
    'ComplexityCalculator'
]
