# Contributing to Gemini File Search API

Thank you for considering contributing to this project!

## Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/yourusername/gemini-file-search.git
   cd gemini-file-search
   ```

3. Set up the development environment:
   ```bash
   make setup
   make install
   ```

4. Create a branch for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Code Standards

### Python Style

- Follow PEP 8
- Use type hints for all functions
- Write docstrings for all public functions and classes
- Maximum line length: 100 characters

### Tools

We use the following tools to maintain code quality:

- **black**: Code formatter
- **ruff**: Fast Python linter
- **mypy**: Static type checker
- **pytest**: Testing framework

Run all checks before committing:

```bash
make format
make lint
make type-check
make test
```

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Adding or updating tests
- `refactor:` Code refactoring
- `chore:` Maintenance tasks

Example:
```
feat: add support for custom metadata filtering
fix: handle timeout errors in upload endpoint
docs: update API endpoint documentation
```

## Testing

### Writing Tests

- Write unit tests for all new functions
- Add integration tests for API endpoints
- Update E2E tests if adding new features

### Running Tests

```bash
# All tests
make test

# Unit tests only
make test-unit

# E2E tests (requires API key)
GOOGLE_API_KEY=your_key make test-e2e

# With coverage
make test-cov
```

## Pull Request Process

1. Ensure all tests pass
2. Update documentation if needed
3. Add entries to CHANGELOG.md (if applicable)
4. Submit a pull request with a clear description

### PR Checklist

- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] PR description explains the changes

## Questions?

Feel free to open an issue for:
- Bug reports
- Feature requests
- Questions about the codebase

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
