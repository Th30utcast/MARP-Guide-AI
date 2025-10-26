``` mermaid
flowchart LR
  subgraph Retrieval["Retrieval Service"]
    RS[(Container)]
    VDB[(Vector DB)]
  end

  subgraph Indexing["Indexing Service"]
    IS[(Container)]
  end

  subgraph Extraction["Extraction Service"]
    ES[(Container)]
  end

  subgraph Ingestion["Ingestion Service"]
    IG[(Container)]
    Store[(Object Store / Files + Metadata DB)]
  end

  subgraph Broker["Event Broker (RabbitMQ)"]
    Q1([documents.discovered])
    Q2([documents.extracted])
    Q3([chunks.indexed])
  end

  RS --- VDB
  IG --- Store
  IG -->|publish DocumentDiscovered| Q1
  Q1 --> ES
  ES -->|publish DocumentExtracted| Q2
  Q2 --> IS
  IS --- VDB
  IS -->|publish ChunksIndexed| Q3
```