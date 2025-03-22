const { buildModule } = require("@nomicfoundation/hardhat-ignition/modules");

const EverythingModule = buildModule("EverythingModule", (m) => {
  const token = m.contract("Everything");

  return { token };
});

module.exports = EverythingModule;