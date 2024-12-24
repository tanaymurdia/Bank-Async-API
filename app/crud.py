from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from app.models import Customer, BankAccount, TransferHistory
from fastapi import HTTPException, status
from sqlalchemy.orm import selectinload
from sqlalchemy import select, update
from sqlalchemy import func

async def create_customer(session: AsyncSession, name: str):
    new_customer = Customer(name=name)
    session.add(new_customer)
    await session.commit()
    await session.refresh(new_customer)
    return new_customer

async def check_customer_exists(session: AsyncSession, customer_id: int):
    result = await session.execute(select(Customer).filter_by(id=customer_id))
    return result.scalar_one_or_none()

async def create_bank_account(session: AsyncSession, customer_id: int, initial_deposit: float):
    customer = await check_customer_exists(session, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer does not exist")

    account = BankAccount(customer_id=customer_id, balance=initial_deposit)
    session.add(account)
    await session.commit()
    await session.refresh(account)
    return account

async def transfer(session: AsyncSession, from_account_id: int, to_account_id: int, amount: float):
    async with session.begin():
        statement = select(BankAccount).where(BankAccount.id.in_([from_account_id, to_account_id])).with_for_update()
        results = await session.execute(statement)
        accounts = results.scalars().all()

        if len(accounts) != 2:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

        account_map = {account.id: account for account in accounts}
        from_account = account_map[from_account_id]
        to_account = account_map[to_account_id]

        if from_account.balance < amount:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient funds")

        from_account.balance -= amount
        to_account.balance += amount

        transfer_record = TransferHistory(
            from_account_id=from_account_id,
            to_account_id=to_account_id,
            amount=amount,
            timestamp=func.now()
        )
        session.add(transfer_record)
    return transfer_record

async def get_balance(session: AsyncSession, account_id: int):
    account = await session.get(BankAccount, account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return account.balance

async def get_transfer_history(session: AsyncSession, account_id: int):
    query = select(TransferHistory).where(
        (TransferHistory.from_account_id == account_id) |
        (TransferHistory.to_account_id == account_id)
    )
    result = await session.execute(query)
    return result.scalars().all()