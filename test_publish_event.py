"""
Test script to publish a DocumentDiscovered event to RabbitMQ.
This ensures proper JSON formatting.
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from common.mq import RabbitMQEventBroker
from common.events import create_document_discovered_event

def main():
    print("🚀 Publishing test DocumentDiscovered event...")
    
    # Connect to RabbitMQ
    try:
        broker = RabbitMQEventBroker(
            host="localhost",
            port=5672,
            username="guest",
            password="guest"
        )
        print("✅ Connected to RabbitMQ")
    except Exception as e:
        print(f"❌ Failed to connect to RabbitMQ: {e}")
        print("💡 Make sure RabbitMQ is running: docker-compose up -d rabbitmq")
        return
    
    # Declare exchange
    if broker.channel:
        broker.channel.exchange_declare(
            exchange="events",
            exchange_type="topic",
            durable=True
        )
    
    # Update this path to point to one of your actual PDFs!
    pdf_path = r"C:\Users\user\Desktop\VS Code\Uni\Year 3\MARP-Guide-AI\storage\General-Regs.pdf"
    
    # Check if file exists
    if not Path(pdf_path).exists():
        print(f"⚠️ PDF not found: {pdf_path}")
        print("Please update the pdf_path variable in this script!")
        broker.close()
        return
    
    file_size = Path(pdf_path).stat().st_size
    
    # Create event using our helper function
    event = create_document_discovered_event(
        document_id="general-regs-2025",
        title="General Regulations",
        url=pdf_path,
        file_size=file_size
    )
    
    print("\n📤 Publishing event:")
    print(json.dumps(event, indent=2))
    
    # Publish
    try:
        broker.publish(
            routing_key="documents.discovered",
            message=json.dumps(event),
            exchange="events"
        )
        print("\n✅ Event published successfully!")
        print("👀 Check the worker terminal for processing logs")
    except Exception as e:
        print(f"\n❌ Failed to publish: {e}")
    finally:
        broker.close()

if __name__ == "__main__":
    main()