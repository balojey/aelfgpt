import sys
sys.path.append('.')

from aelf import AElf
from pipeline.db.models.transaction import Transaction
from pipeline.db.dependencies import get_db_session, init_db
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError


url = "https://tdvw-test-node.aelf.io"
chain = AElf(url)


def get_transactions(block_hash: str) -> list:
    transactions = chain.get_transaction_results(block_hash)
    return transactions


def get_block_height() -> int:
    return chain.get_block_height()


def get_block_hash_by_height(block_height: int) -> str:
    block = chain.get_block_by_height(block_height)
    return block["BlockHash"]


def get_transaction_fees(logs: list[dict] | dict) -> list:
    transaction_fees = chain.get_transaction_fees(logs)


def save_transaction(transaction: dict, transaction_fees: list, session: Session) -> None:
    db_transaction = Transaction(
        id = transaction["TransactionId"],
        block_hash = transaction["BlockHash"],
        error = transaction["Error"],
        return_value = transaction["ReturnValue"],
        status = transaction["Status"],
        transaction_from = transaction["Transaction"]["From"],
        method_name = transaction["Transaction"]["MethodName"],
        ref_block_number = transaction["Transaction"]["RefBlockNumber"],
        ref_block_prefix = transaction["Transaction"]["RefBlockPrefix"],
        signature = transaction["Transaction"]["Signature"],
        transaction_to = transaction["Transaction"]["To"],
        transaction_size = transaction["TransactionSize"]
    )
    if transaction_fees and len(transaction_fees) != 0:
        try:
            db_transaction.transaction_fee_symbol = transaction_fees[0]["transaction_fee_symbol"]
            db_transaction.transaction_fee_amount = float(transaction_fees[0]["transaction_fee_amount"])
            db_transaction.resource_token_fee_symbol = transaction_fees[1]["resource_token_fee_symbol"]
            db_transaction.resource_token_fee_amount = float(transaction_fees[1]["resource_token_fee_amount"])
        except Exception:
            pass
    with session:
        try:
            session.add(db_transaction)
            session.commit()
            print("\n\n", db_transaction.dict())
        except IntegrityError:
            pass


def main():
    while True:
        block_height = get_block_height()
        block_hash = get_block_hash_by_height(block_height)
        block_transactions = get_transactions(block_hash)

        for transaction in block_transactions:
            transaction_fees = get_transaction_fees(transaction["Logs"])
            save_transaction(transaction, transaction_fees, get_db_session())


if __name__ == "__main__":
    init_db()
    main()