This repository contains practice code based on the Udemy course [Django Rest Framework](https://www.udemy.com/course/djangorestframework/).

[![](https://github.com/asarkar/udemy-djangorestframework/workflows/CI/badge.svg)](https://github.com/asarkar/udemy-djangorestframework/actions)

This code deviates from the original course material as necessary to maintain coding conventions and best practices.
Comprehensive unit tests have been added for each section, which the course does not cover.

## Syllabus

1. Start Here
2. Introduction
3. Software Setup
4. REST in Action
5. [Function Based Views and Serializers](section05)
6. [Class Based Views](section06)
7. [Mixins](section07)
8. [Generic Views](section08)
9. [ViewSets](section09)
10. [Nested Serializers](section10)
11. [Pagination](section11)
12. [Filtering](section12)
13. [Security](section13)
14. [Flight Reservation API](section14)
15. [Validations](section15)
16. [Token Auth](section16)
17. Create an Angular Frontend
18. Wrap Up

## Technologies

- **Django** - Web framework
- **Django REST Framework** - REST API toolkit
- **django-filter** - Filtering for DRF views
- **uv** - Python package and project manager
- **ruff, mypy** - Linting

## Development

### Setup

```bash
# Install dependencies
uv sync

# Activate virtual environment (optional, uv run handles this)
source .venv/bin/activate

# Delete cache
find . -type d \( -name '*_cache' -o -name '__pycache__' \) -exec rm -rf {} +
```

### Running a Chapter

```bash
# Run migrations
uv run --directory <chapter> manage.py migrate

# Start development server
uv run --directory <chapter> manage.py runserver
```

**Example:**
```bash
uv run --directory section06 manage.py migrate
uv run --directory section06 manage.py runserver
```

### Running Tests

```bash
# Run tests for a specific chapter
uv run --directory <chapter> manage.py test

# Or use the CI script
./.github/run.sh <chapter>
```

**Example:**
```bash
uv run --directory section06 manage.py test
./.github/run.sh section06
```
