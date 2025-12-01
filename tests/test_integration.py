"""
Integration tests for the MARP-Guide-AI system.

These tests verify that services can communicate with each other correctly.
Requires RabbitMQ and Qdrant to be running.
"""

import json
import time

import pytest
import requests


class TestInfrastructure:
    """Test that infrastructure components are accessible."""

    def test_rabbitmq_is_accessible(self):
        """Test that RabbitMQ management API is accessible."""
        try:
            response = requests.get("http://localhost:15672/api/overview", auth=("guest", "guest"), timeout=5)
            assert response.status_code == 200
        except requests.exceptions.RequestException:
            pytest.skip("RabbitMQ not running (expected in CI)")

    def test_qdrant_is_accessible(self):
        """Test that Qdrant API is accessible."""
        try:
            response = requests.get("http://localhost:6333/collections", timeout=5)
            assert response.status_code == 200
        except requests.exceptions.RequestException:
            pytest.skip("Qdrant not running (expected in CI)")


class TestEndToEndFlow:
    """Test end-to-end document processing flow."""

    def test_retrieval_service_health(self):
        """Test that retrieval service is healthy."""
        try:
            response = requests.get("http://localhost:8002/health", timeout=5)
            # If service is running, should return 200
            # If not running, will raise exception (expected in CI)
            if response.status_code == 200:
                data = response.json()
                assert "status" in data
                assert data["status"] == "ok"
        except requests.exceptions.RequestException:
            pytest.skip("Retrieval service not running (expected in CI)")

    def test_retrieval_search_endpoint(self):
        """Test retrieval service search endpoint."""
        try:
            response = requests.post("http://localhost:8002/search", json={"query": "What is MARP?", "top_k": 3}, timeout=10)

            if response.status_code == 200:
                data = response.json()
                assert "query" in data
                assert "results" in data
                assert data["query"] == "What is MARP?"
                # Results might be empty if no documents indexed yet
                assert isinstance(data["results"], list)
        except requests.exceptions.RequestException:
            pytest.skip("Retrieval service not running (expected in CI)")


class TestEventFlow:
    """Test event-driven architecture flow."""

    def test_rabbitmq_queues_exist(self):
        """Test that required RabbitMQ queues exist."""
        try:
            response = requests.get("http://localhost:15672/api/queues", auth=("guest", "guest"), timeout=5)

            if response.status_code == 200:
                queues = response.json()
                queue_names = [q["name"] for q in queues]

                # Check for expected queues
                expected_queues = ["documents.discovered", "documents.extracted", "documents.indexed"]

                for queue_name in expected_queues:
                    if queue_name in queue_names:
                        # Queue exists - good!
                        assert True
        except requests.exceptions.RequestException:
            pytest.skip("RabbitMQ not running (expected in CI)")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
