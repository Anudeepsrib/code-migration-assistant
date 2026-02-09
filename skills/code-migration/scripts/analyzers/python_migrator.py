import ast
from pathlib import Path
from .base import BaseAnalyzer, MigrationPlan, MigrationStep

class Python2To3Analyzer(BaseAnalyzer):
    def name(self) -> str:
        return "python-2-to-3"

    def analyze(self, file_path: Path) -> MigrationPlan:
        plan = MigrationPlan()
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        try:
            tree = ast.parse(content)
        except SyntaxError:
             plan.add_breaking_change("Syntax Error: File could not be parsed. It might contain valid Python 2 syntax that is invalid in Python 3 (e.g., print statement).")
             return plan

        for node in ast.walk(tree):
            # Example: Check for print statement (Python 2) - AST structure differs
            # In Python 3, print is a Call. In Python 2, it's a Print node.
            # However, ast.parse uses the python version running the script (Python 3).
            # So standard python 2 print statement will raise SyntaxError above.
            
            # Let's look for something that parses in Py3 but is "old style" or commonly changed
            # e.g., using format() instead of f-strings (Modernization)
            
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute) and node.func.attr == 'format':
                     plan.add_step(MigrationStep(
                        description="Suggestion: Use f-strings for better readability (Python 3.6+)",
                        old_code=f"str.format(...)", # We'd need source segment extraction here
                        new_code=f"f'...'",
                        file_path=str(file_path)
                    ))
        
        # Simple text-based checks for things that might not be breaking syntax but are Py2 specific
        if "xrange(" in content:
             plan.add_step(MigrationStep(
                description="Replace 'xrange' with 'range'",
                old_code="xrange(...)",
                new_code="range(...)",
                file_path=str(file_path)
            ))
            
        return plan
