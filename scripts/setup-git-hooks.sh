#!/bin/bash

# Setup Git hooks for security scanning
# This script installs pre-commit hooks for automatic security scanning

set -e

echo "🔧 Setting up Git hooks for security scanning..."

# Create .git/hooks directory if it doesn't exist
mkdir -p .git/hooks

# Install pre-commit hook
echo "Installing pre-commit hook..."

cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook for security scanning

# Run the security scanning script
if [ -f "scripts/pre-commit-security.sh" ]; then
    scripts/pre-commit-security.sh
else
    echo "❌ Security scanning script not found: scripts/pre-commit-security.sh"
    echo "❌ Please run: chmod +x scripts/setup-git-hooks.sh"
    exit 1
fi
EOF

# Make pre-commit hook executable
chmod +x .git/hooks/pre-commit

# Install pre-push hook
echo "Installing pre-push hook..."

cat > .git/hooks/pre-push << 'EOF
#!/bin/bash
# Pre-push hook for security scanning

# Run comprehensive security scan before pushing
if [ -f "scripts/security-scan.sh" ]; then
    scripts/security-scan.sh
else
    echo "❌ Security scanning script not found: scripts/security-scan.sh"
    echo "❌ Please run: chmod +x scripts/setup-git-hooks.sh"
    exit 1
fi
EOF

# Make pre-push hook executable
chmod +x .git/hooks/pre-push

# Install commit-msg hook for security
echo "Installing commit-msg hook..."

cat > .git/hooks/commit-msg << 'EOF
#!/bin/bash
# Commit message hook for security

# Check commit message for potential secrets
if grep -iE "(password|secret|key|token|credential)" "$1" >/dev/null; then
    echo "❌ Commit message may contain sensitive information"
    echo "❌ Please remove any sensitive information from commit message"
    exit 1
fi

# Check for potential secret patterns in commit message
if echo "$1" | grep -E "(sk-[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{36}|aws_access_key_id)" >/dev/null; then
    echo "❌ Commit message may contain secrets"
    echo "❌ Please remove any secrets from commit message"
    exit 1
fi

echo "✅ Commit message security check passed"
EOF

# Make commit-msg hook executable
chmod +x .git/hooks/commit-msg

echo "✅ Git hooks installed successfully!"
echo ""
echo "🔒 Installed hooks:"
echo "  - pre-commit: Security scan before committing"
echo "  - pre-push: Security scan before pushing"
echo "  - commit-msg: Check commit message for secrets"
echo ""
echo "📋 To bypass hooks (not recommended):"
echo "  git commit --no-verify"
echo "  git push --no-verify"
echo ""
echo "🔧 To uninstall hooks:"
echo "  rm .git/hooks/pre-commit"
echo "  rm .git/hooks/pre-push"
echo "  rm .git/hooks/commit-msg"

# Install pre-commit if available
if command -v pre-commit >/dev/null 2>&1; then
    echo ""
    echo "🔧 Installing pre-commit..."
    pre-commit install
    echo ""
    echo "📋 Pre-commit configuration:"
    echo "  - .pre-commit-config.yaml"
    echo "  - Security scanning hooks"
    echo "  - Code formatting checks"
    echo "  - Linting checks"
else
    echo ""
    echo "⚠️  Pre-commit not installed"
    echo "   Install with: pip install pre-commit"
fi

echo "✅ Git hooks setup completed!"
