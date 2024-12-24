from fastapi import FastAPI, HTTPException, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from db.database import get_db
from app.crud import create_bank_account, transfer, get_balance, get_transfer_history, create_customer, check_customer_exists
from app.auth import get_current_user, create_access_token, Token
from pydantic import BaseModel
from app.utils import logger

app = FastAPI()

class AccountCreate(BaseModel):
    customer_id: int
    initial_deposit: float

class CustomerCreate(BaseModel):
    name: str

class TransferAmount(BaseModel):
    from_account_id: int
    to_account_id: int
    amount: float

@app.post("/token", response_model=Token)
async def login_for_access_token(
    request: Request, 
    form_data: OAuth2PasswordRequestForm = Depends()
):
    try:
        logger.info(f"[Token] Login attempt for username={form_data.username}")
        user_in_db = {"username": "user", "hashed_password": "fakehashedpassword"}
        if not user_in_db or not user_in_db["hashed_password"] == "fakehashed" + form_data.password:
            logger.warning(f"[Token] Invalid login attempt for username={form_data.username}")
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token = create_access_token(data={"sub": user_in_db["username"]})
        logger.info(f"[Token] Access token created for username={form_data.username}")
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"[Token] Error generating token for username={form_data.username}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/customers/")
async def create_customer_endpoint(
    customer: CustomerCreate, 
    db: AsyncSession = Depends(get_db)
):
    try:
        logger.info(f"[Create Customer] Creating new customer with name={customer.name}")
        new_customer = await create_customer(db, customer.name)
        logger.info(f"[Create Customer] Created customer with id={new_customer.id}")
        return {"customer_id": new_customer.id}
    except Exception as e:
        logger.error(f"[Create Customer] Error creating customer: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/accounts/")
async def create_new_account(
    request: Request,
    account: AccountCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user: str = Depends(get_current_user)
):
    try:
        logger.info(f"[Create Account] Attempt to create account with customer_id={account.customer_id}")
        customer = await check_customer_exists(db, account.customer_id)
        
        if customer is None:
            logger.error("[Create Account] Customer with given ID does not exist")
            raise HTTPException(status_code=404, detail="Customer does not exist")

        created_account = await create_bank_account(db, account.customer_id, account.initial_deposit)
        logger.info(f"[Create Account] Account created with account_id={created_account.id}")
        return {"account_id": created_account.id, "balance": created_account.balance}
    except Exception as e:
        logger.error(f"[Create Account] Error creating account for customer_id={account.customer_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/transfer/")
async def perform_transfer(
    request: Request,
    transferinfo: TransferAmount,
    db: AsyncSession = Depends(get_db), 
    current_user: str = Depends(get_current_user)
):
    try:
        logger.info(f"[Transfer] Attempting transfer: amount={transferinfo.amount} from account {transferinfo.from_account_id} to account {transferinfo.to_account_id}")
        record = await transfer(db, transferinfo.from_account_id, transferinfo.to_account_id, transferinfo.amount)
        logger.info(f"[Transfer] Transfer successful: amount={record.amount} from account {record.from_account_id} to account {record.to_account_id}")
        return {"from_account_id": record.from_account_id, "to_account_id": record.to_account_id, "amount": record.amount}
    except Exception as e:
        logger.error(f"[Transfer] Error during transfer from account {transferinfo.from_account_id} to {transferinfo.to_account_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/accounts/{account_id}/balance")
async def read_balance(
    account_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    try:
        logger.info(f"[Get Balance] Fetching balance for account_id={account_id}")
        balance = await get_balance(db, account_id)
        logger.info(f"[Get Balance] Balance for account_id={account_id} is {balance}")
        return {"balance": balance}
    except Exception as e:
        logger.error(f"[Get Balance] Error fetching balance for account_id={account_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

@app.get("/accounts/{account_id}/history")
async def read_transfer_history(
    account_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    try:
        logger.info(f"[Get History] Fetching transfer history for account_id={account_id}")
        history = await get_transfer_history(db, account_id)
        logger.info(f"[Get History] Transfer history for account_id={account_id}: {history}")
        return {"transfer_history": history}
    except Exception as e:
        logger.error(f"[Get History] Error fetching transfer history for account_id={account_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    