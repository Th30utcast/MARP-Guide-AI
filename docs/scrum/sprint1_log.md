# Sprint 1 Log

**Sprint:** Sprint 1 (Weeks 1-5)
**Duration:** October 1 - November 7, 2025
**Sprint Goal:** Core RAG pipeline with basic chat (≥1 citation)
**Assessment:** Assessment 1 Presentation - November 7, 2025

---

## Sprint Goal

Deliver functional core system: Ingestion → Extraction → Indexing → Retrieval → Basic RAG Chat with at least 1 citation.

---

## Sprint Commitments

### Selected Epics
- **EPIC 1:** Ingestion
- **EPIC 2:** Extraction
- **EPIC 3:** Indexing
- **EPIC 4:** Retrieval
- **EPIC 5:** RAG & Chat

---

## Sprint Summary

### Week 1 & 2: Foundation
- ✅ Team formation, repository setup
- ✅ Architecture design (microservices + EDA)
- ✅ Tech stack: Python/FastAPI, RabbitMQ, Qdrant, OpenRouter
- ✅ GitHub Projects configured
- ✅ Feature selection: Tier 1 (Auth), Tier 2 (Multi-Model)

### Week 3: Ingestion & Extraction
- ✅ PDF discovery from MARP website
- ✅ PDF download and storage
- ✅ Text extraction with pdfplumber
- ✅ Metadata extraction
- ✅ Events: DocumentDiscovered, DocumentExtracted
- ✅ Docker Compose initial setup

### Week 4: Indexing & Retrieval
- ✅ Chunking strategy: Overlapping
- ✅ Embeddings: all-MiniLM-L6-v2
- ✅ Qdrant integration
- ✅ /search API endpoint with OpenAPI docs
- ✅ Events: ChunksIndexed, IndexingFailed, RetrievalCompleted, ...

### Week 5: RAG, Chat, Integration & Documentation
- ✅ /chat endpoint with OpenRouter integration
- ✅ Prompt engineering for citations
- ✅ Docker Compose full configuration
- ✅ Health checks for all services
- ✅ System integration verified
- ✅ Documentation complete (README, architecture, event catalogue, API specs)
- ✅ Manual testing across full pipeline
- ✅ Assessment 1 preparation

---

## Completed Work

### Services Deployed
1. Ingestion Service
2. Extraction Service
3. Indexing Service
4. Retrieval Service
5. Chat Service

### Events Implemented (7 total)
1. DocumentDiscovered
2. DocumentExtracted
3. ChunksIndexed
4. IngestionFailed
5. ExtractionFailed
6. IndexingFailed
7. RetrievalCompleted

**Requirement:** ≥3 events → **Delivered:** 7 events ✅

### Infrastructure
- Docker Compose orchestration
- RabbitMQ message broker
- Qdrant vector database
- Network architecture: HTTP REST + message queue
- Health endpoints for all services

---

## Assessment 1 Deliverables

✅ Ingestion service functional
✅ Indexing service operational
✅ Retrieval API (/search endpoint)
✅ Basic RAG with ≥1 citation
✅ EDA: 7 events implemented
✅ Docker Compose deployment
✅ Network architecture (all services communicate via HTTP/RabbitMQ)
✅ Documentation (README, event schemas, API specs, architecture diagrams)

---

## Sprint Review Notes

**Demo:** Live demonstration of full pipeline
**Result:** All Sprint 1 requirements met
**Feedback:** Add automated tests in Sprint 2, improve citation consistency

---

## Carry Forward to Sprint 2

### Technical Debt
- Citation format validation
- Automated test suite

### Sprint 2 Focus
- Enhanced RAG
- Web UI
- Automated testing + CI pipeline
- Tier 1 feature: User Authentication
- Tier 2 feature: Multi-Model Comparison

---

**Sprint Status:** ✅ COMPLETED
**Next Sprint:** Sprint 2 (Weeks 6-10)
