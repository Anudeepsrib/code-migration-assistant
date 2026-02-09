#!/bin/bash

# Pre-commit hook for security scanning
# This script runs before each commit to ensure no secrets are committed

set -e

echo "🔒 Running pre-commit security scan..."

# Check for staged files that might contain secrets
STAGED_FILES=$(git diff --cached --name-only)

# File patterns that should be checked for secrets
SECRET_PATTERNS=(
    "\.env"
    "config\.yaml"
    "config\.yml"
    "config\.json"
    "config\.toml"
    "config\.ini"
    "secrets\.yaml"
    "secrets\.yml"
    "secrets\.json"
    "production\.yaml"
    "production\.yml"
    "production\.json"
    "staging\.yaml"
    "staging\.yml"
    "staging\.json"
    "\.pem"
    "\.key"
    "\.crt"
    "\.p12"
    "\.pfx"
    "\.jks"
    "\.keystore"
)

# Check if any staged files match secret patterns
for pattern in "${SECRET_PATTERNS[@]}"; do
    if echo "$STAGED_FILES" | grep -E "$pattern" >/dev/null; then
        echo "❌ Attempting to commit file that may contain secrets: $pattern"
        echo "❌ Please remove or encrypt the sensitive data before committing"
        echo "❌ If this is a false positive, add the file to .gitignore"
        exit 1
    fi
done

# Check for potential secrets in staged content
echo "🔍 Scanning staged files for potential secrets..."

# Check for API keys
if git diff --cached | grep -i "sk-[a-zA-Z0-9]{20,}" >/dev/null; then
    echo "❌ Potential API key found in staged changes"
    echo "❌ Please remove or encrypt the API key before committing"
    exit 1
fi

# Check for passwords
if git diff --cached | grep -i "password.*=" >/dev/null; then
    echo "❌ Potential password found in staged changes"
    echo "❌ Please remove or encrypt the password before committing"
    exit 1
fi

# Check for private keys
if git diff --cached | grep "-----BEGIN.*PRIVATE KEY-----" >/dev/null; then
    echo "❌ Private key found in staged changes"
    echo "❌ Please remove or encrypt the private key before committing"
    exit 1
fi

# Check for certificates
if git diff --cached | grep "-----BEGIN.*CERTIFICATE-----" >/dev/null; then
    echo "❌ Certificate found in staged changes"
    echo "❌ Please remove or encrypt the certificate before committing"
    exit 1
fi

# Check for database credentials
if git diff --cached | grep -i "mysql://.*@" >/dev/null; then
    echo "❌ Database credentials found in staged changes"
    echo "❌ Please remove or encrypt the credentials before committing"
    exit 1
fi

# Check for AWS credentials
if git diff --cached | grep -i "aws_access_key_id\|aws_secret_access_key" >/dev/null; then
    echo "❌ AWS credentials found in staged changes"
    echo "❌ Please remove or encrypt the credentials before committing"
    exit 1
fi

# Check for GitHub tokens
if git diff --cached | grep -i "ghp_[a-zA-Z0-9]{36}" >/dev/null; then
    echo "❌ GitHub token found in staged changes"
    echo "❌ Please remove or encrypt the token before committing"
    exit 1
fi

# Run quick security scan on staged files
echo "🔍 Running quick security scan on staged files..."

# Get staged Python files
STAGED_PYTHON=$(git diff --cached --name-only | grep "\.py$" || true)
if [ -n "$STAGED_PYTHON" ]; then
    echo "Scanning staged Python files for security issues..."
    for file in $STAGED_PYTHON; do
        # Check for dangerous imports
        if git show ":$file" | grep -E "(eval|exec|__import__|open|globals|locals)" >/dev/null; then
            echo "❌ Dangerous function found in staged file: $file"
            echo "❌ Please remove or modify the dangerous code before committing"
            exit 1
        fi
    done
fi

# Get staged JavaScript files
STAGED_JS=$(git diff --cached --name-only | grep -E "\.(js|jsx|ts|tsx)$" || true)
if [ -n "$STAGED_JS" ]; then
    echo "Scanning staged JavaScript files for security issues..."
    for file in $STAGED_JS; do
        # Check for eval
        if git show ":$file" | grep -E "eval\(" >/dev/null; then
            echo "❌ eval() found in staged file: $file"
            echo "❌ Please remove or modify the dangerous code before committing"
            exit 1
        fi
    done
fi

echo "✅ Pre-commit security scan passed!"
exit 0
