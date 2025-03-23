import json
from functools import lru_cache

from eth_account import Account
from web3 import Web3
from web3.middleware import SignAndSendRawMiddlewareBuilder

from game_settings import settings

CONTRACT_ABI = None

with open("../contracts/artifacts/contracts/Immersive.sol/Immersive.json") as f:
    CONTRACT_ABI = json.load(f)["abi"]

w3 = Web3(Web3.HTTPProvider(settings.HARDHAT_URL))
if w3.is_connected():
    print("-" * 50)
    print("Blockchain Connection Successful")
    print("-" * 50)
else:
    print("Blockchain Connection Failed")
    exit(-1)

acct = Account.from_key(settings.PRIVATE_KEY)
w3.middleware_onion.inject(SignAndSendRawMiddlewareBuilder.build(acct), layer=0)
w3.eth.default_account = acct.address

contract_interface = w3.eth.contract(
    address=settings.CONTRACT_ADDRESS, abi=CONTRACT_ABI
)


def blockchain_create_player(address: str, initialMoney: int):
    """
    Creates a new player on the blockchain by invoking the `createPlayer` function
    of the smart contract.

    Args:
        address (str): The blockchain address of the player.
        initialMoney (int): The initial amount of money to assign to the player.

    Returns:
        Transaction hash of the smart contract interaction.
    """
    return contract_interface.functions.createPlayer(address, initialMoney).transact()


def blockchain_give_item(address: str, itemdata: str):
    """
    Assigns an item to the specified player by invoking the `giveItem` function
    of the smart contract.

    Args:
        address (str): The blockchain address of the player to give the item to.
        itemdata (str): The item data to assign to the player.

    Returns:
        Transaction hash of the smart contract interaction.
    """
    return contract_interface.functions.giveItem(address, itemdata).transact()


def blockchain_destroy_item(itemId: int):
    """
    Destroys an item by invoking the `destroyItem` function of the smart contract.

    Args:
        itemId (int): The ID of the item to destroy.

    Returns:
        Transaction hash of the smart contract interaction.
    """
    return contract_interface.functions.destroyItem(itemId).transact()


def blockchain_give_money(address: str, amount: int):
    """
    Transfers money to the specified player by invoking the `giveMoney` function
    of the smart contract.

    Args:
        address (str): The blockchain address of the player to receive the money.
        amount (int): The amount of money to transfer.

    Returns:
        Transaction hash of the smart contract interaction.
    """
    return contract_interface.functions.giveMoney(address, amount).transact()


def blockchain_take_money(address: str, amount: int):
    """
    Takes money from the specified player by invoking the `takeMoney` function
    of the smart contract.

    Args:
        address (str): The blockchain address of the player to take the money from.
        amount (int): The amount of money to take.

    Returns:
        Transaction hash of the smart contract interaction.
    """
    return contract_interface.functions.takeMoney(address, amount).transact()


def blockchain_get_item(itemId: int):
    """
    Retrieves information about a specific item by invoking the `getItem` function
    of the smart contract.

    Args:
        itemId (int): The ID of the item to retrieve.

    Returns:
        The data associated with the item.
    """
    return contract_interface.functions.getItem(itemId).call()


def blockchain_get_items():
    """
    Retrieves a list of all items available on the blockchain by invoking the `getItems`
    function of the smart contract.

    Returns:
        A list of all items.
    """
    return contract_interface.functions.getItems().call()


def blockchain_get_player_data(address: str):
    """
    Retrieves data for a specific player by invoking the `getPlayerData` function
    of the smart contract.

    Args:
        address (str): The blockchain address of the player whose data is to be retrieved.

    Returns:
        The player data.
    """
    return contract_interface.functions.getPlayerData(
        w3.to_checksum_address(address)
    ).call()


def blockchain_get_player_item_ids(address: str):
    """
    Retrieves a list of item IDs that belong to a specific player by invoking the `getPlayerItemIds`
    function of the smart contract.

    Args:
        address (str): The blockchain address of the player.

    Returns:
        A list of item IDs owned by the player.
    """
    return contract_interface.functions.getPlayerItemIds(
        w3.to_checksum_address(address)
    ).call()


def blockchain_get_player_items(address: str):
    """
    Retrieves a list of items owned by a specific player, combining information from
    the `getItems` and `getPlayerItemIds` functions of the smart contract.

    Args:
        address (str): The blockchain address of the player.

    Returns:
        A list of tuples containing item IDs and item data for the player's items.
    """
    items = blockchain_get_items()
    item_ids = blockchain_get_player_item_ids(address)
    return [(i, items[i][0]) for i in item_ids]
