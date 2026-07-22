import httpx
import pytest

from bioiga.api.server import app


@pytest.fixture
async def async_client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.mark.anyio
async def test_health_check(async_client):
    response = await async_client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.anyio
async def test_status_endpoint(async_client):
    response = await async_client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ["idle", "running", "completed", "stopped", "error"]


@pytest.mark.anyio
async def test_simulation_workflow(async_client):
    run_resp = await async_client.post(
        "/api/run",
        json={
            "algorithm": "MPMBPSO",
            "generations": 5,
            "pop_size": 10,
            "num_islands": 2,
            "num_variables": 20,
        },
    )
    assert run_resp.status_code == 200

    stop_resp = await async_client.post("/api/stop")
    assert stop_resp.status_code == 200
