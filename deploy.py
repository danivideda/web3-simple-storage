from solcx import compile_standard, install_solc
import json
from web3 import Web3
from web3._utils.filters import TransactionFilter
import os
from dotenv import load_dotenv

load_dotenv()

with open("SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

# Compile Solidity
install_solc("0.8.0")
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {"outputSelection": {"*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}}},
    },
    solc_version="0.8.0",
)

# Output the compiled code into a JSON file
with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# Get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"]["bytecode"]["object"]

# Get ABI
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# Connecting to Rinkeby (Testnet global)
w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_INFURA_PROJECT_ID")))
chain_id = 4
my_address = "0xEddC298665C5D881750E17F01B0F27224a774b6b"
private_key = os.getenv("PRIVATE_KEY_RINKEBY")

# Working with NEWLY CREATED contract, you need:
# 1. Contract bytecode
# 2. Contract ABI
SimpleStorage = w3.eth.contract(bytecode=bytecode, abi=abi)  # Create contract in python
nonce = w3.eth.getTransactionCount(my_address)  # Get latest transaction for nonce value later

# ----------------------
# 1. Build a transaction
# 2. Sign a transaction
# 3. Send a transaction
# ----------------------

transaction = SimpleStorage.constructor().buildTransaction(  # build transaction
    {
        "gasPrice": w3.eth.gas_price,
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce,
    }
)

signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)  # sign transaction
print("Deploying contract...")
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)  # send this signed transaction
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)  # awaiting block confirmation
print("Deployed!")

# Working with ALREADY DEPLOYED contract, you need:
# Contract address
# Contract ABI
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

# Notes: -----------------------------------------------
# Call -> getting information without changing the state
# Transact -> actually make state change
# ------------------------------------------------------
print(
    simple_storage.functions.retrieve().call()
)  # This is a call function, so it doesn't need to be a signed-transaction

# ----------------------
# 1. Build a transaction
# 2. Sign a transaction
# 3. Send a transaction
# ----------------------

store_transaction = simple_storage.functions.store(15).buildTransaction(  # build transaction
    {
        "gasPrice": w3.eth.gas_price,
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce + 1,
    }
)
signed_store_txn = w3.eth.account.sign_transaction(store_transaction, private_key=private_key)  # sign this transaction
print("Updating contract...")
tx_hash = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)  # send this transaction
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)  # wait for block confirmation
print("Updated!")

print(simple_storage.functions.retrieve().call())
