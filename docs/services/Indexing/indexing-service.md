# Service Name: Indexing Service

## Responsibility

Converts extracted text into searchable vector embeddings and stores them in a vector database (Qdrant).

## Data Owned

- Vector embeddings (384-dimensional, stored in Qdrant collection: `marp-documents`)
- Text chunks with metadata (document_id, title, page, URL, chunk_index)
- Chunk mappings (stored in `/app/storage/extracted/{document_id}/chunks.json`)

## API Endpoints

This service operates as an event-driven worker consuming from RabbitMQ. It does not expose HTTP endpoints except:

- [GET] /health - Health check endpoint (port 8080)

## Indexing Service Events

### Events Consumed

#### DocumentExtracted

Consumes events from the Extraction Service to begin indexing

```json
{
  "eventType": "DocumentExtracted",
  "payload": {
    "document_id": "string",
    "page_count": "integer",
    "pages_ref": "string (path to pages.jsonl)"
  }
}
```

Queue: `indexing_queue`
Routing key: `documents.extracted`

### Events Published

#### ChunksIndexed

Emitted when document chunks are successfully indexed in Qdrant

```json
{
  "eventType": "ChunksIndexed",
  "eventId": "uuid",
  "timestamp": "ISO-8601",
  "correlationId": "uuid",
  "source": "indexing-service",
  "version": "1.0",
  "payload": {
    "document_id": "string",
    "chunk_count": "integer",
    "embedding_model": "all-MiniLM-L6-v2",
    "vector_dimension": 384,
    "collection_name": "marp-documents"
  }
}
```

Routing key: `documents.indexed`

#### IndexingFailed

Emitted when indexing fails

```json
{
  "eventType": "IndexingFailed",
  "payload": {
    "document_id": "string",
    "error": "string",
    "failed_at": "ISO-8601"
  }
}
```

Routing key: `documents.indexing.failed`

## Processing Details

### Text Chunking

- **Strategy**: Token-based sliding window with overlap
- **Max tokens per chunk**: 200 (stays under model's 256 limit)
- **Overlap tokens**: 50 (25% overlap for context preservation)
- **Tokenizer**: SentenceTransformer tokenizer (accurate token counting)

### Embedding Generation

- **Model**: all-MiniLM-L6-v2 (SentenceTransformers)
- **Vector dimension**: 384
- **Batch size**: 32 chunks at a time
- **Model load time**: ~30 seconds (done once at startup)

### Vector Storage (Qdrant)

- **Collection**: marp-documents
- **Distance metric**: Cosine similarity
- **Connection retry**: 10 attempts with 2-second delay between retries
- **Payload schema**:
  - text: string (chunk content)
  - document_id: string
  - chunk_index: integer
  - title: string
  - page: integer
  - url: string

## Debugging Files

The service saves debugging/audit files to disk:

- **chunks.json** - `/app/storage/extracted/{document_id}/chunks.json`
  - All generated chunks before embedding
  - Useful for debugging chunking logic

- **indexed.json** - `/app/storage/extracted/{document_id}/indexed.json`
  - ChunksIndexed event metadata
  - Event sourcing for audit trail

## Configuration

Environment variables:
- `QDRANT_HOST` - Qdrant server hostname (default: "qdrant")
- `QDRANT_PORT` - Qdrant server port (default: 6333)
- `STORAGE_PATH` - Directory for event storage (default: "/app/storage/extracted")
- `RABBITMQ_HOST` - RabbitMQ hostname (default: "rabbitmq")
- `RABBITMQ_PORT` - RabbitMQ port (default: 5672)

## Technical Details

- **Port**: 8080 (health check only)
- **Embedding Model**: sentence-transformers/all-MiniLM-L6-v2
- **Retry Logic**: Qdrant connection retries 10 times with 2s exponential backoff
- **Batch Processing**: Embeds 32 chunks at a time for efficiency
- **Event Storage**: JSON files saved to disk for event sourcing
- **Error Handling**: Publishes IndexingFailed events on errors
