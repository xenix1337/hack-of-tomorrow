# FastAPI RPG API

This is a **FastAPI-based RPG API** that allows interaction with game entities such as **players, locations, quests, agents, and relationships**. It provides RESTful endpoints for managing these entities and supports interactions such as entering locations, speaking to agents, and leaving locations.

## Features
- 🚀 **FastAPI** framework for quick and efficient API development
- 🗄️ **SQLAlchemy** ORM for database management
- 📝 **Pydantic** models for data validation
- 🔄 **CRUD endpoints** for players, locations, quests, agents, and relationships
- 🎭 **Game interactions** like entering a location, talking to agents, and leaving locations
- 📡 **SQLite database** (default) but can be switched to any SQLAlchemy-supported database

---

## 📂 Project Structure
```
📦 fastapi-rpg-api
├── models.py          # Database models (SQLAlchemy)
├── schemas.py         # Pydantic schemas for request/response validation
├── main.py            # FastAPI application & API endpoints
├── game_settings.py   # Game settings configuration
├── lib/
│   ├── prompt_util.py # Utility functions for generating AI prompts
├── http_client.py     # HTTP client for external API calls
├── README.md          # Project documentation (this file)
└── test.db            # SQLite database (auto-generated)
```

---

## 🚀 Getting Started

### 1️⃣ **Installation**
Ensure you have **Python 3.9+** installed, then install dependencies:
```sh
pip install -r requirements.txt
```

### 2️⃣ **Run the API**
Start the FastAPI server:
```sh
uvicorn main:app --reload
```
By default, the server runs on **http://127.0.0.1:8000**

### 3️⃣ **Access API Docs** 📖
FastAPI provides automatic interactive documentation:
- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Redoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 📌 API Endpoints

### **🧑 Player Endpoints**
| Method | Endpoint | Description |
|--------|---------|-------------|
| `GET`  | `/players` | Get all players |
| `POST` | `/players` | Create a new player |

### **📍 Location Endpoints**
| Method | Endpoint | Description |
|--------|---------|-------------|
| `GET`  | `/locations` | Get all locations |
| `POST` | `/locations` | Create a new location |

### **🛡️ Quest Endpoints**
| Method | Endpoint | Description |
|--------|---------|-------------|
| `GET`  | `/quests` | Get all quests |
| `POST` | `/quests` | Create a new quest |

### **🤖 Agent Endpoints**
| Method | Endpoint | Description |
|--------|---------|-------------|
| `GET`  | `/agents` | Get all agents |
| `POST` | `/agents` | Create a new agent |

### **🔗 Relationship Endpoints**
| Method | Endpoint | Description |
|--------|---------|-------------|
| `GET`  | `/relationships` | Get all relationships |
| `POST` | `/relationships` | Create a new relationship |

### **🎭 Game Interaction Endpoints**
| Method | Endpoint | Description |
|--------|---------|-------------|
| `POST` | `/enterLocation` | Enter a location (returns agents, relationships, etc.) |
| `POST` | `/say` | Send a message to an agent |
| `POST` | `/leaveLocation` | Leave a location |

---

## 🔧 Database Setup
By default, the API uses **SQLite (`test.db`)**, but you can change the database in `main.py`:
```python
DATABASE_URL = "sqlite:///./test.db"
```
For **PostgreSQL** or **MySQL**, modify the `DATABASE_URL`:
```python
DATABASE_URL = "postgresql://user:password@localhost/dbname"
DATABASE_URL = "mysql+pymysql://user:password@localhost/dbname"
```
Run database migrations manually if needed:
```sh
from main import engine, Base
Base.metadata.create_all(bind=engine)
```
