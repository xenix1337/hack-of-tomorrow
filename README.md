# **Immersive NPC AI – AI-Driven Living Worlds for MMORPGs**  

## 🏰 **Overview**  
**Immersive NPC AI** is a SaaS solution that enables **NPCs to communicate, remember, and react dynamically** in MMORPGs. Our AI-powered NPCs share information with each other, creating **socially aware, immersive locations** where every interaction has consequences.  

Game developers can integrate our **API-first solution** to enhance NPC behavior, bringing depth and realism to their game worlds.  

---

✅ **AI-Agent NPCs** – Each NPC has memory, personality, and relationship tracking.  
✅ **Dynamic Social Interactions** – NPCs react to what they hear and share knowledge.  
✅ **Reputation System** – Player choices impact multiple NPCs through social networks.  
✅ **Event-Driven Gossip & Lore** – NPCs spread information organically across locations.  
✅ **Seamless API Integration** – Compatible with Unity, Unreal Engine, and custom engines.  

---

## 📦 **Installation & Setup**  


### ** Install Dependencies**  
```bash
pip install -r requirements.txt  # Python dependencies
npm install                      # If frontend or dashboard is included
```

### **Environment Variables**  
Create a `.env` file in the root directory of each module. There is `.env.example` file next to it to help you out!

---

## ⚙️ **Technology Stack**  
🧠 **AI Core:** LLM-based NPC agents (Fetch.ai)
🔗 **Backend:** Python (FastAPI)  
💾 **Database:** SQLite
💾 **Blockchain** EVM (Solidity)
🌐 **API:** REST

---

## 📌 **Roadmap**  
🚀 **v1.0 (MVP)** – Core NPC interactions & knowledge sharing ✅  
🤖 **v1.1** – Advanced memory & long-term reputation tracking  
📢 **v1.2** – Multi-location gossip network  
⚔️ **v2.0** – Faction-based AI behaviors & dynamic quest integration  


🎮 *Let's build truly living worlds together!* 🚀  

# Backend
```bash
python3 -m uvicorn main:app --reload
```

# Agents
```bash
python3 agents.py
python3 narrator.py
```

# Blockchain
## in `contracts`
`npm i`\
`npx hardhat node`\
`npx hardhat ignition deploy ./ignition/modules/Immersive.js --network localhost`\
## in backend
example `.env`
```
HARDHAT_URL=http://localhost:8545
CONTRACT_ADDRESS = 0x1234
PRIVATE_KEY = 0x1234
API_BASE_URL=http://localhost:7999
CORS_ORIGINS=http://127.0.0.1:5173
```

# Frontend
```bash
npm run dev
```
