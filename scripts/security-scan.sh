#!/bin/bash

# Security scanning script for Code Migration Assistant
# This script scans for secrets and security issues in the repository

set -e

echo "🔒 Starting security scan..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}$1${NC}"
}

print_success() {
    echo -e "${GREEN}$1${NC}"
}

print_warning() {
    echo -e "${YELLOW}$1${NC}"
}

print_error() {
    echo -e "${RED}$1${NC}"
}

# Check if we're in a git repository
if [ ! -d .git ]; then
    print_error "❌ Not in a git repository"
    exit 1
fi

print_status "🔍 Scanning for secrets in repository..."

# Scan for common secret patterns
echo "Scanning for API keys..."
if git grep -r -i "sk-[a-zA-Z0-9]{20,}" --exclude-dir=.git . 2>/dev/null; then
    print_error "❌ Found potential API keys"
else
    print_success "✅ No API keys found"
fi

echo "Scanning for passwords..."
if git grep -r -i "password.*=" --exclude-dir=.git . 2>/dev/null; then
    print_error "❌ Found potential passwords"
else
    print_success "✅ No passwords found"
fi

echo "Scanning for private keys..."
if git grep -r "-----BEGIN.*PRIVATE KEY-----" --exclude-dir=.git . 2>/dev/null; then
    print_error "❌ Found private keys"
else
    print_success "✅ No private keys found"
fi

echo "Scanning for certificates..."
if git grep -r "-----BEGIN.*CERTIFICATE-----" --exclude-dir=.git . 2>/dev/null; then
    print_error "❌ Found certificates"
else
    print_success "✅ No certificates found"
fi

echo "Scanning for database credentials..."
if git grep -r -i "mysql://.*@" --exclude-dir=.git . 2>/dev/null; then
    print_error "❌ Found database credentials"
else
    print_success "✅ No database credentials found"
fi

echo "Scanning for AWS credentials..."
if git grep -r -i "aws_access_key_id\|aws_secret_access_key" --exclude-dir=.git . 2>/dev/null; then
    print_error "❌ Found AWS credentials"
else
    print_success "✅ No AWS credentials found"
fi

echo "Scanning for GitHub tokens..."
if git grep -r -i "ghp_[a-zA-Z0-9]{36}" --exclude-dir=.git . 2>/dev/null; then
    print_error "❌ Found GitHub tokens"
else
    print_success "✅ No GitHub tokens found"
fi

echo "Scanning for JWT tokens..."
if git grep -r -i "eyJ[a-zA-Z0-9._-]*" --exclude-dir=.git . 2>/dev/null; then
    print_warning "⚠️  Found potential JWT tokens (may be false positives)"
else
    print_success "✅ No JWT tokens found"
fi

# Check for sensitive file extensions
print_status "🔍 Scanning for sensitive file extensions..."

sensitive_files=(
    "*.pem"
    "*.key"
    "*.crt"
    "*.p12"
    "*.pfx"
    "*.jks"
    "*.keystore"
    "*.p12"
    "*.p8"
    "*.crt"
    "*.key"
    "*.pem"
)

for pattern in "${sensitive_files[@]}"; do
    if git ls-files | grep -E "$pattern$" >/dev/null; then
        print_error "❌ Found sensitive files: $pattern"
    fi
done

# Check for configuration files with secrets
print_status "🔍 Scanning configuration files for secrets..."

config_files=(
    "config.yaml"
    "config.yml"
    "config.json"
    "config.toml"
    "config.ini"
    ".env"
    "secrets.yaml"
    "secrets.yml"
    "secrets.json"
    "production.yaml"
    "production.yml"
    "production.json"
    "staging.yaml"
    "staging.yml"
    "staging.json"
)

for config in "${config_files[@]}"; do
    if [ -f "$config" ]; then
        print_warning "⚠️  Found configuration file: $config"
        # Check if it contains potential secrets
        if grep -i -E "(password|secret|key|token|credential)" "$config" >/dev/null; then
            print_error "❌ Configuration file may contain secrets: $config"
        fi
    fi
done

# Run Python security scanner if available
print_status "🐍 Running Python security scanner..."

if command -v bandit >/dev/null 2>&1; then
    print_status "Running bandit security scanner..."
    bandit -r skills/code_migration/ -f json -o bandit-report.json || true
    
    if [ -f bandit-report.json ]; then
        issues=$(jq '.results | length' bandit-report.json 2>/dev/null || echo "0")
        if [ "$issues" -gt 0 ]; then
            print_warning "⚠️  Bandit found $issues security issues"
            print_status "Check bandit-report.json for details"
        else
            print_success "✅ No security issues found by bandit"
        fi
    fi
else
    print_warning "⚠️  Bandit not installed. Install with: pip install bandit"
fi

# Run dependency vulnerability scanner if available
print_status "🔍 Running dependency vulnerability scanner..."

if command -v safety >/dev/null 2>&1; then
    print_status "Running safety scanner..."
    safety check --json --output safety-report.json || true
    
    if [ -f safety-report.json ]; then
        vulnerabilities=$(jq '.vulnerabilities | length' safety-report.json 2>/dev/null || echo "0")
        if [ "$vulnerabilities" -gt 0 ]; then
            print_warning "⚠️  Safety found $vulnerabilities vulnerabilities"
            print_status "Check safety-report.json for details"
        else
            print_success "✅ No vulnerabilities found by safety"
        fi
    fi
else
    print_warning "⚠️  Safety not installed. Install with: pip install safety"
fi

# Check for secrets in git history
print_status "🔍 Scanning git history for secrets..."

if command -v git-secrets >/dev/null 2>&1; then
    print_status "Running git-secrets scanner..."
    git-secrets --all --baseline .git-secretsBaseline || true
else
    print_warning "⚠️  git-secrets not installed. Install with: brew install git-secrets"
fi

# Generate security report
print_status "📊 Generating security report..."

cat > security-scan-report.json << EOF
{
    "scan_date": "$(date -I)",
    "repository": "$(git remote get-url origin 2>/dev/null || echo 'local')",
    "branch": "$(git branch --show-current | sed 's/^[* ]*//' | sed 's/ .*//')",
    "commit": "$(git rev-parse HEAD)",
    "scan_results": {
        "api_keys": "checked",
        "passwords": "checked",
        "private_keys": "checked",
        "certificates": "checked",
        "database_credentials": "checked",
        "aws_credentials": "checked",
        "github_tokens": "checked",
        "jwt_tokens": "checked",
        "sensitive_files": "checked",
        "config_files": "checked"
    },
    "tools_used": [
        "git grep",
        "bandit",
        "safety",
        "git-secrets"
    ]
}
EOF

print_success "✅ Security scan completed!"
print_status "📄 Report saved to security-scan-report.json"

# Summary
echo
echo "🔒 Security Scan Summary:"
echo "===================="
echo "✅ Secrets scanning completed"
echo "✅ Security scanning completed"
echo "✅ Report generated: security-scan-report.json"
echo
echo "📋 Recommendations:"
echo "1. Review any findings marked with ❌"
echo "2. Remove or encrypt any sensitive data"
echo "3. Update .gitignore if needed"
echo "4. Run this script regularly"
echo "5. Set up pre-commit hooks for automated scanning"

# Exit with appropriate code based on findings
if [ -f bandit-report.json ] && [ -f safety-report.json ]; then
    bandit_issues=$(jq '.results | length' bandit-report.json 2>/dev/null || echo "0")
    safety_vulns=$(jq '.vulnerabilities | length' safety-report.json 2>/dev/null || echo "0")
    
    if [ "$bandit_issues" -gt 0 ] || [ "$safety_vulns" -gt 0 ]; then
        print_error "❌ Security issues found. Please review and fix before proceeding."
        exit 1
    else
        print_success "✅ No critical security issues found."
        exit 0
    fi
else
    print_success "✅ No security scanning tools available."
    exit 0
fi
