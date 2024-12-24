import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from app.main import app
from db.database import get_db

@pytest.fixture(scope="module")
def test_client():
    def override_get_db():
        db = MagicMock()
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client