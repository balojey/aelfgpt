import sys
sys.path.append('.')

from aelf import AElf
from pipeline.db.models.transaction import Transaction
from pipeline.db.dependencies import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import select
import asyncio


url = "https://tdvw-test-node.aelf.io"
chain = AElf(url)


async def get_transactions(block_hash: str) -> list:
    transactions = chain.get_transaction_results(block_hash)
    return transactions


async def get_block_height() -> int:
    return chain.get_block_height()


async def get_block_hash_by_height(block_height: int) -> str:
    block = chain.get_block_by_height(block_height)
    return block["BlockHash"]


async def save_transaction(transaction: dict, session: AsyncSession) -> None:
    db_transaction = Transaction(
        id = transaction["TransactionId"],
        block_hash = transaction["BlockHash"],
        error = transaction["Error"],
        return_value = transaction["ReturnValue"],
        status = transaction["Status"],
        transaction_from = transaction["Transaction"]["From"],
        method_name = transaction["Transaction"]["MethodName"],
        method_params = transaction["Transaction"]["Params"],
        ref_block_number = transaction["Transaction"]["RefBlockNumber"],
        ref_block_prefix = transaction["Transaction"]["RefBlockPrefix"],
        signature = transaction["Transaction"]["Signature"],
        transaction_to = transaction["Transaction"]["To"],
        transaction_size = transaction["TransactionSize"],
        logs = transaction["Logs"],
    )
    session.add(db_transaction)


async def get_transaction(transaction_id: str, session: AsyncSession) -> Transaction:
    transaction = await session.execute(
        select(Transaction).where(Transaction.id == transaction_id)
    )
    return transaction.scalars().first()


async def main():
    while True:
        block_height = await get_block_height()
        block_hash = await get_block_hash_by_height(block_height)
        block_transactions = await get_transactions(block_hash)

        for transaction in block_transactions:
            await save_transaction(transaction, get_db_session())
    # print(await get_transaction("870b92860f1bcc65e67ded8ee70d21322cfb16337781e2bbb7b4e81b729c423e", get_db_session()))




if __name__ == "__main__":
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
    # loop.close()
    asyncio.run(main())