import ast
import logging
from typing import Optional, Union, Any

logger = logging.getLogger("code_migration")

def safe_parse_python(content: str) -> Optional[ast.AST]:
    """
    Safely parse Python code into an AST.
    """
    try:
        return ast.parse(content)
    except SyntaxError as e:
        logger.error(f"Syntax Error parsing Python code: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error parsing code: {e}")
        return None

def get_ast_nodes(tree: ast.AST, node_type: Union[type, tuple]) -> list:
    """
    Extract specific nodes from AST.
    """
    return [node for node in ast.walk(tree) if isinstance(node, node_type)]
