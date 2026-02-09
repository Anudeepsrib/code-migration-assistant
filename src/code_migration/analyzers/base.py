from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path

class MigrationStep:
    def __init__(self, description: str, old_code: str, new_code: str, file_path: str):
        self.description = description
        self.old_code = old_code
        self.new_code = new_code
        self.file_path = file_path

class MigrationPlan:
    def __init__(self):
        self.steps: List[MigrationStep] = []
        self.breaking_changes: List[str] = []
        self.dependencies: List[str] = []

    def add_step(self, step: MigrationStep):
        self.steps.append(step)

    def add_breaking_change(self, change: str):
        self.breaking_changes.append(change)

class BaseAnalyzer(ABC):
    @abstractmethod
    def analyze(self, file_path: Path) -> MigrationPlan:
        """
        Analyze the file and return a migration plan.
        """
        pass

    @abstractmethod
    def name(self) -> str:
        """
        Return the name of the analyzer.
        """
        pass
