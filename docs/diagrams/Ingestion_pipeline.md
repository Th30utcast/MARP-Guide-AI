``` mermaid
sequenceDiagram
  participant IG as Ingestion
  participant BR as Broker
  participant EX as Extraction
  participant IX as Indexing

  IG->>BR: publish DocumentDiscovered {document_id, url, title}
  BR-->>EX: DocumentDiscovered
  EX->>EX: PDF→text+metadata
  EX->>BR: publish DocumentExtracted {document_id, num of pages, url, title, date}
  BR-->>IX: DocumentExtracted
  IX->>IX: Chunk + embed + store
  IX->>BR: publish ChunksIndexed {document_id, chunk_count}

```