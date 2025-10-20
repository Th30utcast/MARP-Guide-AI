# 2) Product Backlog (GitHub)

Manage the live backlog on GitHub; keep this section as the readable overview.

**Boards & Filters**

- Issues: `<repo-url>/issues`
- Project board (Sprints): `<repo-url>/projects/<id>` (Columns: Backlog → To Do → In Progress → In Review → Done)

## Epics & Example Stories

**EPIC: Ingestion**

- Story: Discover & fetch MARP PDFs so they can be processed later.
- AC: Crawl MARP page(s), download PDFs, persist metadata (title, URL, date, pages); emit `DocumentDiscovered`, `DocumentFetched` events.

**EPIC: Extraction**

- Story: Extract text + basic structure from PDFs.
- AC: Page‑aware text; attach page numbers; emit `DocumentExtracted`.

**EPIC: Index**

- Story: Chunk + embed docs for retrieval.
- AC: Custom chunking doc; embeddings with metadata (title, page, URL); emit `ChunksIndexed`.

**EPIC: Retrieval**

- Story: Deterministic `/search` API that returns top‑k snippets.
- AC: Configurable k; returns snippet + title/page/link; OpenAPI documented.

**EPIC: RAG & Chat**

- Story: `/chat` returns a **cited** answer.
- AC: Prompt v1 with citation formatting; ≥1 citation (A1), ≥2 (A2); fallback when no source; emit `AnswerGenerated`.

**EPIC: UX (Web UI)**

- Story: Simple UI to ask questions and show citations.
- AC: Input box, answer view, citations panel; optional history.

**EPIC: Quality (Ops, CI/CD, Tests)**

- Story: Compose, health checks, CI, tests.
- AC: Compose file, service health endpoints, CI workflow, unit/integration tests.

**Tier 1 Feature (choose ONE; record choice)**

- Options: Chat history / Auth / Bookmarks / Doc management UI / Basic monitoring
- **Chosen:** _<fill in>_

**Tier 2 Feature (choose ONE; record choice)**

- Options: Hybrid search / Query rewriting / Re‑ranking / Multi‑model compare / Feedback & metrics / Observability / Rate limiting & semantic cache / A/B testing
- **Chosen:** _<fill in>_

---
