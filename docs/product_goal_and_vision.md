# Product Goal

Build a chat application that answers questions about Lancaster University’s Manual of Academic Regulations and Procedures (MARP) with reliable, cited responses. Target users are students and staff who need quick, trustworthy access to regulations. Value: fast, source-backed answers and explicit “not certain / no source found” fallback when evidence is missing.

# Vision

A production-minded, networked system using microservices and event-driven architecture for ingestion, indexing/retrieval, and chat orchestration, with RAG as a hard requirement and citations (title, page, link) embedded in answers. Use OpenRouter models (free allowed within limits) and only MARP PDFs as the knowledge source. Key Requirements (DoD highlights)

- Answers must be supported by sources; show ≥1 citation in A1 and ≥2 citations in A2. If no source fits, say so explicitly.

- docker compose up must bring up all services; all inter-service comms happen over network protocols (HTTP or a message broker).

- Scrum evidence must be documented: product goal/vision, backlog, sprint logs, and retrospective.
