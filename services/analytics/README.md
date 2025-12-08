# Analytics Service

User interaction event consumer and analytics API for the MARP chatbot.

## Purpose

The Analytics Service:
- Consumes user interaction events from RabbitMQ
- Stores events in memory (production: use PostgreSQL/MongoDB)
- Provides REST API for analytics queries
- Tracks chatbot usage patterns and performance metrics

## Events Consumed

### 1. QuerySubmitted
- **Routing Key**: `analytics.query.submitted`
- **Published By**: Chat Service
- **Data**: User query, session ID, model ID

### 2. ResponseGenerated
- **Routing Key**: `analytics.response.generated`
- **Published By**: Chat Service
- **Data**: Query, response, model ID, latency, token count, citation count

### 3. FeedbackReceived
- **Routing Key**: `analytics.feedback.received`
- **Published By**: Chat Service (future implementation)
- **Data**: Response ID, feedback type (positive/negative), optional comment

### 4. CitationClicked
- **Routing Key**: `analytics.citation.clicked`
- **Published By**: UI Service (future implementation)
- **Data**: Citation ID, document ID, page number, session ID

### 5. ModelComparisonTriggered
- **Routing Key**: `analytics.model.comparison.triggered`
- **Published By**: Chat Service
- **Data**: Query, session ID, list of models

### 6. ModelSelected
- **Routing Key**: `analytics.model.selected`
- **Published By**: Chat Service (future implementation)
- **Data**: Selected model ID, session ID, comparison ID

## API Endpoints

### Health Check
```
GET /health
```
Returns service health status.

### Analytics Summary
```
GET /analytics/summary
```
Returns overall statistics:
- Total queries
- Total responses
- Total feedback events
- Total comparisons
- Average latency
- Average citations per response

**Example Response**:
```json
{
  "total_queries": 150,
  "total_responses": 150,
  "total_feedback": 45,
  "total_comparisons": 30,
  "avg_latency_ms": 1250.5,
  "avg_citations_per_response": 3.2
}
```

### Popular Queries
```
GET /analytics/popular-queries?limit=10
```
Returns most frequently asked questions.

**Example Response**:
```json
[
  {
    "query": "What is MARP?",
    "count": 25
  },
  {
    "query": "How many credits do I need to graduate?",
    "count": 18
  }
]
```

### Model Statistics
```
GET /analytics/model-stats
```
Returns performance metrics for each model:
- Total queries processed
- Average latency
- Total citations generated

**Example Response**:
```json
[
  {
    "model_id": "openai/gpt-4o-mini",
    "total_queries": 100,
    "avg_latency_ms": 1200.0,
    "total_citations": 320
  },
  {
    "model_id": "google/gemma-3n-e2b-it:free",
    "total_queries": 50,
    "avg_latency_ms": 800.0,
    "total_citations": 150
  }
]
```

### Recent Queries
```
GET /analytics/recent-queries?limit=10
```
Returns recent user queries with timestamps.

**Example Response**:
```json
[
  {
    "query": "What is module condonation?",
    "timestamp": "2025-12-08T10:30:00Z",
    "model_id": "openai/gpt-4o-mini",
    "session_id": "abc123"
  }
]
```

## Architecture

```
┌─────────────┐
│ Chat Service│──publish──> QuerySubmitted
└─────────────┘              ResponseGenerated
                             ModelComparisonTriggered
                                    │
                                    v
                            ┌──────────────┐
                            │  RabbitMQ    │
                            │   Exchange   │
                            └──────────────┘
                                    │
                                    v
                            ┌──────────────┐
                            │  Analytics   │ ──consume──> In-Memory Storage
                            │   Service    │
                            └──────────────┘
                                    │
                                    v
                            ┌──────────────┐
                            │  REST API    │ ──query──> Analytics Endpoints
                            └──────────────┘
```

## Storage

**Current**: In-memory lists (development)
**Production Ready**: Use PostgreSQL, MongoDB, or InfluxDB for persistent storage

To upgrade to PostgreSQL:
1. Add PostgreSQL service to docker-compose.yml
2. Replace in-memory lists with SQLAlchemy models
3. Add database migrations with Alembic
4. Update event handlers to write to database

## Configuration

Environment variables:
- `RABBITMQ_HOST`: RabbitMQ hostname (default: `rabbitmq`)
- `RABBITMQ_PORT`: RabbitMQ port (default: `5672`)
- `RABBITMQ_USER`: RabbitMQ username (default: `guest`)
- `RABBITMQ_PASSWORD`: RabbitMQ password (default: `guest`)

## Usage

### Run with Docker Compose
```bash
docker compose up --build analytics
```

The service will:
1. Connect to RabbitMQ
2. Declare queues and bind to routing keys
3. Start consuming events in background threads
4. Expose REST API on port 8005

### Access Analytics API
```bash
# Get summary
curl http://localhost:8005/analytics/summary

# Get popular queries
curl http://localhost:8005/analytics/popular-queries?limit=5

# Get model stats
curl http://localhost:8005/analytics/model-stats

# Get recent queries
curl http://localhost:8005/analytics/recent-queries?limit=20
```

## Testing Events

You can test the analytics service by:
1. Using the chatbot UI (localhost:8080)
2. Sending POST requests to chat service (localhost:8003/chat)
3. Checking analytics API for updated metrics

## Future Enhancements

1. **Persistent Storage**: Replace in-memory with PostgreSQL/MongoDB
2. **Dashboard**: Add Grafana dashboard for visualization
3. **Feedback UI**: Add thumbs up/down buttons to UI
4. **Citation Tracking**: Track which citations users click
5. **Model Selection Tracking**: Track which model users choose after comparison
6. **Query Reformulation Tracking**: Track original vs reformulated queries
7. **Real-time WebSocket**: Push analytics updates to dashboard in real-time
8. **Export**: Export analytics data to CSV/JSON
9. **Alerts**: Set up alerts for performance degradation
10. **A/B Testing**: Compare model performance statistically

## Monitoring

Check service health:
```bash
curl http://localhost:8005/health
```

View logs:
```bash
docker logs marp-analytics --follow
```

Access RabbitMQ Management UI:
```
http://localhost:15672 (guest/guest)
```

Check queues and message rates in RabbitMQ UI.
