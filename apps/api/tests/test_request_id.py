import uuid


async def test_request_id_generated_in_response(client):
    """Test that X-Request-ID is generated and included in response headers."""
    response = await client.get("/healthz")
    assert response.status_code == 200
    request_id = response.headers.get("x-request-id")
    assert request_id is not None
    # Validate it's a valid UUID
    uuid.UUID(request_id)


async def test_request_id_preserved_when_sent(client):
    """Test that if X-Request-ID is sent in the request, same value is returned."""
    custom_id = "my-custom-request-id-12345"
    response = await client.get("/healthz", headers={"X-Request-ID": custom_id})
    assert response.status_code == 200
    assert response.headers.get("x-request-id") == custom_id
