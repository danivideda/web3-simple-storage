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
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.8.0",
)

# Output the compiled code into a JSON file
with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# Get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# Get ABI
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# Connecting to Rinkeby (Testnet global)
w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_INFURA_PROJECT_ID")))
chain_id = 4
my_address = "0xEddC298665C5D881750E17F01B0F27224a774b6b"
private_key = os.getenv("PRIVATE_KEY_RINKEBY")

# Create contract in python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
# Get latest transaction for nonce value
nonce = w3.eth.getTransactionCount(my_address)

# ----------------------
# 1. Build a transaction
# 2. Sign a transaction
# 3. Send a transaction
# ----------------------
# build transaction
transaction = SimpleStorage.constructor().buildTransaction(
    {
        "gasPrice": w3.eth.gas_price,
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce,
    }
)
# sign transaction
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
# send this signed transaction
print("Deploying contract...")
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
# just for awaiting block confirmation, a good practice before executing next code
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Deployed!")

# Working with the contract, you need:
# Contract address
# Contract ABI
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
# Call -> getting information without changing the state
# Transact -> actually make state change

# Initial value
print(simple_storage.functions.retrieve().call())
store_transaction = simple_storage.functions.store(15).buildTransaction(
    {
        "gasPrice": w3.eth.gas_price,
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce + 1,
    }
)
signed_store_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)
print("Updating contract...")
tx_hash = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Updated!")

print(simple_storage.functions.retrieve().call())