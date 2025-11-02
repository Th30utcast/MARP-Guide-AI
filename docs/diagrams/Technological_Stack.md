# Technology Stack

## Core Languages & Frameworks

- **Python 3.11** - All services
- **FastAPI 0.104.1** - Ingestion Service REST API
- **Uvicorn 0.24.0** - ASGI web server for Ingestion Service

## PDF Processing

- **BeautifulSoup4 4.12.2** - Ingestion Service (HTML parsing)
- **lxml ≥5.0.0** - Ingestion Service (parser backend)
- **pdfplumber 0.10.3** - Extraction Service (text extraction)

## Machine Learning

- **sentence-transformers ≥3.0.0** - Indexing Service (embeddings)
- **numpy 1.24.3** - Indexing Service (numerical operations)

## Databases

- **Qdrant 1.7.0** - Vector database (marp-documents collection)
- **RabbitMQ 3.12** - Message broker (event-driven communication)

## Python Clients

- **pika 1.3.2** - All services (RabbitMQ client)
- **requests 2.31.0** - Ingestion Service (HTTP requests)
- **qdrant-client 1.7.0** - Indexing Service (Qdrant client)

## Infrastructure

- **Docker** - Containerization
- **Docker Compose** - Multi-service orchestration
