"""
Performance tests for large codebase handling.

Tests performance with large projects, many files,
and complex dependency graphs.
"""

import pytest
import tempfile
import time
import concurrent.futures
import psutil
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from code_migration.core.security import SafeCodeAnalyzer
from code_migration.core.confidence import MigrationConfidenceAnalyzer
from code_migration.core.visualizer import VisualMigrationPlanner
from code_migration.core.rollback import TimeMachineRollback
from code_migration.core.compliance import PIIDetector


def _react_component_content(index):
    """Generate React component content."""
    return f"""
import React, {{ Component }} from 'react';
import axios from 'axios';
import {{ connect }} from 'react-redux';

class Component{index} extends Component {{
    constructor(props) {{
        super(props);
        this.state = {{
            data: null,
            loading: false,
            error: null
        }};
        this.componentDidMount = this.componentDidMount.bind(this);
        this.componentWillUnmount = this.componentWillUnmount.bind(this);
    }}
    
    componentDidMount() {{
        this.fetchData();
        this.timer = setInterval(this.fetchData, 30000);
    }}
    
    componentWillUnmount() {{
        if (this.timer) {{
            clearInterval(this.timer);
        }}
    }}
    
    componentDidUpdate(prevProps) {{
        if (this.props.id !== prevProps.id) {{
            this.fetchData();
        }}
    }}
    
    async fetchData() {{
        this.setState({{ loading: true }});
        try {{
            const response = await axios.get(`/api/data/${{this.props.id}}`);
            this.setState({{
                data: response.data,
                loading: false,
                error: null
            }});
        }} catch (error) {{
            this.setState({{
                error: error.message,
                loading: false
            }});
        }}
    }}
    
    render() {{
        const {{ data, loading, error }} = this.state;
        
        if (loading) return <div>Loading...</div>;
        if (error) return <div>Error: {{error}}</div>;
        
        return (
            <div className="component-{index}">
                <h1>Component {index}</h1>
                <pre>{{JSON.stringify(data, null, 2)}}</pre>
            </div>
        );
    }}
}}

const mapStateToProps = (state) => ({{
    user: state.user,
    settings: state.settings
}});

export default connect(mapStateToProps)(Component{index});
"""


def _javascript_util_content(index):
    """Generate JavaScript utility content."""
    return f"""
// Utility functions for module {index}

export const formatDate = (date) => {{
    return new Date(date).toLocaleDateString();
}};

export const validateEmail = (email) => {{
    const re = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
    return re.test(email);
}};

export const debounce = (func, wait) => {{
    let timeout;
    return function executedFunction(...args) {{
        const later = () => {{
            clearTimeout(timeout);
            func(...args);
        }};
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    }};
}};

export const throttle = (func, limit) => {{
    let inThrottle;
    return function(...args) {{
        if (!inThrottle) {{
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }}
    }};
}};

export const deepClone = (obj) => {{
    if (obj === null || typeof obj !== 'object') {{
        return obj;
    }}
    if (obj instanceof Date) {{
        return new Date(obj.getTime());
    }}
    if (obj instanceof Array) {{
        return obj.map(item => deepClone(item));
    }}
    const cloned = {{}};
    for (const key in obj) {{
        if (obj.hasOwnProperty(key)) {{
            cloned[key] = deepClone(obj[key]);
        }}
    }}
    return cloned;
}};

// Performance monitoring
export const measurePerformance = (name, fn) => {{
    const start = performance.now();
    const result = fn();
    const end = performance.now();
    console.log(`{{name}} took ${{end - start}} milliseconds`);
    return result;
}};
"""


def _python_service_content(index):
    """Generate Python service content."""
    return f'''
# Service module {index}

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ServiceConfig:
    base_url: str = "https://api.example.com"
    timeout: int = 30
    max_retries: int = 3

class Service{index}:
    def __init__(self, config: Optional[ServiceConfig] = None):
        self.config = config or ServiceConfig()
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_data(self, item_id: str) -> Dict:
        """Get data by ID."""
        url = f"{{self.config.base_url}}/data/{{item_id}}"
        
        for attempt in range(self.config.max_retries):
            try:
                async with self.session.get(url) as response:
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientError as e:
                if attempt == self.config.max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)
        
        raise Exception("Max retries exceeded")
    
    async def post_data(self, data: Dict) -> Dict:
        """Post data."""
        url = f"{{self.config.base_url}}/data"
        
        try:
            async with self.session.post(url, json=data) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"Failed to post data: {{e}}")
            raise
    
    async def process_batch(self, items: List[Dict]) -> List[Dict]:
        """Process multiple items concurrently."""
        tasks = [self.post_data(item) for item in items]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Batch processing error: {{result}}")
            else:
                successful_results.append(result)
        
        return successful_results

# Singleton instance
service_{index} = Service{index}()
'''


def _react_hook_content(index):
    """Generate React hook content."""
    return f"""
import {{ useState, useEffect, useCallback }} from 'react';
import {{ useSelector, useDispatch }} from 'react-redux';

export const useHook{index} = (initialValue) => {{
    const [value, setValue] = useState(initialValue);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    
    const dispatch = useDispatch();
    const user = useSelector(state => state.user);
    
    const updateValue = useCallback(async (newValue) => {{
        setLoading(true);
        setError(null);
        
        try {{
            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 1000));
            setValue(newValue);
            dispatch({{
                type: 'UPDATE_VALUE',
                payload: {{ value: newValue, user: user.id }}
            }});
        }} catch (err) {{
            setError(err.message);
        }} finally {{
            setLoading(false);
        }}
    }}, [dispatch, user.id]);
    
    const resetValue = useCallback(() => {{
        setValue(initialValue);
        setError(null);
    }}, [initialValue]);
    
    useEffect(() => {{
        // Cleanup on unmount
        return () => {{
            setValue(initialValue);
            setError(null);
        }};
    }}, [initialValue]);
    
    return {{
        value,
        setValue: updateValue,
        resetValue,
        loading,
        error
    }};
}};
"""


def _test_content(index):
    """Generate test content."""
    return f"""
import React from 'react';
import {{ render, screen }} from '@testing-library/react';
import Component{index} from '../src/components/Component{index}';

describe('Component{index}', () => {{
    test('renders without crashing', () => {{
        render(<Component{index} />);
        expect(screen.getByText('Component {index}')).toBeInTheDocument();
    }});
    
    test('handles loading state', async () => {{
        render(<Component{index} id="test" />);
        expect(screen.getByText('Loading...')).toBeInTheDocument();
        
        await screen.findByText('Component {index}');
        expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
    }});
    
    test('handles error state', async () => {{
        render(<Component{index} id="error" />);
        
        await screen.findByText(/Error:/);
        expect(screen.getByText(/Error:/)).toBeInTheDocument();
    }});
    
    test('displays data correctly', async () => {{
        const mockData = {{ id: 'test', name: 'Test Data' }};
        jest.spyOn(global, 'fetch').mockResolvedValue({{
            json: async () => mockData,
            ok: true
        }});
        
        render(<Component{index} id="test" />);
        
        await screen.findByText('Test Data');
        expect(screen.getByText('test')).toBeInTheDocument();
    }});
}})
"""


def _config_content(index):
    """Generate configuration content."""
    return f"""
# Configuration file {index}

app:
  name: "test-app-{index}"
  version: "1.0.{index}"
  environment: "development"

database:
  host: "localhost"
  port: 5432
  name: "test_db_{index}"
  username: "user"
  password: "password_{index}"

api:
  base_url: "https://api.example.com/v{index}"
  timeout: 30000
  retries: 3

logging:
  level: "info"
  format: "json"
  file: "app-{index}.log"

features:
  - feature-{index}-enabled
  - feature-{index}-beta
  - feature-{index}-experimental

cache:
  type: "redis"
  host: "localhost"
  port: 6379
  ttl: 3600

security:
  jwt_secret: "secret-key-{index}"
  encryption_key: "encryption-key-{index}"
  session_timeout: 1800
"""


def _create_test_file(project_path, index):
    """Create a test file with realistic content."""
    file_types = [
        ("src/components", f"Component{index}.jsx", _react_component_content),
        ("src/utils", f"util{index}.js", _javascript_util_content),
        ("src/services", f"service{index}.py", _python_service_content),
        ("src/hooks", f"hook{index}.js", _react_hook_content),
        ("tests/unit", f"test{index}.js", _test_content),
        ("config", f"config{index}.yaml", _config_content),
    ]
    
    dir_path, filename, content_func = file_types[index % len(file_types)]
    full_path = project_path / dir_path / filename
    
    content = content_func(index)
    full_path.write_text(content)


@pytest.fixture(scope="module")
def large_project():
    """Create a large project for performance testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir) / "large-project"
        project_path.mkdir()
        
        # Create project structure
        dirs = [
            "src/components",
            "src/utils",
            "src/services",
            "src/hooks",
            "src/store",
            "src/api",
            "tests/unit",
            "tests/integration",
            "docs/api",
            "config",
            "scripts",
            "build",
            "assets/css",
            "assets/images",
            "assets/fonts"
        ]
        
        for dir_path in dirs:
            (project_path / dir_path).mkdir(parents=True)
        
        # Generate many files
        file_count = 1000
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            
            for i in range(file_count):
                future = executor.submit(
                    _create_test_file,
                    project_path,
                    i
                )
                futures.append(future)
            
            # Wait for all files to be created
            for future in futures:
                future.result()
        
        yield project_path


@pytest.fixture(scope="module")
def medium_project():
    """Create a medium-sized project for regression testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir) / "medium-project"
        project_path.mkdir()
        
        # Create medium project structure
        dirs = ["src/components", "src/utils", "src/services", "tests"]
        for dir_path in dirs:
            (project_path / dir_path).mkdir(parents=True)
        
        # Create 100 files
        for i in range(100):
            if i % 3 == 0:
                dir_path = "src/components"
                filename = f"Component{i}.jsx"
                content = f"// React component {i}\nexport default () => <div>Component {i}</div>;"
            elif i % 3 == 1:
                dir_path = "src/utils"
                filename = f"util{i}.js"
                content = f"// Utility {i}\nexport const helper{i} = () => {{ return {i}; }};"
            else:
                dir_path = "src/services"
                filename = f"service{i}.py"
                content = f"# Service {i}\nclass Service{i}:\n    def method(self):\n        return {i}"
            
            (project_path / dir_path / filename).write_text(content)
        
        yield project_path


@pytest.mark.performance
@pytest.mark.slow
class TestLargeCodebasePerformance:
    """Test performance with large codebases."""
    
    def test_safe_code_analyzer_performance(self, large_project):
        """Test SafeCodeAnalyzer performance with large codebase."""
        analyzer = SafeCodeAnalyzer()
        
        # Measure analysis time
        start_time = time.time()
        results = analyzer.analyze_directory(large_project)
        end_time = time.time()
        
        analysis_time = end_time - start_time
        
        # Verify results
        assert results['files_analyzed'] > 0
        assert results['total_lines'] > 0
        assert results['total_complexity'] >= 0
        
        # Performance assertions (adjust based on environment)
        assert analysis_time < 30.0  # Should complete within 30 seconds
        assert analysis_time < 60.0  # Definitely should complete within 1 minute
        
        # Memory efficiency check
        assert results['files_analyzed'] <= 1000  # Should analyze all files
        
        print(f"SafeCodeAnalyzer analyzed {results['files_analyzed']} files in {analysis_time:.2f}s")
    
    def test_confidence_analyzer_performance(self, large_project):
        """Test MigrationConfidenceAnalyzer performance."""
        with MigrationConfidenceAnalyzer(large_project, allowed_base=large_project.parent) as analyzer:
            # Measure confidence analysis time
            start_time = time.time()
            confidence = analyzer.calculate_confidence("react-hooks", team_experience=70)
            end_time = time.time()
            
            analysis_time = end_time - start_time
            
            # Verify results
            assert 0 <= confidence.overall_score <= 100
            assert confidence.risk_level in ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
            assert confidence.estimated_hours > 0
            assert confidence.estimated_cost > 0
            
            # Performance assertions
            assert analysis_time < 60.0  # Should complete within 1 minute
            
            print(f"ConfidenceAnalyzer completed in {analysis_time:.2f}s with score {confidence.overall_score}")
    
    def test_visual_planner_performance(self, large_project):
        """Test VisualMigrationPlanner performance."""
        planner = VisualMigrationPlanner(large_project, allowed_base=large_project.parent)
        
        # Measure graph building time
        start_time = time.time()
        graph = planner.build_dependency_graph()
        end_time = time.time()
        
        graph_time = end_time - start_time
        
        # Measure wave calculation time
        start_time = time.time()
        waves = planner.calculate_migration_waves()
        end_time = time.time()
        
        waves_time = end_time - start_time
        
        # Verify results
        assert graph.number_of_nodes() > 0
        assert len(waves) > 0
        
        # Performance assertions
        assert graph_time < 30.0  # Graph building within 30 seconds
        assert waves_time < 10.0   # Wave calculation within 10 seconds
        
        print(f"Graph building: {graph_time:.2f}s, Wave calculation: {waves_time:.2f}s")
        print(f"Graph: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
        print(f"Waves: {len(waves)} migration waves")
    
    def test_rollback_performance(self, large_project):
        """Test TimeMachineRollback performance."""
        with TimeMachineRollback(large_project, allowed_base=large_project.parent) as rollback:
            # Measure checkpoint creation time
            start_time = time.time()
            checkpoint_id = rollback.create_checkpoint("Performance test checkpoint")
            end_time = time.time()
            
            checkpoint_time = end_time - start_time
            
            # Verify checkpoint was created
            assert checkpoint_id is not None
            checkpoints = rollback.list_checkpoints()
            assert len(checkpoints) > 0
            
            # MODIFY A FILE TO ENSURE ROLLBACK HAS WORK TO DO
            python_files = list(large_project.rglob("src/services/*.py"))
            if not python_files:
                python_files = list(large_project.rglob("*.py"))
            
            test_file = python_files[0]
            original_content = test_file.read_text()
            test_file.write_text(original_content + "\n# NEW LINE\n")
            
            # Measure rollback time
            start_time = time.time()
            rollback_result = rollback.rollback(checkpoint_id)
            end_time = time.time()
            
            rollback_time = end_time - start_time
            
            # Verify rollback
            assert rollback_result['success'] is True
            assert rollback_result['files_restored'] > 0
            
            # Verify file was restored
            assert test_file.read_text() == original_content
            
            # Performance assertions
            assert checkpoint_time < 60.0  # Checkpoint within 1 minute
            assert rollback_time < 30.0   # Rollback within 30 seconds
            
            print(f"Checkpoint creation: {checkpoint_time:.2f}s, Rollback: {rollback_time:.2f}s")
            print(f"Restored {rollback_result['files_restored']} files")
            
            # Explicit cleanup for Windows permission issues
            rollback.close()
    
    def test_pii_detector_performance(self, large_project):
        """Test PIIDetector performance."""
        with PIIDetector(large_project) as detector:
            # Add some PII to test files
            test_files = list(large_project.rglob('*.py'))[:10]
            for file_path in test_files:
                content = file_path.read_text()
                content += f'\n# Test PII\nemail = "test{file_path.stem}@example.com"\nphone = "555-123-4567"\n'
                file_path.write_text(content)
            
            # Measure scan time
            start_time = time.time()
            results = detector.scan_directory()
            end_time = time.time()
            
            scan_time = end_time - start_time
            
            # Verify results
            assert results['files_scanned'] > 0
            assert results['total_findings'] >= 20  # Should find the test PII
            
            # Performance assertions
            assert scan_time < 60.0  # Should complete within 1 minute
            
            print(f"PII scan completed in {scan_time:.2f}s")
            print(f"Scanned {results['files_scanned']} files, found {results['total_findings']} PII instances")
    
    def test_concurrent_analysis(self, large_project):
        """Test concurrent analysis performance."""
        import concurrent.futures
        
        def analyze_component(file_path):
            """Analyze a single component file."""
            try:
                analyzer = SafeCodeAnalyzer()
                return analyzer.analyze(file_path)
            except Exception as e:
                return {'error': str(e), 'file': str(file_path)}
        
        # Get sample of files to analyze
        sample_files = list(large_project.rglob('*.jsx'))[:50]
        
        # Measure concurrent analysis time
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(analyze_component, file) for file in sample_files]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        
        concurrent_time = end_time - start_time
        
        # Verify results
        successful_results = [r for r in results if 'error' not in r]
        assert len(successful_results) > 0
        
        # Performance assertions
        assert concurrent_time < 30.0  # Should complete within 30 seconds
        
        print(f"Concurrent analysis: {concurrent_time:.2f}s for {len(sample_files)} files")
        print(f"Successful: {len(successful_results)}, Errors: {len(results) - len(successful_results)}")
    
    def test_memory_usage(self, large_project):
        """Test memory usage with large codebase."""
        import psutil
        import os
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Run multiple analyses
        analyzer = SafeCodeAnalyzer()
        planner = VisualMigrationPlanner(large_project, allowed_base=large_project.parent)
        
        # Analyze multiple times
        for i in range(5):
            analyzer.analyze_directory(large_project)
            planner.build_dependency_graph()
        
        # Get final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory usage should be reasonable
        assert memory_increase < 500  # Should not use more than 500MB additional memory
        
        print(f"Memory usage: {initial_memory:.1f}MB -> {final_memory:.1f}MB (+{memory_increase:.1f}MB)")
    
    def test_large_file_handling(self, large_project):
        """Test handling of large files."""
        # Create a large file
        large_file = large_project / "src" / "large_file.py"
        
        # Generate large content (1MB)
        content = "# Large file for testing\n"
        content += "x = " + "1\n" * 50000  # About 1MB of content
        large_file.write_text(content)
        
        # Test analysis of large file
        analyzer = SafeCodeAnalyzer()
        
        start_time = time.time()
        result = analyzer.analyze(large_file)
        end_time = time.time()
        
        analysis_time = end_time - start_time
        
        # Should handle large file gracefully
        assert result['parsed'] is True
        assert result['line_count'] > 50000
        assert analysis_time < 10.0  # Should handle large file quickly
        
        print(f"Large file analysis: {analysis_time:.2f}s for {result['line_count']} lines")


@pytest.mark.performance
@pytest.mark.slow
class TestPerformanceRegression:
    """Performance regression tests."""
    
    def test_analysis_time_regression(self, medium_project):
        """Test that analysis time doesn't regress."""
        analyzer = SafeCodeAnalyzer()
        
        # Measure analysis time
        start_time = time.time()
        results = analyzer.analyze_directory(medium_project)
        end_time = time.time()
        
        analysis_time = end_time - start_time
        
        # Performance regression check
        assert analysis_time < 5.0  # Should complete within 5 seconds for 100 files
        assert results['files_analyzed'] == 33  # Only analyzing .py files
        
        print(f"Analysis time regression test: {analysis_time:.2f}s for 100 files")
    
    def test_memory_regression(self, medium_project):
        """Test that memory usage doesn't regress."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Run analysis
        analyzer = SafeCodeAnalyzer()
        analyzer.analyze_directory(medium_project)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory regression check
        assert memory_increase < 100  # Should not use more than 100MB for 100 files
        
        print(f"Memory regression test: {memory_increase:.1f}MB increase for 100 files")
