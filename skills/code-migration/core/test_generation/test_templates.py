"""
Test Templates for common test scenarios.

Provides pre-built test templates:
- Unit test templates
- Integration test templates
- Component test templates
- E2E test templates
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class TestTemplate:
    """Test template definition."""
    template_id: str
    name: str
    description: str
    template_type: str
    language: str
    code: str
    placeholders: List[str]
    tags: List[str]
    created_at: str


class TestTemplates:
    """
    Pre-built test templates library.
    
    Features:
    - Unit test templates
    - Integration test templates
    - Component test templates
    - E2E test templates
    """
    
    def __init__(self, project_path: Path):
        """
        Initialize test templates.
        
        Args:
            project_path: Path to project directory
        """
        self.project_path = Path(project_path)
        self.templates: Dict[str, TestTemplate] = {}
        
        # Initialize built-in templates
        self._initialize_builtin_templates()
    
    def get_template(self, template_id: str) -> Optional[TestTemplate]:
        """
        Get a test template by ID.
        
        Args:
            template_id: Template ID
            
        Returns:
            TestTemplate or None
        """
        return self.templates.get(template_id)
    
    def find_templates(
        self,
        template_type: Optional[str] = None,
        language: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[TestTemplate]:
        """
        Find templates matching criteria.
        
        Args:
            template_type: Optional type filter
            language: Optional language filter
            tags: Optional tags filter
            
        Returns:
            List of matching templates
        """
        matches = list(self.templates.values())
        
        if template_type:
            matches = [t for t in matches if t.template_type == template_type]
        
        if language:
            matches = [t for t in matches if t.language == language]
        
        if tags:
            matches = [
                t for t in matches
                if any(tag in t.tags for tag in tags)
            ]
        
        return matches
    
    def render_template(
        self,
        template_id: str,
        values: Dict[str, str]
    ) -> Optional[str]:
        """
        Render a template with provided values.
        
        Args:
            template_id: Template ID
            values: Values for placeholders
            
        Returns:
            Rendered template string or None
        """
        template = self.templates.get(template_id)
        if not template:
            return None
        
        rendered = template.code
        
        # Replace placeholders
        for placeholder, value in values.items():
            rendered = rendered.replace(f"{{{placeholder}}}", value)
        
        return rendered
    
    def _initialize_builtin_templates(self) -> None:
        """Initialize built-in test templates."""
        # Python unit test templates
        self._add_template(
            template_id='pytest_basic_unit',
            name='Basic Pytest Unit Test',
            description='Basic unit test template using pytest',
            template_type='unit',
            language='python',
            code='''
def test_{function_name}():
    """Test {function_name} basic functionality."""
    # Arrange
    {arrange_code}
    
    # Act
    result = {function_name}({arguments})
    
    # Assert
    assert result is not None
    {assertions}
''',
            placeholders=['function_name', 'arrange_code', 'arguments', 'assertions'],
            tags=['python', 'pytest', 'unit', 'basic']
        )
        
        self._add_template(
            template_id='pytest_parametrized',
            name='Parametrized Pytest Test',
            description='Parametrized test for multiple test cases',
            template_type='unit',
            language='python',
            code='''
import pytest

@pytest.mark.parametrize("input_value,expected", [
    ({test_case_1}),
    ({test_case_2}),
    ({test_case_3}),
])
def test_{function_name}_parametrized(input_value, expected):
    """Test {function_name} with multiple inputs."""
    result = {function_name}(input_value)
    assert result == expected
''',
            placeholders=['function_name', 'test_case_1', 'test_case_2', 'test_case_3'],
            tags=['python', 'pytest', 'unit', 'parametrized']
        )
        
        self._add_template(
            template_id='pytest_fixture',
            name='Pytest Test with Fixtures',
            description='Unit test using pytest fixtures',
            template_type='unit',
            language='python',
            code='''
import pytest

@pytest.fixture
def {fixture_name}():
    """Create test fixture."""
    {fixture_setup}
    return {fixture_return}

def test_{function_name}({fixture_name}):
    """Test {function_name} with fixture."""
    # Use fixture in test
    result = {function_name}({fixture_name})
    assert result is not None
''',
            placeholders=['fixture_name', 'fixture_setup', 'fixture_return', 'function_name'],
            tags=['python', 'pytest', 'unit', 'fixture']
        )
        
        # JavaScript/React test templates
        self._add_template(
            template_id='jest_component_render',
            name='Jest Component Render Test',
            description='Test React component rendering',
            template_type='component',
            language='javascript',
            code='''
import React from 'react';
import { render, screen } from '@testing-library/react';
import {component_name} from '../{component_path}';

describe('{component_name}', () => {
    test('renders without crashing', () => {
        render(<{component_name} />);
        expect(screen.getByTestId('{test_id}')).toBeInTheDocument();
    });
    
    test('renders with props', () => {
        const props = {initial_props};
        render(<{component_name} {...props} />);
        expect(screen.getByText(props.{prop_name})).toBeInTheDocument();
    });
});
''',
            placeholders=['component_name', 'component_path', 'test_id', 'initial_props', 'prop_name'],
            tags=['javascript', 'jest', 'react', 'component']
        )
        
        self._add_template(
            template_id='jest_hook_test',
            name='React Hook Test',
            description='Test custom React hook',
            template_type='unit',
            language='javascript',
            code='''
import { renderHook } from '@testing-library/react-hooks';
import { {hook_name} } from '../{hook_path}';

describe('{hook_name}', () => {
    test('initializes with default value', () => {
        const { result } = renderHook(() => {hook_name}());
        expect(result.current).toBeDefined();
    });
    
    test('updates value on action', () => {
        const { result } = renderHook(() => {hook_name}({initial_value}));
        
        act(() => {
            result.current.{action_method}();
        });
        
        expect(result.current.{value_property}).toBe({expected_value});
    });
});
''',
            placeholders=['hook_name', 'hook_path', 'initial_value', 'action_method', 'value_property', 'expected_value'],
            tags=['javascript', 'jest', 'react', 'hook']
        )
        
        self._add_template(
            template_id='jest_async_test',
            name='Async Function Test',
            description='Test async JavaScript functions',
            template_type='unit',
            language='javascript',
            code='''
describe('{function_name}', () => {
    test('resolves with expected data', async () => {
        const result = await {function_name}({arguments});
        expect(result).toEqual({expected_result});
    });
    
    test('rejects on error', async () => {
        await expect({function_name}({error_arguments})).rejects.toThrow();
    });
});
''',
            placeholders=['function_name', 'arguments', 'expected_result', 'error_arguments'],
            tags=['javascript', 'jest', 'async', 'promise']
        )
        
        # Integration test templates
        self._add_template(
            template_id='pytest_integration',
            name='Integration Test',
            description='Integration test with database/API',
            template_type='integration',
            language='python',
            code='''
import pytest

@pytest.fixture
def client():
    """Create test client."""
    from app import create_app
    app = create_app(testing=True)
    with app.test_client() as client:
        yield client

@pytest.fixture
def db():
    """Set up test database."""
    from app import db
    db.create_all()
    yield db
    db.drop_all()

def test_{endpoint_name}_integration(client, db):
    """Test {endpoint_name} endpoint."""
    # Prepare test data
    {test_data_setup}
    
    # Make request
    response = client.{http_method}('{endpoint_url}')
    
    # Assertions
    assert response.status_code == {expected_status}
    assert {response_assertion}
''',
            placeholders=['endpoint_name', 'test_data_setup', 'http_method', 'endpoint_url', 'expected_status', 'response_assertion'],
            tags=['python', 'pytest', 'integration', 'api']
        )
        
        # Vue component test template
        self._add_template(
            template_id='vue_component_test',
            name='Vue Component Test',
            description='Test Vue component with Vue Test Utils',
            template_type='component',
            language='javascript',
            code='''
import { mount } from '@vue/test-utils';
import {component_name} from '@/components/{component_path}';

describe('{component_name}', () => {
    test('renders correctly', () => {
        const wrapper = mount({component_name});
        expect(wrapper.element).toMatchSnapshot();
    });
    
    test('emits event on action', async () => {
        const wrapper = mount({component_name});
        await wrapper.find('button').trigger('click');
        expect(wrapper.emitted()).toHaveProperty('{event_name}');
    });
    
    test('updates data correctly', async () => {
        const wrapper = mount({component_name});
        await wrapper.setData({ {data_key}: {data_value} });
        expect(wrapper.vm.{data_key}).toBe({data_value});
    });
});
''',
            placeholders=['component_name', 'component_path', 'event_name', 'data_key', 'data_value'],
            tags=['javascript', 'vue', 'component', 'jest']
        )
        
        # Snapshot test template
        self._add_template(
            template_id='snapshot_test',
            name='Snapshot Test',
            description='Snapshot testing for components',
            template_type='snapshot',
            language='javascript',
            code='''
import React from 'react';
import renderer from 'react-test-renderer';
import {component_name} from '../{component_path}';

describe('{component_name} Snapshots', () => {
    test('matches snapshot', () => {
        const tree = renderer
            .create(<{component_name} {props} />)
            .toJSON();
        expect(tree).toMatchSnapshot();
    });
});
''',
            placeholders=['component_name', 'component_path', 'props'],
            tags=['javascript', 'react', 'snapshot']
        )
    
    def _add_template(
        self,
        template_id: str,
        name: str,
        description: str,
        template_type: str,
        language: str,
        code: str,
        placeholders: List[str],
        tags: List[str]
    ) -> None:
        """Add a test template."""
        template = TestTemplate(
            template_id=template_id,
            name=name,
            description=description,
            template_type=template_type,
            language=language,
            code=code,
            placeholders=placeholders,
            tags=tags,
            created_at=datetime.now().isoformat()
        )
        
        self.templates[template_id] = template
    
    def list_template_categories(self) -> Dict[str, List[TestTemplate]]:
        """
        List templates grouped by category.
        
        Returns:
            Dict mapping categories to templates
        """
        categories: Dict[str, List[TestTemplate]] = {}
        
        for template in self.templates.values():
            if template.template_type not in categories:
                categories[template.template_type] = []
            categories[template.template_type].append(template)
        
        return categories
    
    def get_template_statistics(self) -> Dict:
        """
        Get template statistics.
        
        Returns:
            Statistics dictionary
        """
        languages = set(t.language for t in self.templates.values())
        types = set(t.template_type for t in self.templates.values())
        
        return {
            'total_templates': len(self.templates),
            'languages': list(languages),
            'types': list(types),
            'templates_by_type': {
                t: len([tm for tm in self.templates.values() if tm.template_type == t])
                for t in types
            }
        }
