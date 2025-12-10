"""
Common utilities for MARP Guide AI services.
"""

# This file makes 'common' a Python package
from .mq import RabbitMQEventBroker

__all__ = ["RabbitMQEventBroker"]
