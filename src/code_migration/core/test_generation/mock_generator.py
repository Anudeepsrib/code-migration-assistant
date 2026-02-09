"""
Mock Generator for creating test mocks.

Generates mocks and stubs for:
- Function mocking
- Module mocking
- API mocking
- Database mocking
"""

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from ..security import SecurityAuditLogger


@dataclass
class GeneratedMock:
    """Generated mock configuration."""
    mock_id: str
    target_function: str
    mock_code: str
    mock_type: str
    description: str
    created_at: str


class MockGenerator:
    """
    Automated mock generation for tests.
    
    Features:
    - Function mocking
    - Module mocking
    - API mocking
    - Database mocking
    """
    
    def __init__(self, project_path: Path):
        """
        Initialize mock generator.
        
        Args:
            project_path: Path to project directory
        """
        self.project_path = Path(project_path)
        self.generated_mocks: Dict[str, GeneratedMock] = {}
        
        log_dir = self.project_path / '.migration-logs'
        self.audit_logger = SecurityAuditLogger(log_dir)
        
        self.mocks_file = self.project_path / '.migration-mocks.json'
        self._load_generated_mocks()
    
    def generate_mock_for_function(
        self,
        function_name: str,
        language: str,
        mock_type: str = 'default',
        return_value: Optional[str] = None
    ) -> GeneratedMock:
        """
        Generate mock for a function.
        
        Args:
            function_name: Name of function to mock
            language: Programming language
            mock_type: Type of mock (default, spy, stub)
            return_value: Optional return value
            
        Returns:
            GeneratedMock configuration
        """
        mock_id = f"mock_{datetime.now().strftime('%Y%m%d%H%M%S')}_{function_name}"
        
        # Generate mock code based on language
        if language == 'python':
            mock_code = self._generate_python_mock(function_name, mock_type, return_value)
        elif language in ['javascript', 'typescript']:
            mock_code = self._generate_js_mock(function_name, mock_type, return_value)
        else:
            mock_code = f"# Mock for {function_name}"
        
        mock = GeneratedMock(
            mock_id=mock_id,
            target_function=function_name,
            mock_code=mock_code,
            mock_type=mock_type,
            description=f"Mock for {function_name}",
            created_at=datetime.now().isoformat()
        )
        
        self.generated_mocks[mock_id] = mock
        self._save_generated_mocks()
        
        self.audit_logger.log_migration_event(
            migration_type='mock-generation',
            project_path=str(self.project_path),
            user='system',
            action='GENERATE_MOCK',
            result='SUCCESS',
            details={
                'function': function_name,
                'language': language,
                'mock_type': mock_type
            }
        )
        
        return mock
    
    def generate_api_mock(
        self,
        endpoint: str,
        method: str,
        response_data: Optional[Dict] = None,
        status_code: int = 200
    ) -> GeneratedMock:
        """
        Generate API endpoint mock.
        
        Args:
            endpoint: API endpoint URL
            method: HTTP method
            response_data: Mock response data
            status_code: HTTP status code
            
        Returns:
            GeneratedMock configuration
        """
        mock_id = f"mock_api_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Generate API mock code
        mock_code = self._generate_api_mock_code(endpoint, method, response_data, status_code)
        
        mock = GeneratedMock(
            mock_id=mock_id,
            target_function=endpoint,
            mock_code=mock_code,
            mock_type='api',
            description=f"Mock for {method} {endpoint}",
            created_at=datetime.now().isoformat()
        )
        
        self.generated_mocks[mock_id] = mock
        self._save_generated_mocks()
        
        return mock
    
    def generate_database_mock(
        self,
        table_name: str,
        schema: Dict,
        sample_data: Optional[List[Dict]] = None
    ) -> GeneratedMock:
        """
        Generate database mock.
        
        Args:
            table_name: Database table name
            schema: Table schema
            sample_data: Sample data for mocking
            
        Returns:
            GeneratedMock configuration
        """
        mock_id = f"mock_db_{datetime.now().strftime('%Y%m%d%H%M%S')}_{table_name}"
        
        # Generate database mock code
        mock_code = self._generate_database_mock_code(table_name, schema, sample_data)
        
        mock = GeneratedMock(
            mock_id=mock_id,
            target_function=table_name,
            mock_code=mock_code,
            mock_type='database',
            description=f"Mock for {table_name} table",
            created_at=datetime.now().isoformat()
        )
        
        self.generated_mocks[mock_id] = mock
        self._save_generated_mocks()
        
        return mock
    
    def get_mock(self, mock_id: str) -> Optional[GeneratedMock]:
        """
        Get a generated mock by ID.
        
        Args:
            mock_id: Mock ID
            
        Returns:
            GeneratedMock or None
        """
        return self.generated_mocks.get(mock_id)
    
    def list_mocks(self, mock_type: Optional[str] = None) -> List[GeneratedMock]:
        """
        List all generated mocks.
        
        Args:
            mock_type: Optional filter by type
            
        Returns:
            List of GeneratedMock objects
        """
        mocks = list(self.generated_mocks.values())
        
        if mock_type:
            mocks = [m for m in mocks if m.mock_type == mock_type]
        
        return sorted(mocks, key=lambda m: m.created_at, reverse=True)
    
    def _generate_python_mock(
        self,
        function_name: str,
        mock_type: str,
        return_value: Optional[str]
    ) -> str:
        """Generate Python mock code."""
        if mock_type == 'default':
            return f"""
@patch('{function_name}')
def test_with_mock(mock_func):
    # Configure mock
    mock_func.return_value = {return_value or 'None'}
    
    # Call function that uses the mock
    result = function_under_test()
    
    # Assertions
    assert result is not None
    mock_func.assert_called_once()
""".strip()
        
        elif mock_type == 'spy':
            return f"""
@patch('{function_name}')
def test_with_spy(mock_func):
    # Call function that uses the spy
    result = function_under_test()
    
    # Verify the function was called
    mock_func.assert_called_once()
    assert mock_func.call_count == 1
""".strip()
        
        else:  # stub
            return f"""
@patch('{function_name}')
def test_with_stub(mock_func):
    # Configure stub return value
    mock_func.return_value = {return_value or 'None'}
    
    # Call function
    result = function_under_test()
    
    # Assertions
    assert result == {return_value or 'None'}
""".strip()
    
    def _generate_js_mock(
        self,
        function_name: str,
        mock_type: str,
        return_value: Optional[str]
    ) -> str:
        """Generate JavaScript mock code."""
        if mock_type == 'default':
            return f"""
jest.mock('../path/to/module', () => ({{
  {function_name}: jest.fn()
}}));

test('uses mocked function', () => {{
  // Configure mock
  const mockedFunc = require('../path/to/module').{function_name};
  mockedFunc.mockReturnValue({return_value or 'null'});
  
  // Call function
  const result = functionUnderTest();
  
  // Assertions
  expect(mockedFunc).toHaveBeenCalled();
  expect(result).toBeDefined();
}});
""".strip()
        
        elif mock_type == 'spy':
            return f"""
test('spies on function', () => {{
  const spy = jest.spyOn(module, '{function_name}');
  
  // Call function
  functionUnderTest();
  
  // Verify spy
  expect(spy).toHaveBeenCalled();
  spy.mockRestore();
}});
""".strip()
        
        else:  # stub
            return f"""
test('uses stubbed function', () => {{
  const stub = jest.fn().mockReturnValue({return_value or 'null'});
  
  // Use stub in test
  const result = functionUnderTest(stub);
  
  // Assertions
  expect(stub).toHaveBeenCalled();
  expect(result).toBe({return_value or 'null'});
}});
""".strip()
    
    def _generate_api_mock_code(
        self,
        endpoint: str,
        method: str,
        response_data: Optional[Dict],
        status_code: int
    ) -> str:
        """Generate API mock code."""
        response_json = json.dumps(response_data or {}, indent=2)
        
        return f"""
import requests_mock

@requests_mock.Mocker()
def test_api_call(mocker):
    # Mock the API endpoint
    mocker.{method.lower()}(
        '{endpoint}',
        json={response_json},
        status_code={status_code}
    )
    
    # Call function that makes API request
    result = function_that_calls_api()
    
    # Assertions
    assert result is not None
""".strip()
    
    def _generate_database_mock_code(
        self,
        table_name: str,
        schema: Dict,
        sample_data: Optional[List[Dict]]
    ) -> str:
        """Generate database mock code."""
        data_json = json.dumps(sample_data or [], indent=2)
        
        return f"""
from unittest.mock import MagicMock

def test_with_mock_db():
    # Create mock database connection
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    
    # Configure mock
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = {data_json}
    mock_cursor.fetchone.return_value = {data_json}[0] if {data_json} else None
    
    # Use mock in test
    with patch('database.get_connection', return_value=mock_conn):
        result = function_that_queries_db()
    
    # Assertions
    assert result is not None
    mock_cursor.execute.assert_called()
""".strip()
    
    def _load_generated_mocks(self) -> None:
        """Load generated mocks from file."""
        if self.mocks_file.exists():
            try:
                with open(self.mocks_file, 'r') as f:
                    data = json.load(f)
                    for mock_data in data.get('mocks', []):
                        mock = GeneratedMock(**mock_data)
                        self.generated_mocks[mock.mock_id] = mock
            except Exception:
                pass
    
    def _save_generated_mocks(self) -> None:
        """Save generated mocks to file."""
        try:
            data = {
                'mocks': [
                    {
                        'mock_id': m.mock_id,
                        'target_function': m.target_function,
                        'mock_code': m.mock_code,
                        'mock_type': m.mock_type,
                        'description': m.description,
                        'created_at': m.created_at
                    }
                    for m in self.generated_mocks.values()
                ],
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.mocks_file, 'w') as f:
                json.dump(data, f, indent=2)
        
        except Exception:
            pass
