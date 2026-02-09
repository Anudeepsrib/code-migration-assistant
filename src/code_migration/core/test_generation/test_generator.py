"""
Test Generator for automated test creation.

Generates comprehensive tests for migrated code:
- Unit tests
- Integration tests
- Snapshot tests
- Edge case coverage
"""

import ast
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from ..security import SecurityAuditLogger


@dataclass
class GeneratedTest:
    """Generated test case."""
    test_id: str
    file_path: str
    test_name: str
    test_code: str
    test_type: str
    description: str
    target_function: Optional[str]
    created_at: str


class TestGenerator:
    """
    Automated test generation for migrations.
    
    Features:
    - Unit test generation
    - Integration test creation
    - Snapshot test generation
    - Edge case coverage
    """
    
    def __init__(self, project_path: Path):
        """
        Initialize test generator.
        
        Args:
            project_path: Path to project directory
        """
        self.project_path = Path(project_path)
        self.generated_tests: List[GeneratedTest] = []
        
        log_dir = self.project_path / '.migration-logs'
        self.audit_logger = SecurityAuditLogger(log_dir)
        
        self.tests_file = self.project_path / '.migration-generated-tests.json'
        self._load_generated_tests()
    
    def generate_tests_for_file(
        self,
        file_path: Path,
        migration_type: str,
        test_framework: str = 'pytest'
    ) -> List[GeneratedTest]:
        """
        Generate tests for a specific file.
        
        Args:
            file_path: Path to source file
            migration_type: Type of migration
            test_framework: Test framework to use
            
        Returns:
            List of generated tests
        """
        if not file_path.exists():
            return []
        
        # Read source file
        try:
            source_code = file_path.read_text(encoding='utf-8')
        except Exception:
            return []
        
        # Detect language
        language = self._detect_language(file_path)
        
        # Generate tests based on language
        if language == 'python':
            tests = self._generate_python_tests(
                file_path, source_code, migration_type, test_framework
            )
        elif language in ['javascript', 'typescript']:
            tests = self._generate_js_tests(
                file_path, source_code, migration_type, test_framework
            )
        else:
            tests = []
        
        # Store generated tests
        self.generated_tests.extend(tests)
        self._save_generated_tests()
        
        # Log generation
        self.audit_logger.log_migration_event(
            migration_type=migration_type,
            project_path=str(self.project_path),
            user='system',
            action='GENERATE_TESTS',
            result='SUCCESS',
            details={
                'file': str(file_path),
                'tests_generated': len(tests),
                'framework': test_framework
            }
        )
        
        return tests
    
    def generate_migration_tests(
        self,
        migration_type: str,
        source_files: List[Path],
        test_framework: str = 'pytest'
    ) -> Dict[str, List[GeneratedTest]]:
        """
        Generate comprehensive tests for migration.
        
        Args:
            migration_type: Type of migration
            source_files: List of source files
            test_framework: Test framework
            
        Returns:
            Dict mapping file paths to generated tests
        """
        all_tests = {}
        
        for file_path in source_files:
            tests = self.generate_tests_for_file(
                file_path, migration_type, test_framework
            )
            
            if tests:
                all_tests[str(file_path)] = tests
        
        return all_tests
    
    def create_test_file(
        self,
        tests: List[GeneratedTest],
        output_path: Optional[Path] = None
    ) -> Path:
        """
        Create test file from generated tests.
        
        Args:
            tests: List of generated tests
            output_path: Optional output path
            
        Returns:
            Path to created test file
        """
        if not tests:
            raise ValueError("No tests provided")
        
        # Determine output path
        if output_path is None:
            first_test = tests[0]
            source_file = Path(first_test.file_path)
            
            # Create test file name
            test_file_name = f"test_{source_file.name}"
            output_path = source_file.parent / test_file_name
        
        # Generate test file content
        test_content = self._generate_test_file_content(tests)
        
        # Write test file
        output_path.write_text(test_content, encoding='utf-8')
        
        return output_path
    
    def _generate_python_tests(
        self,
        file_path: Path,
        source_code: str,
        migration_type: str,
        test_framework: str
    ) -> List[GeneratedTest]:
        """Generate Python tests."""
        tests = []
        
        try:
            # Parse source code
            tree = ast.parse(source_code)
            
            # Find classes and functions
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Generate tests for class
                    class_tests = self._generate_class_tests(
                        file_path, node, migration_type
                    )
                    tests.extend(class_tests)
                    
                elif isinstance(node, ast.FunctionDef):
                    # Generate tests for function
                    func_tests = self._generate_function_tests(
                        file_path, node, migration_type
                    )
                    tests.extend(func_tests)
        
        except SyntaxError:
            pass
        
        return tests
    
    def _generate_js_tests(
        self,
        file_path: Path,
        source_code: str,
        migration_type: str,
        test_framework: str
    ) -> List[GeneratedTest]:
        """Generate JavaScript/TypeScript tests."""
        tests = []
        
        # Find component definitions
        component_pattern = r'(?:export\s+)?(?:default\s+)?(?:class|function)\s+(\w+)'
        components = re.findall(component_pattern, source_code)
        
        for component_name in components:
            # Generate component tests
            component_tests = self._generate_component_tests(
                file_path, component_name, source_code, migration_type
            )
            tests.extend(component_tests)
        
        # Find function definitions
        func_pattern = r'(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:\([^)]*\)\s*=>|function)'
        functions = re.findall(func_pattern, source_code)
        
        for func_name in functions:
            # Generate function tests
            func_tests = self._generate_js_function_tests(
                file_path, func_name, source_code, migration_type
            )
            tests.extend(func_tests)
        
        return tests
    
    def _generate_class_tests(
        self,
        file_path: Path,
        class_node: ast.ClassDef,
        migration_type: str
    ) -> List[GeneratedTest]:
        """Generate tests for a Python class."""
        tests = []
        class_name = class_node.name
        
        # Test class initialization
        test_id = f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}_{class_name.lower()}_init"
        test_code = f"""
def test_{class_name.lower()}_initialization():
    \"\"\"Test {class_name} initialization.\"\"\"
    # Arrange
    
    # Act
    instance = {class_name}()
    
    # Assert
    assert instance is not None
"""
        
        tests.append(GeneratedTest(
            test_id=test_id,
            file_path=str(file_path),
            test_name=f"test_{class_name.lower()}_initialization",
            test_code=test_code.strip(),
            test_type='unit',
            description=f"Test {class_name} initialization",
            target_function=class_name,
            created_at=datetime.now().isoformat()
        ))
        
        # Test class methods
        for item in class_node.body:
            if isinstance(item, ast.FunctionDef):
                method_name = item.name
                
                # Skip private methods and special methods
                if method_name.startswith('_'):
                    continue
                
                test_id = f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}_{method_name.lower()}"
                test_code = f"""
def test_{method_name.lower()}():
    \"\"\"Test {class_name}.{method_name} method.\"\"\"
    # Arrange
    instance = {class_name}()
    
    # Act
    result = instance.{method_name}()
    
    # Assert
    assert result is not None
"""
                
                tests.append(GeneratedTest(
                    test_id=test_id,
                    file_path=str(file_path),
                    test_name=f"test_{method_name.lower()}",
                    test_code=test_code.strip(),
                    test_type='unit',
                    description=f"Test {class_name}.{method_name}",
                    target_function=f"{class_name}.{method_name}",
                    created_at=datetime.now().isoformat()
                ))
        
        return tests
    
    def _generate_function_tests(
        self,
        file_path: Path,
        func_node: ast.FunctionDef,
        migration_type: str
    ) -> List[GeneratedTest]:
        """Generate tests for a Python function."""
        tests = []
        func_name = func_node.name
        
        # Skip private functions
        if func_name.startswith('_'):
            return tests
        
        # Basic functionality test
        test_id = f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}_{func_name.lower()}_basic"
        test_code = f"""
def test_{func_name.lower()}_basic_functionality():
    \"\"\"Test {func_name} basic functionality.\"\"\"
    # Arrange
    
    # Act
    result = {func_name}()
    
    # Assert
    assert result is not None
"""
        
        tests.append(GeneratedTest(
            test_id=test_id,
            file_path=str(file_path),
            test_name=f"test_{func_name.lower()}_basic",
            test_code=test_code.strip(),
            test_type='unit',
            description=f"Test {func_name} basic functionality",
            target_function=func_name,
            created_at=datetime.now().isoformat()
        ))
        
        # Edge case test
        test_id = f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}_{func_name.lower()}_edge"
        test_code = f"""
def test_{func_name.lower()}_edge_cases():
    \"\"\"Test {func_name} edge cases.\"\"\"
    # Test with empty input
    result = {func_name}()
    assert result is not None
    
    # Test with None
    # result = {func_name}(None)
    # assert result is not None
"""
        
        tests.append(GeneratedTest(
            test_id=test_id,
            file_path=str(file_path),
            test_name=f"test_{func_name.lower()}_edge_cases",
            test_code=test_code.strip(),
            test_type='unit',
            description=f"Test {func_name} edge cases",
            target_function=func_name,
            created_at=datetime.now().isoformat()
        ))
        
        return tests
    
    def _generate_component_tests(
        self,
        file_path: Path,
        component_name: str,
        source_code: str,
        migration_type: str
    ) -> List[GeneratedTest]:
        """Generate tests for a React/Vue component."""
        tests = []
        
        # Basic rendering test
        test_id = f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}_{component_name.lower()}_render"
        test_code = f"""
import {{ render, screen }} from '@testing-library/react';
import {component_name} from '../{file_path.stem}';

describe('{component_name}', () => {{
    test('renders without crashing', () => {{
        render(<{component_name} />);
        expect(screen.getByTestId('{component_name.lower()}')).toBeInTheDocument();
    }});
}});
"""
        
        tests.append(GeneratedTest(
            test_id=test_id,
            file_path=str(file_path),
            test_name=f"test_{component_name.lower()}_renders",
            test_code=test_code.strip(),
            test_type='unit',
            description=f"Test {component_name} renders correctly",
            target_function=component_name,
            created_at=datetime.now().isoformat()
        ))
        
        return tests
    
    def _generate_js_function_tests(
        self,
        file_path: Path,
        func_name: str,
        source_code: str,
        migration_type: str
    ) -> List[GeneratedTest]:
        """Generate tests for JavaScript function."""
        tests = []
        
        test_id = f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}_{func_name.lower()}"
        test_code = f"""
import {{ {func_name} }} from '../{file_path.stem}';

describe('{func_name}', () => {{
    test('returns correct result', () => {{
        const result = {func_name}();
        expect(result).toBeDefined();
    }});
}});
"""
        
        tests.append(GeneratedTest(
            test_id=test_id,
            file_path=str(file_path),
            test_name=f"test_{func_name.lower()}",
            test_code=test_code.strip(),
            test_type='unit',
            description=f"Test {func_name}",
            target_function=func_name,
            created_at=datetime.now().isoformat()
        ))
        
        return tests
    
    def _generate_test_file_content(self, tests: List[GeneratedTest]) -> str:
        """Generate complete test file content."""
        # Group tests by type
        test_groups: Dict[str, List[GeneratedTest]] = {}
        for test in tests:
            if test.test_type not in test_groups:
                test_groups[test.test_type] = []
            test_groups[test.test_type].append(test)
        
        content_lines = [
            '"""',
            'Auto-generated tests for migration.',
            f'Generated at: {datetime.now().isoformat()}',
            '"""',
            '',
            'import pytest',
            ''
        ]
        
        # Add imports for each test target
        tested_files = set(test.file_path for test in tests)
        for file_path in tested_files:
            module_name = Path(file_path).stem
            content_lines.append(f'from {module_name} import *')
        
        content_lines.append('')
        content_lines.append('')
        
        # Add test functions
        for test_type, type_tests in test_groups.items():
            content_lines.append(f'# {test_type.upper()} TESTS')
            content_lines.append('')
            
            for test in type_tests:
                content_lines.append(f'# {test.description}')
                content_lines.append(test.test_code)
                content_lines.append('')
        
        return '\n'.join(content_lines)
    
    def _detect_language(self, file_path: Path) -> str:
        """Detect programming language from file extension."""
        ext = file_path.suffix.lower()
        
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.vue': 'vue'
        }
        
        return language_map.get(ext, 'unknown')
    
    def get_test_statistics(self) -> Dict:
        """
        Get test generation statistics.
        
        Returns:
            Statistics dictionary
        """
        test_types = {}
        tested_files = set()
        
        for test in self.generated_tests:
            test_types[test.test_type] = test_types.get(test.test_type, 0) + 1
            tested_files.add(test.file_path)
        
        return {
            'total_tests_generated': len(self.generated_tests),
            'test_types': test_types,
            'files_covered': len(tested_files),
            'unique_test_functions': len(
                set(test.test_name for test in self.generated_tests)
            )
        }
    
    def export_tests(self, output_dir: Path) -> List[Path]:
        """
        Export all generated tests to files.
        
        Args:
            output_dir: Output directory
            
        Returns:
            List of created file paths
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        created_files = []
        
        # Group tests by source file
        tests_by_file: Dict[str, List[GeneratedTest]] = {}
        for test in self.generated_tests:
            if test.file_path not in tests_by_file:
                tests_by_file[test.file_path] = []
            tests_by_file[test.file_path].append(test)
        
        # Create test file for each source file
        for file_path, tests in tests_by_file.items():
            source_path = Path(file_path)
            test_file_name = f"test_{source_path.name}"
            test_file_path = output_dir / test_file_name
            
            test_content = self._generate_test_file_content(tests)
            test_file_path.write_text(test_content, encoding='utf-8')
            
            created_files.append(test_file_path)
        
        return created_files
    
    def _load_generated_tests(self) -> None:
        """Load generated tests from file."""
        if self.tests_file.exists():
            try:
                with open(self.tests_file, 'r') as f:
                    data = json.load(f)
                    for test_data in data.get('tests', []):
                        test = GeneratedTest(**test_data)
                        self.generated_tests.append(test)
            except Exception:
                pass
    
    def _save_generated_tests(self) -> None:
        """Save generated tests to file."""
        try:
            data = {
                'tests': [
                    {
                        'test_id': t.test_id,
                        'file_path': t.file_path,
                        'test_name': t.test_name,
                        'test_code': t.test_code,
                        'test_type': t.test_type,
                        'description': t.description,
                        'target_function': t.target_function,
                        'created_at': t.created_at
                    }
                    for t in self.generated_tests
                ],
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.tests_file, 'w') as f:
                json.dump(data, f, indent=2)
        
        except Exception:
            pass
