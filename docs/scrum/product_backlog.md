# Product Backlog

**Project:** MARP-Guide AI RAG Chatbot
**Last Updated:** November 5, 2025
**Product Owner:** Martin Grimmer
**Current Sprint:** Sprint 1 (Assessment 1 preparation)

## Backlog Management

- **Live Issues:** https://github.com/Th30utcast/MARP-Guide-AI/issues
- **Project Board:** https://github.com/users/Th30utcast/projects/3
- **Columns:** Backlog → To Do → In Progress → In Review → Done

---

## Feature Selection

### Tier 1 Feature (Foundation)
**Chosen:** ✅ User Authentication & Session Management
- Login/logout functionality
- Session handling
- User-specific chat isolation

### Tier 2 Feature (Advanced)
**Chosen:** ✅ Multi-Model Comparison
- Parallel answer generation with different LLMs
- Side-by-side UI comparison
- Model performance metrics

---

## Epic Overview

| Epic ID | Epic Name | Priority | Status |
|---------|-----------|----------|--------|
| E1 | Ingestion | High | ✅ Done |
| E2 | Extraction | High | ✅ Done |
| E3 | Indexing | High | ✅ Done |
| E4 | Retrieval | High | ✅ Done |
| E5 | RAG & Chat | High | 🔄 In Progress |
| E6 | UX (Web UI) | Medium | 📋 To Do |
| E7 | Quality & Testing | Medium | 📋 To Do |
| E8 | User Authentication (Tier 1) | Medium | 📋 To Do |
| E9 | Multi-Model Comparison (Tier 2) | Medium | 📋 To Do |

---

## EPIC 1: Ingestion Service

**Goal:** Automatically discover and fetch MARP PDFs, storing text and metadata
**Status:** ✅ Completed (Sprint 1)

### User Stories

#### Story 1.1: Discover MARP PDF Links
**As a** system administrator
**I want** the system to automatically discover MARP PDF documents from the university website
**So that** we can keep the knowledge base up-to-date without manual intervention

**Status:** ✅ Done

---

#### Story 1.2: Download and Store PDFs
**As a** system
**I want** to download discovered PDFs and store them locally
**So that** we have a persistent copy for processing

**Status:** ✅ Done

---

## EPIC 2: Extraction Service

**Goal:** Extract text and metadata from PDF documents with page-level awareness
**Status:** ✅ Completed (Sprint 1)

### User Stories

#### Story 2.1: Extract Text from PDFs
**As a** system
**I want** to extract text content from PDF files
**So that** the text can be indexed and searched

**Status:** ✅ Done

---

#### Story 2.2: Extract PDF Metadata
**As a** system
**I want** to extract PDF metadata (title, author, creation date)
**So that** we can provide proper attribution and context

**Status:** ✅ Done

---

## EPIC 3: Indexing Service

**Goal:** Chunk documents and generate embeddings for vector search
**Status:** ✅ Completed (Sprint 1)

### User Stories

#### Story 3.1: Implement Chunking Strategy
**As a** developer
**I want** to chunk documents into semantically meaningful segments
**So that** retrieval returns relevant context

**Status:** ✅ Done

---

#### Story 3.2: Generate Embeddings
**As a** system
**I want** to generate vector embeddings for each chunk
**So that** semantic search is possible

**Status:** ✅ Done

---

#### Story 3.3: Store in Vector Database
**As a** system
**I want** to store embeddings in Qdrant vector database
**So that** fast similarity search is possible

**Status:** ✅ Done

---

## EPIC 4: Retrieval Service

**Goal:** Provide deterministic API to retrieve top-k relevant document snippets
**Status:** ✅ Completed (Sprint 1)

### User Stories

#### Story 4.1: Implement /search Endpoint
**As a** developer
**I want** a REST API endpoint that returns relevant snippets
**So that** other services can retrieve context for queries


**Status:** ✅ Done

---

#### Story 4.2: Document Retrieval API
**As a** developer
**I want** OpenAPI/Swagger documentation for the retrieval API
**So that** it's easy to integrate with other services

**Status:** ✅ Done

---

#### Story 4.3: Retrieval Logging and Events
**As a** developer
**I want** retrieval operations to be logged and emit events
**So that** we can monitor usage and performance

**Status:** ✅ Done

---

## EPIC 5: RAG & Chat Service

**Goal:** Provide chat endpoint that generates cited answers using OpenRouter LLM
**Status:** ✅ Completed (Sprint 1)

### User Stories

#### Story 5.1: Basic Chat Endpoint with 1 Citation
**As a** user
**I want** to ask questions and get answers with at least 1 citation
**So that** I can trust the information provided

**Status:** ✅ Done (Assessment 1 requirement)

---

#### Story 5.2: Enhanced RAG with 2+ Citations
**As a** user
**I want** answers with at least 2 citations
**So that** I have more confidence in the information

**Status:** 🔄 In Progress (Assessment 2 requirement)

---

#### Story 5.3: Citation Formatting and Validation
**As a** developer
**I want** citations to follow a consistent format
**So that** users can easily verify sources

**Status:** 📋 To Do

---

#### Story 5.4: No Source Fallback
**As a** user
**I want** clear communication when no source exists
**So that** I know the system's limitations

**Status:** 📋 To Do

---

## EPIC 6: UX (Web UI)

**Goal:** Simple web interface for asking questions and viewing citations
**Status:** 📋 To Do (Sprint 2)

### User Stories

#### Story 6.1: Question Input Interface
**As a** user
**I want** a simple interface to ask questions
**So that** I can interact with the system easily

**Status:** 📋 To Do

---

#### Story 6.2: Answer Display with Citations
**As a** user
**I want** to see answers with clearly displayed citations
**So that** I can understand and verify the information

**Status:** 📋 To Do

---

## EPIC 7: Quality, Operations & Testing

**Goal:** Reliable deployment, monitoring, and testing infrastructure
**Status:** 📋 Partially Complete (Sprint 1 & 2)

### User Stories

#### Story 7.1: Docker Compose Configuration
**As a** developer
**I want** docker compose up to start all services
**So that** deployment is simple and reproducible

**Status:** ✅ Done

---

#### Story 7.2: Service Health Checks
**As a** developer
**I want** health check endpoints for all services
**So that** Docker can monitor service status

**Status:** ✅ Done

---

#### Story 7.3: Automated Testing
**As a** developer
**I want** automated unit and integration tests
**So that** we can verify system correctness

**Status:** 📋 To Do (Sprint 2)

---

#### Story 7.4: CI Pipeline with GitHub Actions
**As a** developer
**I want** automated tests to run on every push
**So that** we catch bugs early

**Status:** 📋 To Do (Sprint 2)

---

## EPIC 8: User Authentication & Session Management (Tier 1)

**Goal:** Implement login/logout with user-specific chat isolation
**Status:** 📋 Planned (Sprint 2)

### User Stories

#### Story 8.1: User Registration
**As a** new user
**I want** to create an account
**So that** I can save my chat history

**Status:** 📋 To Do

---

#### Story 8.2: Login/Logout
**As a** user
**I want** to log in and log out
**So that** I can access my personal chat history

**Status:** 📋 To Do

---

#### Story 8.3: User-Specific Chat Isolation
**As a** user
**I want** my chats to be private
**So that** others cannot see my questions

**Status:** 📋 To Do

---

## EPIC 9: Multi-Model Comparison (Tier 2)

**Goal:** Enable parallel answer generation with multiple LLMs for comparison
**Status:** 📋 Planned (Sprint 2)

### User Stories

#### Story 9.1: Multi-Model Response Generation
**As a** user
**I want** to compare answers from different LLMs
**So that** I can evaluate quality and consistency

**Status:** 📋 To Do

---

#### Story 9.2: Side-by-Side UI Comparison
**As a** user
**I want** to see answers from different models side-by-side
**So that** I can easily compare them

**Status:** 📋 To Do

---

## Sprint Allocation

### Sprint 1 (Weeks 1-5) - Assessment 1
- ✅ EPIC 1: Ingestion
- ✅ EPIC 2: Extraction
- ✅ EPIC 3: Indexing
- ✅ EPIC 4: Retrieval
- ✅ EPIC 5: RAG & Chat

### Sprint 2 (Weeks 6-10) - Assessment 2
- 🔄 EPIC 5: RAG & Chat
- 📋 EPIC 6: UX
- 📋 EPIC 7: Quality
- 📋 EPIC 8: User Authentication
- 📋 EPIC 9: Multi-Model Comparison

---

**Last Updated:** November 5, 2025
**Next Review:** Sprint 2 Planning (Week 6)
