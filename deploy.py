from solcx import install_solc, set_solc_version, compile_standard
import json
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

# Install and set the Solidity compiler version
install_solc('0.8.0')
set_solc_version('0.8.0')

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

# Compile the Solidity code
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    }
)

with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# Get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"]["bytecode"]["object"]

# Get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# For connecting to ganache
w3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/2e984651218b450d9f215b45eab1eac3"))
chain_id = 1
my_address = "0xF14EE03b938F140b49760979532D13926931AEA3"
private_key = os.getenv("PRIVATE_KEY")

# Create the contract in python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

# Get the latest transaction
nonce = w3.eth.get_transaction_count(my_address)

# 1. Build a transaciton
# 2. Sign a transaction
# 3. Send a transaction
transaction = SimpleStorage.constructor().build_transaction({"chainId":chain_id, "from":my_address, "nonce":nonce})

signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)

# Send this signed transaction
print("Deploying contract...")
tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Deployed!")

## Working with the contract, you always need
# Contract Address
# Contract ABI
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
# Call -> Simulate making the call and getting a return value
# Transact -> Actually make a state change

# Initial value of favorite number
print(simple_storage.functions.retrieve().call())
print("Updating Contract...")

store_transaction = simple_storage.functions.store(15).build_transaction({"chainId":chain_id, "from":my_address, "nonce":nonce + 1})

signed_stored_txn = w3.eth.account.sign_transaction(store_transaction, private_key=private_key)

send_store_tx_hash = w3.eth.send_raw_transaction(signed_stored_txn.raw_transaction)

tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx_hash)

print("Updated!")
print(simple_storage.functions.retrieve().call())








