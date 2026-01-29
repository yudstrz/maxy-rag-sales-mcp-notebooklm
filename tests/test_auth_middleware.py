
import pytest
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.testclient import TestClient
from starlette.middleware import Middleware
from starlette.applications import Starlette
from starlette.routing import Route
from notebooklm_mcp.server import APIKeyAuthMiddleware, validate_api_key
import notebooklm_mcp.server as server

# Dummy endpoint for testing
async def homepage(request):
    return JSONResponse({"message": "Hello, world!"})

async def health(request):
    return JSONResponse({"status": "healthy"})

# Create a test app wrapped with the middleware
def create_app(api_key):
    # Determine the routes
    routes = [
        Route("/", homepage),
        Route("/health", health)
    ]
    
    # We need to monkeypatch the global _api_key in the server module
    # But since the middleware uses the global from the module, setting it on the module should work
    server._api_key = api_key
    
    middleware = [
        Middleware(APIKeyAuthMiddleware)
    ]
    
    return Starlette(routes=routes, middleware=middleware)

def test_no_api_key_configured():
    """If no API key is set globally, everything should be open."""
    server._api_key = None
    app = create_app(None)
    client = TestClient(app)
    
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, world!"}

    response = client.get("/health")
    assert response.status_code == 200

def test_api_key_configured_success():
    """With API key configured, correct header should pass."""
    key = "secret_key"
    app = create_app(key)
    client = TestClient(app)
    
    headers = {"Authorization": f"Bearer {key}"}
    response = client.get("/", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, world!"}

def test_api_key_configured_missing_header():
    """With API key configured, missing header should fail 401."""
    key = "secret_key"
    app = create_app(key)
    client = TestClient(app)
    
    response = client.get("/")
    assert response.status_code == 401
    assert "error" in response.json()

def test_api_key_configured_wrong_key():
    """With API key configured, wrong key should fail 401."""
    key = "secret_key"
    app = create_app(key)
    client = TestClient(app)
    
    headers = {"Authorization": "Bearer wrong_key"}
    response = client.get("/", headers=headers)
    assert response.status_code == 401
    assert response.json()["error"] == "Invalid API key"

def test_api_key_configured_invalid_format():
    """With API key configured, non-Bearer header should fail 401."""
    key = "secret_key"
    app = create_app(key)
    client = TestClient(app)
    
    headers = {"Authorization": f"Basic {key}"}
    response = client.get("/", headers=headers)
    assert response.status_code == 401

def test_health_check_exempt():
    """Health check should be accessible even without key."""
    key = "secret_key"
    app = create_app(key)
    client = TestClient(app)
    
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
