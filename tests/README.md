# Test Suite for MARP-Guide-AI

This directory contains all tests for the MARP-Guide-AI system.

## Test Structure

```
tests/
├── test_common.py        # Tests for common modules (events, config, mq, health, logging)
├── test_ingestion.py     # Tests for ingestion service
├── test_extraction.py    # Tests for extraction service
├── test_indexing.py      # Tests for indexing service
├── test_retrieval.py     # Tests for retrieval service
├── test_chat.py          # Tests for chat service (future)
└── test_integration.py   # Integration tests (require services running)
```

## Running Tests

### Install Testing Dependencies

```bash
pip install -r requirements-test.txt
```

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/test_common.py -v
pytest tests/test_ingestion.py -v
```

### Run with Coverage

```bash
pytest --cov=common --cov=services --cov-report=html
```

This generates an HTML coverage report in `htmlcov/index.html`.

### Run Only Unit Tests (Fast)

```bash
pytest -m unit
```

### Run Only Integration Tests

```bash
# Requires RabbitMQ and Qdrant running
docker compose up -d rabbitmq qdrant
pytest -m integration
```

## Test Types

### Unit Tests
- Fast, isolated tests
- Mock external dependencies
- Test individual functions and classes
- Files: `test_common.py`, `test_ingestion.py`, `test_extraction.py`, `test_indexing.py`, `test_retrieval.py`

### Integration Tests
- Test services working together
- Require actual infrastructure (RabbitMQ, Qdrant)
- Slower but more comprehensive
- File: `test_integration.py`

## What Each Test File Covers

### test_common.py
- Event creation functions (DocumentDiscovered, DocumentExtracted, etc.)
- Event schema validation
- Routing key constants
- Configuration loading
- Helper functions (UUID generation, timestamps)

### test_ingestion.py
- PDF scraping from MARP website
- Document ID extraction from URLs
- PDF downloading logic
- Event saving to disk (event sourcing)
- Error handling during ingestion

### test_extraction.py
- PDF text extraction with pdfplumber
- Metadata extraction (title, author, year)
- Handling empty pages
- Year extraction from PDF dates
- Event publishing

### test_indexing.py
- Token-based document chunking
- Chunk overlap verification
- Embedding generation
- Qdrant storage operations
- Event handling

### test_retrieval.py
- FastAPI endpoint testing (/health, /search)
- Query embedding generation
- Search result formatting
- Deduplication logic
- Text truncation for long results
- Input validation

### test_integration.py
- RabbitMQ connectivity
- Qdrant connectivity
- Retrieval service health checks
- End-to-end search functionality
- Queue existence verification

## CI/CD Integration

Tests run automatically on GitHub Actions:
- On every push to main, develop, or feature branches
- On every pull request
- Multiple jobs run in parallel for speed
- Docker images are built and tested

See [.github/workflows/ci.yml](../.github/workflows/ci.yml) for CI configuration.

## Writing New Tests

### Test Naming Convention
- Files: `test_<module>.py`
- Classes: `Test<Feature>`
- Functions: `test_<what_it_tests>`

### Example Test Structure

```python
import pytest
from unittest.mock import Mock, patch

class TestMyFeature:
    """Test my feature functionality."""

    def test_success_case(self):
        """Test that feature works correctly."""
        # Arrange
        input_data = "test"

        # Act
        result = my_function(input_data)

        # Assert
        assert result == "expected"

    def test_error_handling(self):
        """Test that errors are handled properly."""
        with pytest.raises(ValueError):
            my_function(invalid_input)
```

### Mocking External Dependencies

```python
@patch('module.external_dependency')
def test_with_mock(self, mock_dependency):
    """Test using mocked dependency."""
    mock_dependency.return_value = "mocked result"

    result = function_that_uses_dependency()

    assert result == "expected"
    mock_dependency.assert_called_once()
```

## Coverage Goals

- **Common modules**: 90%+ coverage
- **Service logic**: 80%+ coverage
- **Worker entry points**: 70%+ coverage (harder to test due to blocking nature)

## Troubleshooting

### Tests fail with "ModuleNotFoundError"
Make sure you're running from the project root and paths are correct:
```bash
cd MARP-Guide-AI
pytest
```

### Integration tests skip with "service not running"
This is expected in CI. To run locally:
```bash
docker compose up -d rabbitmq qdrant
pytest tests/test_integration.py
```

### Import errors in tests
Check that `sys.path.insert(0, str(project_root))` is at the top of the test file.

## Future Improvements

- [ ] Add performance benchmarks
- [ ] Add stress tests for high load scenarios
- [ ] Add security tests
- [ ] Increase coverage to 90%+
- [ ] Add mutation testing
- [ ] Add contract tests between services
