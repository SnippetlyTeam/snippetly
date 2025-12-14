# 🪝 Pre-commit Hooks Setup

Automatic code quality checks before every commit.

## Quick Setup

### 1. Install pre-commit

```bash
pip install pre-commit
```

Or with uv (recommended):
```bash
uv tool install pre-commit
```

### 2. Install hooks

```bash
# From project root
pre-commit install

# Install commit-msg hook (for conventional commits)
pre-commit install --hook-type commit-msg
```

### 3. Test

```bash
# Run on all files
pre-commit run --all-files

# Run on staged files (happens automatically on commit)
git add .
git commit -m "test: pre-commit hooks"
```

---

## What Gets Checked

### ✅ All Files
- Trailing whitespace
- End-of-file newline
- Large files (max 1MB)
- Merge conflicts
- Private keys detection
- YAML/JSON/TOML syntax

### 🐍 Backend (Python)
- **Ruff** - Fast linter + formatter
- Imports sorting
- Code style (PEP 8)
- Unused variables
- Security issues

### ⚛️ Frontend (JS/TS)
- **Prettier** - Code formatting
- ESLint (optional, disabled by default)

### 🏗️ Infrastructure
- **Terraform** - Format + validate
- **Dockerfile** - Hadolint linting
- **Shell scripts** - ShellCheck

### 🔒 Security
- **detect-secrets** - Prevent committing secrets
- Private key detection

### 📝 Commits
- **Conventional Commits** format validation

---

## Conventional Commits

Format: `<type>(<scope>): <description>`

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style (formatting)
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `test`: Tests
- `build`: Build system
- `ci`: CI/CD changes
- `chore`: Maintenance

**Examples:**
```bash
git commit -m "feat(auth): add OAuth2 login"
git commit -m "fix(api): resolve CORS issue"
git commit -m "docs: update deployment guide"
```

---

## Skip Hooks (Emergency)

```bash
# Skip all hooks
git commit --no-verify -m "emergency fix"

# Skip specific hook
SKIP=ruff git commit -m "fix: urgent patch"
```

**Warning:** Only use in emergencies!

---

## Customize Hooks

### Disable Specific Checks

Edit `.pre-commit-config.yaml`:

```yaml
# Disable ESLint (already commented)
# - repo: https://github.com/pre-commit/mirrors-eslint

# Disable mypy type checking (already commented)
# - repo: https://github.com/pre-commit/mirrors-mypy
```

### Add Custom Checks

```yaml
repos:
  - repo: local
    hooks:
      - id: pytest-fast
        name: Run fast tests
        entry: pytest tests/unit -v
        language: system
        pass_filenames: false
```

---

## Update Hooks

```bash
# Update to latest versions
pre-commit autoupdate

# Run updated hooks
pre-commit run --all-files
```

---

## Troubleshooting

**Hooks failing:**
```bash
# See what failed
pre-commit run --all-files --verbose

# Clear cache
pre-commit clean
pre-commit gc
```

**Terraform validate fails:**
```bash
# Init terraform first
cd infra/terraform
terraform init
```

**detect-secrets fails:**
```bash
# Create baseline (first time)
detect-secrets scan > .secrets.baseline

# Update baseline
detect-secrets scan --baseline .secrets.baseline
```

---

## CI/CD Integration

Pre-commit runs automatically in GitHub Actions via:

```yaml
# .github/workflows/ci-cd-dev.yml
- name: Ruff lint
  run: uv run ruff check .

- name: Prettier check
  run: npm run format:check
```

---

## Benefits

✅ Catch issues **before** CI/CD
✅ Consistent code style across team
✅ Prevent committing secrets
✅ Faster code reviews
✅ Auto-fix formatting issues

---

## Performance Tips

**Slow hooks:**
- mypy (type checking) - disabled by default
- ESLint - disabled by default
- Terraform validate - cached

**Speed up:**
```bash
# Run only on changed files
git commit  # Auto-runs on staged files only

# Skip slow checks locally (CI still runs them)
SKIP=terraform_validate git commit -m "docs: update README"
```
