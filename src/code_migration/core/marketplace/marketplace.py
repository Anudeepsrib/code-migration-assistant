"""
Migration Marketplace for community-driven patterns.

Provides marketplace features:
- Pattern sharing and discovery
- Community ratings and reviews
- Pattern validation
- Search and filtering
"""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from ..security import SecurityAuditLogger


@dataclass
class CommunityPattern:
    """Community-contributed migration pattern."""
    pattern_id: str
    name: str
    description: str
    migration_type: str
    author: str
    version: str
    code_template: str
    documentation: str
    tags: List[str]
    downloads: int
    rating: float
    review_count: int
    created_at: str
    updated_at: str
    validated: bool


class MigrationMarketplace:
    """
    Community marketplace for migration patterns.
    
    Features:
    - Pattern sharing
    - Pattern discovery
    - Community ratings
    - Validation system
    """
    
    def __init__(self, project_path: Path):
        """
        Initialize migration marketplace.
        
        Args:
            project_path: Path to project directory
        """
        self.project_path = Path(project_path)
        self.patterns: Dict[str, CommunityPattern] = {}
        self.downloaded_patterns: Dict[str, str] = {}  # pattern_id -> download_path
        
        log_dir = self.project_path / '.migration-logs'
        self.audit_logger = SecurityAuditLogger(log_dir)
        
        self.marketplace_file = self.project_path / '.migration-marketplace.json'
        self._load_patterns()
        
        # Initialize with sample patterns if empty
        if not self.patterns:
            self._initialize_sample_patterns()
    
    def search_patterns(
        self,
        query: Optional[str] = None,
        migration_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        min_rating: Optional[float] = None,
        sort_by: str = 'rating'
    ) -> List[CommunityPattern]:
        """
        Search for patterns in marketplace.
        
        Args:
            query: Search query string
            migration_type: Filter by migration type
            tags: Filter by tags
            min_rating: Minimum rating filter
            sort_by: Sort field (rating, downloads, date)
            
        Returns:
            List of matching patterns
        """
        results = list(self.patterns.values())
        
        # Apply query filter
        if query:
            query_lower = query.lower()
            results = [
                p for p in results
                if (query_lower in p.name.lower() or
                    query_lower in p.description.lower() or
                    query_lower in p.tags)
            ]
        
        # Apply migration type filter
        if migration_type:
            results = [p for p in results if p.migration_type == migration_type]
        
        # Apply tags filter
        if tags:
            results = [
                p for p in results
                if any(tag in p.tags for tag in tags)
            ]
        
        # Apply rating filter
        if min_rating is not None:
            results = [p for p in results if p.rating >= min_rating]
        
        # Sort results
        if sort_by == 'rating':
            results = sorted(results, key=lambda p: p.rating, reverse=True)
        elif sort_by == 'downloads':
            results = sorted(results, key=lambda p: p.downloads, reverse=True)
        elif sort_by == 'date':
            results = sorted(results, key=lambda p: p.created_at, reverse=True)
        
        return results
    
    def get_pattern(self, pattern_id: str) -> Optional[CommunityPattern]:
        """
        Get a specific pattern by ID.
        
        Args:
            pattern_id: Pattern ID
            
        Returns:
            CommunityPattern or None
        """
        return self.patterns.get(pattern_id)
    
    def download_pattern(
        self,
        pattern_id: str,
        output_dir: Optional[Path] = None
    ) -> Optional[Path]:
        """
        Download a pattern to local project.
        
        Args:
            pattern_id: Pattern ID to download
            output_dir: Optional output directory
            
        Returns:
            Path to downloaded pattern or None
        """
        pattern = self.patterns.get(pattern_id)
        if not pattern:
            return None
        
        # Determine output path
        if output_dir is None:
            output_dir = self.project_path / 'migration-patterns'
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create pattern file
        pattern_file = output_dir / f"{pattern_id}.json"
        
        # Save pattern
        pattern_data = {
            'pattern_id': pattern.pattern_id,
            'name': pattern.name,
            'description': pattern.description,
            'migration_type': pattern.migration_type,
            'author': pattern.author,
            'version': pattern.version,
            'code_template': pattern.code_template,
            'documentation': pattern.documentation,
            'tags': pattern.tags,
            'rating': pattern.rating,
            'downloaded_at': datetime.now().isoformat()
        }
        
        pattern_file.write_text(
            json.dumps(pattern_data, indent=2),
            encoding='utf-8'
        )
        
        # Update download count
        pattern.downloads += 1
        self.downloaded_patterns[pattern_id] = str(pattern_file)
        
        self._save_patterns()
        
        self.audit_logger.log_migration_event(
            migration_type='marketplace',
            project_path=str(self.project_path),
            user='system',
            action='DOWNLOAD_PATTERN',
            result='SUCCESS',
            details={
                'pattern_id': pattern_id,
                'pattern_name': pattern.name,
                'download_path': str(pattern_file)
            }
        )
        
        return pattern_file
    
    def rate_pattern(
        self,
        pattern_id: str,
        rating: float,
        review: Optional[str] = None
    ) -> bool:
        """
        Rate a pattern.
        
        Args:
            pattern_id: Pattern ID
            rating: Rating value (0-5)
            review: Optional review text
            
        Returns:
            True if rated successfully
        """
        if pattern_id not in self.patterns:
            return False
        
        if not 0 <= rating <= 5:
            return False
        
        pattern = self.patterns[pattern_id]
        
        # Calculate new rating (weighted average)
        current_total = pattern.rating * pattern.review_count
        new_total = current_total + rating
        pattern.review_count += 1
        pattern.rating = new_total / pattern.review_count
        
        pattern.updated_at = datetime.now().isoformat()
        
        self._save_patterns()
        
        self.audit_logger.log_migration_event(
            migration_type='marketplace',
            project_path=str(self.project_path),
            user='system',
            action='RATE_PATTERN',
            result='SUCCESS',
            details={
                'pattern_id': pattern_id,
                'rating': rating,
                'new_average': pattern.rating
            }
        )
        
        return True
    
    def submit_pattern(
        self,
        name: str,
        description: str,
        migration_type: str,
        code_template: str,
        documentation: str,
        tags: List[str],
        author: str = 'anonymous'
    ) -> str:
        """
        Submit a new pattern to marketplace.
        
        Args:
            name: Pattern name
            description: Pattern description
            migration_type: Migration type
            code_template: Code template
            documentation: Documentation
            tags: Tags for categorization
            author: Pattern author
            
        Returns:
            Pattern ID
        """
        pattern_id = f"pattern_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        pattern = CommunityPattern(
            pattern_id=pattern_id,
            name=name,
            description=description,
            migration_type=migration_type,
            author=author,
            version='1.0.0',
            code_template=code_template,
            documentation=documentation,
            tags=tags,
            downloads=0,
            rating=0.0,
            review_count=0,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            validated=False
        )
        
        self.patterns[pattern_id] = pattern
        self._save_patterns()
        
        self.audit_logger.log_migration_event(
            migration_type='marketplace',
            project_path=str(self.project_path),
            user=author,
            action='SUBMIT_PATTERN',
            result='SUCCESS',
            details={
                'pattern_id': pattern_id,
                'pattern_name': name,
                'migration_type': migration_type
            }
        )
        
        return pattern_id
    
    def get_popular_patterns(self, limit: int = 10) -> List[CommunityPattern]:
        """
        Get most popular patterns.
        
        Args:
            limit: Maximum number of patterns
            
        Returns:
            List of popular patterns
        """
        return sorted(
            self.patterns.values(),
            key=lambda p: p.downloads,
            reverse=True
        )[:limit]
    
    def get_top_rated_patterns(self, limit: int = 10) -> List[CommunityPattern]:
        """
        Get top rated patterns.
        
        Args:
            limit: Maximum number of patterns
            
        Returns:
            List of top rated patterns
        """
        # Filter patterns with at least 3 reviews
        rated_patterns = [
            p for p in self.patterns.values()
            if p.review_count >= 3
        ]
        
        return sorted(
            rated_patterns,
            key=lambda p: p.rating,
            reverse=True
        )[:limit]
    
    def get_marketplace_statistics(self) -> Dict:
        """
        Get marketplace statistics.
        
        Returns:
            Statistics dictionary
        """
        migration_types = {}
        authors = set()
        total_downloads = 0
        total_reviews = 0
        
        for pattern in self.patterns.values():
            migration_types[pattern.migration_type] = migration_types.get(
                pattern.migration_type, 0
            ) + 1
            authors.add(pattern.author)
            total_downloads += pattern.downloads
            total_reviews += pattern.review_count
        
        return {
            'total_patterns': len(self.patterns),
            'total_downloads': total_downloads,
            'total_reviews': total_reviews,
            'unique_authors': len(authors),
            'migration_types': migration_types,
            'average_rating': sum(p.rating for p in self.patterns.values()) / max(len(self.patterns), 1)
        }
    
    def _initialize_sample_patterns(self) -> None:
        """Initialize with sample patterns."""
        sample_patterns = [
            {
                'name': 'React Class to Hooks - Basic',
                'description': 'Simple pattern for converting React class components to functional components with hooks',
                'migration_type': 'react-hooks',
                'code_template': '''function {component_name}() {
  const [state, setState] = useState(initialState);
  
  useEffect(() => {
    // componentDidMount logic
    return () => {
      // componentWillUnmount cleanup
    };
  }, []);
  
  return (
    <div>{/* component JSX */}</div>
  );
}''',
                'documentation': 'Use this pattern for basic class components with simple state',
                'tags': ['react', 'hooks', 'basic', 'class-conversion']
            },
            {
                'name': 'Vue Options to Composition API',
                'description': 'Convert Vue 2 Options API components to Vue 3 Composition API',
                'migration_type': 'vue3',
                'code_template': '''export default {
  setup() {
    const state = reactive({ ... });
    
    onMounted(() => {
      // mounted logic
    });
    
    return {
      ...toRefs(state)
    };
  }
};''',
                'documentation': 'Standard pattern for Vue 3 Composition API conversion',
                'tags': ['vue', 'composition-api', 'vue3', 'migration']
            },
            {
                'name': 'Python 2 to 3 Print Migration',
                'description': 'Convert Python 2 print statements to Python 3 print function',
                'migration_type': 'python3',
                'code_template': '''# Python 2
# print "Hello", name

# Python 3
print("Hello", name)''',
                'documentation': 'Simple print statement to function conversion',
                'tags': ['python', 'python3', 'print', 'basic']
            }
        ]
        
        for pattern_data in sample_patterns:
            self.submit_pattern(
                name=pattern_data['name'],
                description=pattern_data['description'],
                migration_type=pattern_data['migration_type'],
                code_template=pattern_data['code_template'],
                documentation=pattern_data['documentation'],
                tags=pattern_data['tags'],
                author='community'
            )
    
    def _load_patterns(self) -> None:
        """Load patterns from file."""
        if self.marketplace_file.exists():
            try:
                with open(self.marketplace_file, 'r') as f:
                    data = json.load(f)
                    for pattern_data in data.get('patterns', []):
                        pattern = CommunityPattern(**pattern_data)
                        self.patterns[pattern.pattern_id] = pattern
            except Exception:
                pass
    
    def _save_patterns(self) -> None:
        """Save patterns to file."""
        try:
            data = {
                'patterns': [
                    {
                        'pattern_id': p.pattern_id,
                        'name': p.name,
                        'description': p.description,
                        'migration_type': p.migration_type,
                        'author': p.author,
                        'version': p.version,
                        'code_template': p.code_template,
                        'documentation': p.documentation,
                        'tags': p.tags,
                        'downloads': p.downloads,
                        'rating': p.rating,
                        'review_count': p.review_count,
                        'created_at': p.created_at,
                        'updated_at': p.updated_at,
                        'validated': p.validated
                    }
                    for p in self.patterns.values()
                ],
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.marketplace_file, 'w') as f:
                json.dump(data, f, indent=2)
        
        except Exception:
            pass
