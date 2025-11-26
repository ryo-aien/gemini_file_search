"""
End-to-end flow test for File Search API.

This test requires a valid GOOGLE_API_KEY in the environment.
It tests the full flow: Create Store -> Upload Document -> List Documents -> Delete.

To run: GOOGLE_API_KEY=your_key pytest tests/e2e/test_flow.py -v -s
"""

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app

# Skip if no API key
pytestmark = pytest.mark.skipif(
    not os.getenv("GOOGLE_API_KEY"), reason="GOOGLE_API_KEY not set"
)


@pytest.fixture
def client() -> TestClient:
    """Create test client with real API key."""
    return TestClient(app)


@pytest.fixture
def sample_file(tmp_path: Path) -> Path:
    """Create a sample text file for testing."""
    file_path = tmp_path / "test_document.txt"
    file_path.write_text("This is a test document for Gemini File Search API testing.")
    return file_path


def test_full_flow(client: TestClient, sample_file: Path) -> None:
    """
    Test the complete flow:
    1. Create a store
    2. Upload a document
    3. List documents
    4. Delete document
    5. Delete store
    """
    # Step 1: Create a store
    response = client.post(
        "/api/stores", json={"displayName": "E2E Test Store"}
    )
    assert response.status_code == 201
    store = response.json()
    assert "name" in store
    store_name = store["name"]
    store_id = store_name.split("/")[-1]
    print(f"\n✓ Created store: {store_name}")

    try:
        # Step 2: Upload a document
        with open(sample_file, "rb") as f:
            files = {"file": ("test_document.txt", f, "text/plain")}
            data = {
                "display_name": "Test Document",
                "max_tokens_per_chunk": 200,
                "max_overlap_tokens": 20,
            }
            response = client.post(
                f"/api/stores/{store_id}/upload", files=files, data=data
            )

        assert response.status_code == 202
        operation = response.json()
        assert "name" in operation
        print(f"✓ Started upload operation: {operation['name']}")

        # Step 3: List documents (may be pending initially)
        response = client.get(f"/api/stores/{store_id}/documents")
        assert response.status_code == 200
        documents_data = response.json()
        documents = documents_data.get("documents", [])
        print(f"✓ Found {len(documents)} document(s) in store")

        # Step 4: Delete documents (if any)
        for doc in documents:
            doc_id = doc["name"].split("/")[-1]
            response = client.delete(
                f"/api/stores/{store_id}/documents/{doc_id}?force=true"
            )
            assert response.status_code == 204
            print(f"✓ Deleted document: {doc['name']}")

    finally:
        # Step 5: Delete the store (cleanup)
        response = client.delete(f"/api/stores/{store_id}?force=true")
        assert response.status_code == 204
        print(f"✓ Deleted store: {store_name}")


def test_store_crud(client: TestClient) -> None:
    """Test basic CRUD operations for stores."""
    # Create
    response = client.post("/api/stores", json={"displayName": "CRUD Test Store"})
    assert response.status_code == 201
    store = response.json()
    store_id = store["name"].split("/")[-1]

    try:
        # Read (Get)
        response = client.get(f"/api/stores/{store_id}")
        assert response.status_code == 200
        retrieved_store = response.json()
        assert retrieved_store["name"] == store["name"]

        # List
        response = client.get("/api/stores")
        assert response.status_code == 200
        stores_data = response.json()
        assert "fileSearchStores" in stores_data

    finally:
        # Delete
        response = client.delete(f"/api/stores/{store_id}?force=true")
        assert response.status_code == 204
