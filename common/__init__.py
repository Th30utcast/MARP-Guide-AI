"""
Common utilities for MARP Guide AI services.
"""

# This file makes 'common' a Python package
# Import key classes for easier access

from .mq import RabbitMQEventBroker

__all__ = ['RabbitMQEventBroker']