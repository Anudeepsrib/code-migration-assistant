# User Guide

## Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Basic Usage](#basic-usage)
4. [Migration Types](#migration-types)
5. [Advanced Features](#advanced-features)
6. [Configuration](#configuration)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Git (for rollback functionality)
- 8GB+ RAM (for large codebases)

### Installation

```bash
# Clone the repository
git clone https://github.com/anudeepsrib/code-migration-assistant.git
cd code-migration-assistant

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-security.txt

# Verify installation
python -m skills.code_migration --version
```

### First Migration

```bash
# Analyze your project
migrate analyze ./my-project --type react-hooks --confidence

# Create visual plan
migrate plan ./my-project --type react-hooks --output plan.html

# Execute migration with safety
migrate run ./my-project --type react-hooks --auto-rollback
```

## Installation

### System Requirements

| Component | Minimum | Recommended |
|------------|---------|-------------|
| Python | 3.8 | 3.11 |
| RAM | 4GB | 8GB+ |
| Storage | 1GB | 5GB+ |
| OS | Linux/macOS/Windows | Linux/macOS |

### Dependencies

#### Core Dependencies
```bash
pip install click rich pyyaml networkx
```

#### Security Dependencies
```bash
pip install bandit safety cryptography audit-log
```

#### Optional Dependencies
```bash
# For enhanced visualization
pip install matplotlib seaborn

# For advanced analysis
pip install psutil memory-profiler

# For development
pip install pytest pytest-cov black isort mypy
```

### Docker Installation

```bash
# Pull the image
docker pull code-migration-assistant:latest

# Run with mounted volume
docker run -v /path/to/project:/project code-migration-assistant \
  migrate analyze /project --type react-hooks
```

### Development Installation

```bash
# Clone repository
git clone https://github.com/anudeepsrib/code-migration-assistant.git
cd code-migration-assistant

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest skills/code-migration/tests/

# Run security checks
bandit -r skills/code_migration/
safety check
```

## Basic Usage

### Command Line Interface

The Code Migration Assistant provides a comprehensive CLI for all operations.

#### Basic Commands

```bash
# Show help
migrate --help

# Show version
migrate --version

# List available migration types
migrate list-types
```

#### Analysis Commands

```bash
# Basic analysis
migrate analyze ./project --type react-hooks

# Detailed confidence analysis
migrate analyze ./project --type react-hooks --confidence --detailed

# Risk assessment
migrate analyze ./project --type react-hooks --risk-analysis

# Generate HTML report
migrate analyze ./project --type react-hooks --report-html --output analysis.html
```

#### Planning Commands

```bash
# Generate dependency graph
migrate visualize ./project --output graph.html

# Create migration plan
migrate plan ./project --type react-hooks --output plan.html

# Timeline planning
migrate plan ./project --type react-hooks --timeline --output timeline.html

# Interactive planning
migrate plan ./project --type react-hooks --interactive
```

#### Execution Commands

```bash
# Dry run (preview changes)
migrate run ./project --type react-hooks --dry-run

# Execute migration
migrate run ./project --type react-hooks

# Execute with automatic rollback on error
migrate run ./project --type react-hooks --auto-rollback

# Execute specific files
migrate run ./src/components --type react-hooks --files Button.jsx,UserProfile.jsx
```

#### Rollback Commands

```bash
# Create checkpoint
migrate checkpoint create "Before migration"

# List checkpoints
migrate checkpoint list

# Rollback to checkpoint
migrate rollback --to 20250208_143022

# Partial rollback
migrate rollback --to 20250208_143022 --files src/components/Button.jsx

# Rollback preview
migrate rollback --to 20250208_143022 --dry-run
```

#### Compliance Commands

```bash
# Scan for PII
migrate compliance scan ./project --pii

# Scan for secrets
migrate compliance scan ./project --secrets

# Generate compliance report
migrate compliance report --soc2 --gdpr --hipaa --output compliance/

# Data anonymization
migrate compliance anonymize ./project --output anonymized/
```

### Python API

You can also use the migration assistant programmatically:

```python
from skills.code_migration.core.confidence import MigrationConfidenceAnalyzer
from skills.code_migration.core.visualizer import VisualMigrationPlanner
from skills.code_migration.core.rollback import TimeMachineRollback

# Initialize components
analyzer = MigrationConfidenceAnalyzer("./my-project")
planner = VisualMigrationPlanner("./my-project")
rollback = TimeMachineRollback("./my-project")

# Analyze migration confidence
confidence = analyzer.calculate_confidence("react-hooks", team_experience=70)
print(f"Confidence Score: {confidence.overall_score}/100")
print(f"Risk Level: {confidence.risk_level}")

# Create visual plan
planner.build_dependency_graph()
waves = planner.calculate_migration_waves()
planner.generate_d3_visualization("migration-graph.html")

# Create checkpoint before migration
checkpoint_id = rollback.create_checkpoint("Pre-migration backup")

# Execute migration (your custom logic here)
# ...

# Rollback if needed
if migration_failed:
    rollback.rollback(checkpoint_id)
```

## Migration Types

### React Hooks Migration

**Source**: React Class Components  
**Target**: Functional Components with Hooks  
**Confidence**: 85-95%

```bash
migrate analyze ./react-project --type react-hooks
migrate run ./react-project --type react-hooks
```

**Features**:
- Automatic conversion of class components to functional components
- Lifecycle method to hook conversion
- State management migration
- Context API integration
- Testing updates

**Example Transformation**:
```jsx
// Before
class UserProfile extends Component {
    constructor(props) {
        super(props);
        this.state = { user: null, loading: true };
        this.fetchUser = this.fetchUser.bind(this);
    }
    
    componentDidMount() {
        this.fetchUser();
    }
    
    async fetchUser() {
        const response = await fetch(`/api/users/${this.props.id}`);
        this.setState({ user: await response.json(), loading: false });
    }
    
    render() {
        const { user, loading } = this.state;
        if (loading) return <div>Loading...</div>;
        return <div>{user.name}</div>;
    }
}

// After
const UserProfile = ({ id }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    
    useEffect(() => {
        const fetchUser = async () => {
            const response = await fetch(`/api/users/${id}`);
            setUser(await response.json());
            setLoading(false);
        };
        fetchUser();
    }, [id]);
    
    if (loading) return <div>Loading...</div>;
    return <div>{user.name}</div>;
};
```

### Vue 3 Migration

**Source**: Vue 2 Options API  
**Target**: Vue 3 Composition API  
**Confidence**: 80-90%

```bash
migrate analyze ./vue-project --type vue3
migrate run ./vue-project --type vue3
```

**Features**:
- Options API to Composition API conversion
- Reactivity system migration
- Lifecycle hooks update
- TypeScript support
- Plugin system updates

### Python 3 Migration

**Source**: Python 2.7  
**Target**: Python 3.x  
**Confidence**: 90-98%

```bash
migrate analyze ./python-project --type python3
migrate run ./python-project --type python3
```

**Features**:
- Print statement conversion
- Integer division handling
- String encoding updates
- Exception syntax changes
- Library imports update

### TypeScript Migration

**Source**: JavaScript  
**Target**: TypeScript  
**Confidence**: 70-85%

```bash
migrate analyze ./js-project --type typescript
migrate run ./js-project --type typescript
```

**Features**:
- Type inference and annotation
- Interface generation
- Config file creation
- JSDoc to TypeScript conversion

## Advanced Features

### Migration Confidence Analysis

Get detailed risk assessment and confidence scoring:

```bash
migrate analyze ./project --type react-hooks --confidence --detailed
```

**Output Example**:
```
🔍 Analyzing Migration Confidence...

Overall Confidence: 87/100 (LOW RISK)
Migration Complexity: MODERATE

Risk Factors:
├─ Test Coverage: 92/100 ✅
├─ Code Complexity: 78/100 ✅
├─ Dependencies: 85/100 ✅
├─ Code Quality: 90/100 ✅
├─ Breaking Changes: 75/100 ⚠️
└─ Team Experience: 80/100 ✅

📊 Estimates:
├─ Time: 24.5 hours
├─ Cost: $2,450 (at $100/hr)
└─ Risk Level: LOW

✅ RECOMMENDATIONS:
1. Create staging environment for testing
2. Plan incremental rollout (not big-bang)
3. Set up monitoring and alerting
4. Add more tests for complex components
```

### Visual Migration Planning

Generate interactive dependency graphs and migration timelines:

```bash
# Interactive dependency graph
migrate visualize ./project --output graph.html

# Migration timeline with Gantt chart
migrate plan ./project --type react-hooks --timeline --output timeline.html
```

**Features**:
- Interactive D3.js dependency visualization
- Zoom, pan, and drag capabilities
- Migration wave calculation
- File-level dependency analysis
- Timeline scheduling with work calendars

### Time Machine Rollback

Advanced rollback with surgical precision:

```bash
# Create checkpoint
migrate checkpoint create "Before major changes"

# List all checkpoints
migrate checkpoint list

# Full rollback
migrate rollback --to 20250208_143022

# Partial rollback (specific files)
migrate rollback --to 20250208_143022 --files src/components/Button.jsx

# Rollback preview
migrate rollback --to 20250208_143022 --dry-run
```

**Features**:
- Git-based checkpoints with integrity verification
- Surgical file-level rollback
- Conflict resolution
- Incremental checkpoints
- Automatic backup creation

### Compliance Scanning

Enterprise compliance with GDPR, HIPAA, SOC2:

```bash
# Scan for PII and secrets
migrate compliance scan ./project --pii --secrets

# Generate compliance reports
migrate compliance report --soc2 --gdpr --hipaa --output compliance/

# Data anonymization
migrate compliance anonymize ./project --output anonymized/
```

**Features**:
- PII detection (email, phone, SSN, credit cards)
- PHI detection (medical records, patient data)
- Secrets detection (API keys, passwords)
- GDPR/HIPAA/SOC2 compliance reporting
- Data masking and anonymization

## Configuration

### Configuration Files

#### Security Configuration

Create `config/security_policy.yaml`:

```yaml
security:
  input_validation:
    max_file_size: 10485760  # 10MB
    max_lines: 1000
    allowed_extensions: ['.py', '.js', '.jsx', '.ts', '.tsx', '.vue']
  
  path_sanitization:
    allowed_base: "./project"
    max_path_length: 4096
  
  rate_limiting:
    migrations_per_hour: 10
    file_ops_per_minute: 100
```

#### Compliance Configuration

Create `config/compliance_rules.yaml`:

```yaml
compliance:
  gdpr:
    pii_detection: true
    data_retention_days: 90
  
  hipaa:
    phi_detection: true
    audit_logging: true
  
  soc2:
    audit_trail: true
    encryption_required: true
```

#### Migration Configuration

Create `config/migration_rules.yaml`:

```yaml
migrations:
  react-hooks:
    convert_lifecycle: true
    update_tests: true
    preserve_comments: true
  
  vue3:
    update_dependencies: true
    convert_options_api: true
    typescript_support: false
```

### Environment Variables

```bash
# API Configuration
export MIGRATION_API_URL="https://api.code-migration.ai"
export MIGRATION_API_KEY="your-api-key"

# Security Configuration
export MIGRATION_SECURITY_LEVEL="high"
export MIGRATION_AUDIT_LOGGING="true"

# Performance Configuration
export MIGRATION_MAX_WORKERS="4"
export MIGRATION_TIMEOUT="300"
```

### Custom Rules

Create custom migration rules:

```python
# custom_rules.py
from skills.code_migration.core.rules import BaseRule

class CustomReactRule(BaseRule):
    def apply(self, code):
        # Custom transformation logic
        return transformed_code

# Register the rule
migrate register-rule custom_rules.CustomReactRule --type react-hooks
```

## Troubleshooting

### Common Issues

#### Migration Fails with Security Error

**Problem**: Migration blocked by security controls

**Solution**:
```bash
# Check what's being blocked
migrate analyze ./file.jsx --security-check

# Adjust security settings if needed
migrate config security --level medium
```

#### Memory Issues with Large Projects

**Problem**: Out of memory errors on large codebases

**Solution**:
```bash
# Limit concurrent operations
migrate analyze ./large-project --workers 2 --batch-size 50

# Use incremental analysis
migrate analyze ./large-project --incremental
```

#### Rollback Fails

**Problem**: Cannot rollback to checkpoint

**Solution**:
```bash
# Check checkpoint integrity
migrate checkpoint verify 20250208_143022

# Force rollback if needed
migrate rollback --to 20250208_143022 --force
```

#### Compliance Scan Too Slow

**Problem**: Compliance scanning taking too long

**Solution**:
```bash
# Limit file types
migrate compliance scan ./project --pii --extensions .py,.js,.jsx

# Use parallel processing
migrate compliance scan ./project --pii --parallel
```

### Debug Mode

Enable debug logging:

```bash
# Enable debug mode
export MIGRATION_DEBUG=true
migrate analyze ./project --type react-hooks --verbose

# Check logs
tail -f .migration-logs/security_audit.jsonl
```

### Getting Help

```bash
# Get help for specific command
migrate analyze --help
migrate run --help
migrate rollback --help

# Check system status
migrate status

# Validate configuration
migrate config validate
```

### Performance Issues

#### Optimize for Large Projects

```bash
# Use performance settings
migrate analyze ./large-project --performance-mode

# Limit analysis scope
migrate analyze ./large-project --include src/components --exclude tests

# Use caching
migrate analyze ./large-project --cache
```

#### Memory Optimization

```bash
# Reduce memory usage
migrate analyze ./project --memory-limit 2GB

# Use streaming mode
migrate analyze ./project --streaming
```

## Best Practices

### Before Migration

1. **Create Backup**
   ```bash
   migrate checkpoint create "Pre-migration backup"
   ```

2. **Analyze Thoroughly**
   ```bash
   migrate analyze ./project --type react-hooks --confidence --risk-analysis
   ```

3. **Test on Small Subset**
   ```bash
   migrate run ./src/components --type react-hooks --dry-run --files Button.jsx
   ```

4. **Review Compliance**
   ```bash
   migrate compliance scan ./project --pii --secrets
   ```

### During Migration

1. **Use Incremental Approach**
   ```bash
   migrate run ./project --type react-hooks --waves --auto-rollback
   ```

2. **Monitor Progress**
   ```bash
   migrate status --watch
   ```

3. **Validate Each Wave**
   ```bash
   migrate validate --wave 1
   ```

### After Migration

1. **Run Tests**
   ```bash
   npm test
   pytest
   ```

2. **Verify Functionality**
   ```bash
   migrate verify ./project --type react-hooks
   ```

3. **Update Documentation**
   ```bash
   migrate docs update ./project --type react-hooks
   ```

4. **Clean Up**
   ```bash
   migrate cleanup --keep-checkpoints 5
   ```

### Security Best Practices

1. **Regular Security Scans**
   ```bash
   migrate compliance scan ./project --security
   ```

2. **Monitor Audit Logs**
   ```bash
   migrate audit recent --security-events
   ```

3. **Update Dependencies**
   ```bash
   migrate security update
   ```

### Team Collaboration

1. **Share Migration Plans**
   ```bash
   migrate plan ./project --export plan.json
   ```

2. **Code Review**
   ```bash
   migrate review ./project --type react-hooks
   ```

3. **Document Changes**
   ```bash
   migrate docs generate ./project --type react-hooks
   ```

### Production Deployment

1. **Staging Environment**
   ```bash
   migrate deploy ./project --staging --type react-hooks
   ```

2. **Canary Deployment**
   ```bash
   migrate deploy ./project --canary --type react-hooks --percentage 10
   ```

3. **Monitoring**
   ```bash
   migrate monitor ./project --alerts
   ```

---

## Need Help?

- **Documentation**: https://docs.code-migration.ai
- **Community**: https://slack.code-migration.ai
- **Issues**: https://github.com/anudeepsrib/code-migration-assistant/issues
- **Support**: support@code-migration.ai

For more detailed information about specific features, see the [API Documentation](docs/api/README.md) and [Migration Guides](docs/migrations/README.md).
