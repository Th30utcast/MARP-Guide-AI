"""
Simple test script to simulate DocumentDiscovered event for local testing
"""
import os
import json
from pathlib import Path

# Configuration
TEST_PDFS_DIR = "test-pdfs"
DISCOVERED_EVENTS_FILE = "discovered_events.json"

def simulate_document_discovered():
    """
    Simulates the DocumentDiscovered event by scanning test-pdfs folder
    and creating event records for each PDF found
    """
    discovered_events = []
    
    # Check if test-pdfs folder exists
    if not os.path.exists(TEST_PDFS_DIR):
        print(f"❌ {TEST_PDFS_DIR} folder not found!")
        return
    
    # Find all PDFs in the test-pdfs folder
    pdf_files = list(Path(TEST_PDFS_DIR).glob("*.pdf"))
    
    if not pdf_files:
        print(f"❌ No PDFs found in {TEST_PDFS_DIR}")
        return
    
    print(f"✅ Found {len(pdf_files)} PDF(s):\n")
    
    for pdf_path in pdf_files:
        # Create a DocumentDiscovered event
        event = {
            "event_type": "DocumentDiscovered",
            "file_name": pdf_path.name,
            "file_path": str(pdf_path.absolute()),
            "file_size": os.path.getsize(pdf_path)
        }
        discovered_events.append(event)
        print(f"  📄 {pdf_path.name} ({event['file_size']} bytes)")
    
    print(f"\n🔄 Ready to process {len(discovered_events)} document(s) for extraction\n")
    
    return discovered_events

if __name__ == "__main__":
    events = simulate_document_discovered()
    if events:
        print("Events ready for DocumentExtracted processing:")
        print(json.dumps(events, indent=2))