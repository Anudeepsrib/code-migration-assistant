import ast
from code_migration.core.security.input_validator import CodeValidator, SecurityError

patterns = [
    "def invalid_syntax(",
    "if True print('no colon')",
    "yield 42",
    "return 1",
    "!!!"
]

for p in patterns:
    print(f"Pattern: {p!r}")
    try:
        CodeValidator.validate_pattern(p)
        print("  Result: Success (ERROR: expected SecurityError)")
    except SecurityError as e:
        print(f"  Result: Caught SecurityError: {e}")
    except Exception as e:
        print(f"  Result: Caught unexpected exception: {type(e).__name__}: {e}")
