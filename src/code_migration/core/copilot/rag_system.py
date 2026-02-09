"""
RAG (Retrieval-Augmented Generation) system for knowledge retrieval.

Provides intelligent context retrieval:
- Vector-based semantic search
- Document chunking and indexing
- Relevance scoring
- Context assembly
"""

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import hashlib


@dataclass
class KnowledgeChunk:
    """Knowledge chunk data structure."""
    chunk_id: str
    content: str
    source: str
    chunk_type: str
    metadata: Dict
    embedding: Optional[List[float]] = None
    created_at: str = None


class RAGSystem:
    """
    Retrieval-Augmented Generation system.
    
    Features:
    - Semantic document retrieval
    - Knowledge chunking
    - Relevance scoring
    - Context assembly
    """
    
    def __init__(self, project_path: Path):
        """
        Initialize RAG system.
        
        Args:
            project_path: Path to project directory
        """
        self.project_path = Path(project_path)
        self.chunks: Dict[str, KnowledgeChunk] = {}
        self.index: Dict[str, List[str]] = {}  # keyword -> chunk_ids
        
        self.index_file = self.project_path / '.migration-rag-index.json'
        self._load_index()
        
        # Build index if empty
        if not self.chunks:
            self._build_initial_index()
    
    def retrieve_relevant_context(
        self,
        query: str,
        intent: Optional[str] = None,
        conversation_history: Optional[List] = None,
        limit: int = 5
    ) -> List[str]:
        """
        Retrieve relevant context for a query.
        
        Args:
            query: Search query
            intent: Optional intent filter
            conversation_history: Optional conversation context
            limit: Maximum number of chunks to return
            
        Returns:
            List of relevant context strings
        """
        # Extract keywords from query
        keywords = self._extract_keywords(query)
        
        # Find matching chunks
        matching_chunks = self._find_matching_chunks(keywords, intent)
        
        # Score chunks by relevance
        scored_chunks = self._score_chunks(matching_chunks, query, keywords)
        
        # Sort by score and limit
        sorted_chunks = sorted(
            scored_chunks,
            key=lambda x: x['score'],
            reverse=True
        )[:limit]
        
        # Return chunk contents
        return [chunk['chunk'].content for chunk in sorted_chunks]
    
    def add_document(
        self,
        content: str,
        source: str,
        doc_type: str,
        metadata: Optional[Dict] = None
    ) -> List[str]:
        """
        Add a document to the knowledge base.
        
        Args:
            content: Document content
            source: Document source identifier
            doc_type: Type of document
            metadata: Optional metadata
            
        Returns:
            List of created chunk IDs
        """
        chunk_ids = []
        
        # Chunk the document
        chunks = self._chunk_document(content, source, doc_type, metadata or {})
        
        # Add chunks to index
        for chunk in chunks:
            self.chunks[chunk.chunk_id] = chunk
            chunk_ids.append(chunk.chunk_id)
            
            # Index by keywords
            keywords = self._extract_keywords(chunk.content)
            for keyword in keywords:
                if keyword not in self.index:
                    self.index[keyword] = []
                if chunk.chunk_id not in self.index[keyword]:
                    self.index[keyword].append(chunk.chunk_id)
        
        self._save_index()
        return chunk_ids
    
    def search(
        self,
        query: str,
        doc_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Search the knowledge base.
        
        Args:
            query: Search query
            doc_type: Optional document type filter
            limit: Maximum results
            
        Returns:
            List of search results
        """
        keywords = self._extract_keywords(query)
        
        # Find matching chunks
        chunk_scores: Dict[str, int] = {}
        
        for keyword in keywords:
            if keyword in self.index:
                for chunk_id in self.index[keyword]:
                    chunk = self.chunks.get(chunk_id)
                    if chunk:
                        # Filter by document type
                        if doc_type and chunk.chunk_type != doc_type:
                            continue
                        
                        chunk_scores[chunk_id] = chunk_scores.get(chunk_id, 0) + 1
        
        # Sort by score
        sorted_chunks = sorted(
            chunk_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        # Format results
        results = []
        for chunk_id, score in sorted_chunks:
            chunk = self.chunks.get(chunk_id)
            if chunk:
                results.append({
                    'chunk_id': chunk_id,
                    'content': chunk.content,
                    'source': chunk.source,
                    'type': chunk.chunk_type,
                    'score': score,
                    'metadata': chunk.metadata
                })
        
        return results
    
    def get_chunk(self, chunk_id: str) -> Optional[KnowledgeChunk]:
        """
        Get a specific chunk by ID.
        
        Args:
            chunk_id: Chunk ID
            
        Returns:
            KnowledgeChunk or None
        """
        return self.chunks.get(chunk_id)
    
    def update_chunk(self, chunk_id: str, new_content: str) -> bool:
        """
        Update a chunk's content.
        
        Args:
            chunk_id: Chunk ID to update
            new_content: New content
            
        Returns:
            True if updated successfully
        """
        if chunk_id not in self.chunks:
            return False
        
        chunk = self.chunks[chunk_id]
        
        # Remove old keywords from index
        old_keywords = self._extract_keywords(chunk.content)
        for keyword in old_keywords:
            if keyword in self.index and chunk_id in self.index[keyword]:
                self.index[keyword].remove(chunk_id)
        
        # Update content
        chunk.content = new_content
        
        # Add new keywords to index
        new_keywords = self._extract_keywords(new_content)
        for keyword in new_keywords:
            if keyword not in self.index:
                self.index[keyword] = []
            if chunk_id not in self.index[keyword]:
                self.index[keyword].append(chunk_id)
        
        self._save_index()
        return True
    
    def delete_chunk(self, chunk_id: str) -> bool:
        """
        Delete a chunk.
        
        Args:
            chunk_id: Chunk ID to delete
            
        Returns:
            True if deleted successfully
        """
        if chunk_id not in self.chunks:
            return False
        
        chunk = self.chunks[chunk_id]
        
        # Remove from index
        keywords = self._extract_keywords(chunk.content)
        for keyword in keywords:
            if keyword in self.index and chunk_id in self.index[keyword]:
                self.index[keyword].remove(chunk_id)
                
                # Clean up empty keyword entries
                if not self.index[keyword]:
                    del self.index[keyword]
        
        # Remove chunk
        del self.chunks[chunk_id]
        
        self._save_index()
        return True
    
    def get_statistics(self) -> Dict:
        """
        Get RAG system statistics.
        
        Returns:
            Statistics dictionary
        """
        doc_types = {}
        sources = set()
        
        for chunk in self.chunks.values():
            doc_types[chunk.chunk_type] = doc_types.get(chunk.chunk_type, 0) + 1
            sources.add(chunk.source)
        
        return {
            'total_chunks': len(self.chunks),
            'total_keywords': len(self.index),
            'document_types': doc_types,
            'unique_sources': len(sources),
            'average_chunk_size': self._calculate_average_chunk_size()
        }
    
    def _chunk_document(
        self,
        content: str,
        source: str,
        doc_type: str,
        metadata: Dict
    ) -> List[KnowledgeChunk]:
        """Chunk a document into smaller pieces."""
        chunks = []
        
        # Simple chunking by paragraphs/sections
        # Split on double newlines or headers
        sections = re.split(r'\n\n+|\n#{1,3}\s+', content)
        
        for i, section in enumerate(sections):
            section = section.strip()
            if not section or len(section) < 50:  # Skip very short sections
                continue
            
            # Generate chunk ID
            chunk_hash = hashlib.md5(
                f"{source}_{i}_{section[:100]}".encode()
            ).hexdigest()[:12]
            chunk_id = f"chunk_{chunk_hash}"
            
            chunk = KnowledgeChunk(
                chunk_id=chunk_id,
                content=section,
                source=source,
                chunk_type=doc_type,
                metadata={
                    **metadata,
                    'section_index': i,
                    'word_count': len(section.split()),
                    'char_count': len(section)
                },
                created_at=datetime.now().isoformat()
            )
            
            chunks.append(chunk)
        
        return chunks
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Split into words
        words = text.split()
        
        # Filter out common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'between', 'among', 'is', 'are',
            'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do',
            'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
            'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he',
            'she', 'it', 'we', 'they', 'them', 'their', 'there', 'then', 'than'
        }
        
        # Filter words
        keywords = [
            word for word in words
            if len(word) > 2  # Minimum length
            and word not in stop_words
            and not word.isdigit()
        ]
        
        # Return unique keywords (limited to prevent index bloat)
        return list(set(keywords))[:20]
    
    def _find_matching_chunks(
        self,
        keywords: List[str],
        intent: Optional[str] = None
    ) -> List[KnowledgeChunk]:
        """Find chunks matching keywords."""
        chunk_scores: Dict[str, int] = {}
        
        for keyword in keywords:
            if keyword in self.index:
                for chunk_id in self.index[keyword]:
                    chunk = self.chunks.get(chunk_id)
                    if not chunk:
                        continue
                    
                    # Filter by intent if provided
                    if intent:
                        if intent == 'troubleshoot' and chunk.chunk_type != 'troubleshooting':
                            continue
                        if intent == 'code_help' and chunk.chunk_type != 'code_example':
                            continue
                    
                    chunk_scores[chunk_id] = chunk_scores.get(chunk_id, 0) + 1
        
        # Return matching chunks
        matching_chunks = []
        for chunk_id in chunk_scores:
            chunk = self.chunks.get(chunk_id)
            if chunk:
                matching_chunks.append(chunk)
        
        return matching_chunks
    
    def _score_chunks(
        self,
        chunks: List[KnowledgeChunk],
        query: str,
        query_keywords: List[str]
    ) -> List[Dict]:
        """Score chunks by relevance."""
        scored_chunks = []
        query_lower = query.lower()
        
        for chunk in chunks:
            score = 0
            chunk_lower = chunk.content.lower()
            
            # Exact match bonus
            if query_lower in chunk_lower:
                score += 10
            
            # Keyword frequency
            chunk_keywords = self._extract_keywords(chunk.content)
            keyword_overlap = set(query_keywords) & set(chunk_keywords)
            score += len(keyword_overlap) * 2
            
            # Source relevance
            if chunk.chunk_type == 'documentation':
                score += 3
            elif chunk.chunk_type == 'code_example':
                score += 2
            
            # Content length factor (prefer medium-length chunks)
            content_length = len(chunk.content)
            if 200 <= content_length <= 1000:
                score += 1
            
            # Recency bonus
            if chunk.metadata.get('recency_score'):
                score += chunk.metadata['recency_score']
            
            scored_chunks.append({
                'chunk': chunk,
                'score': score
            })
        
        return scored_chunks
    
    def _calculate_average_chunk_size(self) -> float:
        """Calculate average chunk size in characters."""
        if not self.chunks:
            return 0
        
        total_size = sum(len(chunk.content) for chunk in self.chunks.values())
        return total_size / len(self.chunks)
    
    def _build_initial_index(self) -> None:
        """Build initial knowledge base index."""
        # Add built-in migration knowledge
        builtin_knowledge = [
            {
                'content': """
                React Hooks Migration Guide:
                
                When migrating from class components to functional components with hooks:
                
                1. Replace class definitions with function definitions
                2. Convert state from this.state to useState hook
                3. Replace lifecycle methods with useEffect
                4. Convert event handlers to regular functions
                5. Remove constructor and this bindings
                
                Common patterns:
                - componentDidMount -> useEffect with empty dependency array
                - componentDidUpdate -> useEffect with specific dependencies
                - componentWillUnmount -> useEffect cleanup function
                - this.setState -> useState setter function
                """,
                'source': 'builtin_react_hooks',
                'type': 'documentation',
                'metadata': {'topic': 'react-hooks', 'priority': 'high'}
            },
            {
                'content': """
                Vue 3 Composition API Migration:
                
                Converting from Options API to Composition API:
                
                1. Replace export default with setup() function
                2. Move data() properties to ref() or reactive()
                3. Convert methods to regular functions
                4. Replace lifecycle hooks with onMounted, onUnmounted
                5. Use computed() for computed properties
                6. Move watchers to watch() or watchEffect()
                
                Key differences:
                - No more 'this' keyword
                - Explicit imports required
                - Better TypeScript support
                - More flexible code organization
                """,
                'source': 'builtin_vue3',
                'type': 'documentation',
                'metadata': {'topic': 'vue3', 'priority': 'high'}
            },
            {
                'content': """
                Python 3 Migration Checklist:
                
                Common changes needed:
                
                1. Print statements: print x -> print(x)
                2. Integer division: 5/2 = 2.5, use 5//2 for integer division
                3. Unicode strings: All strings are unicode by default
                4. Dictionary methods: .keys(), .values(), .items() return views
                5. xrange -> range
                6. .next() method -> next() function
                7. Reduce moved to functools
                8. ConfigParser renamed to configparser
                
                Testing:
                - Use 2to3 tool for automated conversion
                - Test thoroughly after migration
                - Update dependencies to Python 3 compatible versions
                """,
                'source': 'builtin_python3',
                'type': 'documentation',
                'metadata': {'topic': 'python3', 'priority': 'high'}
            },
            {
                'content': """
                Security Best Practices for Migration:
                
                Before migration:
                - Run security scans on existing code
                - Review for exposed secrets
                - Check for vulnerabilities in dependencies
                
                During migration:
                - Validate all inputs
                - Use parameterized queries
                - Sanitize file paths
                - Check for injection vulnerabilities
                
                After migration:
                - Run security scans again
                - Verify no new vulnerabilities introduced
                - Update security documentation
                - Review access controls
                
                Tools to use:
                - Bandit for Python security
                - ESLint security plugins
                - Dependency vulnerability scanners
                """,
                'source': 'builtin_security',
                'type': 'documentation',
                'metadata': {'topic': 'security', 'priority': 'high'}
            },
            {
                'content': """
                Troubleshooting Common Migration Issues:
                
                Issue: Tests failing after migration
                Solution: Update test setup, check for mocking issues, verify imports
                
                Issue: Performance degradation
                Solution: Profile the code, optimize hot paths, check for unnecessary re-renders
                
                Issue: Build errors
                Solution: Update build configuration, check for missing dependencies, verify file paths
                
                Issue: Runtime errors
                Solution: Check for null/undefined values, verify API compatibility, review error logs
                
                Issue: Type errors
                Solution: Update type definitions, add proper type annotations, check for breaking changes
                
                General tips:
                - Always have a rollback plan
                - Test in staging environment first
                - Monitor metrics after migration
                - Have team ready for quick fixes
                """,
                'source': 'builtin_troubleshooting',
                'type': 'troubleshooting',
                'metadata': {'topic': 'troubleshooting', 'priority': 'high'}
            }
        ]
        
        for knowledge in builtin_knowledge:
            self.add_document(
                content=knowledge['content'],
                source=knowledge['source'],
                doc_type=knowledge['type'],
                metadata=knowledge['metadata']
            )
    
    def _load_index(self) -> None:
        """Load index from file."""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r') as f:
                    data = json.load(f)
                    
                    # Load chunks
                    for chunk_data in data.get('chunks', []):
                        chunk = KnowledgeChunk(**chunk_data)
                        self.chunks[chunk.chunk_id] = chunk
                    
                    # Load index
                    self.index = data.get('index', {})
            
            except Exception:
                pass
    
    def _save_index(self) -> None:
        """Save index to file."""
        try:
            data = {
                'chunks': [
                    {
                        'chunk_id': c.chunk_id,
                        'content': c.content,
                        'source': c.source,
                        'chunk_type': c.chunk_type,
                        'metadata': c.metadata,
                        'created_at': c.created_at
                    }
                    for c in self.chunks.values()
                ],
                'index': self.index,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.index_file, 'w') as f:
                json.dump(data, f, indent=2)
        
        except Exception:
            pass
