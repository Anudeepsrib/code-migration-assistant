import re
from pathlib import Path
from .base import BaseAnalyzer, MigrationPlan, MigrationStep

class ReactClassToHooksAnalyzer(BaseAnalyzer):
    def name(self) -> str:
        return "react-class-to-hooks"

    def analyze(self, file_path: Path) -> MigrationPlan:
        plan = MigrationPlan()
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Simplified Regex-based detection for POC
        # Look for class components
        class_regex = re.compile(r'class\s+(\w+)\s+extends\s+(?:React\.)?Component\s*{')
        
        match = class_regex.search(content)
        if match:
            component_name = match.group(1)
            
            # Extract render method content (very naive)
            render_regex = re.compile(r'render\s*\(\)\s*{([\s\S]*?)}')
            render_match = render_regex.search(content)
            
            if render_match:
                render_body = render_match.group(1).strip()
                # Remove 'return' to get just the JSX (simplification)
                # In real world, we'd need to parse this properly
                
                new_code = f"const {component_name} = () => {{\n"
                new_code += f"  {render_body}\n"
                new_code += "};\n"
                new_code += f"export default {component_name};"

                plan.add_step(MigrationStep(
                    description=f"Convert class component '{component_name}' to functional component with Hooks",
                    old_code=match.group(0) + " ... }", # Just a snippet
                    new_code=new_code,
                    file_path=str(file_path)
                ))
                
                # Check for state usage
                if "this.state" in content:
                    plan.add_breaking_change("State detected: Manual conversion to useState hook required.")
                
                # Check for lifecycle methods
                if "componentDidMount" in content:
                     plan.add_breaking_change("Lifecycle method detected: Manual conversion to useEffect hook required.")

        return plan
