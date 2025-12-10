# MARP-Guide-AI

![CI Pipeline](https://github.com/Th30utcast/MARP-Guide-AI/actions/workflows/ci.yml/badge.svg)

A Retrieval-Augmented Generation (RAG) chatbot that answers questions about Lancaster University's Manual of Academic Regulations and Procedures (MARP).

---

## Table of Contents

- [Product Overview](#product-overview)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
  - [Prerequisites](#prerequisites)
  - [Setup](#setup)
  - [Running the System](#running-the-system)
  - [Testing the Chat Service](#testing-the-chat-service)
- [Service Access Details](#service-access-details)
- [Data Storage](#data-storage)
- [Development](#development)
  - [Project Structure](#project-structure)
  - [Code Quality Tools](#code-quality-tools)
- [Testing](#testing)
  - [Running Tests Locally](#running-tests-locally)
  - [CI/CD Pipeline](#cicd-pipeline)
- [Docker Build Optimization](#docker-build-optimization)
- [Troubleshooting](#troubleshooting)
- [Technology Stack](#technology-stack)

---

## Product Overview

**Target Audience**: Students and staff who need quick access to university regulations.

**Value Proposition**: Reliable, quickly accessible information with proper source citations.

**Key Features**:

- **Semantic Search**: Answers derived from MARP PDF documents using vector embeddings
- **Proper Citations**: Results include title, page number, and source link
- **Multi-Model Comparison**: Compare answers from 3 different LLMs side-by-side
- **User Authentication**: Secure registration and session management
- **Usage Analytics**: Track queries, model preferences, and user interactions
- **Interactive Web UI**: React-based interface with Lancaster University branding

---

## Architecture

This system uses a **microservices architecture** with **event-driven communication** via RabbitMQ.

### High-Level Architecture Overview

```mermaid
graph TB
  subgraph Users["User Layer"]
    Student[Students]
    Staff[Staff]
  end

  subgraph Presentation["Presentation Layer"]
    WebUI[Web UI<br/>React + Vite]
    Auth[Authentication Service<br/>FastAPI]
  end

  subgraph Application["Application Layer"]
    Chat[Chat Service<br/>RAG + Multi-Model]
    Retrieval[Retrieval Service<br/>Semantic Search]
    Analytics[Analytics Service<br/>Usage Tracking]
  end

  subgraph DataProcessing["Data Processing Layer"]
    Ingestion[Ingestion Service<br/>PDF Discovery]
    Extraction[Extraction Service<br/>Text Extraction]
    Indexing[Indexing Service<br/>Embeddings]
  end

  subgraph Infrastructure["Infrastructure Layer"]
    RabbitMQ[RabbitMQ<br/>Message Broker]
    Qdrant[(Qdrant<br/>Vector Database)]
    Storage[(File Storage<br/>PDFs + Events)]
    PostgreSQL[(PostgreSQL<br/>User Data)]
    Redis[(Redis<br/>Sessions)]
  end

  subgraph External["External Systems"]
    MARP[Lancaster MARP<br/>Website]
    OpenRouter[OpenRouter API<br/>LLM Provider]
  end

  %% User interactions
  Student --> WebUI
  Staff --> WebUI
  WebUI --> Auth
  WebUI --> Chat
  WebUI --> Analytics

  %% Auth connections
  Auth --> PostgreSQL
  Auth --> Redis

  %% Application layer flows
  Chat --> Retrieval
  Chat --> OpenRouter
  Chat --> Auth
  Chat --> RabbitMQ
  Analytics --> RabbitMQ
  Retrieval --> Qdrant

  %% Data processing pipeline
  MARP -->|Scrape PDFs| Ingestion
  Ingestion -->|DocumentDiscovered| RabbitMQ
  RabbitMQ -->|Event| Extraction
  Extraction -->|DocumentExtracted| RabbitMQ
  RabbitMQ -->|Event| Indexing
  Indexing -->|Store Vectors| Qdrant

  %% Storage connections
  Ingestion --> Storage
  Extraction --> Storage
  Indexing --> Storage

  %% Analytics tracking
  RabbitMQ -.->|Analytics Events| Analytics

  %% Styling
  style DataProcessing fill:#00A310,stroke:#333,stroke-width:2px
  style Infrastructure fill:#A3A300,stroke:#333,stroke-width:2px
  style Presentation fill:#00A310,stroke:#333,stroke-width:2px
  style Application fill:#00A310,stroke:#333,stroke-width:2px
  style External fill:#003BD1,stroke:#333,stroke-width:2px
  style Users fill:#FF6B6B,stroke:#333,stroke-width:2px
```

**Legend:**

- ✅ **Green** - Operational (All services fully implemented)
- **Yellow** - Infrastructure (Always-on services)
- **Blue** - External Systems
- **Red** - End Users

### Components

**Data Processing Pipeline:**
1. **Ingestion Service** - Discovers and downloads MARP PDFs from Lancaster's website
2. **Extraction Service** - Extracts text and metadata from PDFs using pdfplumber
3. **Indexing Service** - Chunks documents semantically and generates vector embeddings

**Application Services:**
4. **Retrieval Service** - REST API for semantic search over indexed documents
5. **Chat Service** - RAG-powered question answering with LLM integration and multi-model comparison
6. **Authentication Service** - User registration, login, and session management
7. **Analytics Service** - Tracks user interactions and provides usage insights
8. **Web UI** - React-based frontend for chat interaction

**Infrastructure:**
9. **Qdrant** - Vector database for semantic search (384-dimensional embeddings)
10. **RabbitMQ** - Message broker for event-driven communication
11. **PostgreSQL** - User data storage (credentials, profiles)
12. **Redis** - Session token storage and caching

### Event Flow Pipeline

**Data Processing:**
```
Ingestion → DocumentDiscovered → Extraction → DocumentExtracted → Indexing → ChunksIndexed
```

**User Query:**
```
User → Auth (validate) → Chat → Retrieval → LLM (OpenRouter) → User
                                    ↓
                              Analytics (tracking)
```

For detailed architecture diagrams and service documentation, see:

- [Microservices & Broker](docs/services/Microservices_Broker.md) - Complete system architecture
- [Ingestion Pipeline](docs/services/Ingestion/Ingestion_pipeline.md) - PDF discovery flow
- [Authentication Pipeline](docs/services/Auth/Auth_pipeline.md) - User auth flows
- [Multi-Model Pipeline](docs/services/MultiModel/MultiModel_pipeline.md) - Comparison flow
- [Web UI Pipeline](docs/services/UI/UI_pipeline.md) - Frontend interaction flows
- [Event Catalogue](docs/events/event-catalogue.md) - All system events

---

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- At least 4GB of RAM available for containers
- OpenRouter API key (free tier available)

### Setup

1. **Get an OpenRouter API Key**:

   - Visit [openrouter.ai](https://openrouter.ai)
   - Sign up for a free account
   - Get your API key from the dashboard

2. **Configure environment variables**:

   Your `.env` file should look like:

   ```bash
   OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx
   ```

   **Note:** If you experience authentication issues, ensure `OPENROUTER_API_KEY` is not exported in your terminal environment (run `unset OPENROUTER_API_KEY` or use a fresh terminal).

### Running the System

1. **Clone the repository**:

   ```bash
   git clone https://github.com/Th30utcast/MARP-Guide-AI.git
   cd MARP-Guide-AI
   ```

2. **Enable Docker BuildKit** (Windows - for faster builds):

   ```powershell
   .\scripts\enable-buildkit.ps1
   ```

3. **Start all services**:

   ```bash
   docker compose up --build
   ```

   This will start:

   - **Infrastructure**: RabbitMQ, Qdrant, PostgreSQL, Redis
   - **Data Pipeline**: Ingestion, Extraction, Indexing services
   - **Application**: Retrieval, Chat, Auth, Analytics services
   - **Frontend**: React Web UI (port 8080)

4. **Monitor logs**:

   ```bash
   # View all services
   docker compose logs -f

   # View specific service
   docker compose logs -f chat
   docker compose logs -f retrieval
   ```

5. **Access the application**:
   - **Web UI**: <http://localhost:8080> (Main interface - **start here!**)
   - Ingestion Service: <http://localhost:8001/health>
   - Retrieval Service: <http://localhost:8002/health>
   - Chat Service: <http://localhost:8003/health>
   - Auth Service: <http://localhost:8004/health>
   - Analytics Service: <http://localhost:8005/health>
   - RabbitMQ Management UI: <http://localhost:15672> (guest/guest)
   - Qdrant Dashboard: <http://localhost:6333/dashboard>

### Using the Application

#### Web UI (Recommended)

The **easiest way** to use the system:

1. **Open the Web UI**: <http://localhost:8080>
2. **Register an account**: Click "Register" and create credentials
3. **Login**: Use your credentials to get a session token
4. **Ask questions**:
   - First query: Get a single LLM answer with citations
   - Second query: Automatic multi-model comparison (3 models side-by-side)
   - Select your preferred answer to help improve the system
5. **View analytics**: Check usage statistics and popular queries

#### API Testing (For Developers)

**Authentication Required**: The Chat API now requires a Bearer token.

**Step 1: Register a user**

```bash
curl -X POST http://localhost:8004/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass123"}'
```

**Step 2: Login and get token**

```bash
curl -X POST http://localhost:8004/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass123"}'
```

Response: `{"token": "your-session-token-here"}`

**Step 3: Chat with token**

```bash
curl -X POST http://localhost:8003/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-session-token-here" \
  -d '{"query": "What is MARP?", "top_k": 5}'
```

**Multi-Model Comparison:**

```bash
curl -X POST http://localhost:8003/chat/compare \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-session-token-here" \
  -d '{"query": "What happens if I am ill during exams?", "top_k": 5}'
```

#### Interactive API Documentation

1. **Chat API**: <http://localhost:8003/docs>
2. **Auth API**: <http://localhost:8004/docs>
3. **Analytics API**: <http://localhost:8005/docs>
4. **Retrieval API**: <http://localhost:8002/docs>

Note: Use the "Authorize" button in Swagger UI to add your Bearer token.

### Stopping the System

```bash
docker compose down
```

To also remove volumes (PDFs and vector data):

```bash
docker compose down -v
```

---

## Service Access Details

### Web UI (Primary Interface)

- **URL**: <http://localhost:8080>
- **Features**:
  - User registration and login
  - RAG-powered chat with citations
  - Multi-model comparison (automatic on 2nd query)
  - Analytics dashboard
  - Lancaster University branding

### Authentication Service

- **URL**: <http://localhost:8004>
- **Interactive Docs**: <http://localhost:8004/docs>
- **Endpoints**:
  - `POST /register` - Create new user account
  - `POST /login` - Get session token (24h expiry)
  - `POST /validate-session` - Verify Bearer token
  - `POST /password-reset` - Reset user password

### Chat Service API

- **URL**: <http://localhost:8003>
- **Interactive Docs**: <http://localhost:8003/docs>
- **Endpoints** (All require `Authorization: Bearer <token>`):
  - `GET /health` - Health check
  - `POST /chat` - Single model RAG with citations
  - `POST /chat/compare` - Multi-model comparison (3 models)
  - `POST /chat/comparison/select` - Record user's model preference

### Analytics Service

- **URL**: <http://localhost:8005>
- **Interactive Docs**: <http://localhost:8005/docs>
- **Endpoints**:
  - `GET /analytics/summary` - Overall usage statistics
  - `GET /analytics/queries/popular` - Most common queries
  - `GET /analytics/models/stats` - Per-model performance metrics
  - `GET /analytics/users/{user_id}/history` - User query history

### Retrieval Service API

- **URL**: <http://localhost:8002>
- **Interactive Docs**: <http://localhost:8002/docs>
- **Endpoints**:
  - `GET /health` - Health check
  - `POST /search` - Semantic search endpoint (no auth required)

### Ingestion Service

- **URL**: <http://localhost:8001>
- **Interactive Docs**: <http://localhost:8001/docs>
- **Endpoints**:
  - `GET /health` - Health check
  - `GET /stats` - Ingestion statistics
  - `POST /ingest` - Manually trigger PDF discovery

### Infrastructure UIs

#### RabbitMQ Management

- **URL**: <http://localhost:15672>
- **Username**: `guest`
- **Password**: `guest`
- **Key queues**: `documents.discovered`, `documents.extracted`, `documents.indexed`, `analytics.*`

#### Qdrant Vector Database

- **HTTP API**: <http://localhost:6333>
- **Dashboard**: <http://localhost:6333/dashboard>
- **Collection**: `marp-documents` (384 dimensions, cosine similarity)
- **Embedding Model**: `all-MiniLM-L6-v2`

#### PostgreSQL Database

- **Host**: `localhost:5432`
- **Database**: `marp_auth`
- **User**: `postgres`
- **Schema**: Users table with bcrypt password hashing

#### Redis Cache

- **Host**: `localhost:6379`
- **Purpose**: Session token storage (24h TTL)

---

## Data Storage

### PDFs Directory

Downloaded PDFs are stored in:

```
pdfs/
  Intro-to-MARP.pdf
  General-Regs.pdf
  Study-Regs.pdf
  ...
```

### Extracted Data

All events and extracted data are stored in:

```
storage/extracted/{documentId}/
  discovered.json    # DocumentDiscovered event
  pages.jsonl        # Extracted page text (one JSON per line)
  extracted.json     # DocumentExtracted event
  chunks.json        # Document chunks for debugging
  indexed.json       # ChunksIndexed event
```

---

## Development

### Project Structure

```
MARP-Guide-AI/
├── .github/
│   └── workflows/
│       └── ci.yml              # CI/CD pipeline configuration
├── services/
│   ├── ingestion/              # PDF discovery and download
│   │   ├── ingestion_service.py
│   │   └── worker.py
│   ├── extraction/             # PDF text extraction
│   │   ├── extraction_service.py
│   │   └── worker.py
│   ├── indexing/               # Chunking and embeddings
│   │   ├── indexing_service.py
│   │   └── worker.py
│   ├── retrieval/              # Semantic search API
│   │   ├── retrieval_service.py
│   │   ├── retrieval_utils.py
│   │   └── worker.py
│   ├── chat/                   # RAG-powered Q&A
│   │   ├── chat_service.py
│   │   ├── retrieval_client.py
│   │   ├── openrouter_client.py
│   │   └── prompt_templates.py
│   ├── auth/                   # User authentication
│   │   ├── auth_service.py
│   │   ├── database.py
│   │   └── models.py
│   ├── analytics/              # Usage tracking
│   │   ├── analytics_service.py
│   │   └── worker.py
│   └── ui/                     # React web interface
│       ├── src/
│       │   ├── components/     # React components
│       │   ├── services/       # API clients
│       │   └── App.jsx         # Main app component
│       ├── package.json
│       └── vite.config.js
├── common/                     # Shared modules
│   ├── events.py               # Event schemas
│   ├── mq.py                   # RabbitMQ utilities
│   ├── config.py               # Configuration
│   ├── health.py               # Health checks
│   └── logging_config.py       # Logging setup
├── tests/                      # All test files
│   ├── test_ingestion.py
│   ├── test_extraction.py
│   ├── test_indexing.py
│   ├── test_retrieval.py
│   ├── test_chat.py
│   ├── test_common.py
│   ├── test_integration.py
│   └── README.md               # Testing documentation
├── scripts/                    # Utility scripts
│   ├── chat.sh                 # Chat CLI (Linux/Mac)
│   ├── chat.bat                # Chat CLI (Windows CMD)
│   ├── chat.ps1                # Chat CLI (Windows PowerShell)
│   └── enable-buildkit.ps1     # Enable Docker BuildKit
├── docs/                       # Documentation
│   ├── services/               # Service documentation
│   ├── events/                 # Event catalogue
│   └── scrum/                  # Sprint planning
├── pdfs/                       # Downloaded MARP PDFs
├── storage/                    # Extracted content storage
├── pyproject.toml              # Python tool configuration
├── requirements.txt            # Python dependencies
├── requirements-test.txt       # Test dependencies
└── docker-compose.yml          # Service orchestration
```

### Code Quality Tools

Configuration is centralized in `pyproject.toml`:

**Format code:**

```bash
black services/ common/ tests/
isort services/ common/ tests/
```

**Lint code:**

```bash
flake8 services/ common/ tests/
```

**Configuration:**

- **black**: Code formatter (line length: 127)
- **isort**: Import sorter (compatible with black)
- **flake8**: Linter for code quality
- **pytest**: Test framework with coverage
- **coverage**: Code coverage tracking

---

## Testing

### Running Tests Locally

**Install test dependencies:**

```bash
pip install -r requirements-test.txt
```

**Run all tests:**

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=common --cov=services --cov-report=html

# Run specific test file
pytest tests/test_retrieval.py -v

# Run specific test function
pytest tests/test_retrieval.py::test_search_endpoint_success -v
```

**Run tests by marker:**

```bash
# Run only unit tests (fast)
pytest -m unit

# Run only integration tests (requires services)
pytest -m integration
```

**View coverage report:**

```bash
# Generate HTML report
pytest --cov=common --cov=services --cov-report=html

# Open in browser
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
```

See [tests/README.md](tests/README.md) for comprehensive testing documentation including:

- Test structure and organization
- Writing new tests
- Mocking strategies
- CI/CD integration
- Troubleshooting guide

### CI/CD Pipeline

The project uses **GitHub Actions** for automated testing. The CI pipeline runs on every push and pull request.

**Pipeline Stages:**

1. **Lint** (fast, parallel)

   - Code formatting checks (black, isort)
   - Linting with flake8
   - Syntax error detection

2. **Unit Tests** (parallel, depends on lint)

   - All service tests run in parallel
   - Coverage reports generated (HTML, XML, terminal)
   - Artifacts uploaded for download

3. **Integration Tests** (sequential, depends on unit tests)

   - Docker Compose starts RabbitMQ and Qdrant
   - Proper health checks with 60-second timeouts
   - Service logs displayed on failure
   - Cleanup with `docker compose down -v`

4. **Docker Build** (parallel with integration)

   - All service images built and tested
   - Verifies images are functional

5. **Coverage Report** (final summary)
   - Aggregates coverage from all test jobs
   - Displays summary in GitHub Actions

**CI Configuration:** [.github/workflows/ci.yml](.github/workflows/ci.yml)

**Trigger Conditions:**

- Push to `main`, `develop`, `feature/**`, `hotfix/**` branches
- Pull requests to `main` and `develop`

**Viewing Results:**

1. Go to GitHub repository → **Actions** tab
2. Select latest workflow run
3. View job results and logs
4. Download coverage artifacts

**Job Dependencies:**

```
Lint (fast)
  ↓
Unit Tests (parallel) → Integration Tests + Docker Build (parallel)
  ↓
Coverage Report (summary)
```

This follows the **fail-fast** principle: linting errors stop the pipeline immediately, saving time and resources.

---

## Docker Build Optimization

All Dockerfiles have been optimized with **BuildKit cache mounts** for significantly faster builds.

### Enable BuildKit

**Windows (PowerShell):**

```powershell
.\scripts\enable-buildkit.ps1
docker compose up --build
```

**Linux/macOS:**

```bash
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1
docker compose up --build
```

**Make it permanent (Windows):**

1. Press `Win + X` → System → Advanced system settings
2. Environment Variables → New (User variables)
3. Add: `DOCKER_BUILDKIT` = `1`
4. Add: `COMPOSE_DOCKER_CLI_BUILD` = `1`

### Performance Improvements

| Build Type            | Before    | After       | Improvement              |
| --------------------- | --------- | ----------- | ------------------------ |
| First build           | 10-15 min | 10-15 min   | Same (needs to download) |
| Rebuild (code change) | 10-15 min | **3-5 min** | **3-5x faster**          |
| Rebuild (no changes)  | 8-10 min  | **30 sec**  | **16-20x faster**        |

### How It Works

All Dockerfiles now use:

```dockerfile
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt
```

This caches pip downloads between builds without increasing the final image size.

---

## Troubleshooting

### Docker won't start

```bash
docker compose logs rabbitmq
docker compose logs qdrant
docker compose logs ingestion
```

### RabbitMQ connection failed

1. Check status: `docker compose ps rabbitmq`
2. View logs: `docker compose logs rabbitmq | grep "started"`
3. Restart: `docker compose restart rabbitmq`

### Qdrant connection failed

1. Check status: `docker compose ps qdrant`
2. Test API: `curl http://localhost:6333/collections`
3. Restart: `docker compose restart qdrant`

### No PDFs being downloaded

1. Check logs: `docker compose logs ingestion`
2. Check stats: Visit <http://localhost:8001/stats>
3. Manually trigger: Visit <http://localhost:8001/docs> → `POST /ingest`

### Events not flowing through pipeline

1. Check RabbitMQ queues: <http://localhost:15672> (guest/guest)
2. Verify service health: <http://localhost:8001/health>
3. Check worker logs: `docker compose logs extraction indexing`

### Authentication errors

1. Ensure session token is valid (24h expiry)
2. Check Redis connection: `docker compose ps redis`
3. Re-login to get fresh token: `POST /login`
4. View auth logs: `docker compose logs auth`

### UI not loading

1. Check UI service: `docker compose ps ui`
2. View logs: `docker compose logs ui`
3. Verify port 8080 is not in use: `lsof -i :8080` (Mac/Linux)
4. Clear browser cache and retry

### Tests failing locally

1. Ensure dependencies installed: `pip install -r requirements-test.txt`
2. Run from project root: `cd MARP-Guide-AI && pytest`
3. For integration tests: `docker compose up -d rabbitmq qdrant`

---

## Technology Stack

### Core Infrastructure

| Technology     | Version         | Purpose                       |
| -------------- | --------------- | ----------------------------- |
| Docker         | Latest          | Containerization platform     |
| Docker Compose | Latest          | Multi-container orchestration |
| RabbitMQ       | 3.12-management | Message broker                |
| Qdrant         | Latest          | Vector database               |
| PostgreSQL     | 15-alpine       | User data storage             |
| Redis          | 7-alpine        | Session token storage         |

### Python Services

| Technology      | Version | Purpose                     |
| --------------- | ------- | --------------------------- |
| Python          | 3.11    | Programming language        |
| FastAPI         | 0.104.1 | Web framework for REST APIs |
| Uvicorn         | 0.24.0  | ASGI server                 |
| Starlette       | 0.27.0  | ASGI framework              |
| Pydantic        | 2.0+    | Data validation             |
| Pika            | 1.3.2   | RabbitMQ client             |
| psycopg2-binary | Latest  | PostgreSQL adapter          |
| redis           | Latest  | Redis client                |
| bcrypt          | Latest  | Password hashing            |

### Data Processing

| Technology            | Version | Purpose              |
| --------------------- | ------- | -------------------- |
| sentence-transformers | 3.0.0+  | Generate embeddings  |
| qdrant-client         | 1.7.0   | Qdrant Python client |
| pdfplumber            | 0.10.3  | PDF text extraction  |
| BeautifulSoup4        | 4.12.2  | HTML parsing         |
| lxml                  | 5.0.0+  | XML/HTML parser      |
| httpx                 | 0.25.2  | Async HTTP client    |
| requests              | 2.31.0  | HTTP client          |
| numpy                 | 1.24.3  | Numerical computing  |
| openai                | Latest  | OpenAI SDK client    |

### AI/ML Models

- **Embedding Model**: `all-MiniLM-L6-v2` (384 dimensions, cosine similarity)
- **LLM Provider**: OpenRouter (free tier available)
- **Default LLM**: `openai/gpt-4o-mini` (Temperature: 0.4, Max Tokens: 1200)
- **Multi-Model Comparison**: 3 models compared in parallel (GPT-4o Mini, Gemma 3n, DeepSeek Chat)
- **Max Context**: 3500 tokens for comprehensive answers

### Frontend

| Technology            | Version | Purpose                    |
| --------------------- | ------- | -------------------------- |
| React                 | 18.2.0  | UI framework               |
| React DOM             | 18.2.0  | React rendering            |
| Vite                  | 5.0.0   | Build tool & dev server    |
| Tailwind CSS          | 3.3.6   | Utility-first CSS          |
| PostCSS               | 8.4.32  | CSS processing             |
| Autoprefixer          | 10.4.16 | CSS vendor prefixing       |
| Axios                 | 1.6.0   | HTTP client                |
| react-markdown        | 9.0.0   | Markdown rendering         |
| prop-types            | 15.8.1  | React prop validation      |
| @vitejs/plugin-react  | 4.2.0   | Vite React plugin          |
| Nginx                 | Alpine  | Production static server   |

### Development Tools

| Tool           | Version | Purpose                   |
| -------------- | ------- | ------------------------- |
| pytest         | 7.4.3   | Testing framework         |
| pytest-cov     | 4.1.0   | Coverage plugin           |
| pytest-mock    | 3.12.0  | Mocking support           |
| pytest-asyncio | 0.21.1  | Async test support        |
| responses      | 0.24.1  | HTTP request mocking      |
| black          | 23.11.0 | Code formatter            |
| isort          | Latest  | Import sorter             |
| flake8         | 6.1.0   | Linter for code quality   |
| pre-commit     | Latest  | Git hooks for formatting  |
| GitHub Actions | N/A     | CI/CD pipeline            |

---

## Contributors

- Development Team: [Contributors](https://github.com/Th30utcast/MARP-Guide-AI/graphs/contributors)

---

## License

This project is developed as part of Lancaster University's coursework.

---

**Questions or Issues?** Open an issue on [GitHub](https://github.com/Th30utcast/MARP-Guide-AI/issues)
