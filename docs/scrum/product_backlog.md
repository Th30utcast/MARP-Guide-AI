# Product Backlog

**Project:** MARP-Guide AI RAG Chatbot
**Last Updated:** December 10, 2025
**Product Owner:** Martin Grimmer
**Current Sprint:** Sprint 2 (Assessment 2 complete)

## Backlog Management

- **Live Issues:** https://github.com/Th30utcast/MARP-Guide-AI/issues
- **Project Board:** https://github.com/users/Th30utcast/projects/3
- **Columns:** Backlog → To Do → In Progress → In Review → Done

---

## Feature Selection

### Tier 1 Feature (Foundation)
**Chosen:** ✅ User Authentication & Session Management (COMPLETED)
- Login/logout functionality
- Session handling
- User-specific chat isolation
- Model preference storage
- Admin user support

### Tier 2 Feature (Advanced)
**Chosen:** ✅ Multi-Model Comparison (COMPLETED)
- Parallel answer generation with 3 LLMs
- Side-by-side UI comparison
- Model selection analytics
- Performance metrics

---

## Epic Overview

| Epic ID | Epic Name | Priority | Status |
|---------|-----------|----------|--------|
| E1 | Ingestion | High | ✅ Done |
| E2 | Extraction | High | ✅ Done |
| E3 | Indexing | High | ✅ Done |
| E4 | Retrieval | High | ✅ Done |
| E5 | RAG & Chat | High | ✅ Done |
| E6 | UX (Web UI) | Medium | ✅ Done |
| E7 | Quality & Testing | Medium | ✅ Done |
| E8 | User Authentication (Tier 1) | Medium | ✅ Done |
| E9 | Multi-Model Comparison (Tier 2) | Medium | ✅ Done |
| E10 | Analytics Service | Medium | ✅ Done |

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
**Status:** ✅ Completed (Sprint 2)

### User Stories

#### Story 5.1: Basic Chat Endpoint with 1 Citation
**As a** user
**I want** to ask questions and get answers with at least 1 citation
**So that** I can trust the information provided

**Status:** ✅ Done (Assessment 1)

---

#### Story 5.2: Enhanced RAG with 2+ Citations
**As a** user
**I want** answers with at least 2 citations
**So that** I have more confidence in the information

**Status:** ✅ Done (Assessment 2)

---

#### Story 5.3: Query Reformulation
**As a** user
**I want** my queries to be automatically improved
**So that** I get better search results even with typos

**Status:** ✅ Done (Assessment 2)

---

#### Story 5.4: Anti-Hallucination Protection
**As a** user
**I want** answers to be rejected if they lack citations
**So that** I can trust the system isn't making things up

**Status:** ✅ Done (Assessment 2)

---

#### Story 5.5: Citation Deduplication
**As a** user
**I want** duplicate citations to be removed
**So that** citation lists are clean and concise

**Status:** ✅ Done (Assessment 2)

---

## EPIC 6: UX (Web UI)

**Goal:** Simple web interface for asking questions and viewing citations
**Status:** ✅ Completed (Sprint 2)

### User Stories

#### Story 6.1: Question Input Interface
**As a** user
**I want** a simple interface to ask questions
**So that** I can interact with the system easily

**Status:** ✅ Done

---

#### Story 6.2: Answer Display with Citations
**As a** user
**I want** to see answers with clearly displayed citations
**So that** I can understand and verify the information

**Status:** ✅ Done

---

#### Story 6.3: Authentication UI
**As a** user
**I want** login and registration screens
**So that** I can access my personalized experience

**Status:** ✅ Done

---

#### Story 6.4: Model Comparison UI
**As a** user
**I want** to view side-by-side model comparisons
**So that** I can evaluate different LLM responses

**Status:** ✅ Done

---

## EPIC 7: Quality, Operations & Testing

**Goal:** Reliable deployment, monitoring, and testing infrastructure
**Status:** ✅ Completed (Sprint 2)

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

#### Story 7.3: Input Validation
**As a** developer
**I want** comprehensive input validation across all services
**So that** we prevent invalid data from causing errors

**Status:** ✅ Done

---

#### Story 7.4: Error Handling
**As a** developer
**I want** clear error messages and proper exception handling
**So that** debugging is easier

**Status:** ✅ Done

---

#### Story 7.5: Logging and Monitoring
**As a** developer
**I want** structured logging across all services
**So that** we can track system behavior

**Status:** ✅ Done

---

## EPIC 8: User Authentication & Session Management (Tier 1)

**Goal:** Implement login/logout with user-specific chat isolation
**Status:** ✅ Completed (Sprint 2)

### User Stories

#### Story 8.1: User Registration
**As a** new user
**I want** to create an account
**So that** I can access the system

**Status:** ✅ Done

---

#### Story 8.2: Login/Logout
**As a** user
**I want** to log in and log out
**So that** I can access my personalized experience

**Status:** ✅ Done

---

#### Story 8.3: Session Management
**As a** user
**I want** my session to persist for 24 hours
**So that** I don't have to log in repeatedly

**Status:** ✅ Done

---

#### Story 8.4: Model Preference Storage
**As a** user
**I want** to save my preferred LLM model
**So that** future chats use my selected model

**Status:** ✅ Done

---

#### Story 8.5: Admin User Support
**As an** administrator
**I want** admin-level access to view global analytics
**So that** I can monitor system usage

**Status:** ✅ Done

---

## EPIC 9: Multi-Model Comparison (Tier 2)

**Goal:** Enable parallel answer generation with multiple LLMs for comparison
**Status:** ✅ Completed (Sprint 2)

### User Stories

#### Story 9.1: Multi-Model Response Generation
**As a** user
**I want** to compare answers from 3 different LLMs
**So that** I can evaluate quality and consistency

**Status:** ✅ Done

---

#### Story 9.2: Parallel Execution
**As a** system
**I want** to generate answers from all models simultaneously
**So that** comparison is fast

**Status:** ✅ Done

---

#### Story 9.3: Model Selection Analytics
**As a** user
**I want** my model selection to be tracked
**So that** the system can learn which models are preferred

**Status:** ✅ Done

---

#### Story 9.4: Shared Context
**As a** user
**I want** all models to receive the same retrieval context
**So that** the comparison is fair

**Status:** ✅ Done

---

## EPIC 10: Analytics Service

**Goal:** Track user interactions and system metrics
**Status:** ✅ Completed (Sprint 2)

### User Stories

#### Story 10.1: Event Consumption
**As a** system
**I want** to consume analytics events from RabbitMQ
**So that** we can track user behavior

**Status:** ✅ Done

---

#### Story 10.2: Analytics Endpoints
**As an** administrator
**I want** API endpoints to view system metrics
**So that** I can understand usage patterns

**Status:** ✅ Done

---

#### Story 10.3: User-Specific Analytics
**As a** user
**I want** to view my own usage statistics
**So that** I can track my queries

**Status:** ✅ Done

---

#### Story 10.4: Admin Analytics
**As an** administrator
**I want** to view global system analytics
**So that** I can monitor overall usage

**Status:** ✅ Done

---

## Sprint Allocation

### Sprint 1 (Weeks 1-5) - Assessment 1
- ✅ EPIC 1: Ingestion
- ✅ EPIC 2: Extraction
- ✅ EPIC 3: Indexing
- ✅ EPIC 4: Retrieval
- ✅ EPIC 5: RAG & Chat (Basic)

### Sprint 2 (Weeks 6-10) - Assessment 2
- ✅ EPIC 5: RAG & Chat (Enhanced)
- ✅ EPIC 6: UX (Web UI)
- ✅ EPIC 7: Quality & Operations
- ✅ EPIC 8: User Authentication (Tier 1)
- ✅ EPIC 9: Multi-Model Comparison (Tier 2)
- ✅ EPIC 10: Analytics Service

---

## Event Summary

**Total Events Implemented:** 10

### Document Processing Pipeline Events (4)
1. DocumentDiscovered
2. DocumentExtracted
3. ChunksIndexed
4. RetrievalCompleted

### Error Events (3)
5. IngestionFailed
6. ExtractionFailed
7. IndexingFailed

### User Interaction & Analytics Events (3)
8. QuerySubmitted
9. ResponseGenerated
10. ModelComparisonTriggered

---

**Last Updated:** December 10, 2025
**Sprint Status:** Sprint 2 COMPLETED
**Assessment 2:** December 10, 2025
