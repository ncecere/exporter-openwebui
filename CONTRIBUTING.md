# Contributing to OpenWebUI Prometheus Exporter

First off, thanks for taking the time to contribute! 🎉

## Code of Conduct

This project and everyone participating in it is governed by the "Good Luck With That" philosophy. Be excellent to each other, and remember that with great power comes great responsibility.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* Use a clear and descriptive title
* Describe the exact steps which reproduce the problem
* Provide specific examples to demonstrate the steps
* Describe the behavior you observed after following the steps
* Explain which behavior you expected to see instead and why
* Include logs if relevant

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* A clear and descriptive title
* A detailed description of the proposed functionality
* Any possible drawbacks
* If relevant, include mock-ups of any UI/UX aspects

### Pull Requests

* Fill in the required template
* Follow the Python style guide (PEP 8)
* Include comments in your code where necessary
* Update documentation as needed
* Add tests if applicable
* Update CHANGELOG.md with your changes

## Development Process

1. Fork the repo
2. Create a new branch from `main`
3. Make your changes
4. Run tests if available
5. Push to your fork
6. Submit a pull request

### Setting Up Development Environment

```bash
# Clone your fork
git clone https://github.com/ncecere/exporter-openwebui.git
cd exporter-openwebui

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt
```

### Code Style

* Follow PEP 8
* Use meaningful variable names
* Keep functions focused and small
* Comment complex logic
* Use type hints where possible

### Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line

Example:
```
Add user activity metrics collector

- Add new metrics for tracking user session duration
- Include labels for user roles
- Update documentation with new metrics
- Add tests for new collector

Fixes #123
```

### Documentation

* Update README.md if adding new features
* Update ENV-VARS.md if adding new configuration options
* Update POSTGRES_SETUP.md if changing database requirements
* Keep CHANGELOG.md up to date

### Testing

* Add tests for new functionality if applicable
* Ensure existing tests pass
* Test your changes with a real PostgreSQL database

## Project Structure

```
exporter-openwebui/
├── collectors/           # Metric collectors
├── db/                  # Database connection handling
├── utils/              # Utility functions
├── main.py            # Main application
└── config.py          # Configuration
```

### Adding New Metrics

1. Identify the appropriate collector or create a new one
2. Follow the existing pattern for metric creation
3. Use clear metric names following Prometheus conventions
4. Add appropriate labels
5. Document new metrics in README.md

## Questions?

Feel free to open an issue for clarification on any of these points.

Remember: GOOD LUCK WITH THAT! 🚀
