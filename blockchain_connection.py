from web3 import Web3
import json

#Initialize the connection to the local blockchain
#local blockchain used for this project is 127.0.0.1:7545
w3 = Web3 (Web3.HTTPProvider("http://127.0.0.1:7545"))

#Load the ABI(Application Binary Interface(VotingSystem.json)) from Truffle build folder
with open ('build/contracts/VotingSystem.json') as f:
    voting_system_abi = json.load(f)['abi']

#Set the contract address will use one contract address
contract_address = '0xF0904668F9d115A2997451a560ec7A3c26af3F33'

#Create an instance of the contract
voting_system_contract = w3.eth.contract(address=contract_address, abi=voting_system_abi)

