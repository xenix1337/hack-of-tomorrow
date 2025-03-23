// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

contract Immersive {
    address public ownerAddr;

    constructor() {
        ownerAddr = msg.sender;
    }

    struct Player {
        uint256 money;
        uint256 ownedItemsNum;
    }

    struct Item {
        string data;
        address owner;
    }

    Item[] public items;
    uint256 nextitemId = 0;

    mapping(address => Player) public addressToPlayer;

    function createPlayer(
        address addr,
        uint256 initialMoney
    ) public {
        require(msg.sender == ownerAddr, "Only owner can create player");
        addressToPlayer[addr] = Player(initialMoney, 0);
    }

    function giveMoney(address to, uint256 amount) public {
        require(msg.sender == ownerAddr, "Only owner can give money");
        addressToPlayer[to].money += amount;
    }

    function takeMoney(address from, uint256 amount) public {
        require(msg.sender == ownerAddr, "Only owner can take money");
        addressToPlayer[from].money -= amount;
    }

    function giveItem(address to, string memory data) public {
        require(msg.sender == ownerAddr, "Only owner can give item");
        items.push(Item(data, to));
        addressToPlayer[to].ownedItemsNum++;
        nextitemId++;
    }

    function destroyItem(uint256 itemId) public {
        require(msg.sender == ownerAddr, "Only owner can destroy item");
        require(items[itemId].owner != address(0), "Item does not exist");
        addressToPlayer[items[itemId].owner].ownedItemsNum--;
        delete items[itemId];
    }

    function getItem(uint256 itemId) public view returns (Item memory) {
        return items[itemId];
    }

    function getItems() public view returns (Item[] memory) {
        return items;
    }

    function getPlayerData(
        address player
    ) public view returns (uint256, uint256) {
        return (
            addressToPlayer[player].money,
            addressToPlayer[player].ownedItemsNum
        );
    }

    function getPlayerItemIds(
        address player
    ) public view returns (uint256[] memory) {
        uint256[] memory itemIds = new uint256[](
            addressToPlayer[player].ownedItemsNum
        );
        uint256 j = 0;
        for (uint256 i = 0; i < nextitemId; i++) {
            if (items[i].owner == player) {
                itemIds[j] = i;
                j++;
            }
        }
        return itemIds;
    }
}
