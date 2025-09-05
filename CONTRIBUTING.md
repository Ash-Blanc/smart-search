# Contributing to Smart Search

First off, thanks for taking the time to contribute! 🎉

The following is a set of guidelines for contributing to Smart Search. These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

## 📇 Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## 🚀 How Can I Contribute?

### Reporting Bugs

This section guides you through submitting a bug report for Smart Search. Following these guidelines helps maintainers and the community understand your report 📝, reproduce the behavior 💻, and find related reports 🔎.

Before creating bug reports, please check the existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

- Use a clear and descriptive title for the issue
- Describe the exact steps which reproduce the problem
- Provide specific examples to demonstrate the steps
- Describe the behavior you observed after following the steps
- Explain which behavior you expected to see instead and why
- Include screenshots if possible
- Note your environment (OS, Python version, etc.)

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion for Smart Search, including completely new features and minor improvements to existing functionality.

- Use a clear and descriptive title for the issue
- Provide a step-by-step description of the suggested enhancement
- Provide specific examples to demonstrate the steps
- Describe the current behavior and explain which behavior you expected to see instead
- Explain why this enhancement would be useful to most Smart Search users

### Pull Requests

The process described here has several goals:

- Maintain Smart Search's quality
- Fix problems that are important to users
- Engage the community in working toward the best possible Smart Search
- Enable a sustainable system for Smart Search's maintainers to review contributions

Please follow these steps to have your contribution considered by the maintainers:

1. Follow all instructions in the template
2. Follow the [styleguides](#styleguides)
3. After you submit your pull request, verify that all status checks are passing

While the prerequisites above must be satisfied prior to having your pull request reviewed, the reviewer(s) may ask you to complete additional design work, tests, or other changes before your pull request can be ultimately accepted.

## 📝 Styleguides

### Git Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

### Python Styleguide

All Python code must adhere to [PEP 8](https://pep8.org/).

- Use 4 spaces for indentation
- Use descriptive variable names
- Write docstrings for all functions, classes, and modules
- Keep functions and methods small and focused
- Use type hints where appropriate

### Documentation Styleguide

- Use [Markdown](https://daringfireball.net/projects/markdown/) for documentation
- Reference functions and variables in backticks
- Follow the existing documentation style

## 🧪 Testing

- Write tests for new features
- Ensure all tests pass before submitting a pull request
- Run tests with `uv run pytest`

## 🛠️ Development Setup

1. Fork and clone the repository
2. Install dependencies with `uv sync`
3. Create a new branch for your feature or bug fix
4. Make your changes
5. Run tests with `uv run pytest`
6. Commit your changes and push to your fork
7. Submit a pull request

Thank you for contributing to Smart Search! 🙏