from unittest.mock import AsyncMock, patch, MagicMock
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import Customer, BankAccount, TransferHistory

client = TestClient(app)

@pytest.fixture(scope="module")
def token():
    with patch("app.auth.create_access_token") as mock_create_access_token:
        mock_create_access_token.return_value = "testtoken"
        
        response = client.post("/token", data={"username": "user", "password": "password"})
        print("Mock: ", response.json())
        return response.json()["access_token"]
    
@pytest.mark.asyncio
async def test_create_customer(token):
    mock_customer_data = Customer(id=1, name="Tanay")

    with patch('app.main.create_customer', new_callable=AsyncMock, return_value=mock_customer_data):
        
        headers = {"Authorization": f"Bearer {token}"}
        print("headers",headers)
        response = client.post("/customers/", json={"name": "Tanay"}, headers=headers)

        print("response: ", response.json())
        assert response.status_code == 200
        assert response.json() == {"customer_id": 1}


@pytest.mark.asyncio
async def test_create_customer_missing_name(token):
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/customers/", json={}, headers=headers)

    assert response.status_code == 422 
    assert "detail" in response.json() 


@pytest.mark.asyncio
async def test_create_account(token):
    mock_account_data = Customer(id=1, name="Tanay")

    with patch('app.main.check_customer_exists', new_callable=AsyncMock, return_value=mock_account_data):

        mock_account_data = BankAccount(id=1,customer_id=1, balance=100)
        print("mock_account_data:", mock_account_data)
        with patch('app.main.create_bank_account', new_callable=AsyncMock, return_value=mock_account_data):
            
            headers = {"Authorization": f"Bearer {token}"}
            print("headers",headers)

            response = client.post("/accounts/", json={"customer_id": 1, "initial_deposit": 100}, headers=headers)
            print("response: ", response.json())

            assert response.status_code == 200
            assert response.json() == {'account_id': 1, 'balance': 100}


@pytest.mark.asyncio
async def test_create_account_invalid_customer(token):
    with patch('app.main.check_customer_exists', new_callable=AsyncMock, return_value=None):
        headers = {"Authorization": f"Bearer {token}"}

        response = client.post("/accounts/", json={"customer_id": 999, "initial_deposit": 100}, headers=headers)

        assert response.status_code == 500 


@pytest.mark.asyncio
async def test_create_transfer(token):
    mock_transfer_data = TransferHistory(id=1,from_account_id=1,
            to_account_id=2,
            amount=100.0)

    with patch('app.main.transfer', new_callable=AsyncMock, return_value=mock_transfer_data):
        headers = {"Authorization": f"Bearer {token}"}
        print("headers",headers)

        response = client.post("/transfer/", json={"from_account_id": 1,
                                                    "to_account_id": 2,
                                                    "amount" : 100.0}, headers=headers)

        print("response: ", response.json())

        assert response.status_code == 200
        assert response.json() == {'from_account_id': 1, 'to_account_id': 2, 'amount': 100.0}


@pytest.mark.asyncio
async def test_create_transfer_incomplete(token):
    with patch('app.main.transfer', new_callable=AsyncMock):
        headers = {"Authorization": f"Bearer {token}"}
        print("headers",headers)

        response = client.post("/transfer/", json={"from_account_id": 1,
                                                    # "to_account_id": 2,
                                                    "amount" : 100.0}, headers=headers)

        print("response: ", response.json())

        assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_account_balance(token):
    with patch('app.main.get_balance', new_callable=AsyncMock, return_value=100):
        headers = {"Authorization": f"Bearer {token}"}
        print("headers",headers)

        response = client.get("/accounts/1/balance", headers=headers)

        print("response: ", response.json())
        assert response.status_code == 200
        assert response.json() == {'balance': 100}


@pytest.mark.asyncio
async def test_get_account_transfer_history(token):
    mock_transfer_data = [TransferHistory(id=1,from_account_id=1,
            to_account_id=2,
            amount=100.0)]
    with patch('app.main.get_transfer_history', new_callable=AsyncMock, return_value=mock_transfer_data):
        headers = {"Authorization": f"Bearer {token}"}
        print("headers",headers)

        response = client.get("/accounts/1/history", headers=headers)

        print("response: ", response.json())
        assert response.status_code == 200
        assert len(response.json()["transfer_history"]) > 0
