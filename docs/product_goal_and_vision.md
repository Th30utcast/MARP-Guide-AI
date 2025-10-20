# 1) Product Goal & Vision

## Product Goal

Build a chat application that answers questions about Lancaster University’s **Manual of Academic Regulations and Procedures (MARP)** with **reliable, cited** responses. Target users are students and staff who need quick, trustworthy access to regulations. Value: fast, source‑backed answers and an explicit fallback when evidence is missing.

## Vision

A production‑minded, networked system using **microservices** and **event‑driven architecture** for ingestion, indexing/retrieval, and chat orchestration, with **RAG** as a hard requirement and citations (title, page, link) embedded in answers. Use only MARP PDFs as the knowledge source (OpenRouter/compatible LLMs allowed within limits).

## Definition of Done (module-aligned)

- Answers must include citations (≥1 citation for A1; ≥2 for A2). If no suitable source exists, the system must say so explicitly.
- `docker compose up` brings up all services; inter‑service comms over network protocols (HTTP/message broker).
- Scrum evidence maintained in this README (or `/docs`) and GitHub (Issues/Projects/PRs).
