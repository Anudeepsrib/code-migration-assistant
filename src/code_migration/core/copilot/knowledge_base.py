"""
Knowledge base for migration patterns and best practices.

Provides comprehensive knowledge storage:
- Migration pattern templates
- Best practices documentation
- Code transformation examples
- Troubleshooting guides
"""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class MigrationPattern:
    """Migration pattern template."""
    pattern_id: str
    name: str
    migration_type: str
    description: str
    source_pattern: str
    target_pattern: str
    prerequisites: List[str]
    steps: List[str]
    code_examples: List[Dict]
    created_at: str


@dataclass
class BestPractice:
    """Best practice guideline."""
    practice_id: str
    category: str
    title: str
    description: str
    severity: str
    applicable_types: List[str]
    examples: List[Dict]
    created_at: str


class KnowledgeBase:
    """
    Comprehensive knowledge base for migrations.
    
    Features:
    - Migration pattern storage
    - Best practices documentation
    - Code transformation templates
    - Troubleshooting guides
    """
    
    def __init__(self, project_path: Path):
        """
        Initialize knowledge base.
        
        Args:
            project_path: Path to project directory
        """
        self.project_path = Path(project_path)
        self.patterns: Dict[str, MigrationPattern] = {}
        self.practices: Dict[str, BestPractice] = {}
        self.templates: Dict[str, str] = {}
        
        self.knowledge_file = self.project_path / '.migration-knowledge.json'
        self._load_knowledge()
        
        # Initialize with built-in knowledge
        if not self.patterns:
            self._initialize_builtin_knowledge()
    
    def get_recommendations(
        self,
        migration_type: str,
        file_path: Optional[str] = None
    ) -> List[Dict]:
        """
        Get migration recommendations.
        
        Args:
            migration_type: Type of migration
            file_path: Optional specific file path
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Get patterns for migration type
        patterns = [
            p for p in self.patterns.values()
            if p.migration_type == migration_type
        ]
        
        for pattern in patterns:
            recommendations.append({
                'title': pattern.name,
                'description': pattern.description,
                'priority': 'HIGH',
                'topic': pattern.name,
                'type': 'pattern',
                'pattern_id': pattern.pattern_id
            })
        
        # Get best practices for migration type
        practices = [
            bp for bp in self.practices.values()
            if migration_type in bp.applicable_types
        ]
        
        for practice in practices:
            recommendations.append({
                'title': practice.title,
                'description': practice.description,
                'priority': practice.severity,
                'topic': practice.category,
                'type': 'best_practice',
                'practice_id': practice.practice_id
            })
        
        return recommendations
    
    def get_pattern(self, pattern_id: str) -> Optional[MigrationPattern]:
        """
        Get a specific migration pattern.
        
        Args:
            pattern_id: Pattern ID
            
        Returns:
            MigrationPattern or None
        """
        return self.patterns.get(pattern_id)
    
    def get_transformation_template(
        self,
        migration_type: str,
        source_pattern: str,
        target_pattern: str
    ) -> str:
        """
        Get code transformation template.
        
        Args:
            migration_type: Type of migration
            source_pattern: Source code pattern
            target_pattern: Target code pattern
            
        Returns:
            Transformation template string
        """
        # Find matching pattern
        for pattern in self.patterns.values():
            if (pattern.migration_type == migration_type and
                pattern.source_pattern == source_pattern and
                pattern.target_pattern == target_pattern):
                
                if pattern.code_examples:
                    return pattern.code_examples[0].get('target', '')
        
        # Return generic template if no match found
        return self._generate_generic_template(
            migration_type, source_pattern, target_pattern
        )
    
    def analyze_code_patterns(
        self,
        code: str,
        language: str
    ) -> List[Dict]:
        """
        Analyze code for migration patterns.
        
        Args:
            code: Code to analyze
            language: Programming language
            
        Returns:
            List of identified patterns/issues
        """
        issues = []
        
        # Find relevant patterns
        relevant_patterns = [
            p for p in self.patterns.values()
            if p.source_pattern in code
        ]
        
        for pattern in relevant_patterns:
            if pattern.source_pattern in code:
                issues.append({
                    'type': 'pattern_match',
                    'severity': 'INFO',
                    'message': f"Pattern detected: {pattern.name}",
                    'pattern_id': pattern.pattern_id,
                    'suggestion': f"Consider migrating to: {pattern.target_pattern}"
                })
        
        return issues
    
    def add_pattern(
        self,
        name: str,
        migration_type: str,
        description: str,
        source_pattern: str,
        target_pattern: str,
        prerequisites: List[str],
        steps: List[str],
        code_examples: List[Dict]
    ) -> str:
        """
        Add a new migration pattern.
        
        Args:
            name: Pattern name
            migration_type: Migration type
            description: Pattern description
            source_pattern: Source code pattern
            target_pattern: Target code pattern
            prerequisites: Required prerequisites
            steps: Migration steps
            code_examples: Code examples
            
        Returns:
            Pattern ID
        """
        pattern_id = f"pattern_{migration_type}_{name.lower().replace(' ', '_')}"
        
        pattern = MigrationPattern(
            pattern_id=pattern_id,
            name=name,
            migration_type=migration_type,
            description=description,
            source_pattern=source_pattern,
            target_pattern=target_pattern,
            prerequisites=prerequisites,
            steps=steps,
            code_examples=code_examples,
            created_at=datetime.now().isoformat()
        )
        
        self.patterns[pattern_id] = pattern
        self._save_knowledge()
        
        return pattern_id
    
    def add_best_practice(
        self,
        category: str,
        title: str,
        description: str,
        severity: str,
        applicable_types: List[str],
        examples: List[Dict]
    ) -> str:
        """
        Add a new best practice.
        
        Args:
            category: Practice category
            title: Practice title
            description: Practice description
            severity: Severity level
            applicable_types: Applicable migration types
            examples: Code examples
            
        Returns:
            Practice ID
        """
        practice_id = f"practice_{category}_{title.lower().replace(' ', '_')}"
        
        practice = BestPractice(
            practice_id=practice_id,
            category=category,
            title=title,
            description=description,
            severity=severity,
            applicable_types=applicable_types,
            examples=examples,
            created_at=datetime.now().isoformat()
        )
        
        self.practices[practice_id] = practice
        self._save_knowledge()
        
        return practice_id
    
    def get_statistics(self) -> Dict:
        """
        Get knowledge base statistics.
        
        Returns:
            Statistics dictionary
        """
        migration_types = set(p.migration_type for p in self.patterns.values())
        categories = set(bp.category for bp in self.practices.values())
        
        return {
            'total_patterns': len(self.patterns),
            'total_practices': len(self.practices),
            'migration_types_covered': len(migration_types),
            'categories_covered': len(categories),
            'migration_types': list(migration_types),
            'categories': list(categories)
        }
    
    def search_patterns(self, query: str) -> List[MigrationPattern]:
        """
        Search for patterns matching query.
        
        Args:
            query: Search query
            
        Returns:
            List of matching patterns
        """
        query_lower = query.lower()
        matches = []
        
        for pattern in self.patterns.values():
            if (query_lower in pattern.name.lower() or
                query_lower in pattern.description.lower() or
                query_lower in pattern.migration_type.lower()):
                matches.append(pattern)
        
        return matches
    
    def _generate_generic_template(
        self,
        migration_type: str,
        source_pattern: str,
        target_pattern: str
    ) -> str:
        """Generate generic transformation template."""
        return f"""
// Migration: {migration_type}
// Pattern: {source_pattern} → {target_pattern}

// TODO: Replace this pattern:
{source_pattern}

// With this pattern:
{target_pattern}

// Additional considerations:
// - Test thoroughly after migration
// - Update related components
// - Verify no breaking changes
"""
    
    def _initialize_builtin_knowledge(self) -> None:
        """Initialize with built-in knowledge."""
        # React Hooks patterns
        self.add_pattern(
            name="Class Component to Function Component",
            migration_type="react-hooks",
            description="Convert React class component to functional component with hooks",
            source_pattern="class Component extends React.Component",
            target_pattern="function Component() { hooks }",
            prerequisites=["React 16.8+", "Understanding of hooks"],
            steps=[
                "Replace class definition with function",
                "Convert constructor state to useState",
                "Replace lifecycle methods with useEffect",
                "Update event handlers"
            ],
            code_examples=[
                {
                    'source': """
class UserProfile extends Component {
    constructor(props) {
        super(props);
        this.state = { user: null };
    }
    componentDidMount() {
        this.fetchUser();
    }
    render() {
        return <div>{this.state.user.name}</div>;
    }
}""",
                    'target': """
function UserProfile() {
    const [user, setUser] = useState(null);
    
    useEffect(() => {
        fetchUser();
    }, []);
    
    return <div>{user?.name}</div>;
}"""
                }
            ]
        )
        
        # Vue 3 patterns
        self.add_pattern(
            name="Options API to Composition API",
            migration_type="vue3",
            description="Convert Vue 2 Options API to Vue 3 Composition API",
            source_pattern="export default { data() {}, methods: {} }",
            target_pattern="export default { setup() { return {} } }",
            prerequisites=["Vue 3", "Understanding of Composition API"],
            steps=[
                "Replace export default with setup() function",
                "Convert data() to ref() or reactive()",
                "Move methods inside setup()",
                "Update lifecycle hooks",
                "Return values from setup()"
            ],
            code_examples=[
                {
                    'source': """
export default {
    data() {
        return { count: 0 };
    },
    methods: {
        increment() {
            this.count++;
        }
    }
}""",
                    'target': """
export default {
    setup() {
        const count = ref(0);
        
        const increment = () => {
            count.value++;
        };
        
        return { count, increment };
    }
}"""
                }
            ]
        )
        
        # Python 3 patterns
        self.add_pattern(
            name="Print Statement to Function",
            migration_type="python3",
            description="Convert Python 2 print statement to Python 3 print function",
            source_pattern="print value",
            target_pattern="print(value)",
            prerequisites=["Python 3.0+"],
            steps=[
                "Add parentheses around print arguments",
                "Update multiple arguments to use sep parameter"
            ],
            code_examples=[
                {
                    'source': 'print "Hello", name',
                    'target': 'print("Hello", name)'
                }
            ]
        )
        
        # Best practices
        self.add_best_practice(
            category="security",
            title="Validate User Input",
            description="Always validate and sanitize user input to prevent injection attacks",
            severity="CRITICAL",
            applicable_types=["react-hooks", "vue3", "python3", "typescript"],
            examples=[
                {
                    'good': 'const sanitized = sanitizeInput(userInput)',
                    'bad': 'eval(userInput)'
                }
            ]
        )
        
        self.add_best_practice(
            category="testing",
            title="Write Tests Before Migration",
            description="Ensure comprehensive test coverage exists before starting migration",
            severity="HIGH",
            applicable_types=["react-hooks", "vue3", "python3", "typescript"],
            examples=[
                {
                    'description': 'Run tests before migration',
                    'command': 'npm test'
                }
            ]
        )
        
        self.add_best_practice(
            category="planning",
            title="Create Rollback Plan",
            description="Always have a rollback strategy before starting migration",
            severity="HIGH",
            applicable_types=["react-hooks", "vue3", "python3", "typescript"],
            examples=[
                {
                    'description': 'Create checkpoint before migration',
                    'command': 'migrate checkpoint create "Pre-migration"'
                }
            ]
        )
    
    def _load_knowledge(self) -> None:
        """Load knowledge from file."""
        if self.knowledge_file.exists():
            try:
                with open(self.knowledge_file, 'r') as f:
                    data = json.load(f)
                    
                    # Load patterns
                    for pattern_data in data.get('patterns', []):
                        pattern = MigrationPattern(**pattern_data)
                        self.patterns[pattern.pattern_id] = pattern
                    
                    # Load practices
                    for practice_data in data.get('practices', []):
                        practice = BestPractice(**practice_data)
                        self.practices[practice.practice_id] = practice
            
            except Exception:
                pass
    
    def _save_knowledge(self) -> None:
        """Save knowledge to file."""
        try:
            data = {
                'patterns': [
                    {
                        'pattern_id': p.pattern_id,
                        'name': p.name,
                        'migration_type': p.migration_type,
                        'description': p.description,
                        'source_pattern': p.source_pattern,
                        'target_pattern': p.target_pattern,
                        'prerequisites': p.prerequisites,
                        'steps': p.steps,
                        'code_examples': p.code_examples,
                        'created_at': p.created_at
                    }
                    for p in self.patterns.values()
                ],
                'practices': [
                    {
                        'practice_id': bp.practice_id,
                        'category': bp.category,
                        'title': bp.title,
                        'description': bp.description,
                        'severity': bp.severity,
                        'applicable_types': bp.applicable_types,
                        'examples': bp.examples,
                        'created_at': bp.created_at
                    }
                    for bp in self.practices.values()
                ],
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.knowledge_file, 'w') as f:
                json.dump(data, f, indent=2)
        
        except Exception:
            pass
