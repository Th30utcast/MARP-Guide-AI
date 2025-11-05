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
- **Payload schema**:
  - text: string (chunk content)
  - document_id: string
  - chunk_index: integer
  - title: string
  - page: integer
  - url: string
