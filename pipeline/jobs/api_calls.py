from pprint import pprint
from aelf import AElf, AElfToolkit


url = "https://tdvw-test-node.aelf.io"

chain = AElf(url)
toolkit = AElfToolkit(url, "")

block_height = chain.get_block_height()
block = chain.get_block_by_height(block_height=block_height)
block_hash = block["BlockHash"]
transaction_results = chain.get_transaction_results(block_hash=block_hash)
# print("\n\nTransaction Results: ", end="")
# pprint(transaction_results)
# print("\n\n")


for transaction_result in transaction_results:
    transaction_id = transaction_result["TransactionId"]
    transaction = chain.get_transaction_result(transaction_id=transaction_id)
    # pprint(transaction)
    # print("\n\n")
    # transaction_fees = chain.get_transaction_fees(transaction["Logs"])
    # pprint(transaction_fees)
    # print("\n\n")
    address = chain.get_formatted_address(transaction["Transaction"]["From"])
    pprint(address)
    symbol, address, _ = address.split("_")
    balance = toolkit.get_balance(symbol, address)
    print(balance)
    print("\n\n")

# peers = chain.get_peers()
# pprint(peers)
