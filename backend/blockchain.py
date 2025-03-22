import os
from web3 import Web3
from web3.middleware import SignAndSendRawMiddlewareBuilder
from eth_account import Account
from dotenv import load_dotenv
import json

load_dotenv()


HARDHAT_URL = os.getenv("HARDHAT_URL")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
CONTRACT_ABI = None

with open("../contracts/artifacts/contracts/Everything.sol/Everything.json") as f:
    CONTRACT_ABI = json.load(f)["abi"]

w3 = Web3(Web3.HTTPProvider(HARDHAT_URL))
if w3.is_connected():
    print("-" * 50)
    print("Connection Successful")
    print("-" * 50)
else:
    print("Blockchain Connection Failed")
    exit(-1)

acct = Account.from_key(os.getenv("PRIVATE_KEY"))
w3.middleware_onion.inject(SignAndSendRawMiddlewareBuilder.build(
    acct), layer=0)
w3.eth.default_account = acct.address

contract_interface = w3.eth.contract(
    address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)


def createPlayer(address, name, initaialMoney):
    return contract_interface.functions.createPlayer(address, name, initaialMoney).transact()


def giveItem(address, itemdata):
    return contract_interface.functions.giveItem(address, itemdata).transact()


def destroyItem(itemId):
    return contract_interface.functions.destroyItem(itemId).transact()


def giveMoney(address, amount):
    return contract_interface.functions.giveMoney(address, amount).transact()


def takeMoney(address, amount):
    return contract_interface.functions.takeMoney(address, amount).transact()


def getItem(itemId):
    return contract_interface.functions.getItem(itemId).call()


def getItems():
    return contract_interface.functions.getItems().call()


def getPlayerData(address):
    return contract_interface.functions.getPlayerData(
        w3.to_checksum_address(address)).call()


def getPlayerItemIds(address):
    return contract_interface.functions.getPlayerItemIds(
        w3.to_checksum_address(address)).call()


# createPlayer("0x70997970C51812dc3A010C7d01b50e0d17dc79C8", "Player1", 1000)
# giveItem("0x70997970C51812dc3A010C7d01b50e0d17dc79C8", "item1".encode())
# giveItem("0x70997970C51812dc3A010C7d01b50e0d17dc79C8", "item2".encode())
# destroyItem(0)
# giveMoney("0x70997970C51812dc3A010C7d01b50e0d17dc79C8", 100)
# takeMoney("0x70997970C51812dc3A010C7d01b50e0d17dc79C8", 20)
# print(getPlayerData("0x70997970C51812dc3A010C7d01b50e0d17dc79C8"))
# print(getItems())
# print(getPlayerItemIds("0x70997970C51812dc3A010C7d01b50e0d17dc79C8"))
# print(getItem(1))
