const { buildModule } = require("@nomicfoundation/hardhat-ignition/modules");

const ImmersiveModule = buildModule("ImmersiveModule", (m) => {
  const immersive = m.contract("Immersive");

  m.call(immersive, "giveMoney", ["0x70997970C51812dc3A010C7d01b50e0d17dc79C8", 100]);
  m.call(immersive, "giveItem", ["0x70997970C51812dc3A010C7d01b50e0d17dc79C8", "bow"], { "id": "bow" });
  m.call(immersive, "giveItem", ["0x70997970C51812dc3A010C7d01b50e0d17dc79C8", "health potion"], { "id": "potion" });

  return { immersive };
});

module.exports = ImmersiveModule;
