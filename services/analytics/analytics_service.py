"""
Analytics Service - User Interaction Event Consumer
Consumes events from RabbitMQ and stores them for analytics queries
"""

import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

import requests
from fastapi import FastAPI, Header, HTTPException, Query
from pydantic import BaseModel

# Add common module to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from common.mq import RabbitMQEventBroker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Analytics Service", version="1.0.0")

# In-memory storage for events (in production, use a database like PostgreSQL)
query_events: List[Dict] = []
response_events: List[Dict] = []
feedback_events: List[Dict] = []
citation_clicked_events: List[Dict] = []
model_comparison_events: List[Dict] = []
model_selected_events: List[Dict] = []


class PopularQuery(BaseModel):
    query: str
    count: int


class ModelStats(BaseModel):
    model_id: str
    total_queries: int
    avg_latency_ms: float
    total_citations: int


class AnalyticsSummary(BaseModel):
    total_queries: int
    total_responses: int
    total_feedback: int
    total_comparisons: int
    avg_latency_ms: float
    avg_citations_per_response: float


def handle_query_submitted(ch, method, properties, body):
    """Handle QuerySubmitted events"""
    try:
        event = json.loads(body)
        query_events.append(event)
        logger.info(f"Stored QuerySubmitted event: {event['payload']['query'][:50]}...")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.error(f"Error handling QuerySubmitted event: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def handle_response_generated(ch, method, properties, body):
    """Handle ResponseGenerated events"""
    try:
        event = json.loads(body)
        response_events.append(event)
        logger.info(
            f"Stored ResponseGenerated event: model={event['payload']['modelId']}, latency={event['payload']['latencyMs']}ms"
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.error(f"Error handling ResponseGenerated event: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def handle_feedback_received(ch, method, properties, body):
    """Handle FeedbackReceived events"""
    try:
        event = json.loads(body)
        feedback_events.append(event)
        logger.info(f"Stored FeedbackReceived event: type={event['payload']['feedbackType']}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.error(f"Error handling FeedbackReceived event: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def handle_citation_clicked(ch, method, properties, body):
    """Handle CitationClicked events"""
    try:
        event = json.loads(body)
        citation_clicked_events.append(event)
        logger.info(f"Stored CitationClicked event: doc={event['payload']['documentId']}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.error(f"Error handling CitationClicked event: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def handle_model_comparison_triggered(ch, method, properties, body):
    """Handle ModelComparisonTriggered events"""
    try:
        event = json.loads(body)
        model_comparison_events.append(event)
        logger.info(f"Stored ModelComparisonTriggered event: models={len(event['payload']['models'])}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.error(f"Error handling ModelComparisonTriggered event: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def handle_model_selected(ch, method, properties, body):
    """Handle ModelSelected events"""
    try:
        event = json.loads(body)
        model_selected_events.append(event)
        logger.info(f"Stored ModelSelected event: model={event['payload']['modelId']}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.error(f"Error handling ModelSelected event: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def check_if_admin(authorization: Optional[str]) -> bool:
    """Check if the user is an admin by validating session with auth service"""
    if not authorization or not authorization.startswith("Bearer "):
        return False

    try:
        auth_url = os.getenv("AUTH_URL", "http://auth:8004")
        response = requests.get(f"{auth_url}/auth/validate", headers={"Authorization": authorization}, timeout=5)

        if response.status_code == 200:
            data = response.json()
            return data.get("is_admin", False)
        return False
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        return False


@app.get("/health")
def health():
    return {"status": "healthy", "service": "analytics"}


@app.get("/analytics/summary", response_model=AnalyticsSummary)
def get_summary(
    user_id: Optional[str] = Query(None, description="User ID for filtering"),
    authorization: Optional[str] = Header(None),
):
    """Get analytics summary (admins see all data, users see only their own)"""
    is_admin = check_if_admin(authorization)

    if is_admin:
        user_query_events = query_events
        user_response_events = response_events
        user_feedback_events = feedback_events
        user_comparison_events = model_comparison_events
    else:
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required for non-admin users")
        user_query_events = [e for e in query_events if e["payload"].get("userId") == user_id]
        user_response_events = [e for e in response_events if e["payload"].get("userId") == user_id]
        user_feedback_events = [e for e in feedback_events if e["payload"].get("userId") == user_id]
        user_comparison_events = [e for e in model_comparison_events if e["payload"].get("userId") == user_id]

    total_queries = len(user_query_events)
    total_responses = len(user_response_events)
    total_feedback = len(user_feedback_events)
    total_comparisons = len(user_comparison_events)

    avg_latency = 0.0
    avg_citations = 0.0

    if total_responses > 0:
        avg_latency = sum(e["payload"]["latencyMs"] for e in user_response_events) / total_responses
        avg_citations = sum(e["payload"]["citationCount"] for e in user_response_events) / total_responses

    return AnalyticsSummary(
        total_queries=total_queries,
        total_responses=total_responses,
        total_feedback=total_feedback,
        total_comparisons=total_comparisons,
        avg_latency_ms=round(avg_latency, 2),
        avg_citations_per_response=round(avg_citations, 2),
    )


@app.get("/analytics/popular-queries", response_model=List[PopularQuery])
def get_popular_queries(
    user_id: Optional[str] = Query(None, description="User ID for filtering"),
    limit: int = Query(10, ge=1, le=100),
    authorization: Optional[str] = Header(None),
):
    """Get most popular queries (admins see all data, users see only their own)"""
    is_admin = check_if_admin(authorization)
    query_counts = {}

    if is_admin:
        user_query_events = query_events
    else:
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required for non-admin users")
        user_query_events = [e for e in query_events if e["payload"].get("userId") == user_id]

    for event in user_query_events:
        query = event["payload"]["query"]
        query_counts[query] = query_counts.get(query, 0) + 1

    sorted_queries = sorted(query_counts.items(), key=lambda x: x[1], reverse=True)

    return [PopularQuery(query=query, count=count) for query, count in sorted_queries[:limit]]


@app.get("/analytics/model-stats", response_model=List[ModelStats])
def get_model_stats(
    user_id: Optional[str] = Query(None, description="User ID for filtering"), authorization: Optional[str] = Header(None)
):
    """Get statistics for each model (admins see all data, users see only their own)"""
    is_admin = check_if_admin(authorization)
    model_data = {}

    if is_admin:
        user_response_events = response_events
    else:
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required for non-admin users")
        user_response_events = [e for e in response_events if e["payload"].get("userId") == user_id]

    for event in user_response_events:
        model_id = event["payload"]["modelId"]
        if model_id not in model_data:
            model_data[model_id] = {"queries": 0, "total_latency": 0, "total_citations": 0}

        model_data[model_id]["queries"] += 1
        model_data[model_id]["total_latency"] += event["payload"]["latencyMs"]
        model_data[model_id]["total_citations"] += event["payload"]["citationCount"]

    results = []
    for model_id, data in model_data.items():
        avg_latency = data["total_latency"] / data["queries"] if data["queries"] > 0 else 0
        results.append(
            ModelStats(
                model_id=model_id,
                total_queries=data["queries"],
                avg_latency_ms=round(avg_latency, 2),
                total_citations=data["total_citations"],
            )
        )

    return results


@app.get("/analytics/recent-queries")
def get_recent_queries(
    user_id: Optional[str] = Query(None, description="User ID for filtering"),
    limit: int = Query(10, ge=1, le=100),
    authorization: Optional[str] = Header(None),
):
    """Get recent queries (admins see all data, users see only their own)"""
    is_admin = check_if_admin(authorization)

    if is_admin:
        user_query_events = query_events
    else:
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required for non-admin users")
        user_query_events = [e for e in query_events if e["payload"].get("userId") == user_id]

    recent = user_query_events[-limit:][::-1]
    return [
        {
            "query": e["payload"]["query"],
            "timestamp": e["timestamp"],
            "model_id": e["payload"]["modelId"],
            "session_id": e["payload"]["userSessionId"],
        }
        for e in recent
    ]


@app.post("/analytics/reset")
def reset_analytics():
    """Reset all analytics data"""
    query_events.clear()
    response_events.clear()
    feedback_events.clear()
    citation_clicked_events.clear()
    model_comparison_events.clear()
    model_selected_events.clear()

    logger.info("🔄 Analytics data reset - all events cleared")

    return {
        "status": "success",
        "message": "All analytics data has been reset",
        "cleared": {
            "queries": True,
            "responses": True,
            "feedback": True,
            "citation_clicks": True,
            "model_comparisons": True,
            "model_selections": True,
        },
    }


@app.on_event("startup")
def startup_event():
    """Initialize RabbitMQ consumer and start consuming events"""
    import threading

    def consume_events():
        try:
            broker = RabbitMQEventBroker(
                host=os.getenv("RABBITMQ_HOST", "rabbitmq"),
                port=int(os.getenv("RABBITMQ_PORT", "5672")),
                username=os.getenv("RABBITMQ_USER", "guest"),
                password=os.getenv("RABBITMQ_PASS", "guest"),
            )

            queues = [
                ("analytics_query_submitted", "analytics.query.submitted", handle_query_submitted),
                ("analytics_response_generated", "analytics.response.generated", handle_response_generated),
                ("analytics_feedback_received", "analytics.feedback.received", handle_feedback_received),
                ("analytics_citation_clicked", "analytics.citation.clicked", handle_citation_clicked),
                (
                    "analytics_model_comparison",
                    "analytics.model.comparison.triggered",
                    handle_model_comparison_triggered,
                ),
                ("analytics_model_selected", "analytics.model.selected", handle_model_selected),
            ]

            for queue_name, routing_key, handler in queues:
                broker.declare_queue(queue_name, durable=True)
                broker.channel.queue_bind(exchange="events", queue=queue_name, routing_key=routing_key)
                logger.info(f"Bound queue {queue_name} to routing key {routing_key}")

            for queue_name, _, handler in queues:

                def consume_queue(q_name, q_handler):
                    consumer_broker = RabbitMQEventBroker(
                        host=os.getenv("RABBITMQ_HOST", "rabbitmq"),
                        port=int(os.getenv("RABBITMQ_PORT", "5672")),
                        username=os.getenv("RABBITMQ_USER", "guest"),
                        password=os.getenv("RABBITMQ_PASS", "guest"),
                    )
                    consumer_broker.consume(q_name, q_handler, auto_ack=False)

                thread = threading.Thread(target=consume_queue, args=(queue_name, handler), daemon=True)
                thread.start()

            logger.info("✅ Analytics service started consuming events")

        except Exception as e:
            logger.error(f"❌ Failed to initialize analytics consumer: {e}")

    consumer_thread = threading.Thread(target=consume_events, daemon=True)
    consumer_thread.start()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8005)
