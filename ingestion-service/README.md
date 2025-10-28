# MARP Ingestion Service

Microservice for discovering and fetching MARP PDFs from Lancaster University.

## Features

- **Discovery**: Scrapes MARP website to find all PDF links
- **Fetching**: Downloads PDFs to shared storage
- **Event Publishing**: Emits `DocumentDiscovered` events to RabbitMQ
- **REST API**: FastAPI endpoints for triggering ingestion and health checks
- **Docker**: Fully containerized with Docker Compose

## Project Structure

```
ingestion-service/
├── main.py           # FastAPI app and orchestrator
├── scraper.py        # Web scraper for MARP website
├── fetcher.py        # PDF downloader
├── event_broker.py   # RabbitMQ event publisher
├── requirements.txt  # Python dependencies
├── Dockerfile        # Container image
└── README.md
```

## API Endpoints

### `GET /`
Root endpoint with service info.

### `GET /health`
Health check endpoint.
- Returns 200 if healthy
- Returns 503 if RabbitMQ disconnected

### `POST /ingest`
Trigger the ingestion process:
1. Discover PDFs from MARP website
2. Download PDFs to shared storage
3. Publish `DocumentDiscovered` events

Returns statistics about discovered/fetched/published documents.

### `GET /stats`
Get ingestion statistics (total PDFs stored).

## Events Published

### `DocumentDiscovered`
Published when a PDF is successfully discovered and fetched.

```json
{
  "eventType": "DocumentDiscovered",
  "eventId": "uuid",
  "timestamp": "2025-10-27T10:30:00Z",
  "correlationId": "uuid",
  "source": "ingestion-service",
  "version": "1.0",
  "payload": {
    "documentId": "marp-xxx",
    "title": "Document Title",
    "url": "/app/pdfs/marp-xxx.pdf",
    "originalUrl": "https://lancaster.ac.uk/.../doc.pdf",
    "discoveredAt": "2025-10-27T10:30:00Z",
    "fileSize": 1024567
  }
}
```

## Running Locally

### Prerequisites
- Docker Desktop installed and running

### Start the service
```bash
# From project root
cd /Users/skrilexon/Desktop/SoftwareDesign2/Discorvery

# Start all services
docker-compose up --build

# Or in background
docker-compose up -d --build
```

### Trigger ingestion
```bash
curl -X POST http://localhost:8001/ingest
```

### Check health
```bash
curl http://localhost:8001/health
```

### View logs
```bash
docker-compose logs -f ingestion
```

### Stop services
```bash
docker-compose down
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MARP_URL` | Lancaster MARP page | URL to scrape for PDFs |
| `RABBITMQ_HOST` | `localhost` | RabbitMQ hostname |
| `RABBITMQ_PORT` | `5672` | RabbitMQ port |
| `RABBITMQ_USER` | `guest` | RabbitMQ username |
| `RABBITMQ_PASS` | `guest` | RabbitMQ password |
| `PDF_OUTPUT_DIR` | `/app/pdfs` | Directory to store PDFs |

## Integration with Other Services

### Extraction Service
The Extraction service should:
1. Listen for `DocumentDiscovered` events on the `documents.discovered` queue
2. Read PDFs from the shared volume (`/app/pdfs`)
3. Extract text and publish `DocumentExtracted` events

### Shared Volume
PDFs are stored in `./shared-pdfs/` which is mounted to `/app/pdfs` in containers.

## Development

### Install dependencies locally
```bash
cd ingestion-service
pip install -r requirements.txt
```

### Run without Docker (requires RabbitMQ running)
```bash
export RABBITMQ_HOST=localhost
export PDF_OUTPUT_DIR=./pdfs
python main.py
```

## RabbitMQ Management UI

Access at: http://localhost:15672
- Username: `guest`
- Password: `guest`

View queues, exchanges, and messages.
