from web3 import Web3, Account
import json
from web3.middleware import geth_poa_middleware
from web3.exceptions import ExtraDataLengthError
from dotenv import load_dotenv
from tqdm import tqdm
import os

load_dotenv()
CELO_PRIVATE_KEY = os.getenv('CELO_PRIVATE_KEY')

# Load ABI from the JSON file
with open("certificates_abi.json") as f:
    contract_abi = json.load(f)

provider_url = "https://alfajores-forno.celo-testnet.org"
web3 = Web3(Web3.HTTPProvider(provider_url))

deployer = web3.eth.account.from_key(CELO_PRIVATE_KEY)
account = deployer
print(f"Connected to Celo network. Address: {deployer.address}")


web3.middleware_onion.inject(geth_poa_middleware, layer=0)  
contract_abi = contract_abi
contract_address = "0xAF8a7D5756D992b9E7f119d108aD36cA5cF2bb4a"
certificate_contract = web3.eth.contract(address=contract_address, abi=contract_abi)

def get_balance(account_address, contract_address, token="CELO"):
    # Get cUSD contract
    cusd_contract = certificate_contract
    if token == "CELO":
        return web3.from_wei(web3.eth.get_balance(account_address), 'ether')
    elif token == "cUSD":
        amount = cusd_contract.functions.balanceOf(account_address).call()
        balance = web3.from_wei(amount, 'ether')
        return balance
    else:
        raise ValueError("Invalid token type")

def issue_certificate(name, issuer, issue_date):
    # Encode the function call to issueCertificate
    transaction = certificate_contract.functions.issueCertificate(name, issuer, issue_date).build_transaction({
        'chainId': 44787,  # Alfajores testnet chainId
        'gas': 3000000,    # Adjust gas value as needed
        'gasPrice': web3.to_wei('10', 'gwei'),  # Adjust gasPrice as needed
        "nonce": web3.eth.get_transaction_count(account.address),
    })

    # Sign the transaction with the account's private key
    signed_transaction = web3.eth.account.sign_transaction(transaction, CELO_PRIVATE_KEY)

    # Send the signed transaction
    tx_hash = web3.eth.send_raw_transaction(signed_transaction.rawTransaction)

    # Wait for the transaction to be mined
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

    # Check if the transaction was successful
    if tx_receipt['status'] == 1:
        # Fetch the certificate data from the blockchain using the event
        certificate_data = fetch_certificate_data(tx_receipt['transactionHash'])
        if certificate_data:
            print("Certificate issued successfully!")
            return certificate_data
        else:
            print("Failed to fetch certificate data.")
    else:
        print("Failed to issue certificate.")
        return None
def fetch_certificate_data(tx_hash):
    # Find the certificate data by searching for the event in the transaction receipt
    tx_receipt = web3.eth.get_transaction_receipt(tx_hash)
    for event in certificate_contract.events.CertificateIssued().process_receipt(tx_receipt):
        certificate_data = {
            "id": event.args.id.hex(),
            "name": event.args.name,
            "issuer": event.args.issuer,
            "issuerAddress": event.args.issuerAddress,
            "issueDate": event.args.issueDate,
        }
        return certificate_data

    return None
def get_certificate(index):
    try:
        certificate = certificate_contract.functions.getCertificate(index).call()
        # certificate is a tuple containing (certificateId, name, issuer, issue_date, issuer_address)
        certificateId, name, issuer, issuer_address, issue_date = certificate
        print(f"Certificate ID: {certificateId}, Name: {name}, Issuer: {issuer}, Issuer address: {issuer_address}, Issue Date: {issue_date}")
    except Exception as e:
        print(f"Error retrieving certificate: {e}")

def verify_certificate(certificate_id):
    try:
        result = certificate_contract.functions.verifyCertificate(certificate_id).call()
        if result:
            print("Certificate is valid.")
        else:
            print("Certificate not found or invalid.")
    except Exception as e:
        print(f"Error verifying certificate: {e}")
if __name__ == "__main__":
    # Example usage
    issue_certificate("Cliff Omollo", "New York Giants", 198256998)
    # get_certificate(0)  # Adjust the certificate index as needed