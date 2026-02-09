"""
Migration Co-pilot engine for AI-powered assistance.

Main engine that coordinates:
- Natural language processing
- RAG-based knowledge retrieval
- Context-aware responses
- Migration recommendations
"""

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from ..security import SecurityAuditLogger
from .rag_system import RAGSystem
from .knowledge_base import KnowledgeBase


@dataclass
class ChatMessage:
    """Chat message data structure."""
    message_id: str
    timestamp: str
    role: str  # 'user', 'assistant', 'system'
    content: str
    context: Dict
    metadata: Dict


@dataclass
class CopilotResponse:
    """Co-pilot response structure."""
    response_id: str
    message: str
    suggestions: List[str]
    code_examples: List[str]
    documentation_links: List[str]
    confidence: float
    context_used: List[str]


class MigrationCopilot:
    """
    AI-powered Migration Co-pilot.
    
    Features:
    - Natural language chat interface
    - Context-aware responses
    - RAG-based knowledge retrieval
    - Migration pattern recommendations
    - Interactive troubleshooting
    """
    
    def __init__(self, project_path: Path):
        """
        Initialize Migration Co-pilot.
        
        Args:
            project_path: Path to project directory
        """
        self.project_path = Path(project_path)
        self.conversation_history: List[ChatMessage] = []
        self.rag_system = RAGSystem(project_path)
        self.knowledge_base = KnowledgeBase(project_path)
        
        log_dir = self.project_path / '.migration-logs'
        self.audit_logger = SecurityAuditLogger(log_dir)
        
        self.conversation_file = self.project_path / '.migration-copilot.json'
        self._load_conversation_history()
        
        # Initialize with system context
        self._initialize_context()
    
    def chat(self, user_message: str, context: Optional[Dict] = None) -> CopilotResponse:
        """
        Process user message and generate response.
        
        Args:
            user_message: User's message
            context: Optional conversation context
            
        Returns:
            CopilotResponse with answer and suggestions
        """
        # Create user message
        user_msg = ChatMessage(
            message_id=f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now().isoformat(),
            role='user',
            content=user_message,
            context=context or {},
            metadata={}
        )
        
        self.conversation_history.append(user_msg)
        
        # Analyze intent
        intent = self._analyze_intent(user_message)
        
        # Retrieve relevant knowledge
        knowledge_context = self.rag_system.retrieve_relevant_context(
            query=user_message,
            intent=intent,
            conversation_history=self.conversation_history[-10:]  # Last 10 messages
        )
        
        # Generate response
        response = self._generate_response(
            user_message=user_message,
            intent=intent,
            knowledge_context=knowledge_context,
            conversation_context=self.conversation_history[-5:]  # Last 5 messages
        )
        
        # Create assistant message
        assistant_msg = ChatMessage(
            message_id=f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}_response",
            timestamp=datetime.now().isoformat(),
            role='assistant',
            content=response.message,
            context={'intent': intent, 'knowledge_used': knowledge_context},
            metadata={
                'confidence': response.confidence,
                'suggestions_count': len(response.suggestions),
                'code_examples_count': len(response.code_examples)
            }
        )
        
        self.conversation_history.append(assistant_msg)
        
        # Log interaction
        self.audit_logger.log_migration_event(
            migration_type='copilot',
            project_path=str(self.project_path),
            user='user',
            action='CHAT_INTERACTION',
            result='SUCCESS',
            details={
                'message_id': user_msg.message_id,
                'intent': intent,
                'confidence': response.confidence
            }
        )
        
        self._save_conversation_history()
        
        return response
    
    def get_migration_recommendations(
        self,
        migration_type: str,
        file_path: Optional[str] = None
    ) -> List[Dict]:
        """
        Get AI-powered migration recommendations.
        
        Args:
            migration_type: Type of migration
            file_path: Optional specific file to analyze
            
        Returns:
            List of recommendation dictionaries
        """
        # Query knowledge base for recommendations
        recommendations = self.knowledge_base.get_recommendations(
            migration_type=migration_type,
            file_path=file_path
        )
        
        # Enhance with RAG context
        enhanced_recommendations = []
        for rec in recommendations:
            context = self.rag_system.retrieve_relevant_context(
                query=f"{migration_type} {rec.get('topic', '')}",
                limit=3
            )
            
            rec['additional_context'] = context
            enhanced_recommendations.append(rec)
        
        return enhanced_recommendations
    
    def analyze_code_issues(self, code: str, language: str) -> List[Dict]:
        """
        Analyze code for migration issues.
        
        Args:
            code: Code to analyze
            language: Programming language
            
        Returns:
            List of identified issues
        """
        issues = []
        
        # Pattern-based analysis
        if language == 'javascript' or language == 'jsx':
            # Check for class components
            if 'class.*extends.*Component' in code or 'createClass' in code:
                issues.append({
                    'type': 'class_component',
                    'severity': 'INFO',
                    'message': 'Class component detected. Consider migrating to functional component with hooks.',
                    'suggestion': 'Use function component with useState and useEffect hooks'
                })
            
            # Check for lifecycle methods
            lifecycle_methods = ['componentDidMount', 'componentWillUnmount', 'componentDidUpdate']
            for method in lifecycle_methods:
                if method in code:
                    issues.append({
                        'type': 'lifecycle_method',
                        'severity': 'INFO',
                        'message': f'Lifecycle method {method} detected. Can be replaced with useEffect.',
                        'suggestion': f'Replace {method} with useEffect hook'
                    })
            
            # Check for this.setState
            if 'this.setState' in code:
                issues.append({
                    'type': 'set_state',
                    'severity': 'INFO',
                    'message': 'this.setState detected. Replace with useState hook.',
                    'suggestion': 'const [state, setState] = useState(initialValue)'
                })
        
        elif language == 'python':
            # Check for Python 2 patterns
            if 'print ' in code and 'print(' not in code:
                issues.append({
                    'type': 'python2_print',
                    'severity': 'ERROR',
                    'message': 'Python 2 print statement detected. Must use print() function in Python 3.',
                    'suggestion': 'Replace "print x" with "print(x)"'
                })
            
            # Check for integer division
            if re.search(r'/\s*\d+', code):
                issues.append({
                    'type': 'integer_division',
                    'severity': 'WARNING',
                    'message': 'Integer division may behave differently in Python 3.',
                    'suggestion': 'Use // for integer division or ensure proper float handling'
                })
        
        # Query knowledge base for additional issues
        additional_issues = self.knowledge_base.analyze_code_patterns(
            code=code,
            language=language
        )
        
        issues.extend(additional_issues)
        
        return issues
    
    def generate_code_example(
        self,
        migration_type: str,
        source_pattern: str,
        target_pattern: str
    ) -> str:
        """
        Generate code transformation example.
        
        Args:
            migration_type: Type of migration
            source_pattern: Source code pattern
            target_pattern: Target code pattern
            
        Returns:
            Generated code example
        """
        # Get transformation template from knowledge base
        template = self.knowledge_base.get_transformation_template(
            migration_type=migration_type,
            source_pattern=source_pattern,
            target_pattern=target_pattern
        )
        
        return template
    
    def troubleshoot_issue(
        self,
        issue_description: str,
        error_message: Optional[str] = None,
        stack_trace: Optional[str] = None
    ) -> CopilotResponse:
        """
        Troubleshoot a migration issue.
        
        Args:
            issue_description: Description of the issue
            error_message: Optional error message
            stack_trace: Optional stack trace
            
        Returns:
            CopilotResponse with troubleshooting steps
        """
        # Build troubleshooting query
        query = issue_description
        if error_message:
            query += f" Error: {error_message}"
        
        # Retrieve troubleshooting knowledge
        troubleshooting_context = self.rag_system.retrieve_relevant_context(
            query=query,
            intent='troubleshoot',
            limit=5
        )
        
        # Generate troubleshooting response
        response = self._generate_troubleshooting_response(
            issue_description=issue_description,
            error_message=error_message,
            stack_trace=stack_trace,
            context=troubleshooting_context
        )
        
        return response
    
    def get_conversation_summary(self) -> Dict:
        """
        Get summary of current conversation.
        
        Returns:
            Conversation summary dictionary
        """
        user_messages = [m for m in self.conversation_history if m.role == 'user']
        assistant_messages = [m for m in self.conversation_history if m.role == 'assistant']
        
        # Extract topics discussed
        topics = set()
        for msg in self.conversation_history:
            if 'intent' in msg.context:
                topics.add(msg.context['intent'])
        
        return {
            'total_messages': len(self.conversation_history),
            'user_messages': len(user_messages),
            'assistant_messages': len(assistant_messages),
            'topics_discussed': list(topics),
            'conversation_duration': self._calculate_conversation_duration(),
            'average_confidence': self._calculate_average_confidence()
        }
    
    def clear_conversation(self) -> None:
        """Clear conversation history."""
        self.conversation_history.clear()
        self._save_conversation_history()
    
    def _analyze_intent(self, message: str) -> str:
        """Analyze user message intent."""
        message_lower = message.lower()
        
        # Define intent patterns
        intents = {
            'troubleshoot': ['error', 'issue', 'problem', 'failed', 'not working', 'bug'],
            'recommend': ['recommend', 'suggest', 'best practice', 'should I'],
            'explain': ['explain', 'how does', 'what is', 'why'],
            'code_help': ['code', 'example', 'transform', 'convert', 'migrate'],
            'planning': ['plan', 'schedule', 'timeline', 'estimate'],
            'security': ['security', 'safe', 'risk', 'vulnerable'],
            'general': []
        }
        
        # Check for intent matches
        for intent, keywords in intents.items():
            if any(keyword in message_lower for keyword in keywords):
                return intent
        
        return 'general'
    
    def _generate_response(
        self,
        user_message: str,
        intent: str,
        knowledge_context: List[str],
        conversation_context: List[ChatMessage]
    ) -> CopilotResponse:
        """Generate copilot response."""
        response_id = f"resp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Base response generation on intent
        if intent == 'troubleshoot':
            message, suggestions, code_examples = self._generate_troubleshooting_response(
                user_message, knowledge_context
            )
        elif intent == 'recommend':
            message, suggestions, code_examples = self._generate_recommendation_response(
                user_message, knowledge_context
            )
        elif intent == 'explain':
            message, suggestions, code_examples = self._generate_explanation_response(
                user_message, knowledge_context
            )
        elif intent == 'code_help':
            message, suggestions, code_examples = self._generate_code_help_response(
                user_message, knowledge_context
            )
        elif intent == 'planning':
            message, suggestions, code_examples = self._generate_planning_response(
                user_message, knowledge_context
            )
        elif intent == 'security':
            message, suggestions, code_examples = self._generate_security_response(
                user_message, knowledge_context
            )
        else:
            message, suggestions, code_examples = self._generate_general_response(
                user_message, knowledge_context
            )
        
        # Calculate confidence based on knowledge context quality
        confidence = self._calculate_confidence(knowledge_context, intent)
        
        # Generate documentation links
        doc_links = self._generate_documentation_links(intent, knowledge_context)
        
        return CopilotResponse(
            response_id=response_id,
            message=message,
            suggestions=suggestions,
            code_examples=code_examples,
            documentation_links=doc_links,
            confidence=confidence,
            context_used=knowledge_context
        )
    
    def _generate_troubleshooting_response(
        self, message: str, context: List[str]
    ) -> tuple:
        """Generate troubleshooting response."""
        response_msg = "I can help you troubleshoot this issue. Here are some steps to resolve it:"
        
        suggestions = [
            "Check the error logs for more details",
            "Verify all dependencies are installed correctly",
            "Try clearing the cache and rebuilding",
            "Check for syntax errors in the migrated code"
        ]
        
        code_examples = context[:2] if context else []
        
        return response_msg, suggestions, code_examples
    
    def _generate_recommendation_response(
        self, message: str, context: List[str]
    ) -> tuple:
        """Generate recommendation response."""
        response_msg = "Based on your project and best practices, here are my recommendations:"
        
        suggestions = [
            "Start with a pilot migration on a small component",
            "Ensure comprehensive test coverage before migration",
            "Use the visual planner to understand dependencies",
            "Set up automated rollback before making changes"
        ]
        
        code_examples = context[:1] if context else []
        
        return response_msg, suggestions, code_examples
    
    def _generate_explanation_response(
        self, message: str, context: List[str]
    ) -> tuple:
        """Generate explanation response."""
        response_msg = "Let me explain this concept and how it applies to your migration:"
        
        suggestions = [
            "Would you like to see a code example?",
            "Do you want to know about best practices for this?",
            "Should I explain the differences between the old and new approach?"
        ]
        
        code_examples = context[:3] if context else []
        
        return response_msg, suggestions, code_examples
    
    def _generate_code_help_response(
        self, message: str, context: List[str]
    ) -> tuple:
        """Generate code help response."""
        response_msg = "Here's how you can transform this code:"
        
        suggestions = [
            "Run the migration in dry-run mode first",
            "Review the changes before applying them",
            "Test the transformed code thoroughly",
            "Consider using the automated migration tool"
        ]
        
        code_examples = context[:5] if context else []
        
        return response_msg, suggestions, code_examples
    
    def _generate_planning_response(
        self, message: str, context: List[str]
    ) -> tuple:
        """Generate planning response."""
        response_msg = "Here's a recommended migration plan:"
        
        suggestions = [
            "Analyze project complexity using the confidence scorer",
            "Create a visual migration plan with waves",
            "Set up checkpoints before each migration wave",
            "Plan for rollback scenarios"
        ]
        
        code_examples = []
        
        return response_msg, suggestions, code_examples
    
    def _generate_security_response(
        self, message: str, context: List[str]
    ) -> tuple:
        """Generate security response."""
        response_msg = "Security is crucial during migration. Here are key considerations:"
        
        suggestions = [
            "Run security scans before and after migration",
            "Check for exposed secrets in the codebase",
            "Validate all inputs to prevent injection attacks",
            "Ensure audit logging is properly configured"
        ]
        
        code_examples = context[:2] if context else []
        
        return response_msg, suggestions, code_examples
    
    def _generate_general_response(
        self, message: str, context: List[str]
    ) -> tuple:
        """Generate general response."""
        response_msg = "I'm here to help with your migration! Here's what I can assist with:"
        
        suggestions = [
            "Explain migration concepts and patterns",
            "Provide code transformation examples",
            "Help troubleshoot migration issues",
            "Recommend best practices"
        ]
        
        code_examples = context[:2] if context else []
        
        return response_msg, suggestions, code_examples
    
    def _generate_troubleshooting_response(
        self,
        issue_description: str,
        error_message: Optional[str],
        stack_trace: Optional[str],
        context: List[str]
    ) -> CopilotResponse:
        """Generate troubleshooting response."""
        response_id = f"resp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Build troubleshooting message
        message = f"I've analyzed your issue: {issue_description}\n\n"
        message += "Here are the troubleshooting steps:\n\n"
        
        steps = [
            "1. Check the error message and identify the specific component",
            "2. Verify the migration was applied correctly",
            "3. Check for any missing dependencies",
            "4. Review the migration logs for more details"
        ]
        
        message += "\n".join(steps)
        
        if error_message:
            message += f"\n\nError Details:\n{error_message}"
        
        suggestions = [
            "Would you like me to analyze the specific error in more detail?",
            "Should I help you roll back to the previous version?",
            "Do you want to see examples of correct migration patterns?"
        ]
        
        code_examples = context[:3] if context else []
        doc_links = self._generate_documentation_links('troubleshoot', context)
        
        return CopilotResponse(
            response_id=response_id,
            message=message,
            suggestions=suggestions,
            code_examples=code_examples,
            documentation_links=doc_links,
            confidence=0.85,
            context_used=context
        )
    
    def _calculate_confidence(self, context: List[str], intent: str) -> float:
        """Calculate response confidence."""
        base_confidence = 0.7
        
        # Increase confidence based on context quality
        if len(context) >= 3:
            base_confidence += 0.1
        if len(context) >= 5:
            base_confidence += 0.1
        
        # Adjust based on intent specificity
        if intent != 'general':
            base_confidence += 0.05
        
        return min(base_confidence, 0.95)
    
    def _generate_documentation_links(
        self, intent: str, context: List[str]
    ) -> List[str]:
        """Generate relevant documentation links."""
        links = []
        
        # Base documentation links
        base_links = {
            'troubleshoot': [
                'https://docs.code-migration.ai/troubleshooting',
                'https://docs.code-migration.ai/common-issues'
            ],
            'recommend': [
                'https://docs.code-migration.ai/best-practices',
                'https://docs.code-migration.ai/patterns'
            ],
            'explain': [
                'https://docs.code-migration.ai/concepts',
                'https://docs.code-migration.ai/migration-types'
            ],
            'code_help': [
                'https://docs.code-migration.ai/examples',
                'https://docs.code-migration.ai/api-reference'
            ],
            'planning': [
                'https://docs.code-migration.ai/planning',
                'https://docs.code-migration.ai/visual-planner'
            ],
            'security': [
                'https://docs.code-migration.ai/security',
                'https://docs.code-migration.ai/compliance'
            ],
            'general': [
                'https://docs.code-migration.ai',
                'https://docs.code-migration.ai/getting-started'
            ]
        }
        
        links.extend(base_links.get(intent, base_links['general']))
        
        return links
    
    def _calculate_conversation_duration(self) -> float:
        """Calculate conversation duration in minutes."""
        if len(self.conversation_history) < 2:
            return 0
        
        start_time = datetime.fromisoformat(self.conversation_history[0].timestamp)
        end_time = datetime.fromisoformat(self.conversation_history[-1].timestamp)
        
        duration = (end_time - start_time).total_seconds() / 60
        return duration
    
    def _calculate_average_confidence(self) -> float:
        """Calculate average confidence from assistant messages."""
        assistant_messages = [m for m in self.conversation_history if m.role == 'assistant']
        
        if not assistant_messages:
            return 0
        
        confidences = []
        for msg in assistant_messages:
            if 'confidence' in msg.metadata:
                confidences.append(msg.metadata['confidence'])
        
        return sum(confidences) / len(confidences) if confidences else 0
    
    def _initialize_context(self) -> None:
        """Initialize conversation context."""
        system_msg = ChatMessage(
            message_id=f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}_system",
            timestamp=datetime.now().isoformat(),
            role='system',
            content='Migration Co-pilot initialized. Ready to assist with migrations.',
            context={'initialization': True},
            metadata={}
        )
        
        self.conversation_history.append(system_msg)
    
    def _load_conversation_history(self) -> None:
        """Load conversation history from file."""
        if self.conversation_file.exists():
            try:
                with open(self.conversation_file, 'r') as f:
                    data = json.load(f)
                    for msg_data in data.get('messages', []):
                        msg = ChatMessage(**msg_data)
                        self.conversation_history.append(msg)
            except Exception:
                pass
    
    def _save_conversation_history(self) -> None:
        """Save conversation history to file."""
        try:
            # Keep only last 100 messages
            recent_messages = self.conversation_history[-100:]
            
            data = {
                'messages': [
                    {
                        'message_id': m.message_id,
                        'timestamp': m.timestamp,
                        'role': m.role,
                        'content': m.content,
                        'context': m.context,
                        'metadata': m.metadata
                    }
                    for m in recent_messages
                ]
            }
            
            with open(self.conversation_file, 'w') as f:
                json.dump(data, f, indent=2)
        
        except Exception:
            pass
