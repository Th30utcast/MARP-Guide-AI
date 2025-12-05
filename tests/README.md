# Test Suite for MARP-Guide-AI

This directory contains all tests for the MARP-Guide-AI system, following best practices from the Week 7-8 lecture series.

## Table of Contents
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Test Types](#test-types)
- [What Each Test File Covers](#what-each-test-file-covers)
- [CI/CD Integration](#cicd-integration)
- [Writing New Tests](#writing-new-tests)
- [Adding Tests for New Features](#adding-tests-for-new-features)
- [Coverage Goals](#coverage-goals)
- [Troubleshooting](#troubleshooting)

---

## Test Structure

```
tests/
├── test_common.py        # Tests for common modules (events, config, mq, health, logging)
├── test_ingestion.py     # Tests for ingestion service
├── test_extraction.py    # Tests for extraction service
├── test_indexing.py      # Tests for indexing service
├── test_retrieval.py     # Tests for retrieval service
├── test_chat.py          # Tests for chat service
├── test_integration.py   # Integration tests (require services running)
└── README.md             # This file
```

---

## Running Tests

### Install Testing Dependencies

```bash
# From project root
pip install -r requirements-test.txt
```

The `requirements-test.txt` includes:
- `pytest` - Testing framework
- `pytest-cov` - Coverage plugin
- `pytest-mock` - Mocking utilities
- `httpx` - HTTP client for testing FastAPI

### Run All Tests

```bash
# Run all tests with verbose output
pytest

# Run with coverage (recommended)
pytest --cov=common --cov=services --cov-report=html --cov-report=term-missing

# View coverage report
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
```

### Run Specific Test File

```bash
pytest tests/test_common.py -v
pytest tests/test_ingestion.py -v
pytest tests/test_retrieval.py -v
```

### Run Specific Test Function

```bash
pytest tests/test_retrieval.py::test_search_endpoint_success -v
```

### Run Tests by Marker

Tests are marked with pytest markers for easy filtering:

```bash
# Run only unit tests (fast, no external dependencies)
pytest -m unit

# Run only integration tests (requires services)
pytest -m integration

# Run only slow tests
pytest -m slow
```

### Run with Coverage

```bash
# Generate HTML coverage report
pytest --cov=common --cov=services --cov-report=html

# Generate terminal coverage report
pytest --cov=common --cov=services --cov-report=term-missing

# Generate XML coverage report (for CI)
pytest --cov=common --cov=services --cov-report=xml
```

Coverage reports are saved in:
- HTML: `htmlcov/index.html`
- XML: `coverage.xml`

### Watch Mode (Run Tests on File Change)

Install pytest-watch:
```bash
pip install pytest-watch
```

Run in watch mode:
```bash
ptw  # Watches for file changes and reruns tests
```

---

## Test Types

### Unit Tests
**Purpose**: Test individual functions and classes in isolation

**Characteristics**:
- Fast (milliseconds per test)
- Mock external dependencies (databases, APIs, message queues)
- No network calls
- No file I/O (mocked)

**Files**: `test_common.py`, `test_ingestion.py`, `test_extraction.py`, `test_indexing.py`, `test_retrieval.py`, `test_chat.py`

**Example**:
```python
@patch('qdrant_client.QdrantClient')
def test_search_endpoint(mock_qdrant):
    """Unit test with mocked Qdrant client."""
    mock_qdrant.search.return_value = [mock_result]
    # Test retrieval service without real database
```

### Integration Tests
**Purpose**: Test services working together with real infrastructure

**Characteristics**:
- Slower (seconds per test)
- Use real RabbitMQ and Qdrant
- Test actual service communication
- Test event flows

**File**: `test_integration.py`

**Running Integration Tests**:
```bash
# Start required services
docker compose up -d rabbitmq qdrant

# Run integration tests
pytest tests/test_integration.py -v

# Stop services
docker compose down
```

---

## What Each Test File Covers

### test_common.py
**Module Tested**: `common/`

**Coverage**:
- Event creation functions (`create_document_discovered`, `create_document_extracted`, etc.)
- Event schema validation (Pydantic models)
- Routing key constants (`ROUTING_KEY_DISCOVERED`, etc.)
- Configuration loading and validation
- Helper functions (UUID generation, timestamps)
- RabbitMQ broker connection handling
- Health check utilities

**Key Tests**:
- `test_create_document_discovered_event` - Event structure validation
- `test_routing_keys` - Correct routing key generation
- `test_event_serialization` - JSON serialization of events

### test_ingestion.py
**Service Tested**: `services/ingestion/`

**Coverage**:
- PDF scraping from Lancaster MARP website
- Document ID extraction from URLs
- PDF downloading logic
- Event saving to disk (event sourcing)
- Error handling during ingestion
- HTTP request handling with proper headers

**Key Tests**:
- `test_scrape_marp_pdfs` - Web scraping functionality
- `test_download_pdf` - PDF download and storage
- `test_save_event` - Event persistence to filesystem
- `test_error_handling` - Graceful error handling

### test_extraction.py
**Service Tested**: `services/extraction/`

**Coverage**:
- PDF text extraction with pdfplumber
- Metadata extraction (title, author, creation date)
- Handling empty pages and malformed PDFs
- Year extraction from PDF dates
- Event publishing to RabbitMQ
- Page-by-page processing

**Key Tests**:
- `test_extract_text_from_pdf` - Text extraction accuracy
- `test_extract_metadata` - PDF metadata parsing
- `test_handle_empty_pages` - Edge case handling
- `test_year_extraction` - Date parsing logic

### test_indexing.py
**Service Tested**: `services/indexing/`

**Coverage**:
- Token-based document chunking
- Chunk overlap verification
- Embedding generation with sentence-transformers
- Qdrant storage operations (upsert, collection management)
- Event handling and processing
- Semantic chunking logic

**Key Tests**:
- `test_chunk_document` - Text chunking algorithm
- `test_chunk_overlap` - Overlap between chunks
- `test_generate_embeddings` - Embedding model integration
- `test_store_in_qdrant` - Vector database operations

### test_retrieval.py
**Service Tested**: `services/retrieval/`

**Coverage**:
- FastAPI endpoint testing (`/health`, `/search`)
- Query embedding generation
- Search result formatting and metadata
- Deduplication logic (same document, different chunks)
- Text truncation for long results (1700 char limit)
- Input validation (top_k limits, query length)

**Key Tests**:
- `test_search_endpoint_success` - Successful search flow
- `test_search_endpoint_deduplication` - Duplicate removal
- `test_search_endpoint_long_text_truncation` - Text truncation
- `test_search_endpoint_validation` - Input validation

**Note**: Tests use `query_points` API (updated for Qdrant 1.7.0+)

### test_chat.py
**Service Tested**: `services/chat/`

**Coverage**:
- FastAPI endpoint testing (`/health`, `/chat`)
- Integration with retrieval service
- LLM prompt generation with RAG context
- Citation extraction and formatting
- OpenRouter API integration
- Error handling (no results, API failures)

**Key Tests**:
- `test_chat_endpoint_success` - Full RAG pipeline
- `test_chat_with_citations` - Citation formatting
- `test_chat_error_handling` - API error scenarios
- `test_prompt_template` - Prompt generation logic

### test_integration.py
**Integration Tests**: Multi-service flows

**Coverage**:
- RabbitMQ connectivity and message flow
- Qdrant connectivity and search operations
- Retrieval service health checks
- End-to-end search functionality
- Queue existence verification
- Event-driven pipeline testing

**Key Tests**:
- `test_rabbitmq_connection` - Message broker availability
- `test_qdrant_connection` - Vector database availability
- `test_retrieval_search_integration` - Full search flow
- `test_event_flow` - DocumentDiscovered → DocumentExtracted flow

**Requirements**:
```bash
docker compose up -d rabbitmq qdrant
```

---

## CI/CD Integration

Tests run automatically on GitHub Actions in `.github/workflows/ci.yml`:

### CI Pipeline Stages

1. **Lint** (fast, parallel)
   - Code formatting (black, isort)
   - Linting (flake8)
   - Syntax error detection

2. **Unit Tests** (parallel, depends on lint)
   - All service tests run in parallel
   - Coverage reports generated
   - Artifacts uploaded

3. **Integration Tests** (sequential, depends on unit tests)
   - Docker Compose starts RabbitMQ and Qdrant
   - Proper health checks with timeouts
   - Service logs on failure

4. **Docker Build** (parallel with integration)
   - All service images built
   - Image functionality tested

5. **Coverage Report** (final summary)
   - Aggregates all coverage reports
   - Displays summary in GitHub Actions

### Trigger Conditions

- Push to `main`, `develop`, `feature/**`, `hotfix/**` branches
- Pull requests to `main` and `develop`

### Viewing CI Results

1. Go to GitHub repository
2. Click **Actions** tab
3. Select latest workflow run
4. View job results and logs
5. Download coverage artifacts

---

## Writing New Tests

### Test Naming Convention

Follow pytest conventions:

- **Files**: `test_<module>.py` (e.g., `test_retrieval.py`)
- **Classes**: `Test<Feature>` (e.g., `TestSearchEndpoint`)
- **Functions**: `test_<what_it_tests>` (e.g., `test_search_returns_results`)

### Test Structure (AAA Pattern)

Use the **Arrange-Act-Assert** pattern:

```python
import pytest
from unittest.mock import Mock, patch

def test_search_endpoint_success():
    """Test that search endpoint returns results correctly."""
    # Arrange - Set up test data and mocks
    query = "What is MARP?"
    expected_results = [...]

    # Act - Execute the function being tested
    response = client.post("/search", json={"query": query, "top_k": 5})

    # Assert - Verify the outcome
    assert response.status_code == 200
    assert len(response.json()["results"]) == 5
```

### Using Pytest Fixtures

Fixtures provide reusable setup code:

```python
import pytest

@pytest.fixture
def mock_qdrant_client():
    """Fixture that provides a mocked Qdrant client."""
    with patch('qdrant_client.QdrantClient') as mock:
        mock.return_value.search.return_value = []
        yield mock

def test_with_fixture(mock_qdrant_client):
    """Test using the fixture."""
    # Fixture is automatically passed
    result = search_function()
    mock_qdrant_client.search.assert_called_once()
```

### Mocking External Dependencies

Always mock external dependencies in unit tests:

```python
from unittest.mock import Mock, patch

@patch('services.retrieval.retrieval_utils.QdrantClient')
@patch('services.retrieval.retrieval_utils.SentenceTransformer')
def test_search_with_mocks(mock_transformer, mock_qdrant):
    """Test with multiple mocked dependencies."""
    # Configure mocks
    mock_transformer.return_value.encode.return_value = [0.1, 0.2, 0.3]
    mock_qdrant.return_value.query_points.return_value = mock_results

    # Test function
    result = search("query")

    # Verify mocks were called correctly
    mock_transformer.encode.assert_called_once_with("query")
    mock_qdrant.query_points.assert_called_once()
```

### Testing FastAPI Endpoints

Use `TestClient` from fastapi.testclient:

```python
from fastapi.testclient import TestClient
from retrieval_service import app

def test_health_endpoint():
    """Test /health endpoint returns 200."""
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

### Marking Tests

Use pytest markers to categorize tests:

```python
import pytest

@pytest.mark.unit
def test_unit_test():
    """Fast unit test."""
    assert True

@pytest.mark.integration
def test_integration_test():
    """Slower integration test."""
    assert True

@pytest.mark.slow
def test_slow_test():
    """Very slow test."""
    assert True
```

Markers are defined in `pyproject.toml`:
```toml
[tool.pytest.ini_options]
markers = [
    "unit: Unit tests (fast, no external dependencies)",
    "integration: Integration tests (require services running)",
    "slow: Slow running tests",
]
```

---

## Adding Tests for New Features

### Step-by-Step Guide

1. **Create test file** (if new service):
   ```bash
   touch tests/test_new_service.py
   ```

2. **Add imports**:
   ```python
   import pytest
   from unittest.mock import Mock, patch
   from pathlib import Path
   import sys

   # Add project root to path
   project_root = Path(__file__).parent.parent
   sys.path.insert(0, str(project_root))

   from services.new_service.service import function_to_test
   ```

3. **Write test class**:
   ```python
   class TestNewFeature:
       """Test new feature functionality."""

       def test_basic_functionality(self):
           """Test that feature works."""
           result = function_to_test("input")
           assert result == "expected"
   ```

4. **Run tests**:
   ```bash
   pytest tests/test_new_service.py -v
   ```

5. **Check coverage**:
   ```bash
   pytest tests/test_new_service.py --cov=services/new_service --cov-report=html
   ```

6. **Update CI** (if needed):
   - Add new test job to `.github/workflows/ci.yml`
   - Follow existing pattern for other services

### Example: Adding Test for New Retrieval Function

```python
# tests/test_retrieval.py

@patch('services.retrieval.retrieval_utils.QdrantClient')
def test_new_search_feature(mock_qdrant):
    """Test new search feature with filtering."""
    # Arrange
    mock_result = Mock()
    mock_result.points = [create_mock_point("test")]
    mock_qdrant.return_value.query_points.return_value = mock_result

    # Act
    from retrieval_service import app
    client = TestClient(app)
    response = client.post("/search", json={
        "query": "test query",
        "top_k": 5,
        "filter": {"year": 2024}  # New filter parameter
    })

    # Assert
    assert response.status_code == 200
    assert "results" in response.json()

    # Verify filter was passed to Qdrant
    call_args = mock_qdrant.query_points.call_args
    assert "filter" in call_args[1]
```

---

## Coverage Goals

Following professor's recommendations (Week 7-8):

| Module Type | Target Coverage | Notes |
|-------------|----------------|-------|
| **Common modules** | 90%+ | Core utilities, well-defined |
| **Service logic** | 80%+ | Business logic, APIs |
| **Worker entry points** | 70%+ | Harder to test (blocking, async) |
| **Integration tests** | N/A | Focus on critical paths |

### Checking Coverage

```bash
# Generate coverage report
pytest --cov=common --cov=services --cov-report=term-missing

# View detailed HTML report
pytest --cov=common --cov=services --cov-report=html
open htmlcov/index.html
```

### Improving Coverage

1. Identify uncovered lines in HTML report
2. Add tests for edge cases
3. Mock hard-to-reach code paths
4. Add integration tests for complex flows

---

## Troubleshooting

### Tests fail with "ModuleNotFoundError"

**Problem**: Python can't find modules to import

**Solution**: Make sure you're running from project root:
```bash
cd MARP-Guide-AI  # Project root
pytest
```

If still failing, check `sys.path.insert()` at top of test file:
```python
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
```

### Integration tests skip with "service not running"

**Problem**: RabbitMQ or Qdrant not available

**Solution**: This is expected in CI. To run locally:
```bash
# Start services
docker compose up -d rabbitmq qdrant

# Wait for services to be ready (30 seconds)
sleep 30

# Run integration tests
pytest tests/test_integration.py -v

# Stop services
docker compose down
```

### Import errors in tests

**Problem**: Circular imports or missing dependencies

**Solution**:
1. Check that dependencies are installed: `pip install -r requirements-test.txt`
2. Verify import order (common modules before services)
3. Check for circular dependencies

### Mocks not working as expected

**Problem**: Mocked functions still call real code

**Solution**:
1. Patch the correct location (where it's used, not where it's defined):
   ```python
   # Wrong: @patch('qdrant_client.QdrantClient')
   # Right:
   @patch('services.retrieval.retrieval_utils.QdrantClient')
   ```

2. Verify patch path matches import:
   ```python
   # If service does: from qdrant_client import QdrantClient
   # Patch: 'services.retrieval.retrieval_utils.QdrantClient'
   ```

### Tests pass locally but fail in CI

**Problem**: Environment differences (paths, dependencies, timing)

**Solutions**:
1. Check CI logs in GitHub Actions
2. Verify all dependencies in `requirements-test.txt`
3. Check for hardcoded paths (use `Path(__file__).parent`)
4. Add timing delays for async operations
5. Check environment variables in `.github/workflows/ci.yml`

### Warnings spam in test output

**Problem**: Deprecation warnings from dependencies

**Solution**: Warnings are now enabled by default (good for code quality). To filter specific warnings:
```python
# In test file
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
```

Or configure in `pyproject.toml`:
```toml
[tool.pytest.ini_options]
filterwarnings = [
    "ignore::DeprecationWarning:pydantic.*:",
]
```

---

## Best Practices Summary

✅ **Do**:
- Write tests before fixing bugs (TDD approach)
- Mock external dependencies in unit tests
- Use descriptive test names
- Follow AAA pattern (Arrange-Act-Assert)
- Test edge cases and error conditions
- Keep tests fast (< 1 second for unit tests)
- Run tests locally before pushing
- Check coverage regularly

❌ **Don't**:
- Test implementation details (test behavior, not code)
- Mock everything (integration tests need real services)
- Write flaky tests (inconsistent results)
- Ignore failing tests
- Skip test documentation
- Hardcode file paths or credentials
- Leave print statements in tests

---

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [unittest.mock Guide](https://docs.python.org/3/library/unittest.mock.html)
- Professor's Week 7-8 Lectures on Testing Strategies

---

**Questions?** Ask the team or check the main [README.md](../README.md) for setup instructions.
