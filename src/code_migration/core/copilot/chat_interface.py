"""
Chat interface for Migration Co-pilot.

Provides interactive chat capabilities:
- Command-line chat interface
- Rich formatting with colors
- Conversation management
- Context preservation
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .copilot_engine import MigrationCopilot, CopilotResponse


class ChatInterface:
    """
    Interactive chat interface for Migration Co-pilot.
    
    Features:
    - Interactive chat session
    - Rich text formatting
    - Conversation history
    - Context management
    """
    
    def __init__(self, project_path: Path):
        """
        Initialize chat interface.
        
        Args:
            project_path: Path to project directory
        """
        self.project_path = Path(project_path)
        self.copilot = MigrationCopilot(project_path)
        self.session_start = datetime.now()
        
    def start_interactive_session(self) -> None:
        """Start interactive chat session."""
        self._print_welcome_message()
        
        while True:
            try:
                # Get user input
                user_input = input("\n🧑 You: ").strip()
                
                # Check for exit commands
                if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
                    self._print_goodbye_message()
                    break
                
                # Check for special commands
                if user_input.startswith('/'):
                    self._handle_command(user_input)
                    continue
                
                # Skip empty input
                if not user_input:
                    continue
                
                # Get response from copilot
                response = self.copilot.chat(user_input)
                
                # Print response
                self._print_response(response)
                
            except KeyboardInterrupt:
                print("\n\n👋 Session interrupted. Goodbye!")
                break
            except EOFError:
                break
    
    def send_message(self, message: str, context: Optional[Dict] = None) -> CopilotResponse:
        """
        Send a message to the copilot.
        
        Args:
            message: User message
            context: Optional context
            
        Returns:
            CopilotResponse
        """
        return self.copilot.chat(message, context)
    
    def get_conversation_summary(self) -> Dict:
        """
        Get summary of current conversation.
        
        Returns:
            Conversation summary
        """
        return self.copilot.get_conversation_summary()
    
    def clear_conversation(self) -> None:
        """Clear conversation history."""
        self.copilot.clear_conversation()
        print("🗑️  Conversation history cleared.")
    
    def _print_welcome_message(self) -> None:
        """Print welcome message."""
        print("""
🚀 Welcome to Migration Co-pilot!

I'm your AI assistant for code migrations. I can help you with:

💡 Migration recommendations and best practices
📝 Code transformation examples
🔧 Troubleshooting migration issues
📊 Migration planning and estimates
🔒 Security considerations
❓ General migration questions

Type your message to start chatting, or use these commands:
  /help      - Show available commands
  /status    - Show conversation status
  /clear     - Clear conversation history
  /summary   - Show conversation summary
  /recommend - Get migration recommendations
  /analyze   - Analyze code for issues
  /exit      - End the session

Let's make your migration successful! 🎯
        """)
    
    def _print_goodbye_message(self) -> None:
        """Print goodbye message."""
        summary = self.get_conversation_summary()
        duration = summary.get('conversation_duration', 0)
        
        print(f"""
👋 Thanks for using Migration Co-pilot!

Session Summary:
- Duration: {duration:.1f} minutes
- Messages exchanged: {summary.get('total_messages', 0)}
- Topics discussed: {', '.join(summary.get('topics_discussed', []))}

Have a great migration! 🚀
        """)
    
    def _print_response(self, response: CopilotResponse) -> None:
        """Print copilot response with formatting."""
        print(f"\n🤖 Co-pilot (confidence: {response.confidence:.0%}):")
        print(f"{response.message}\n")
        
        # Print suggestions
        if response.suggestions:
            print("💡 Suggestions:")
            for i, suggestion in enumerate(response.suggestions, 1):
                print(f"  {i}. {suggestion}")
            print()
        
        # Print code examples
        if response.code_examples:
            print("💻 Code Examples:")
            for i, example in enumerate(response.code_examples, 1):
                print(f"  Example {i}:")
                # Format code with indentation
                lines = example.split('\n')
                for line in lines[:10]:  # Show first 10 lines
                    print(f"    {line}")
                if len(lines) > 10:
                    print(f"    ... ({len(lines) - 10} more lines)")
                print()
        
        # Print documentation links
        if response.documentation_links:
            print("📚 Documentation:")
            for link in response.documentation_links:
                print(f"  - {link}")
            print()
    
    def _handle_command(self, command: str) -> None:
        """Handle special commands."""
        cmd = command.lower().strip()
        
        if cmd == '/help':
            self._print_help()
        elif cmd == '/status':
            self._print_status()
        elif cmd == '/clear':
            self.clear_conversation()
        elif cmd == '/summary':
            self._print_summary()
        elif cmd == '/recommend':
            self._handle_recommend_command()
        elif cmd == '/analyze':
            self._handle_analyze_command()
        elif cmd.startswith('/recommend '):
            migration_type = cmd.replace('/recommend ', '').strip()
            self._get_recommendations(migration_type)
        else:
            print(f"❓ Unknown command: {command}")
            print("Type /help for available commands.")
    
    def _print_help(self) -> None:
        """Print help message."""
        print("""
📋 Available Commands:

General:
  /help      - Show this help message
  /status    - Show conversation status
  /summary   - Show conversation summary
  /clear     - Clear conversation history
  /exit      - End the session

Migration:
  /recommend [type]  - Get migration recommendations
  /analyze   - Analyze code for migration issues
  /plan      - Create migration plan
  /troubleshoot [issue] - Get troubleshooting help

Examples:
  /recommend react-hooks
  /recommend vue3
  /analyze src/components/Button.jsx
  /troubleshoot "Tests failing after migration"
        """)
    
    def _print_status(self) -> None:
        """Print conversation status."""
        summary = self.get_conversation_summary()
        
        print(f"""
📊 Conversation Status:

Duration: {summary.get('conversation_duration', 0):.1f} minutes
Messages: {summary.get('total_messages', 0)} total
          {summary.get('user_messages', 0)} from you
          {summary.get('assistant_messages', 0)} from me

Topics Discussed:
{chr(10).join(f"  - {topic}" for topic in summary.get('topics_discussed', [])) or "  None yet"}

Average Confidence: {summary.get('average_confidence', 0):.0%}
        """)
    
    def _print_summary(self) -> None:
        """Print conversation summary."""
        summary = self.get_conversation_summary()
        
        print(f"""
📝 Conversation Summary:

Session Duration: {summary.get('conversation_duration', 0):.1f} minutes
Total Messages: {summary.get('total_messages', 0)}

Topics Discussed ({len(summary.get('topics_discussed', []))}):
{chr(10).join(f"  • {topic}" for topic in summary.get('topics_discussed', [])) or "  No specific topics"}

Quality Metrics:
• Average Response Confidence: {summary.get('average_confidence', 0):.0%}
• Assistant Responses: {summary.get('assistant_messages', 0)}
• User Questions: {summary.get('user_messages', 0)}

This conversation is being saved for future reference.
        """)
    
    def _handle_recommend_command(self) -> None:
        """Handle recommend command interactively."""
        print("Available migration types:")
        print("  1. react-hooks (React Class → Hooks)")
        print("  2. vue3 (Vue 2 → Vue 3)")
        print("  3. python3 (Python 2 → 3)")
        print("  4. typescript (JavaScript → TypeScript)")
        
        choice = input("\nEnter migration type (or 'cancel'): ").strip().lower()
        
        if choice == 'cancel':
            return
        
        if choice in ['1', 'react-hooks']:
            self._get_recommendations('react-hooks')
        elif choice in ['2', 'vue3']:
            self._get_recommendations('vue3')
        elif choice in ['3', 'python3']:
            self._get_recommendations('python3')
        elif choice in ['4', 'typescript']:
            self._get_recommendations('typescript')
        else:
            print(f"❌ Unknown migration type: {choice}")
    
    def _get_recommendations(self, migration_type: str) -> None:
        """Get and display migration recommendations."""
        print(f"\n🔍 Getting recommendations for {migration_type} migration...\n")
        
        recommendations = self.copilot.get_migration_recommendations(migration_type)
        
        if not recommendations:
            print("No specific recommendations found.")
            return
        
        print(f"Found {len(recommendations)} recommendations:\n")
        
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec.get('title', 'Recommendation')}")
            print(f"   Priority: {rec.get('priority', 'Medium')}")
            print(f"   {rec.get('description', '')}")
            
            if rec.get('additional_context'):
                print(f"   Additional context: {len(rec['additional_context'])} items")
            
            print()
    
    def _handle_analyze_command(self) -> None:
        """Handle analyze command interactively."""
        file_path = input("Enter file path to analyze (or 'cancel'): ").strip()
        
        if file_path.lower() == 'cancel':
            return
        
        language = input("Enter language (javascript/python/etc.): ").strip().lower()
        
        full_path = self.project_path / file_path
        
        if not full_path.exists():
            print(f"❌ File not found: {file_path}")
            return
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            print(f"\n🔍 Analyzing {file_path}...\n")
            
            issues = self.copilot.analyze_code_issues(code, language)
            
            if not issues:
                print("✅ No migration issues detected in this file.")
                return
            
            print(f"Found {len(issues)} potential issues:\n")
            
            for i, issue in enumerate(issues, 1):
                severity_emoji = {
                    'ERROR': '🔴',
                    'WARNING': '🟡',
                    'INFO': '🔵'
                }.get(issue.get('severity', 'INFO'), '⚪')
                
                print(f"{i}. {severity_emoji} {issue.get('type', 'Issue')}")
                print(f"   Severity: {issue.get('severity', 'Unknown')}")
                print(f"   {issue.get('message', '')}")
                
                if issue.get('suggestion'):
                    print(f"   💡 Suggestion: {issue['suggestion']}")
                
                print()
        
        except Exception as e:
            print(f"❌ Error analyzing file: {e}")
